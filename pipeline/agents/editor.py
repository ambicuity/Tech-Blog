from __future__ import annotations

import re

from pipeline.config import AGENT_VERSION
from pipeline.models import AgentResult
from pipeline.utils import build_front_matter, parse_front_matter

FORBIDDEN_OPENERS = [
    "In this post",
    "Let's explore",
    "In this article",
]

FORBIDDEN_CLOSERS = [
    "In conclusion",
    "To summarize",
]


def _authority_score(body: str) -> float:
    score = 0.85
    if "```" not in body:
        score -= 0.15
    if len(re.findall(r"\b(maybe|perhaps|might)\b", body, re.IGNORECASE)) > 8:
        score -= 0.05
    if "Operational Checklist" not in body:
        score -= 0.1
    return max(0.0, min(1.0, round(score, 3)))


def edit(draft: str) -> AgentResult:
    meta, body = parse_front_matter(draft)
    lines = body.splitlines()

    # Remove generic openers in first paragraph.
    for idx in range(min(8, len(lines))):
        for phrase in FORBIDDEN_OPENERS:
            if phrase.lower() in lines[idx].lower():
                lines[idx] = lines[idx].replace(phrase, "")

    # Remove generic closers.
    for idx in range(max(0, len(lines) - 12), len(lines)):
        for phrase in FORBIDDEN_CLOSERS:
            if phrase.lower() in lines[idx].lower():
                lines[idx] = lines[idx].replace(phrase, "")

    body = "\n".join(lines)
    score = _authority_score(body)
    status = "passed" if score >= 0.8 else "failed"

    return AgentResult(
        name="editor",
        version=AGENT_VERSION,
        status=status,
        confidence=score,
        artifacts={"authority_score": score, "patched_draft": build_front_matter(meta, body)},
        errors=[] if status == "passed" else ["authority_score_below_threshold"],
    )
