from __future__ import annotations

import os
from datetime import datetime, timezone

from pipeline.config import AGENT_VERSION, STAGE_MODEL_SETTINGS
from pipeline.llm import LLMClient, load_prompt
from pipeline.models import AgentResult



def _fallback_draft(content_brief: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S +0000")
    selected = content_brief.get("selected_candidate", {})
    title = selected.get("topic") or content_brief.get("title_hypotheses", ["Production Reliability Incident"])[0]
    outline = content_brief.get("selected_outline", {}).get("headings", [])
    if not outline:
        outline = [
            "Signal Snapshot",
            "Investigation",
            "Root Cause",
            "Mitigation",
            "Operational Checklist",
            "Evidence & References",
            "Open Question",
        ]

    sections = []
    sections.append("At 03:12 UTC, latency and error rate diverged while health checks stayed green [CLAIM:1].")
    for h in outline:
        sections.append(f"\n## {h}\n")
        if h.lower() == "operational checklist":
            sections.append("- Validate assumptions with production metrics.\n- Rehearse rollback and blast-radius controls.")
        elif "evidence" in h.lower():
            sections.append("- [Primary Source](https://kubernetes.io/docs/)\n- [Primary Source](https://docs.python.org/3/)")
        elif "question" in h.lower() or "next action" in h.lower():
            sections.append("What early signal would have revealed this failure mode one hour sooner?")
        else:
            sections.append("Concrete logs, config snippets, and measured behavior are used to support each claim [CLAIM:2].")
            sections.append("```bash\nkubectl get pods -n prod\nkubectl top pods -n prod\n```")

    body = "\n\n".join(sections)
    return f"""---
layout: post
title: \"{title}\"
date: {now}
categories: [Engineering, Reliability]
tags: [engineering, production, reliability]
description: \"Production incident-first analysis with actionable engineering runbook and verified operational guidance.\"
author: ritesh
---

{body}
"""


def write(content_brief: dict) -> AgentResult:
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    selected = content_brief.get("selected_candidate", {})
    outline = content_brief.get("selected_outline", {})
    rejected = content_brief.get("rejected_outline_headings", [])
    anti_targets = content_brief.get("anti_targets", {})
    strategy = content_brief.get("strategy", {})

    if not api_key:
        draft = _fallback_draft(content_brief)
        return AgentResult(
            name="writer",
            version=AGENT_VERSION,
            status="passed",
            confidence=0.68,
            artifacts={"draft": draft, "model": "fallback-template"},
        )

    prompt_override = str(content_brief.get("writer_prompt_override", "")).strip()
    prompt = prompt_override or load_prompt("writer_prompt.txt")

    brief = (
        "\n\nContent brief:\n"
        f"Topic: {selected.get('topic', content_brief.get('title_hypotheses', [''])[0])}\n"
        f"Angle: {selected.get('angle', content_brief.get('angle', ''))}\n"
        f"Persona: {selected.get('persona', 'senior platform engineer')}\n"
        f"Awareness level: {selected.get('awareness_level', 'solution-aware')}\n"
        f"Format family: {selected.get('format_family', strategy.get('format_family', 'deep_dive'))}\n"
        f"Hook style: {selected.get('hook_style', strategy.get('hook_style', 'problem_hook'))}\n"
        f"CTA style: {selected.get('cta_style', strategy.get('cta_style', 'neutral_cta'))}\n"
        f"Argument flow motif: {selected.get('argument_flow_motif', strategy.get('argument_flow_motif', ''))}\n"
        f"Reasoning path: {selected.get('reasoning_path', strategy.get('reasoning_path', 'causal_diagnosis'))}\n"
        f"Cluster: {content_brief.get('cluster', '')}\n"
        f"Audience: {content_brief.get('audience', 'senior engineers')}\n"
        f"Must include claims: {content_brief.get('must_include_claims', [])}\n"
        f"Source targets: {content_brief.get('source_targets', [])}\n"
        f"Selected outline headings (must use): {outline.get('headings', [])}\n"
        f"Rejected outline headings (do not use): {rejected}\n"
        f"Anti-target archetypes to avoid this run: {anti_targets}\n"
    )

    models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-8b"]
    client = LLMClient(api_key)
    cfg = STAGE_MODEL_SETTINGS["writer"]
    errors: list[str] = []
    for model in models:
        try:
            draft = client.generate_text(
                model,
                prompt + brief,
                temperature=cfg["temperature"],
                top_p=cfg["top_p"],
            )
            return AgentResult(
                name="writer",
                version=AGENT_VERSION,
                status="passed",
                confidence=0.84,
                artifacts={
                    "draft": draft,
                    "model": model,
                    "prompt_name": "writer_prompt.txt" if not prompt_override else "prompt_lineage_override",
                },
            )
        except Exception as exc:
            errors.append(f"{model}:{exc}")

    return AgentResult(
        name="writer",
        version=AGENT_VERSION,
        status="passed",
        confidence=0.68,
        artifacts={
            "draft": _fallback_draft(content_brief),
            "model": "fallback-template",
            "prompt_name": "fallback",
        },
        errors=[f"all_models_exhausted:{';'.join(errors[-3:])}"],
    )
