from __future__ import annotations

import os
import re

from pipeline.config import AGENT_VERSION, STAGE_MODEL_SETTINGS
from pipeline.llm import LLMClient, load_prompt, try_parse_json
from pipeline.models import AgentResult


KNOWN_BAD_PATTERNS = [
    r"successThreshold\s+defaults\s+to\s+2",
    r"In conclusion",
]


def _heuristic_review(draft: str) -> dict:
    claims = re.findall(r"\[CLAIM:[^\]]+\]", draft)
    critical: list[str] = []
    uncertain: list[dict] = []
    missing: list[str] = []

    for pat in KNOWN_BAD_PATTERNS:
        if re.search(pat, draft, re.IGNORECASE):
            critical.append(f"pattern_detected:{pat}")

    if len(claims) < 3:
        missing.append("insufficient_claim_annotations")
    if "Operational Checklist" not in draft:
        missing.append("missing_operational_checklist")

    score = 0.9
    if critical:
        score -= 0.3
    score -= min(0.2, 0.05 * len(missing))

    return {
        "factual_score": max(0.0, round(score, 3)),
        "critical_inaccuracies": critical,
        "uncertain_claims": uncertain,
        "missing_context": missing,
        "verified_claims": claims,
    }


def review(draft: str) -> AgentResult:
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    parsed: dict

    if api_key:
        try:
            client = LLMClient(api_key)
            prompt = load_prompt("tech_review_prompt.txt") + "\n\nDraft:\n" + draft[:18000]
            cfg = STAGE_MODEL_SETTINGS["critic"]
            raw = client.generate_text("gemini-2.5-flash", prompt, temperature=cfg["temperature"], top_p=cfg["top_p"])
            parsed = try_parse_json(raw)
        except Exception:
            parsed = {}
    else:
        parsed = {}

    if not parsed:
        parsed = _heuristic_review(draft)

    factual_score = float(parsed.get("factual_score", 0.0))
    critical = parsed.get("critical_inaccuracies", []) or []
    uncertain = parsed.get("uncertain_claims", []) or []

    status = "passed"
    errors: list[str] = []
    if factual_score < 0.85:
        status = "failed"
        errors.append("factual_score_below_threshold")
    if critical:
        status = "failed"
        errors.append("critical_inaccuracies_present")
    if len(uncertain) > 2:
        status = "failed"
        errors.append("too_many_uncertain_claims")

    return AgentResult(
        name="technical_reviewer",
        version=AGENT_VERSION,
        status=status,
        confidence=max(0.0, min(1.0, factual_score)),
        artifacts=parsed,
        errors=errors,
    )
