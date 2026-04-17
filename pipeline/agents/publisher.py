from __future__ import annotations

from pathlib import Path

from pipeline.config import AGENT_VERSION, SAMPLE_COUNTER_FILE, THRESHOLDS
from pipeline.models import AgentResult


def _load_counter(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def _save_counter(path: Path, value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(value) + "\n", encoding="utf-8")


def decide(gate_results: dict, aggregate_confidence: float) -> AgentResult:
    all_pass = all(v.get("passed", False) for v in gate_results.values())

    requires_sampling_review = False
    reason = ""
    outcome = "QUARANTINE"

    if all_pass and aggregate_confidence >= THRESHOLDS["aggregate"]:
        count = _load_counter(SAMPLE_COUNTER_FILE) + 1
        _save_counter(SAMPLE_COUNTER_FILE, count)
        if count % 5 == 0:
            outcome = "QUARANTINE"
            requires_sampling_review = True
            reason = "sampling_review_required"
        else:
            outcome = "PASS"
            reason = "all_gates_passed"
    elif all_pass:
        outcome = "REPAIR"
        reason = "aggregate_confidence_below_threshold"
    else:
        outcome = "QUARANTINE"
        reason = "gate_failure"

    return AgentResult(
        name="publisher",
        version=AGENT_VERSION,
        status="passed" if outcome in {"PASS", "REPAIR"} else "failed",
        confidence=aggregate_confidence,
        artifacts={
            "outcome": outcome,
            "confidence": aggregate_confidence,
            "requires_sampling_review": requires_sampling_review,
            "reason": reason,
        },
        errors=[] if outcome in {"PASS", "REPAIR"} else [reason],
    )
