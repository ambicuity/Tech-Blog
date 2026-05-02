from __future__ import annotations

import os
import random
import re
from datetime import datetime, timezone

from pipeline.config import AGENT_VERSION, ENTROPY_CONFIG, POSTS_DIR, STAGE_MODEL_SETTINGS, STARTER_CLUSTERS
from pipeline.evolution import enforce_hard_constraints
from pipeline.llm import LLMClient, load_prompt, try_parse_json
from pipeline.models import AgentResult
from pipeline.novelty.dedup import tokenize
from pipeline.novelty.memory import NoveltyMemory


INTENT_TYPES = [
    "tutorial",
    "incident",
    "contrarian",
    "teardown",
    "benchmark",
    "migration",
    "postmortem",
]

TOPIC_BANK = [
    "Kubernetes readiness and startup probe correctness under load",
    "CrashLoopBackOff diagnosis for AI-generated Python services",
    "Async I/O bottlenecks hidden by green health checks",
    "Memory amplification patterns in data-processing microservices",
    "Retry storm containment in distributed systems",
    "Autoscaling misconfigurations that inflate cloud spend",
    "Safe rollout patterns for AI-authored infrastructure code",
    "Observability blind spots in event-driven architectures",
    "Queue backpressure and latency collapse in production",
    "Container resource limits vs real runtime behavior",
    "Release engineering controls for AI-assisted code changes",
    "Operational runbooks that reduce MTTR during incidents",
    "Silent data corruption in replicated database clusters",
    "DNS propagation delays causing cascading API failures",
    "TLS certificate rotation outages in service mesh environments",
    "Connection pool exhaustion under bursty traffic patterns",
    "Garbage collection pauses triggering health check timeouts",
    "Log aggregation pipeline failures that hide production errors",
    "Feature flag misconfiguration causing partial outages",
    "Database migration rollbacks that leave schema drift",
    "Sidecar container resource contention in Kubernetes pods",
    "Rate limiter bypass through header manipulation in API gateways",
    "Cold start latency in serverless functions and mitigation strategies",
    "Envoy proxy misconfigurations causing silent request drops",
    "Distributed tracing gaps that obscure cross-service failures",
]

FORMAT_FAMILIES = ["incident_report", "deep_dive", "analysis", "teardown", "playbook", "postmortem"]
HOOK_STYLES = ["incident_hook", "metric_hook", "question_hook", "story_hook", "contrarian_hook"]
CTA_STYLES = ["reflective_question", "checklist_cta", "action_cta", "measurement_cta"]



def _extract_recent_titles(limit: int = 200) -> list[str]:
    titles: list[str] = []
    files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    for file in files[:limit]:
        txt = file.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', txt, re.MULTILINE)
        if match:
            titles.append(match.group(1).strip())
    return titles


def _extract_recent_summaries(limit: int = 40) -> list[str]:
    out: list[str] = []
    files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    for file in files[:limit]:
        txt = file.read_text(encoding="utf-8", errors="ignore")
        lines = txt.splitlines()
        body_start = 0
        if txt.startswith("---\n"):
            try:
                body_start = lines.index("---", 1) + 1
            except ValueError:
                body_start = 0
        body = "\n".join(lines[body_start:]).strip()
        if body:
            out.append(body[:320].replace("\n", " "))
    return out


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _cluster_for_topic(text: str) -> tuple[str, str]:
    low = text.lower()
    cluster = STARTER_CLUSTERS[0]
    cluster_key = "ai_code_in_production"
    if "kubernetes" in low or "pod" in low or "probe" in low:
        cluster = STARTER_CLUSTERS[1]
        cluster_key = "kubernetes_failure_forensics"
    elif "python" in low or "async" in low or "memory" in low:
        cluster = STARTER_CLUSTERS[2]
        cluster_key = "python_runtime_performance"
    elif "cost" in low or "autoscaling" in low or "retry" in low:
        cluster = STARTER_CLUSTERS[3]
        cluster_key = "cloud_cost_reliability"
    return cluster, cluster_key


def _fallback_candidates(topic_hint: str | None, strategy: dict, count: int = 12) -> list[dict]:
    seed = int(datetime.now(timezone.utc).timestamp())
    rng = random.Random(seed)
    topics = [topic_hint] if topic_hint else []
    topics.extend(TOPIC_BANK)
    rng.shuffle(topics)
    pool = []
    for idx in range(count):
        topic = topics[idx % len(topics)]
        intent = INTENT_TYPES[idx % len(INTENT_TYPES)]
        ff = strategy.get("format_family") if idx % 3 == 0 else FORMAT_FAMILIES[idx % len(FORMAT_FAMILIES)]
        hk = strategy.get("hook_style") if idx % 3 == 0 else HOOK_STYLES[idx % len(HOOK_STYLES)]
        cta = strategy.get("cta_style") if idx % 3 == 0 else CTA_STYLES[idx % len(CTA_STYLES)]
        arg = strategy.get("argument_flow_motif")
        pool.append(
            {
                "topic": topic,
                "angle": f"{intent} framing of {topic}",
                "persona": "senior platform engineer",
                "awareness_level": ["problem-aware", "solution-aware", "decision-ready"][idx % 3],
                "format_family": ff,
                "hook_style": hk,
                "cta_style": cta,
                "argument_flow_motif": arg,
                "reasoning_path": strategy.get("reasoning_path", "causal_diagnosis"),
                "risk_flags": [],
                "why_new": "Angle and structure intentionally rotated against recent posts.",
            }
        )
    return pool


def _llm_candidates(topic_hint: str | None, recent_titles: list[str], recent_summaries: list[str], strategy: dict) -> list[dict]:
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        return []

    prompt = load_prompt("planner_prompt.txt")
    context = (
        f"\n\nTopic hint: {topic_hint or ''}\n"
        f"Selected strategy: {strategy}\n"
        f"Recent titles to avoid repeating:\n- "
        + "\n- ".join(recent_titles[:100])
        + "\n\nRecent post summaries:\n- "
        + "\n- ".join(recent_summaries[:40])
    )

    client = LLMClient(api_key)
    cfg = STAGE_MODEL_SETTINGS["planner"]
    try:
        raw = client.generate_text(
            "gemini-2.5-flash",
            prompt + context,
            temperature=cfg["temperature"],
            top_p=cfg["top_p"],
        )
        parsed = try_parse_json(raw)
        candidates = parsed.get("candidates", []) if isinstance(parsed, dict) else []
        valid: list[dict] = []
        for c in candidates:
            if not isinstance(c, dict):
                continue
            topic = str(c.get("topic", "")).strip()
            angle = str(c.get("angle", "")).strip()
            if not topic or not angle:
                continue
            valid.append(
                {
                    "topic": topic,
                    "angle": angle,
                    "persona": str(c.get("persona", "senior platform engineer")),
                    "awareness_level": str(c.get("awareness_level", "solution-aware")),
                    "format_family": str(c.get("format_family", strategy.get("format_family", "deep_dive"))),
                    "hook_style": str(c.get("hook_style", strategy.get("hook_style", "problem_hook"))),
                    "cta_style": str(c.get("cta_style", strategy.get("cta_style", "neutral_cta"))),
                    "argument_flow_motif": str(c.get("argument_flow_motif", strategy.get("argument_flow_motif", ""))),
                    "reasoning_path": str(c.get("reasoning_path", strategy.get("reasoning_path", "causal_diagnosis"))),
                    "risk_flags": c.get("risk_flags", []) if isinstance(c.get("risk_flags", []), list) else [],
                    "why_new": str(c.get("why_new", "")),
                }
            )
        return valid[:12]
    except Exception:
        return []


def _score_candidates(candidates: list[dict], recent_titles: list[str]) -> list[dict]:
    recent_tok = [tokenize(t) for t in recent_titles[:200]]
    scored: list[dict] = []
    for c in candidates:
        title_like = f"{c['topic']} {c['angle']}"
        tok = tokenize(title_like)
        max_sim = 0.0
        for t in recent_tok:
            max_sim = max(max_sim, _jaccard(tok, t))
        novelty = round(1.0 - max_sim, 6)
        c2 = dict(c)
        c2["novelty_similarity"] = round(max_sim, 6)
        c2["novelty_score"] = novelty
        scored.append(c2)
    scored.sort(key=lambda x: (-x["novelty_score"], x["novelty_similarity"]))
    return scored


def plan(topic_hint: str | None = None, memory: NoveltyMemory | None = None) -> AgentResult:
    recent_titles = _extract_recent_titles()
    recent_summaries = _extract_recent_summaries()

    strategy = memory.select_strategy() if memory else {
        "strategy_id": "incident_forensics_v1",
        "format_family": "incident_report",
        "hook_style": "incident_hook",
        "cta_style": "reflective_question",
        "argument_flow_motif": "symptom->telemetry->root_cause->mitigation->checklist",
        "reasoning_path": "causal_diagnosis",
    }

    candidates = _llm_candidates(topic_hint, recent_titles, recent_summaries, strategy)
    if len(candidates) < 8:
        fallback = _fallback_candidates(topic_hint, strategy, count=12)
        candidates = (candidates + fallback)[:12]

    scored = _score_candidates(candidates, recent_titles)

    # Hard anti-repetition constraints over window N.
    constrained: list[dict] = []
    rejected_hard: list[str] = []
    if memory:
        rc = memory.fetch_recent_constraints(window=int(ENTROPY_CONFIG["constraint_window"]))
        for c in scored:
            ok, reason = enforce_hard_constraints(
                candidate=c,
                recent_constraints=rc,
                window=int(ENTROPY_CONFIG["constraint_window"]),
            )
            if ok:
                constrained.append(c)
            else:
                rejected_hard.append(reason)

    candidate_pool = constrained if constrained else scored
    top4 = candidate_pool[:4]
    if not top4:
        return AgentResult(
            name="planner",
            version=AGENT_VERSION,
            status="failed",
            confidence=0.0,
            errors=["no_candidate_topics"],
        )

    selected = random.SystemRandom().choice(top4)
    cluster, cluster_key = _cluster_for_topic(selected["topic"] + " " + selected["angle"])

    artifacts = {
        "strategy": strategy,
        "candidate_pool": candidate_pool[:12],
        "selected_candidates": top4,
        "selected_candidate": selected,
        "title_hypotheses": [selected["topic"]],
        "angle": selected["angle"],
        "audience": "senior engineers and platform teams",
        "must_include_claims": [
            "Root-cause mechanism",
            "Failure mode under production load",
            "Operational mitigation",
        ],
        "source_targets": [
            "official docs",
            "runtime metrics/logs",
            "platform vendor references",
        ],
        "cluster": cluster,
        "cluster_key": cluster_key,
        "pillar": cluster,
        "recent_summaries": recent_summaries[:40],
        "hard_constraint_rejections": rejected_hard,
    }

    best_sim = selected.get("novelty_similarity", 1.0)
    status = "passed" if best_sim < 0.88 else "failed"
    return AgentResult(
        name="planner",
        version=AGENT_VERSION,
        status=status,
        confidence=max(0.0, min(1.0, selected.get("novelty_score", 0.0))),
        artifacts=artifacts,
        errors=[] if status == "passed" else ["topic_duplicate_risk"],
    )
