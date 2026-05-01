from __future__ import annotations

import os
import re

from pipeline.config import AGENT_VERSION, STAGE_MODEL_SETTINGS
from pipeline.llm import LLMClient, load_prompt, try_parse_json
from pipeline.models import AgentResult
from pipeline.novelty import embed_text
from pipeline.novelty.memory import NoveltyMemory, extract_argument_flow_graph, extract_headings
from pipeline.utils import parse_front_matter


KEY_PATTERNS = [
    ("symptom->telemetry->root_cause->mitigation->checklist", "reasoning_path_clone"),
    ("claim->counterfactual->evidence->tradeoff->decision", "counterfactual_clone"),
    ("timeline->branch_point->root_cause->prevention", "timeline_clone"),
]



def _heuristic_red_team(draft: str, nearest: list[dict]) -> dict:
    meta, body = parse_front_matter(draft)
    headings = extract_headings(body)
    _, motif = extract_argument_flow_graph(headings, body)

    reused = []
    why = []
    for key, label in KEY_PATTERNS:
        if key in motif:
            reused.append(label)
            why.append(f"argument_flow_motif_matches:{key}")

    # Rhythm and transition reuse heuristic.
    low = body.lower()
    transition_hits = sum(low.count(t) for t in ["however", "in practice", "that said", "the real issue"])
    if transition_hits >= 6:
        reused.append("paragraph_rhythm_reuse")
        why.append(f"transition_profile_high:{transition_hits}")

    hidden_similarity = 0.20
    proof = []
    if nearest:
        for r in nearest[:3]:
            sim = float(r.get("similarity", 0.0))
            if sim > hidden_similarity:
                hidden_similarity = sim
                proof.append(
                    {
                        "post_path": r.get("post_path", ""),
                        "similarity": round(sim, 6),
                        "argument_flow_motif": r.get("argument_flow_motif", ""),
                    }
                )

    if hidden_similarity > 0.83:
        reused.append("semantic_clone_risk")
        why.append("high_body_similarity")

    target = "angle"
    if any("argument" in x or "reasoning" in x for x in reused):
        target = "reasoning"
    elif any("rhythm" in x for x in reused):
        target = "structure"
    elif hidden_similarity > 0.86:
        target = "topic"

    return {
        "hidden_similarity_score": round(hidden_similarity, 6),
        "reused_patterns": sorted(set(reused)),
        "proof_snippets": proof,
        "why_similar": why,
        "recommended_mutation_target": target,
    }


def review(draft: str, memory: NoveltyMemory) -> AgentResult:
    meta, body = parse_front_matter(draft)
    body_vec = embed_text(body[:12000])
    nearest = memory.nearest_records("body_vec", body_vec, k=15, limit=500)

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    parsed: dict | None = None

    if api_key:
        try:
            prompt = load_prompt("red_team_prompt.txt")
            context = {
                "nearest": [
                    {
                        "post_path": n.get("post_path", ""),
                        "similarity": n.get("similarity", 0.0),
                        "argument_flow_motif": n.get("argument_flow_motif", ""),
                        "structure_family": n.get("structure_family", ""),
                        "hook_style": n.get("hook_style", ""),
                        "cta_style": n.get("cta_style", ""),
                    }
                    for n in nearest[:15]
                ]
            }
            payload = f"\n\nNearest history:\n{context}\n\nDraft:\n{draft[:18000]}"
            client = LLMClient(api_key)
            cfg = STAGE_MODEL_SETTINGS["red_team"]
            raw = client.generate_text(
                "gemini-2.5-flash-lite",
                prompt + payload,
                temperature=cfg["temperature"],
                top_p=cfg["top_p"],
            )
            parsed = try_parse_json(raw)
        except Exception:
            parsed = None

    if not parsed:
        parsed = _heuristic_red_team(draft, nearest)

    hidden = float(parsed.get("hidden_similarity_score", 0.0))
    reused = parsed.get("reused_patterns", []) or []
    target = str(parsed.get("recommended_mutation_target", "angle"))

    status = "passed"
    errors: list[str] = []
    if hidden >= 0.85 or len(reused) >= 2:
        status = "failed"
        errors.append("hidden_similarity_or_reused_patterns")

    return AgentResult(
        name="red_team_reviewer",
        version=AGENT_VERSION,
        status=status,
        confidence=max(0.0, round(1.0 - hidden, 6)),
        artifacts={
            "hidden_similarity_score": hidden,
            "reused_patterns": reused,
            "proof_snippets": parsed.get("proof_snippets", []),
            "why_similar": parsed.get("why_similar", []),
            "recommended_mutation_target": target,
        },
        errors=errors,
    )
