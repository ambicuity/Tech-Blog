"""Instrument LLM chat calls with the OpenTelemetry GenAI conventions.

Emit exactly what the pinned convention snapshot says (see convention.py);
nothing the spec reserves as Opt-In is recorded unless the caller opts in.

Versions: opentelemetry-sdk 1.45.1, Python 3.12.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import Decimal

from opentelemetry import trace
from opentelemetry.metrics import get_meter
from opentelemetry.trace import Status, StatusCode

from convention import (
    KNOWN_CURRENT_METRICS,
    LEGACY_RENAMES,
    find_legacy,
    missing_required,
    unknown,
)

METRIC_DURATION = "gen_ai.client.inference.duration"
assert METRIC_DURATION in KNOWN_CURRENT_METRICS


@dataclass(frozen=True)
class ChatUsage:
    """Token counts as reported by the provider for one call."""

    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    reasoning_output_tokens: int = 0
    finish_reasons: tuple[str, ...] = ("stop",)


@dataclass(frozen=True)
class ChatResult:
    text: str
    usage: ChatUsage
    response_model: str


class StubProvider:
    """A deterministic stand-in for a model provider.

    It never calls a network or a real model; the token counts it returns are
    the harness's fixture data. Used so every claim about the instrumentation
    is measured, not imagined.
    """

    def __init__(self, model: str, usage: ChatUsage, latency_s: float = 0.25):
        self.model = model
        self.usage = usage
        self.latency_s = latency_s

    def chat(self, messages: list[dict]) -> ChatResult:
        time.sleep(self.latency_s)
        return ChatResult(
            text="stubbed reply",
            usage=self.usage,
            response_model=self.model,
        )


class GenAIObserver:
    """Emit GenAI-convention spans and metrics around a provider call.

    Prompts and completions are Opt-In attributes in the conventions, so
    ``capture_content`` defaults to False: with it off, no message content
    ever lands on a span, and a collector never has to redact what was never
    recorded.
    """

    def __init__(self, tracer=None, meter=None, capture_content: bool = False):
        self._tracer = tracer or trace.get_tracer("genai_observe")
        self._meter = meter or get_meter("genai_observe")
        self._capture_content = capture_content
        self._duration = self._meter.create_histogram(
            name=METRIC_DURATION,
            unit="s",
            description="Duration of a GenAI inference call",
        )

    def chat(self, provider: StubProvider, operation: str, messages: list[dict],
             **request_options) -> ChatResult:
        request_model = provider.model
        span_name = f"{operation} {request_model}"  # SHOULD per client-inference.md
        attrs = {
            "gen_ai.operation.name": operation,
            "gen_ai.provider.name": request_options.pop("provider_name", "stub"),
            "gen_ai.request.model": request_model,
        }
        if "temperature" in request_options:
            attrs["gen_ai.request.temperature"] = request_options["temperature"]
        if "max_tokens" in request_options:
            attrs["gen_ai.request.max_tokens"] = request_options["max_tokens"]
        if self._capture_content:
            attrs["gen_ai.input.messages"] = messages

        start = time.perf_counter()
        with self._tracer.start_as_current_span(
            span_name, attributes=attrs
        ) as span:
            try:
                result = provider.chat(messages)
            except Exception as exc:  # never let a failed call vanish silently
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            usage = result.usage
            span.set_attribute("gen_ai.response.model", result.response_model)
            span.set_attribute("gen_ai.response.id", f"stub-{id(result)}")
            span.set_attribute(
                "gen_ai.response.finish_reasons", list(usage.finish_reasons)
            )
            span.set_attribute("gen_ai.usage.input_tokens", usage.input_tokens)
            span.set_attribute("gen_ai.usage.output_tokens", usage.output_tokens)
            # Recommended "when available and non-zero": emit them so cost
            # accounting downstream cannot silently miss them.
            for name, value in (
                ("gen_ai.usage.cache_read.input_tokens", usage.cache_read_input_tokens),
                ("gen_ai.usage.cache_write.input_tokens", usage.cache_write_input_tokens),
                ("gen_ai.usage.reasoning.output_tokens", usage.reasoning_output_tokens),
            ):
                if value:
                    span.set_attribute(name, value)
            if self._capture_content:
                span.set_attribute("gen_ai.output.messages", result.text)
            # Metric attributes must be scalars: message content rides the
            # span only, never the histogram.
            metric_attrs = {
                k: v for k, v in attrs.items()
                if k in ("gen_ai.operation.name", "gen_ai.provider.name",
                         "gen_ai.request.model")
            }
            self._duration.record(time.perf_counter() - start, metric_attrs)
            return result


@dataclass(frozen=True)
class Price:
    """USD per million tokens, read from the provider pricing page.

    Each token class gets its own rate: reasoning and cache tokens are not
    priced the same as plain input/output on every provider.
    """

    input: Decimal
    output: Decimal
    cache_read_input: Decimal
    cache_write_input: Decimal
    reasoning_output: Decimal


class CostLedger:
    """Derive cost from span token counts and a dated price table.

    The conventions record tokens, never currency, because prices move and
    vary by contract. An unknown (provider, model) pair raises instead of
    pricing at zero: a silent $0 is how a budget alert goes blind.

    Assumption, stated plainly: the cache and reasoning breakdowns are
    subsets of the input/output totals (the provider reports X cached out of
    Y input tokens), so plain input is total minus the breakdowns. If your
    provider reports them as separate counters, adjust the subtraction.
    """

    def __init__(self, prices: dict[tuple[str, str], Price], prices_as_of: str):
        self._prices = prices
        self.prices_as_of = prices_as_of

    def cost(self, provider: str, model: str, usage: ChatUsage) -> Decimal:
        price = self._prices.get((provider, model))
        if price is None:
            raise KeyError(f"no price for {(provider, model)}; add it before estimating")
        million = Decimal(1_000_000)
        plain_input = Decimal(usage.input_tokens - usage.cache_read_input_tokens
                              - usage.cache_write_input_tokens)
        plain_output = Decimal(usage.output_tokens - usage.reasoning_output_tokens)
        return (
            plain_input / million * price.input
            + Decimal(usage.cache_read_input_tokens) / million * price.cache_read_input
            + Decimal(usage.cache_write_input_tokens) / million * price.cache_write_input
            + plain_output / million * price.output
            + Decimal(usage.reasoning_output_tokens) / million * price.reasoning_output
        )


def normalize_legacy(attributes: dict) -> dict:
    """Collector-side dual-read mapping: rename legacy attributes to current.

    Emit-side stays pure (only current names); the collector applies this map
    so dashboards can query one name while old instrumentations are retired.
    """
    return {LEGACY_RENAMES.get(k, k): v for k, v in attributes.items()}


def check_conformance(attributes: dict) -> list[str]:
    """Human-readable conformance report for one span's attributes."""
    problems = []
    for missing in missing_required(attributes):
        problems.append(f"missing required attribute {missing}")
    for legacy, current in find_legacy(attributes).items():
        problems.append(f"legacy attribute {legacy}; use {current}")
    for name in unknown(attributes):
        problems.append(f"unknown attribute {name} not in the pinned snapshot")
    return problems


@dataclass
class DualReadDashboard:
    """Merge legacy and current readings so one dashboard sees both eras."""

    def read(self, new_attrs: dict, legacy_attrs: dict) -> dict:
        merged = normalize_legacy(dict(legacy_attrs))
        merged.update(new_attrs)  # current names win on conflict
        return merged
