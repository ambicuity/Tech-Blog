from __future__ import annotations

from dataclasses import asdict, dataclass

from pipeline.config import AGENT_VERSION, NOVELTY_THRESHOLDS
from pipeline.models import AgentResult
from pipeline.novelty import (
    NoveltyMemory,
    build_body_trigrams,
    classify_cta_style,
    classify_hook_style,
    embed_text,
    extract_intro,
    normalized_levenshtein_similarity,
)
from pipeline.novelty.memory import extract_argument_flow_graph, extract_headings
from pipeline.utils import parse_front_matter


@dataclass
class NoveltyCheck:
    passed: bool
    score: float
    reasons: list[str]
    metrics: dict


class NoveltyReviewer:
    def __init__(self, memory: NoveltyMemory) -> None:
        self.memory = memory

    def check_outline(self, outline: dict) -> NoveltyCheck:
        headings = outline.get("headings", []) if isinstance(outline, dict) else []
        outline_text = "\n".join(f"## {h}" for h in headings)
        outline_vec = embed_text(outline_text)
        hook_style = str(outline.get("hook_style", "problem_hook"))
        heading_signature = " > ".join(str(h).lower() for h in headings)
        arg_motif = str(outline.get("argument_flow_motif", ""))

        max_outline, nearest_outline = self.memory.max_cosine("outline_vec", outline_vec, top_k=20)

        best_head = 0.0
        best_head_path = ""
        arg_reuse = 0
        for row in self.memory.fetch_records(limit=300):
            sim = normalized_levenshtein_similarity(heading_signature, row.get("heading_signature", ""))
            if sim > best_head:
                best_head = sim
                best_head_path = row.get("post_path", "")
            if arg_motif and row.get("argument_flow_motif", "") == arg_motif:
                arg_reuse += 1

        hook_reuse = self.memory.hook_reuse_count(hook_style, recent_n=5)

        reasons: list[str] = []
        if max_outline >= NOVELTY_THRESHOLDS["outline_embedding_cosine"]:
            reasons.append(f"outline_embedding_too_similar:{nearest_outline}:{max_outline:.3f}")
        if best_head >= NOVELTY_THRESHOLDS["heading_similarity_max"]:
            reasons.append(f"heading_signature_too_similar:{best_head_path}:{best_head:.3f}")
        if hook_reuse > NOVELTY_THRESHOLDS["hook_reuse_last5_max"]:
            reasons.append(f"hook_style_overused:{hook_style}:{hook_reuse}")
        if arg_reuse > 0:
            reasons.append(f"argument_flow_motif_reused:{arg_motif}:{arg_reuse}")

        score = 1.0
        score -= min(0.5, max(0.0, max_outline - 0.5))
        score -= min(0.3, max(0.0, best_head - 0.5))
        if hook_reuse:
            score -= min(0.2, 0.05 * hook_reuse)
        if arg_reuse:
            score -= min(0.2, 0.05 * arg_reuse)
        score = max(0.0, round(score, 3))

        return NoveltyCheck(
            passed=not reasons,
            score=score,
            reasons=reasons,
            metrics={
                "outline_embedding_cosine": max_outline,
                "nearest_outline_post": nearest_outline,
                "heading_signature_similarity": best_head,
                "nearest_heading_post": best_head_path,
                "hook_reuse_last5": hook_reuse,
                "argument_flow_motif_reuse": arg_reuse,
            },
        )

    def check_draft(self, draft: str) -> AgentResult:
        meta, body = parse_front_matter(draft)
        title = meta.get("title", "").strip().strip('"')
        intro = extract_intro(body)
        cta_style = classify_cta_style(body)
        hook_style = classify_hook_style(intro)

        headings = extract_headings(body)
        _, arg_motif = extract_argument_flow_graph(headings, body)

        title_vec = embed_text(title)
        intro_vec = embed_text(intro)
        body_vec = embed_text(body[:12000])
        body_trigrams = set(build_body_trigrams(body))

        title_sim, title_nearest = self.memory.max_cosine("title_vec", title_vec, top_k=200)
        intro_sim, intro_nearest = self.memory.max_cosine("intro_vec", intro_vec, top_k=200)
        body_sim, body_nearest = self.memory.max_cosine("body_vec", body_vec, top_k=200)

        max_trigram_overlap = 0.0
        trigram_post = ""
        arg_reuse = 0
        for row in self.memory.fetch_records(limit=300):
            prior = set(row.get("body_trigrams", []))
            if body_trigrams and prior:
                overlap = len(body_trigrams & prior) / max(1, len(body_trigrams))
                if overlap > max_trigram_overlap:
                    max_trigram_overlap = overlap
                    trigram_post = row.get("post_path", "")
            if arg_motif and row.get("argument_flow_motif", "") == arg_motif:
                arg_reuse += 1

        cta_repeat = self.memory.cta_repeat_risk(cta_style)

        reasons: list[str] = []
        if title_sim >= NOVELTY_THRESHOLDS["title_embedding_cosine"]:
            reasons.append(f"title_embedding_too_similar:{title_nearest}:{title_sim:.3f}")
        if intro_sim >= NOVELTY_THRESHOLDS["intro_embedding_cosine"]:
            reasons.append(f"intro_embedding_too_similar:{intro_nearest}:{intro_sim:.3f}")
        if body_sim >= NOVELTY_THRESHOLDS["body_embedding_cosine"]:
            reasons.append(f"body_embedding_too_similar:{body_nearest}:{body_sim:.3f}")
        if max_trigram_overlap >= NOVELTY_THRESHOLDS["body_trigram_overlap"]:
            reasons.append(f"body_trigram_overlap_high:{trigram_post}:{max_trigram_overlap:.3f}")
        if cta_repeat:
            reasons.append(f"cta_style_repeated_three_times:{cta_style}")
        if arg_reuse > 0:
            reasons.append(f"argument_flow_motif_reused:{arg_motif}:{arg_reuse}")

        novelty_score = 1.0
        novelty_score -= min(0.2, max(0.0, title_sim - 0.6))
        novelty_score -= min(0.2, max(0.0, intro_sim - 0.6))
        novelty_score -= min(0.2, max(0.0, body_sim - 0.6))
        novelty_score -= min(0.2, max(0.0, max_trigram_overlap - 0.08))
        if cta_repeat:
            novelty_score -= 0.1
        if arg_reuse:
            novelty_score -= min(0.2, 0.04 * arg_reuse)
        novelty_score = max(0.0, round(novelty_score, 3))

        status = "passed" if not reasons else "failed"
        artifacts = {
            "novelty_score": novelty_score,
            "reasons": reasons,
            "metrics": {
                "title_embedding_cosine": title_sim,
                "title_nearest": title_nearest,
                "intro_embedding_cosine": intro_sim,
                "intro_nearest": intro_nearest,
                "body_embedding_cosine": body_sim,
                "body_nearest": body_nearest,
                "body_trigram_overlap": round(max_trigram_overlap, 6),
                "body_trigram_nearest": trigram_post,
                "cta_style": cta_style,
                "hook_style": hook_style,
                "argument_flow_motif": arg_motif,
                "argument_flow_reuse": arg_reuse,
            },
        }

        return AgentResult(
            name="novelty_reviewer",
            version=AGENT_VERSION,
            status=status,
            confidence=novelty_score,
            artifacts=artifacts,
            errors=[] if status == "passed" else reasons,
        )


def as_artifact(check: NoveltyCheck) -> dict:
    return asdict(check)
