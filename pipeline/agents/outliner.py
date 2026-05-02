from __future__ import annotations

import os
import re

from pipeline.config import AGENT_VERSION, STAGE_MODEL_SETTINGS
from pipeline.llm import LLMClient, load_prompt, try_parse_json
from pipeline.models import AgentResult

HOOKS = ["incident_hook", "metric_hook", "question_hook", "story_hook", "contrarian_hook"]
CTAS = ["reflective_question", "checklist_cta", "action_cta", "measurement_cta"]
FAMILIES = ["incident_report", "analysis", "teardown", "playbook", "postmortem", "deep_dive"]


def _topic_key(topic: str) -> str:
    toks = re.findall(r"[a-z0-9]+", topic.lower())
    if not toks:
        return "system"
    return " ".join(toks[:2])


def _fallback_outlines(candidate: dict) -> list[dict]:
    topic = str(candidate.get("topic", "system reliability"))
    tkey = _topic_key(topic)

    base_hook = str(candidate.get("hook_style", "incident_hook"))
    base_cta = str(candidate.get("cta_style", "reflective_question"))
    base_family = str(candidate.get("format_family", "analysis"))
    base_motif = str(candidate.get("argument_flow_motif", "symptom->telemetry->root_cause->mitigation->checklist"))

    alt_hook = HOOKS[(HOOKS.index(base_hook) + 1) % len(HOOKS)] if base_hook in HOOKS else HOOKS[0]
    alt_cta = CTAS[(CTAS.index(base_cta) + 1) % len(CTAS)] if base_cta in CTAS else CTAS[0]
    alt_family = FAMILIES[(FAMILIES.index(base_family) + 1) % len(FAMILIES)] if base_family in FAMILIES else FAMILIES[0]

    return [
        {
            "outline_id": "o1",
            "format_family": base_family,
            "hook_style": base_hook,
            "cta_style": base_cta,
            "rhetorical_family": base_family,
            "argument_flow_motif": base_motif,
            "headings": [
                f"{tkey.title()} Signal Snapshot",
                f"{tkey.title()} Investigation Timeline",
                f"{tkey.title()} Root Cause Mechanism",
                f"{tkey.title()} Mitigation and Hardening",
                "Operational Checklist",
                "Evidence & References",
                "Open Question",
            ],
        },
        {
            "outline_id": "o2",
            "format_family": alt_family,
            "hook_style": alt_hook,
            "cta_style": alt_cta,
            "rhetorical_family": "analysis",
            "argument_flow_motif": "claim->counterfactual->evidence->tradeoff->decision",
            "headings": [
                f"{tkey.title()} Problem Surface",
                "System Constraints",
                "Competing Explanations",
                "What the Metrics Actually Show",
                f"{tkey.title()} Production Guidance",
                "Operational Checklist",
                "Evidence & References",
            ],
        },
        {
            "outline_id": "o3",
            "format_family": "teardown",
            "hook_style": HOOKS[(HOOKS.index(alt_hook) + 1) % len(HOOKS)] if alt_hook in HOOKS else "question_hook",
            "cta_style": "action_cta",
            "rhetorical_family": "deep_dive",
            "argument_flow_motif": "surface->mechanism->failure_mode->redesign",
            "headings": [
                f"{tkey.title()} Context and Failure Trigger",
                f"{tkey.title()} Design Teardown",
                "Failure Modes Under Load",
                "Safer Design Pattern",
                "Operational Checklist",
                "Evidence & References",
                "Next Action",
            ],
        },
    ]


def _validate_outline_payload(parsed: dict) -> list[dict]:
    outlines = parsed.get("outlines", []) if isinstance(parsed, dict) else []
    valid: list[dict] = []
    for idx, item in enumerate(outlines):
        if not isinstance(item, dict):
            continue
        heads = item.get("headings", [])
        if not isinstance(heads, list) or len(heads) < 5:
            continue
        valid.append(
            {
                "outline_id": str(item.get("outline_id", f"o{idx+1}")),
                "format_family": str(item.get("format_family", "analysis")),
                "hook_style": str(item.get("hook_style", "problem_hook")),
                "cta_style": str(item.get("cta_style", "neutral_cta")),
                "rhetorical_family": str(item.get("rhetorical_family", "deep_dive")),
                "argument_flow_motif": str(item.get("argument_flow_motif", "")),
                "headings": [str(h).strip() for h in heads if str(h).strip()],
            }
        )
    return valid


def generate_outlines(candidate: dict, recent_summaries: list[str], exploration: bool = False) -> AgentResult:
    api_key = os.environ.get("GOOGLE_API_KEY", "")

    if not api_key:
        return AgentResult(
            name="outliner",
            version=AGENT_VERSION,
            status="passed",
            confidence=0.65,
            artifacts={"outlines": _fallback_outlines(candidate), "model": "fallback-outline-template"},
        )

    prompt = load_prompt("outline_prompt.txt")
    strategy = {
        "format_family": candidate.get("format_family", "deep_dive"),
        "hook_style": candidate.get("hook_style", "problem_hook"),
        "cta_style": candidate.get("cta_style", "neutral_cta"),
        "argument_flow_motif": candidate.get("argument_flow_motif", ""),
        "reasoning_path": candidate.get("reasoning_path", ""),
    }
    payload = (
        f"\n\nCandidate:\n{candidate}\n"
        f"\nPreferred strategy:\n{strategy}\n"
        f"\nExploration mode: {exploration}\n"
        f"\nRecent post summaries (avoid structural reuse):\n- "
        + "\n- ".join(recent_summaries[:20])
    )

    client = LLMClient(api_key)
    cfg = STAGE_MODEL_SETTINGS["outline"]
    temperature = min(0.95, cfg["temperature"] + (0.08 if exploration else 0.0))
    try:
        raw = client.generate_text(
            "gemini-2.5-flash",
            prompt + payload,
            temperature=temperature,
            top_p=cfg["top_p"],
        )
        parsed = try_parse_json(raw)
        outlines = _validate_outline_payload(parsed)
        if not outlines:
            outlines = _fallback_outlines(candidate)
            model = "fallback-outline-template"
            conf = 0.6
        else:
            model = "gemini-2.5-flash"
            conf = 0.82
        return AgentResult(
            name="outliner",
            version=AGENT_VERSION,
            status="passed",
            confidence=conf,
            artifacts={"outlines": outlines[: (5 if exploration else 3)], "model": model},
        )
    except Exception as exc:
        return AgentResult(
            name="outliner",
            version=AGENT_VERSION,
            status="passed",
            confidence=0.58,
            artifacts={"outlines": _fallback_outlines(candidate), "model": "fallback-outline-template"},
            errors=[f"outline_generation_error:{exc}"],
        )
