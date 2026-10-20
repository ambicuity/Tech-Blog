"""Pinned snapshot of the OpenTelemetry GenAI semantic conventions.

The conventions live in the dedicated repository
https://github.com/open-telemetry/semantic-conventions-genai
(opened 2026-10-20). At that date the repo had zero tagged releases and every
gen_ai.* signal was marked Development, so "current" means the main-branch
state on that day. Pin the commit, not the repo: the names move.

Snapshot date: 2026-10-20
Commit: 547934afa90a34298441caf80c43b27255c3a292
"""

CONVENTION_COMMIT = "547934afa90a34298441caf80c43b27255c3a292"
CONVENTION_SNAPSHOT_DATE = "2026-10-20"

# Span type for a client-side inference operation, per
# docs/gen-ai/client-inference.md. Span name SHOULD be
# "{gen_ai.operation.name} {gen_ai.request.model}".
SPAN_CLIENT_INFERENCE = "gen_ai.client.inference"

# Required attributes on the client inference span.
REQUIRED_ATTRS = frozenset({
    "gen_ai.operation.name",
    "gen_ai.provider.name",
})

# Attributes the instrumentation emits when the data is available
# (Recommended / Conditionally Required levels in client-inference.md).
KNOWN_CURRENT_ATTRS = frozenset({
    "gen_ai.operation.name",
    "gen_ai.provider.name",
    "gen_ai.request.model",
    "gen_ai.response.model",
    "gen_ai.response.id",
    "gen_ai.response.finish_reasons",
    "gen_ai.request.temperature",
    "gen_ai.request.max_tokens",
    "gen_ai.request.stream",
    "gen_ai.request.choice.count",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.usage.cache_write.input_tokens",
    "gen_ai.usage.reasoning.output_tokens",
    "gen_ai.usage.text.input_tokens",
    "gen_ai.usage.text.output_tokens",
    # Opt-In: prompt/response content. Emitted only when capture is on.
    "gen_ai.input.messages",
    "gen_ai.output.messages",
    "gen_ai.system_instructions",
    "gen_ai.tool.definitions",
})

# Metrics the instrumentation records, per client-inference.md and
# gen-ai-metrics.md.
KNOWN_CURRENT_METRICS = frozenset({
    "gen_ai.client.inference.duration",
    "gen_ai.client.inference.time_to_first_chunk",
    "gen_ai.client.inference.time_per_output_chunk",
    "gen_ai.client.inference.usage.input_tokens",
    "gen_ai.client.inference.usage.output_tokens",
    "gen_ai.client.inference.usage.cache_read.input_tokens",
    "gen_ai.client.inference.usage.cache_write.input_tokens",
    "gen_ai.client.inference.usage.reasoning.output_tokens",
})

# Legacy names an old instrumentation may still emit, mapped to the name the
# pinned snapshot expects. Verified by diffing the main repository's
# docs/gen-ai at tag v1.36.0 against the dedicated repo main branch
# (2026-10-20), plus the dedicated repo's changelog.d breaking fragments.
LEGACY_RENAMES = {
    # v1.36.0 main repo: "gen_ai.system" was Required; the dedicated repo
    # replaced it with gen_ai.provider.name.
    "gen_ai.system": "gen_ai.provider.name",
    # Renamed in the dedicated repo (changelog fragments + docs):
    # the operation.* metric prefix became client.inference.*.
    "gen_ai.client.operation.duration": "gen_ai.client.inference.duration",
    "gen_ai.client.operation.time_to_first_chunk": "gen_ai.client.inference.time_to_first_chunk",
    "gen_ai.client.operation.time_per_output_chunk": "gen_ai.client.inference.time_per_output_chunk",
    "gen_ai.client.operation.usage.input_tokens": "gen_ai.client.inference.usage.input_tokens",
    "gen_ai.client.operation.usage.output_tokens": "gen_ai.client.inference.usage.output_tokens",
    "gen_ai.usage.cache_creation.input_tokens": "gen_ai.usage.cache_write.input_tokens",
}


def find_legacy(attributes):
    """Return {legacy_name: current_name} for every emitted legacy attribute."""
    return {
        name: LEGACY_RENAMES[name]
        for name in attributes
        if name in LEGACY_RENAMES
    }


def missing_required(attributes):
    """Return the required attributes absent from the emitted set."""
    return sorted(REQUIRED_ATTRS - set(attributes))


def unknown(attributes):
    """Return emitted gen_ai.* attributes not in the pinned snapshot."""
    return sorted(
        name for name in attributes
        if name.startswith("gen_ai.") and name not in KNOWN_CURRENT_ATTRS
    )
