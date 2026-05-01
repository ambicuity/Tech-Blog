from __future__ import annotations

import re
from urllib.parse import urlparse

from pipeline.config import FORBIDDEN_HEADERS, THRESHOLDS
from pipeline.models import GateResult
from pipeline.utils import parse_front_matter


def structural_gate(draft: str) -> GateResult:
    meta, body = parse_front_matter(draft)
    critical: list[str] = []
    warnings: list[str] = []

    required = ["layout", "title", "date", "categories", "tags", "description", "author"]
    for field in required:
        if field not in meta:
            critical.append(f"missing_front_matter:{field}")

    fences = draft.count("```")
    if fences % 2 != 0:
        critical.append("unclosed_code_fence")

    body_lower = body.lower()
    body_lines_lower = [line.strip() for line in body_lower.splitlines()]
    for h in FORBIDDEN_HEADERS:
        if any(line == h for line in body_lines_lower):
            critical.append(f"forbidden_header:{h}")

    if "Operational Checklist" not in body:
        warnings.append("missing_operational_checklist")
    if "Evidence & References" not in body:
        warnings.append("missing_evidence_section")

    passed = not critical
    score = 1.0 if passed else 0.0
    return GateResult("structural", passed, score, 1.0, critical, warnings)


def factual_gate(tech_review: dict) -> GateResult:
    critical = []
    warnings = []
    score = float(tech_review.get("factual_score", 0.0))

    if tech_review.get("critical_inaccuracies"):
        critical.append("critical_inaccuracies_present")
    uncertain = tech_review.get("uncertain_claims", [])
    if len(uncertain) > 2:
        critical.append("too_many_uncertain_claims")
    if score < THRESHOLDS["factual"]:
        critical.append("factual_score_below_threshold")

    missing = tech_review.get("missing_context", [])
    for m in missing:
        warnings.append(f"missing_context:{m}")

    return GateResult("factual", not critical, score, THRESHOLDS["factual"], critical, warnings)


def seo_gate(seo_review: dict) -> GateResult:
    score = float(seo_review.get("seo_score", 0.0))
    critical = []
    warnings = seo_review.get("warnings", []) or []
    if score < THRESHOLDS["seo"]:
        critical.append("seo_score_below_threshold")
    return GateResult("seo", not critical, score, THRESHOLDS["seo"], critical, warnings)


def link_gate(draft: str) -> GateResult:
    _, body = parse_front_matter(draft)
    links = re.findall(r"\]\(([^)]+)\)", body)
    internal = [l for l in links if l.startswith("/posts/")]
    external = [l for l in links if l.startswith("http://") or l.startswith("https://")]

    critical: list[str] = []
    warnings: list[str] = []

    if len(internal) < 2:
        critical.append("internal_links_below_min")
    if len(external) < 2:
        warnings.append("external_links_below_recommended")

    malformed = 0
    for link in external:
        try:
            p = urlparse(link)
            if not p.scheme or not p.netloc:
                malformed += 1
        except Exception:
            malformed += 1
    if malformed:
        critical.append("malformed_external_links")

    score = 1.0
    if critical:
        score -= 0.4
    if warnings:
        score -= 0.1
    score = max(0.0, round(score, 3))
    return GateResult("link", not critical, score, 0.9, critical, warnings)


def authority_gate(editor_review: dict) -> GateResult:
    score = float(editor_review.get("authority_score", 0.0))
    critical = []
    if score < THRESHOLDS["authority"]:
        critical.append("authority_score_below_threshold")
    return GateResult("authority", not critical, score, THRESHOLDS["authority"], critical, [])


def novelty_gate(novelty_review: dict) -> GateResult:
    score = float(novelty_review.get("novelty_score", 0.0))
    critical = []
    reasons = novelty_review.get("reasons", []) or []
    if reasons:
        critical.extend([f"novelty:{r}" for r in reasons])
    if score < THRESHOLDS["novelty"]:
        critical.append("novelty_score_below_threshold")
    return GateResult("novelty", not critical, score, THRESHOLDS["novelty"], critical, [])


def red_team_gate(red_review: dict) -> GateResult:
    hidden = float(red_review.get("hidden_similarity_score", 0.0))
    patterns = red_review.get("reused_patterns", []) or []
    critical = []
    if hidden >= 0.85:
        critical.append("hidden_similarity_score_high")
    if len(patterns) >= 2:
        critical.append("reused_patterns_detected")
    score = max(0.0, round(1.0 - hidden, 3))
    return GateResult("red_team", not critical, score, THRESHOLDS["red_team"], critical, [])
