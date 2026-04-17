#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.agents.editor import edit
from pipeline.agents.outliner import generate_outlines
from pipeline.agents.planner import HOOK_STYLES, INTENT_TYPES, plan
from pipeline.agents.publisher import decide
from pipeline.agents.review_novelty import NoveltyReviewer, as_artifact
from pipeline.agents.review_red_team import review as red_team_review
from pipeline.agents.review_seo import review as seo_review
from pipeline.agents.review_tech import review as tech_review
from pipeline.agents.writer import write
from pipeline.config import DRAFTS_DIR, ENTROPY_CONFIG, NOVELTY_DB_FILE, POSTS_DIR
from pipeline.evolution import enforce_hard_constraints
from pipeline.gates.validators import (
    authority_gate,
    factual_gate,
    link_gate,
    novelty_gate,
    red_team_gate,
    seo_gate,
    structural_gate,
)
from pipeline.metrics.logger import log_agent_trace
from pipeline.novelty import NoveltyMemory, check_title_duplicate
from pipeline.utils import create_run_id, default_run_paths, ensure_dir, slugify, write_json



def _save_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def _extract_title(draft: str) -> str:
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', draft, re.MULTILINE)
    return m.group(1).strip() if m else "production-engineering-post"


def _post_filename(draft: str) -> str:
    dm = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", draft, re.MULTILINE)
    date = dm.group(1) if dm else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{date}-{slugify(_extract_title(draft))}.md"


def _mutation_target_from(novelty_reasons: list[str], red_team_target: str) -> str:
    if red_team_target in {"angle", "structure", "reasoning", "topic"}:
        return red_team_target
    if novelty_reasons and all(r.startswith("title_embedding") or r.startswith("intro_embedding") for r in novelty_reasons):
        return "angle"
    if any("argument_flow" in r or "heading" in r or "outline" in r for r in novelty_reasons):
        return "structure"
    if any("body_embedding" in r or "trigram" in r for r in novelty_reasons):
        return "reasoning"
    return "angle"


def _mutate_candidate_for_target(candidate: dict, target: str, attempt: int) -> dict:
    c = dict(candidate)
    if target == "angle":
        c["hook_style"] = HOOK_STYLES[(HOOK_STYLES.index(c.get("hook_style", HOOK_STYLES[0])) + 1) % len(HOOK_STYLES)]
        c["angle"] = f"{c.get('angle','')} | reframed opening-{attempt}"
    elif target == "structure":
        c["format_family"] = ["incident_report", "analysis", "teardown", "playbook", "postmortem", "deep_dive"][
            attempt % 6
        ]
        c["angle"] = f"{c.get('angle','')} | alternate structure-{attempt}"
    elif target == "reasoning":
        rp = c.get("reasoning_path", "causal_diagnosis")
        opts = ["causal_diagnosis", "counterfactual", "temporal", "mechanistic", "inversion"]
        c["reasoning_path"] = opts[(opts.index(rp) + 1) % len(opts)] if rp in opts else opts[attempt % len(opts)]
        c["angle"] = f"{c.get('angle','')} | reasoning-shift-{c['reasoning_path']}"
        c["argument_flow_motif"] = ""
    elif target == "topic":
        intent = INTENT_TYPES[attempt % len(INTENT_TYPES)]
        c["angle"] = f"{intent} reframing of {c.get('topic','')}"
    return c


def main() -> int:
    run_id = create_run_id()
    paths = default_run_paths(run_id)
    ensure_dir(paths["run_dir"])

    manifest = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
    }
    write_json(paths["manifest"], manifest)

    memory = NoveltyMemory(NOVELTY_DB_FILE)
    memory.rebuild_from_posts(POSTS_DIR)
    novelty_reviewer = NoveltyReviewer(memory)

    entropy_state = memory.latest_entropy_state()
    exploration_mode = any(a in {"pattern_collapse_alert", "similarity_drift_alert"} for a in entropy_state.get("alerts", []))

    writer_lineage = memory.select_writer_prompt()
    strategy_hard_exclude = set()

    topic_hint = os.environ.get("TOPIC_HINT")
    planner = plan(topic_hint, memory=memory)
    write_json(paths["planner"], planner.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="planner", status=planner.status, confidence=planner.confidence)
    if planner.status != "passed":
        manifest.update({"status": "failed", "reason": "planner_failed"})
        write_json(paths["manifest"], manifest)
        memory.close()
        return 1

    strategy = planner.artifacts.get("strategy", {})
    candidates = planner.artifacts.get("selected_candidates", []) or [planner.artifacts.get("selected_candidate", {})]

    final_draft = ""
    selected_candidate: dict = {}
    selected_outline: dict = {}
    rejected_headings: list[str] = []
    outline_artifact: dict = {"candidate_attempts": []}
    red_artifact: dict = {}
    rejected_stage = ""

    # Regeneration decision tree limits.
    total_failures = 0

    for candidate_index, candidate in enumerate(candidates[:4]):
        topic_failures = 0
        working_candidate = dict(candidate)
        working_candidate.setdefault("argument_flow_motif", strategy.get("argument_flow_motif", ""))
        working_candidate.setdefault("reasoning_path", strategy.get("reasoning_path", "causal_diagnosis"))

        while topic_failures < 3 and total_failures < 10:
            outliner = generate_outlines(
                working_candidate,
                planner.artifacts.get("recent_summaries", []),
                exploration=exploration_mode,
            )
            log_agent_trace(
                paths["traces"],
                run_id=run_id,
                step="outliner",
                status=outliner.status,
                confidence=outliner.confidence,
                model=outliner.artifacts.get("model", ""),
                error=";".join(outliner.errors),
            )
            if outliner.status != "passed":
                topic_failures += 1
                total_failures += 1
                continue

            outlines = outliner.artifacts.get("outlines", [])
            passed_outline = None
            outline_checks = []

            recent_constraints = memory.fetch_recent_constraints(window=int(ENTROPY_CONFIG["constraint_window"]))
            for outline in outlines:
                tuple_candidate = dict(working_candidate)
                tuple_candidate["format_family"] = outline.get("format_family", tuple_candidate.get("format_family", ""))
                tuple_candidate["hook_style"] = outline.get("hook_style", tuple_candidate.get("hook_style", ""))
                tuple_candidate["cta_style"] = outline.get("cta_style", tuple_candidate.get("cta_style", ""))
                tuple_candidate["argument_flow_motif"] = outline.get("argument_flow_motif", tuple_candidate.get("argument_flow_motif", ""))
                ok_hard, reason_hard = enforce_hard_constraints(
                    candidate=tuple_candidate,
                    recent_constraints=recent_constraints,
                    window=int(ENTROPY_CONFIG["constraint_window"]),
                )

                chk = novelty_reviewer.check_outline(outline)
                entry = {"outline": outline, "check": as_artifact(chk), "hard_constraint": {"ok": ok_hard, "reason": reason_hard}}
                outline_checks.append(entry)
                if ok_hard and chk.passed and passed_outline is None:
                    passed_outline = outline
                else:
                    rejected_headings.extend(outline.get("headings", []))

            outline_artifact["candidate_attempts"].append(
                {
                    "candidate_index": candidate_index,
                    "candidate": working_candidate,
                    "outline_checks": outline_checks,
                }
            )

            if not passed_outline:
                topic_failures += 1
                total_failures += 1
                # Fail on structure/argflow -> switch outline family + argument graph skeleton.
                working_candidate = _mutate_candidate_for_target(working_candidate, "structure", topic_failures)
                continue

            anti_recent = memory.fetch_records(limit=6)
            anti_targets = {
                "narrative_archetype": [r.get("narrative_archetype", "") for r in anti_recent[:2]],
                "opening_archetype": [r.get("opening_archetype", "") for r in anti_recent[:2]],
                "argument_flow_motif": [r.get("argument_flow_motif", "") for r in anti_recent[:2]],
            }

            writer_input = dict(planner.artifacts)
            writer_input.update(
                {
                    "strategy": strategy,
                    "selected_candidate": working_candidate,
                    "selected_outline": passed_outline,
                    "rejected_outline_headings": rejected_headings,
                    "anti_targets": anti_targets,
                    "writer_prompt_override": writer_lineage.get("prompt_text", ""),
                }
            )

            writer = write(writer_input)
            log_agent_trace(
                paths["traces"],
                run_id=run_id,
                step="writer",
                status=writer.status,
                confidence=writer.confidence,
                model=writer.artifacts.get("model", ""),
                error=";".join(writer.errors),
            )
            if writer.status != "passed":
                manifest.update({"status": "failed", "reason": "writer_failed", "errors": writer.errors})
                write_json(paths["manifest"], manifest)
                memory.close()
                return 1

            draft = writer.artifacts["draft"]
            _save_text(paths["draft"], draft)

            # Title-only dedup gate.
            is_dup, closest, sim = check_title_duplicate(paths["draft"], POSTS_DIR)
            if is_dup:
                topic_failures += 1
                total_failures += 1
                rejected_headings.extend(passed_outline.get("headings", []))
                outline_artifact.setdefault("title_dedup_failures", []).append(
                    {
                        "candidate_index": candidate_index,
                        "closest": closest,
                        "similarity": round(sim, 6),
                    }
                )
                # Fail title/intro -> mutate hook + opening archetype.
                working_candidate = _mutate_candidate_for_target(working_candidate, "angle", topic_failures)
                continue

            # Pre-publish novelty + red team checks for regeneration decisioning.
            pre_novelty = novelty_reviewer.check_draft(draft)
            pre_red = red_team_review(draft, memory)
            red_artifact = pre_red.artifacts

            if pre_novelty.status != "passed" or pre_red.status != "passed":
                topic_failures += 1
                total_failures += 1

                target = _mutation_target_from(pre_novelty.artifacts.get("reasons", []), pre_red.artifacts.get("recommended_mutation_target", "angle"))

                if topic_failures >= 2 and target != "topic":
                    # Two full failures on same topic -> switch angle family.
                    target = "topic"

                if topic_failures >= 3:
                    # Three failures -> abandon topic.
                    rejected_stage = "prepublish_regeneration_exhausted"
                    break

                working_candidate = _mutate_candidate_for_target(working_candidate, target, topic_failures)
                if target in {"structure", "reasoning"}:
                    rejected_headings.extend(passed_outline.get("headings", []))
                continue

            selected_candidate = working_candidate
            selected_outline = passed_outline
            final_draft = draft
            break

        if final_draft:
            break

    write_json(paths["outline"], outline_artifact)

    if not final_draft:
        manifest.update({"status": "failed", "reason": rejected_stage or "novelty_outline_or_regeneration_failed"})
        write_json(paths["manifest"], manifest)
        memory.record_prompt_result(writer_lineage.get("lineage_id", ""), False)
        memory.record_strategy_result(strategy.get("strategy_id", ""), False)
        memory.close()
        return 1

    tech = tech_review(final_draft)
    write_json(paths["tech_review"], tech.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="technical_reviewer", status=tech.status, confidence=tech.confidence, error=";".join(tech.errors))

    seo = seo_review(
        final_draft,
        selected_candidate.get("topic", planner.artifacts.get("title_hypotheses", [""])[0]),
        planner.artifacts.get("cluster_key", planner.artifacts.get("cluster", "")),
    )
    write_json(paths["seo_review"], seo.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="seo_reviewer", status=seo.status, confidence=seo.confidence, error=";".join(seo.errors))

    final_draft = seo.artifacts.get("patched_draft", final_draft)

    editor = edit(final_draft)
    write_json(paths["editor_review"], editor.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="editor", status=editor.status, confidence=editor.confidence, error=";".join(editor.errors))

    final_draft = editor.artifacts.get("patched_draft", final_draft)
    _save_text(paths["draft"], final_draft)

    novelty = novelty_reviewer.check_draft(final_draft)
    write_json(paths["novelty_review"], novelty.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="novelty_reviewer", status=novelty.status, confidence=novelty.confidence, error=";".join(novelty.errors))

    red = red_team_review(final_draft, memory)
    red_artifact = red.artifacts
    write_json(paths["red_team_review"], red_artifact)
    log_agent_trace(paths["traces"], run_id=run_id, step="red_team_reviewer", status=red.status, confidence=red.confidence, error=";".join(red.errors))

    g1 = structural_gate(final_draft)
    g2 = factual_gate(tech.artifacts)
    g3 = seo_gate(seo.artifacts)
    g4 = link_gate(final_draft)
    g5 = authority_gate(editor.artifacts)
    g6 = novelty_gate(novelty.artifacts)
    g7 = red_team_gate(red_artifact)

    gate_payload = {
        "structural": g1.__dict__,
        "factual": g2.__dict__,
        "seo": g3.__dict__,
        "link": g4.__dict__,
        "authority": g5.__dict__,
        "novelty": g6.__dict__,
        "red_team": g7.__dict__,
    }
    write_json(paths["gate_report"], gate_payload)
    failed_gates = [name for name, payload in gate_payload.items() if not payload.get("passed", False)]

    aggregate = round((g1.score + g2.score + g3.score + g4.score + g5.score + g6.score + g7.score) / 7.0, 3)
    pub = decide(gate_payload, aggregate)
    write_json(paths["publish_decision"], pub.artifacts)
    log_agent_trace(paths["traces"], run_id=run_id, step="publisher", status=pub.status, confidence=pub.confidence, error=";".join(pub.errors))

    outcome = pub.artifacts["outcome"]
    rejected_stage = "" if outcome == "PASS" else pub.artifacts.get("reason", "gate_failure")

    structure_family = selected_outline.get("format_family", selected_candidate.get("format_family", ""))
    hook_style = selected_outline.get("hook_style", selected_candidate.get("hook_style", ""))
    cta_style = selected_outline.get("cta_style", selected_candidate.get("cta_style", ""))
    argument_flow_motif = selected_outline.get("argument_flow_motif", selected_candidate.get("argument_flow_motif", ""))

    if outcome == "PASS":
        filename = _post_filename(final_draft)
        post_path = POSTS_DIR / filename
        _save_text(post_path, final_draft)
        memory.ingest_generated_post(post_path, final_draft)
        manifest.update({"status": "published", "post_path": str(post_path.relative_to(ROOT))})
        print(f"PUBLISHED: {post_path}")
    else:
        quarantine = DRAFTS_DIR / f"{run_id}.md"
        _save_text(quarantine, final_draft)
        manifest.update(
            {
                "status": "quarantined",
                "reason": pub.artifacts.get("reason", "unknown"),
                "quarantine_path": str(quarantine.relative_to(ROOT)),
            }
        )
        print(f"QUARANTINED: {quarantine} ({pub.artifacts.get('reason','')})")

    run_artifact_path = paths["run_dir"].relative_to(ROOT)
    print(
        "RUN SUMMARY: "
        f"status={manifest.get('status')} "
        f"reason={manifest.get('reason', '')} "
        f"failed_gates={','.join(failed_gates) if failed_gates else 'none'} "
        f"run_id={run_id} "
        f"artifacts={run_artifact_path}"
    )

    memory.log_run_telemetry(
        run_id=run_id,
        strategy_id=str(strategy.get("strategy_id", "")),
        prompt_lineage_id=str(writer_lineage.get("lineage_id", "")),
        structure_family=structure_family,
        hook_style=hook_style,
        cta_style=cta_style,
        argument_flow_motif=argument_flow_motif,
        aggregate_conf=aggregate,
        novelty_score=float(novelty.artifacts.get("novelty_score", 0.0)),
        hidden_similarity_score=float(red_artifact.get("hidden_similarity_score", 0.0)),
        rejected_stage=rejected_stage,
    )

    success = outcome == "PASS"
    memory.record_prompt_result(writer_lineage.get("lineage_id", ""), success)
    memory.record_strategy_result(strategy.get("strategy_id", ""), success)

    # Evolution operations.
    successful_publishes = memory.successful_publish_count()
    mutation_info = memory.maybe_mutate_prompt_lineage(
        successful_publishes=successful_publishes,
        interval=int(ENTROPY_CONFIG["mutation_interval_successes"]),
    )
    promote_info = memory.maybe_promote_challenger()

    entropy = memory.compute_entropy_snapshot(run_id)
    cooldown_info = {"cooled": []}
    if "pattern_collapse_alert" in entropy.get("alerts", []):
        cooldown_info = memory.enforce_strategy_cooldowns(window=int(ENTROPY_CONFIG["window"]), top_k=2)

    write_json(
        paths["entropy_report"],
        {
            "entropy": entropy,
            "mutation": mutation_info,
            "promotion": promote_info,
            "cooldowns": cooldown_info,
            "exploration_mode": exploration_mode,
        },
    )

    manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
    write_json(paths["manifest"], manifest)
    memory.close()

    # Exit non-zero only for execution failures (not content quarantine), so CI persists artifacts.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
