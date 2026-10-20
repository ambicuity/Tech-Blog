"""Proving tests for the GenAI-conventions instrumentation.

Everything is measured against the stub provider and the pinned convention
snapshot (convention.py); no claim depends on a real model call.

Versions: opentelemetry-sdk 1.45.1, Python 3.12.
"""

from decimal import Decimal

import pytest

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from convention import (
    CONVENTION_COMMIT,
    KNOWN_CURRENT_ATTRS,
    LEGACY_RENAMES,
    find_legacy,
)
from genai_observe import (
    ChatUsage,
    CostLedger,
    DualReadDashboard,
    GenAIObserver,
    Price,
    StubProvider,
    check_conformance,
    normalize_legacy,
)


@pytest.fixture()
def harness():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    observer = GenAIObserver(
        tracer=provider.get_tracer("test"),
        meter=meter_provider.get_meter("test"),
    )
    return observer, exporter, reader


USAGE = ChatUsage(
    input_tokens=1200,
    output_tokens=300,
    cache_read_input_tokens=400,
    cache_write_input_tokens=100,
    reasoning_output_tokens=60,
)


def run_chat(harness, capture_content=False, **kwargs):
    observer, exporter, reader = harness
    observer._capture_content = capture_content
    provider = StubProvider("stub-model-1", USAGE)
    result = observer.chat(
        provider, "chat", [{"role": "user", "content": "hi"}],
        provider_name="stub", **kwargs,
    )
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    return result, spans[0], reader


# --- The contract -----------------------------------------------------------


def test_convention_snapshot_is_pinned():
    # The names the code emits must trace to one verifiable commit.
    assert CONVENTION_COMMIT == "547934afa90a34298441caf80c43b27255c3a292"


def test_span_name_is_operation_plus_model(harness):
    _, span, _ = run_chat(harness)
    # client-inference.md: span name SHOULD be
    # "{gen_ai.operation.name} {gen_ai.request.model}".
    assert span.name == "chat stub-model-1"


def test_required_attributes_present(harness):
    _, span, _ = run_chat(harness)
    attrs = dict(span.attributes)
    assert attrs["gen_ai.operation.name"] == "chat"
    assert attrs["gen_ai.provider.name"] == "stub"
    assert check_conformance(attrs) == []


def test_emitted_attributes_all_current(harness):
    _, span, _ = run_chat(harness)
    attrs = dict(span.attributes)
    unknown = {a for a in attrs if a not in KNOWN_CURRENT_ATTRS}
    assert unknown == set(), f"emitted non-current attributes: {unknown}"
    assert find_legacy(attrs) == {}


def test_legacy_fixture_is_caught():
    # A span from an instrumentation built on the old names must fail loudly.
    legacy = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "openai",  # v1.36.0 name
        "gen_ai.usage.input_tokens": 1200,
    }
    problems = check_conformance(legacy)
    assert any("gen_ai.system" in p and "gen_ai.provider.name" in p for p in problems)


def test_missing_required_is_caught():
    problems = check_conformance({"gen_ai.operation.name": "chat"})
    assert problems == ["missing required attribute gen_ai.provider.name"]


def test_metric_recorded(harness):
    _, _, reader = run_chat(harness)
    data = reader.get_metrics_data()
    names = {
        m.name
        for rm in data.resource_metrics
        for sm in rm.scope_metrics
        for m in sm.metrics
    }
    assert "gen_ai.client.inference.duration" in names


# --- The three production mistakes ------------------------------------------


def test_prompts_off_by_default(harness):
    # Mistake 2: recording prompts/responses without opting in.
    _, span, _ = run_chat(harness, capture_content=False)
    attrs = dict(span.attributes)
    assert "gen_ai.input.messages" not in attrs
    assert "gen_ai.output.messages" not in attrs
    assert "gen_ai.system_instructions" not in attrs


def test_prompts_opt_in_emits_them(harness):
    _, span, _ = run_chat(harness, capture_content=True)
    attrs = dict(span.attributes)
    assert "gen_ai.input.messages" in attrs
    assert "gen_ai.output.messages" in attrs


def test_cost_includes_cache_and_reasoning_tokens():
    # Mistake 3: a naive input+output sum under-counts when cache and
    # reasoning tokens are priced differently. 1200 in (400 cached at a
    # discount, 100 cache writes) + 300 out (60 reasoning).
    ledger = CostLedger(
        {("stub", "stub-model-1"): Price(
            input=Decimal("1.00"), output=Decimal("3.00"),
            cache_read_input=Decimal("0.10"), cache_write_input=Decimal("1.25"),
            reasoning_output=Decimal("3.00"))},
        prices_as_of="2026-10-20",
    )
    cost = ledger.cost("stub", "stub-model-1", USAGE)
    plain_in, plain_out = Decimal(700), Decimal(240)
    expected = (plain_in * Decimal("1.00") + Decimal(400) * Decimal("0.10")
                + Decimal(100) * Decimal("1.25")
                + plain_out * Decimal("3.00") + Decimal(60) * Decimal("3.00")) / Decimal(1_000_000)
    assert cost == expected


def test_unknown_model_raises_not_silent_zero():
    ledger = CostLedger({}, prices_as_of="2026-10-20")
    with pytest.raises(KeyError):
        ledger.cost("stub", "no-such-model", USAGE)


# --- Migration --------------------------------------------------------------


def test_legacy_names_normalize_to_current():
    legacy = {
        "gen_ai.system": "openai",
        "gen_ai.client.operation.time_to_first_chunk": 0.4,
        "gen_ai.usage.cache_creation.input_tokens": 50,
    }
    mapped = normalize_legacy(legacy)
    assert mapped == {
        "gen_ai.provider.name": "openai",
        "gen_ai.client.inference.time_to_first_chunk": 0.4,
        "gen_ai.usage.cache_write.input_tokens": 50,
    }


def test_dual_read_dashboard_merges_both_eras():
    dash = DualReadDashboard()
    merged = dash.read(
        new_attrs={"gen_ai.provider.name": "openai", "gen_ai.usage.input_tokens": 1200},
        legacy_attrs={"gen_ai.system": "openai"},
    )
    # Current names win on conflict; legacy names are gone.
    assert merged["gen_ai.provider.name"] == "openai"
    assert "gen_ai.system" not in merged


def test_known_renames_covered():
    # Every rename the article cites must have a mapping the collector can use.
    for legacy in ("gen_ai.system",
                   "gen_ai.client.operation.time_to_first_chunk",
                   "gen_ai.usage.cache_creation.input_tokens"):
        assert legacy in LEGACY_RENAMES


# --- Error handling ----------------------------------------------------------


def test_metric_attributes_stay_scalar_with_content_captured(harness):
    # Message content rides the span; the histogram must not receive
    # non-scalar attribute values.
    _, span, reader = run_chat(harness, capture_content=True)
    data = reader.get_metrics_data()
    for rm in data.resource_metrics:
        for sm in rm.scope_metrics:
            for m in sm.metrics:
                for dp in m.data.data_points:
                    for v in dp.attributes.values():
                        assert isinstance(v, (str, bool, int, float)), v
    assert "gen_ai.input.messages" in dict(span.attributes)


def test_failed_call_records_error(harness):
    from opentelemetry.trace import StatusCode

    observer, exporter, _ = harness

    class Failing(StubProvider):
        def chat(self, messages):
            raise ConnectionError("provider down")

    with pytest.raises(ConnectionError):
        observer.chat(Failing("stub-model-1", USAGE), "chat", [],
                      provider_name="stub")
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code == StatusCode.ERROR
