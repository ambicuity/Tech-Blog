from __future__ import annotations

from pathlib import Path

from pipeline.utils import append_jsonl


def log_agent_trace(trace_file: Path, *, run_id: str, step: str, status: str, confidence: float, model: str = "", error: str = "") -> None:
    append_jsonl(
        trace_file,
        {
            "run_id": run_id,
            "step": step,
            "status": status,
            "confidence": confidence,
            "model": model,
            "error": error,
        },
    )
