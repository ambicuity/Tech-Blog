from __future__ import annotations

import json
import math
import random
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pipeline.config import ENTROPY_CONFIG, STRATEGY_CATALOG
from pipeline.utils import parse_front_matter

from .similarity import cosine_similarity, embed_text


@dataclass
class NoveltyRecord:
    post_path: str
    created_at: str
    title: str
    intro: str
    headings: list[str]
    heading_signature: str
    hook_style: str
    cta_style: str
    rhetorical_family: str
    title_vec: list[float]
    intro_vec: list[float]
    outline_vec: list[float]
    body_vec: list[float]
    body_trigrams: list[str]
    argument_flow_graph: dict[str, Any]
    argument_flow_motif: str
    concept_cluster_ids: list[str]
    narrative_archetype: str
    explanation_style: str
    analogy_type: str
    opening_archetype: str
    closing_archetype: str
    rhythm_signature: dict[str, Any]
    structure_family: str


def extract_intro(body: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if not paragraphs:
        return ""
    return paragraphs[0][:1200]


def extract_headings(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", body, re.MULTILINE)]


def classify_hook_style(intro: str) -> str:
    low = intro.lower()
    if "?" in intro[:220]:
        return "question_hook"
    if re.search(r"\b(alert|incident|pager|outage|sev-?1|oomkilled|crashloop)\b", low):
        return "incident_hook"
    if re.search(r"\b\d+%|\d+x|\d+\s*(ms|s|sec|minute|hour)\b", low):
        return "metric_hook"
    if re.search(r"\bI\b|\bwe\b", intro[:220]):
        return "story_hook"
    if re.search(r"\bcounterintuitive|surprising|unexpected|myth\b", low):
        return "contrarian_hook"
    return "problem_hook"


def classify_cta_style(body: str) -> str:
    tail = body[-1500:].lower()
    if "open question" in tail or "hardest question" in tail or "what would" in tail:
        return "reflective_question"
    if "operational checklist" in tail:
        return "checklist_cta"
    if re.search(r"\bnext step|runbook|action items|do this now|start with\b", tail):
        return "action_cta"
    if re.search(r"\bmeasure|monitor|benchmark|baseline\b", tail):
        return "measurement_cta"
    return "neutral_cta"


def classify_rhetorical_family(headings: list[str], body: str) -> str:
    joined = " ".join(h.lower() for h in headings)
    body_low = body.lower()
    if any(k in joined for k in ["root cause", "investigation", "incident", "timeline"]):
        return "incident_report"
    if any(k in joined for k in ["implementation", "step", "setup", "guide", "runbook"]):
        return "tutorial"
    if any(k in joined for k in ["tradeoff", "comparison", "vs", "benchmark", "counterfactual"]):
        return "analysis"
    if any(k in body_low for k in ["postmortem", "blast radius", "rollback"]):
        return "postmortem"
    return "deep_dive"


def classify_structure_family(headings: list[str]) -> str:
    joined = " ".join(h.lower() for h in headings)
    if any(k in joined for k in ["timeline", "incident", "investigation"]):
        return "incident_report"
    if any(k in joined for k in ["tradeoff", "comparison", "counterfactual", "constraints"]):
        return "analysis"
    if any(k in joined for k in ["teardown", "mechanism", "failure modes"]):
        return "teardown"
    if any(k in joined for k in ["checklist", "runbook", "playbook"]):
        return "playbook"
    return "deep_dive"


def classify_opening_archetype(intro: str) -> str:
    low = intro.lower()
    if re.search(r"\b(alert|incident|outage|pager|sev)\b", low):
        return "incident_open"
    if "?" in intro[:220]:
        return "question_open"
    if re.search(r"\b\d+%|\d+x|\d+\s*(ms|sec|minutes?)\b", low):
        return "metric_open"
    if re.search(r"\bwe\b|\bi\b", intro[:220]):
        return "story_open"
    return "problem_open"


def classify_closing_archetype(body: str) -> str:
    tail = body[-1000:].lower()
    if "open question" in tail or "what would" in tail or "question" in tail:
        return "question_close"
    if "operational checklist" in tail or "checklist" in tail:
        return "checklist_close"
    if re.search(r"\bnext step|action item|do this\b", tail):
        return "action_close"
    return "summary_close"


def classify_explanation_style(body: str, headings: list[str]) -> str:
    low = body.lower()
    joined = " ".join(h.lower() for h in headings)
    if any(k in joined for k in ["mechanism", "internals", "how it works"]):
        return "mechanistic"
    if any(k in joined for k in ["steps", "runbook", "playbook", "procedure"]):
        return "procedural"
    if re.search(r"\bprobability|likelihood|confidence|distribution\b", low):
        return "probabilistic"
    if "tradeoff" in joined or "tradeoff" in low:
        return "tradeoff_first"
    return "mixed"


def classify_analogy_type(body: str) -> str:
    low = body.lower()
    if any(k in low for k in ["like a pipeline", "assembly line", "conveyor"]):
        return "pipeline"
    if any(k in low for k in ["guardrail", "seatbelt", "safety net"]):
        return "guardrail"
    if any(k in low for k in ["blast radius", "fault line", "shockwave"]):
        return "blast_radius"
    return "none"


def _sentence_lengths(text: str) -> list[int]:
    sents = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    return [len(re.findall(r"[a-z0-9]+", s.lower())) for s in sents]


def _hist(vals: list[int], bins: list[tuple[int, int]]) -> list[float]:
    if not vals:
        return [0.0 for _ in bins]
    total = len(vals)
    out = []
    for lo, hi in bins:
        out.append(round(sum(1 for v in vals if lo <= v <= hi) / total, 6))
    return out


def rhythm_signature(text: str) -> dict[str, Any]:
    lengths = _sentence_lengths(text)
    transitions = [
        "however",
        "in practice",
        "that said",
        "the real issue",
        "meanwhile",
        "therefore",
    ]
    low = text.lower()
    return {
        "sentence_len_hist": _hist(lengths, [(1, 8), (9, 15), (16, 25), (26, 40), (41, 200)]),
        "avg_sentence_len": round(sum(lengths) / max(1, len(lengths)), 3) if lengths else 0.0,
        "punctuation": {
            "comma": low.count(","),
            "semicolon": low.count(";"),
            "colon": low.count(":"),
            "question": low.count("?"),
        },
        "transition_profile": {t: low.count(t) for t in transitions},
    }


def build_body_trigrams(body: str, limit: int = 7000) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", body.lower())[:limit]
    if len(tokens) < 3:
        return []
    grams = [" ".join(tokens[i : i + 3]) for i in range(len(tokens) - 2)]
    seen: set[str] = set()
    out: list[str] = []
    for g in grams:
        if g in seen:
            continue
        seen.add(g)
        out.append(g)
    return out


def extract_argument_flow_graph(headings: list[str], body: str) -> tuple[dict[str, Any], str]:
    motif_tokens = []
    nodes = []
    edges = []
    for idx, h in enumerate(headings):
        hl = h.lower()
        node_id = f"n{idx}"
        ntype = "analysis"
        if any(k in hl for k in ["signal", "symptom", "surface", "context", "timeline"]):
            ntype = "symptom"
            motif_tokens.append("symptom")
        elif any(k in hl for k in ["metric", "telemetry", "evidence", "trace"]):
            ntype = "evidence"
            motif_tokens.append("telemetry")
        elif any(k in hl for k in ["root cause", "mechanism", "why"]):
            ntype = "root_cause"
            motif_tokens.append("root_cause")
        elif any(k in hl for k in ["mitigation", "fix", "hardening", "redesign", "guidance"]):
            ntype = "mitigation"
            motif_tokens.append("mitigation")
        elif any(k in hl for k in ["checklist", "runbook", "action"]):
            ntype = "checklist"
            motif_tokens.append("checklist")
        elif any(k in hl for k in ["tradeoff", "comparison", "counterfactual"]):
            ntype = "tradeoff"
            motif_tokens.append("tradeoff")
        nodes.append({"id": node_id, "label": h, "type": ntype})
        if idx > 0:
            edges.append({"from": f"n{idx-1}", "to": node_id, "type": "supports"})

    if not motif_tokens:
        low = body.lower()
        if "counterfactual" in low:
            motif_tokens = ["claim", "counterfactual", "evidence", "decision"]
        else:
            motif_tokens = ["symptom", "analysis", "mitigation"]
    motif = "->".join(motif_tokens[:6])
    return {"nodes": nodes, "edges": edges}, motif


def concept_cluster_ids(title: str, body: str, k: int = 3) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", (title + " " + body).lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "your",
        "have",
        "will",
        "when",
        "what",
        "where",
    }
    freq: dict[str, int] = {}
    for t in tokens:
        if len(t) < 4 or t in stop:
            continue
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:k]
    out = []
    for tok, _ in top:
        bucket = abs(hash(tok)) % 64
        out.append(f"cluster_{bucket:02d}")
    return out or ["cluster_00"]


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            ins = curr[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, delete, sub))
        prev = curr
    return prev[-1]


def normalized_levenshtein_similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    dist = _levenshtein(a, b)
    denom = max(len(a), len(b), 1)
    return round(1.0 - (dist / denom), 6)


def _record_from_markdown(post_path: Path, content: str) -> NoveltyRecord | None:
    meta, body = parse_front_matter(content)
    title = meta.get("title", "").strip().strip('"')
    if not title:
        m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if m:
            title = m.group(1).strip()
    if not title:
        return None

    headings = extract_headings(body)
    heading_signature = " > ".join(h.lower() for h in headings)
    intro = extract_intro(body)
    hook_style = classify_hook_style(intro)
    cta_style = classify_cta_style(body)
    rhetorical_family = classify_rhetorical_family(headings, body)
    structure_family = classify_structure_family(headings)
    body_trigrams = build_body_trigrams(body)
    outline_text = "\n".join(f"## {h}" for h in headings)
    arg_graph, arg_motif = extract_argument_flow_graph(headings, body)

    narrative_archetype = rhetorical_family
    explanation_style = classify_explanation_style(body, headings)
    analogy_type = classify_analogy_type(body)
    opening_archetype = classify_opening_archetype(intro)
    closing_archetype = classify_closing_archetype(body)
    r_sig = rhythm_signature(body)
    clusters = concept_cluster_ids(title, body)

    return NoveltyRecord(
        post_path=str(post_path),
        created_at=datetime.now(timezone.utc).isoformat(),
        title=title,
        intro=intro,
        headings=headings,
        heading_signature=heading_signature,
        hook_style=hook_style,
        cta_style=cta_style,
        rhetorical_family=rhetorical_family,
        title_vec=embed_text(title),
        intro_vec=embed_text(intro),
        outline_vec=embed_text(outline_text or heading_signature or title),
        body_vec=embed_text(body[:12000]),
        body_trigrams=body_trigrams,
        argument_flow_graph=arg_graph,
        argument_flow_motif=arg_motif,
        concept_cluster_ids=clusters,
        narrative_archetype=narrative_archetype,
        explanation_style=explanation_style,
        analogy_type=analogy_type,
        opening_archetype=opening_archetype,
        closing_archetype=closing_archetype,
        rhythm_signature=r_sig,
        structure_family=structure_family,
    )


class NoveltyMemory:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()
        self._bootstrap_strategies()
        self._bootstrap_prompt_lineage()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    def _ensure_column(self, table: str, column: str, decl: str) -> None:
        cols = [r["name"] for r in self.conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")

    def _ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS novelty_posts (
                post_path TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                title TEXT NOT NULL,
                intro TEXT NOT NULL,
                headings_json TEXT NOT NULL,
                heading_signature TEXT NOT NULL,
                hook_style TEXT NOT NULL,
                cta_style TEXT NOT NULL,
                rhetorical_family TEXT NOT NULL,
                title_vec_json TEXT NOT NULL,
                intro_vec_json TEXT NOT NULL,
                outline_vec_json TEXT NOT NULL,
                body_vec_json TEXT NOT NULL,
                body_trigrams_json TEXT NOT NULL,
                argument_flow_graph_json TEXT NOT NULL DEFAULT '{}',
                argument_flow_motif TEXT NOT NULL DEFAULT '',
                concept_cluster_ids_json TEXT NOT NULL DEFAULT '[]',
                narrative_archetype TEXT NOT NULL DEFAULT '',
                explanation_style TEXT NOT NULL DEFAULT '',
                analogy_type TEXT NOT NULL DEFAULT '',
                opening_archetype TEXT NOT NULL DEFAULT '',
                closing_archetype TEXT NOT NULL DEFAULT '',
                rhythm_signature_json TEXT NOT NULL DEFAULT '{}',
                structure_family TEXT NOT NULL DEFAULT ''
            )
            """
        )

        # Migrate older schema if needed.
        self._ensure_column("novelty_posts", "argument_flow_graph_json", "TEXT NOT NULL DEFAULT '{}' ")
        self._ensure_column("novelty_posts", "argument_flow_motif", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "concept_cluster_ids_json", "TEXT NOT NULL DEFAULT '[]'")
        self._ensure_column("novelty_posts", "narrative_archetype", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "explanation_style", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "analogy_type", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "opening_archetype", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "closing_archetype", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("novelty_posts", "rhythm_signature_json", "TEXT NOT NULL DEFAULT '{}' ")
        self._ensure_column("novelty_posts", "structure_family", "TEXT NOT NULL DEFAULT ''")

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_registry (
                strategy_id TEXT PRIMARY KEY,
                strategy_json TEXT NOT NULL,
                alpha REAL NOT NULL DEFAULT 1.0,
                beta REAL NOT NULL DEFAULT 1.0,
                usage_count INTEGER NOT NULL DEFAULT 0,
                success_count INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                cooldown_until TEXT NOT NULL DEFAULT ''
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_lineage (
                lineage_id TEXT PRIMARY KEY,
                stage TEXT NOT NULL,
                version INTEGER NOT NULL,
                status TEXT NOT NULL,
                prompt_text TEXT NOT NULL,
                parent_lineage_id TEXT NOT NULL DEFAULT '',
                mutation_ops_json TEXT NOT NULL DEFAULT '[]',
                usage_count INTEGER NOT NULL DEFAULT 0,
                success_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entropy_metrics (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                zscores_json TEXT NOT NULL,
                alerts_json TEXT NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_telemetry (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                prompt_lineage_id TEXT NOT NULL,
                structure_family TEXT NOT NULL,
                hook_style TEXT NOT NULL,
                cta_style TEXT NOT NULL,
                argument_flow_motif TEXT NOT NULL,
                aggregate_conf REAL NOT NULL DEFAULT 0.0,
                novelty_score REAL NOT NULL DEFAULT 0.0,
                hidden_similarity_score REAL NOT NULL DEFAULT 0.0,
                rejected_stage TEXT NOT NULL DEFAULT ''
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_novelty_window
            ON novelty_posts(created_at DESC, structure_family, hook_style, cta_style, argument_flow_motif)
            """
        )
        self.conn.commit()

    def _bootstrap_strategies(self) -> None:
        for s in STRATEGY_CATALOG:
            self.conn.execute(
                """
                INSERT INTO strategy_registry(strategy_id, strategy_json, alpha, beta, usage_count, success_count, active, cooldown_until)
                VALUES (?, ?, 1.0, 1.0, 0, 0, 1, '')
                ON CONFLICT(strategy_id) DO NOTHING
                """,
                (s["strategy_id"], json.dumps(s, ensure_ascii=False)),
            )
        self.conn.commit()

    def _bootstrap_prompt_lineage(self) -> None:
        # Writer baseline lineage only; can be expanded to planner/outline.
        rows = self.conn.execute("SELECT lineage_id FROM prompt_lineage WHERE stage='writer'").fetchall()
        if rows:
            return
        base_prompt = ""
        base_path = Path(__file__).resolve().parents[1] / "prompts" / "writer_prompt.txt"
        if base_path.exists():
            base_prompt = base_path.read_text(encoding="utf-8")
        lineage_id = "writer_champion_v1"
        self.conn.execute(
            """
            INSERT INTO prompt_lineage(lineage_id, stage, version, status, prompt_text, parent_lineage_id, mutation_ops_json, usage_count, success_count, created_at)
            VALUES (?, 'writer', 1, 'champion', ?, '', '[]', 0, 0, ?)
            """,
            (lineage_id, base_prompt, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def _mutate_prompt_text(self, text: str) -> tuple[str, list[str]]:
        lines = text.splitlines()
        ops: list[str] = []
        # Constraint reordering mutation.
        hard_idx = None
        for i, ln in enumerate(lines):
            if ln.strip().lower().startswith("you must follow these constraints"):
                hard_idx = i
                break
        if hard_idx is not None:
            block = []
            for j in range(hard_idx + 1, min(hard_idx + 15, len(lines))):
                if lines[j].startswith("-"):
                    block.append(lines[j])
            if len(block) >= 3:
                random.shuffle(block)
                k = 0
                for j in range(hard_idx + 1, min(hard_idx + 15, len(lines))):
                    if lines[j].startswith("-") and k < len(block):
                        lines[j] = block[k]
                        k += 1
                ops.append("constraint_reorder")
        # Style perturbation token.
        lines.append("- Apply slight sentence-rhythm variation run-to-run while preserving technical precision.")
        ops.append("style_perturbation")
        # Framing swap cue.
        lines.append("- Prefer a different explanatory lens than the most recent two posts.")
        ops.append("framing_swap")
        return "\n".join(lines).strip() + "\n", ops

    def maybe_mutate_prompt_lineage(self, successful_publishes: int, interval: int) -> dict[str, Any]:
        if successful_publishes <= 0 or successful_publishes % interval != 0:
            return {"mutated": False}

        champ = self.conn.execute(
            "SELECT * FROM prompt_lineage WHERE stage='writer' AND status='champion' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if not champ:
            return {"mutated": False, "reason": "missing_champion"}

        # 80/20 champion/challenger routing is done by selector; here we create challenger.
        next_version = int(champ["version"]) + 1
        new_id = f"writer_challenger_v{next_version}"
        exists = self.conn.execute("SELECT lineage_id FROM prompt_lineage WHERE lineage_id=?", (new_id,)).fetchone()
        if exists:
            return {"mutated": False, "reason": "challenger_exists"}

        new_prompt, ops = self._mutate_prompt_text(champ["prompt_text"])
        self.conn.execute(
            """
            INSERT INTO prompt_lineage(lineage_id, stage, version, status, prompt_text, parent_lineage_id, mutation_ops_json, usage_count, success_count, created_at)
            VALUES (?, 'writer', ?, 'challenger', ?, ?, ?, 0, 0, ?)
            """,
            (
                new_id,
                next_version,
                new_prompt,
                champ["lineage_id"],
                json.dumps(ops),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()
        return {"mutated": True, "new_lineage_id": new_id, "ops": ops}

    def select_writer_prompt(self) -> dict[str, Any]:
        # 80/20 champion/challenger split.
        rows = self.conn.execute(
            "SELECT * FROM prompt_lineage WHERE stage='writer' AND status IN ('champion','challenger') ORDER BY version DESC"
        ).fetchall()
        if not rows:
            return {"lineage_id": "", "prompt_text": "", "status": "none"}
        champion = next((r for r in rows if r["status"] == "champion"), rows[0])
        challengers = [r for r in rows if r["status"] == "challenger"]
        chosen = champion
        if challengers and random.random() < 0.2:
            chosen = challengers[0]

        self.conn.execute(
            "UPDATE prompt_lineage SET usage_count = usage_count + 1 WHERE lineage_id=?", (chosen["lineage_id"],)
        )
        self.conn.commit()
        return {
            "lineage_id": chosen["lineage_id"],
            "prompt_text": chosen["prompt_text"],
            "status": chosen["status"],
            "version": chosen["version"],
        }

    def record_prompt_result(self, lineage_id: str, success: bool) -> None:
        if not lineage_id:
            return
        if success:
            self.conn.execute(
                "UPDATE prompt_lineage SET success_count = success_count + 1 WHERE lineage_id=?",
                (lineage_id,),
            )
        self.conn.commit()

    def maybe_promote_challenger(self) -> dict[str, Any]:
        champ = self.conn.execute(
            "SELECT * FROM prompt_lineage WHERE stage='writer' AND status='champion' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        challenger = self.conn.execute(
            "SELECT * FROM prompt_lineage WHERE stage='writer' AND status='challenger' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if not champ or not challenger:
            return {"promoted": False}

        # Need enough samples.
        if challenger["usage_count"] < 6:
            return {"promoted": False, "reason": "insufficient_challenger_samples"}

        champ_rate = float(champ["success_count"]) / max(1, int(champ["usage_count"]))
        chal_rate = float(challenger["success_count"]) / max(1, int(challenger["usage_count"]))

        if chal_rate > champ_rate + 0.05:
            self.conn.execute("UPDATE prompt_lineage SET status='retired' WHERE lineage_id=?", (champ["lineage_id"],))
            self.conn.execute("UPDATE prompt_lineage SET status='champion' WHERE lineage_id=?", (challenger["lineage_id"],))
            self.conn.commit()
            return {"promoted": True, "new_champion": challenger["lineage_id"]}

        # rollback challenger if clearly worse.
        if challenger["usage_count"] >= 10 and chal_rate + 0.05 < champ_rate:
            self.conn.execute("UPDATE prompt_lineage SET status='retired' WHERE lineage_id=?", (challenger["lineage_id"],))
            self.conn.commit()
            return {"promoted": False, "retired_challenger": challenger["lineage_id"]}

        return {"promoted": False}

    def select_strategy(self, hard_exclude: set[str] | None = None) -> dict[str, Any]:
        hard_exclude = hard_exclude or set()
        rows = self.conn.execute("SELECT * FROM strategy_registry WHERE active=1").fetchall()
        if not rows:
            return STRATEGY_CATALOG[0]

        now = datetime.now(timezone.utc)
        valid = []
        for r in rows:
            cooldown = r["cooldown_until"]
            if cooldown:
                try:
                    if datetime.fromisoformat(cooldown) > now:
                        continue
                except Exception:
                    pass
            strategy = json.loads(r["strategy_json"])
            if strategy["strategy_id"] in hard_exclude:
                continue
            valid.append((r, strategy))

        if not valid:
            valid = [(r, json.loads(r["strategy_json"])) for r in rows]

        # Underused minimum quota first.
        usages = [int(r["usage_count"]) for r, _ in valid]
        min_usage = min(usages) if usages else 0
        underused = [(r, s) for r, s in valid if int(r["usage_count"]) <= min_usage + 1]
        if underused and random.random() < 0.35:
            chosen_row, chosen = random.choice(underused)
        else:
            # Thompson sampling.
            best = None
            best_score = -1.0
            for r, s in valid:
                alpha = max(1e-6, float(r["alpha"]))
                beta = max(1e-6, float(r["beta"]))
                score = random.betavariate(alpha, beta)
                if score > best_score:
                    best_score = score
                    best = (r, s)
            assert best is not None
            chosen_row, chosen = best

        self.conn.execute(
            "UPDATE strategy_registry SET usage_count = usage_count + 1 WHERE strategy_id=?",
            (chosen["strategy_id"],),
        )
        self.conn.commit()
        return chosen

    def record_strategy_result(self, strategy_id: str, success: bool) -> None:
        row = self.conn.execute("SELECT alpha, beta, success_count FROM strategy_registry WHERE strategy_id=?", (strategy_id,)).fetchone()
        if not row:
            return
        alpha = float(row["alpha"]) + (1.0 if success else 0.0)
        beta = float(row["beta"]) + (0.0 if success else 1.0)
        self.conn.execute(
            "UPDATE strategy_registry SET alpha=?, beta=?, success_count=success_count + ? WHERE strategy_id=?",
            (alpha, beta, 1 if success else 0, strategy_id),
        )
        self.conn.commit()

    def enforce_strategy_cooldowns(self, window: int, top_k: int = 2) -> dict[str, Any]:
        rows = self.conn.execute(
            "SELECT strategy_id FROM run_telemetry ORDER BY created_at DESC LIMIT ?",
            (window,),
        ).fetchall()
        freq: dict[str, int] = {}
        for r in rows:
            sid = r["strategy_id"]
            freq[sid] = freq.get(sid, 0) + 1
        if not freq:
            return {"cooled": []}
        ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:top_k]
        cooled = []
        until = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
        for sid, cnt in ranked:
            self.conn.execute(
                "UPDATE strategy_registry SET cooldown_until=? WHERE strategy_id=?",
                (until, sid),
            )
            cooled.append({"strategy_id": sid, "count": cnt, "cooldown_until": until})
        self.conn.commit()
        return {"cooled": cooled}

    def upsert_record(self, rec: NoveltyRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO novelty_posts (
                post_path, created_at, title, intro, headings_json, heading_signature,
                hook_style, cta_style, rhetorical_family,
                title_vec_json, intro_vec_json, outline_vec_json, body_vec_json, body_trigrams_json,
                argument_flow_graph_json, argument_flow_motif, concept_cluster_ids_json,
                narrative_archetype, explanation_style, analogy_type,
                opening_archetype, closing_archetype, rhythm_signature_json, structure_family
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(post_path) DO UPDATE SET
                created_at=excluded.created_at,
                title=excluded.title,
                intro=excluded.intro,
                headings_json=excluded.headings_json,
                heading_signature=excluded.heading_signature,
                hook_style=excluded.hook_style,
                cta_style=excluded.cta_style,
                rhetorical_family=excluded.rhetorical_family,
                title_vec_json=excluded.title_vec_json,
                intro_vec_json=excluded.intro_vec_json,
                outline_vec_json=excluded.outline_vec_json,
                body_vec_json=excluded.body_vec_json,
                body_trigrams_json=excluded.body_trigrams_json,
                argument_flow_graph_json=excluded.argument_flow_graph_json,
                argument_flow_motif=excluded.argument_flow_motif,
                concept_cluster_ids_json=excluded.concept_cluster_ids_json,
                narrative_archetype=excluded.narrative_archetype,
                explanation_style=excluded.explanation_style,
                analogy_type=excluded.analogy_type,
                opening_archetype=excluded.opening_archetype,
                closing_archetype=excluded.closing_archetype,
                rhythm_signature_json=excluded.rhythm_signature_json,
                structure_family=excluded.structure_family
            """,
            (
                rec.post_path,
                rec.created_at,
                rec.title,
                rec.intro,
                json.dumps(rec.headings, ensure_ascii=False),
                rec.heading_signature,
                rec.hook_style,
                rec.cta_style,
                rec.rhetorical_family,
                json.dumps(rec.title_vec),
                json.dumps(rec.intro_vec),
                json.dumps(rec.outline_vec),
                json.dumps(rec.body_vec),
                json.dumps(rec.body_trigrams, ensure_ascii=False),
                json.dumps(rec.argument_flow_graph, ensure_ascii=False),
                rec.argument_flow_motif,
                json.dumps(rec.concept_cluster_ids, ensure_ascii=False),
                rec.narrative_archetype,
                rec.explanation_style,
                rec.analogy_type,
                rec.opening_archetype,
                rec.closing_archetype,
                json.dumps(rec.rhythm_signature, ensure_ascii=False),
                rec.structure_family,
            ),
        )
        self.conn.commit()

    def rebuild_from_posts(self, posts_dir: Path) -> int:
        count = 0
        for p in sorted(posts_dir.glob("*.md")):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            rec = _record_from_markdown(p, txt)
            if not rec:
                continue
            self.upsert_record(rec)
            count += 1
        return count

    def ingest_generated_post(self, post_path: Path, content: str) -> bool:
        rec = _record_from_markdown(post_path, content)
        if not rec:
            return False
        self.upsert_record(rec)
        return True

    def fetch_records(self, limit: int = 1000) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM novelty_posts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "post_path": row["post_path"],
                    "created_at": row["created_at"],
                    "title": row["title"],
                    "intro": row["intro"],
                    "headings": json.loads(row["headings_json"]),
                    "heading_signature": row["heading_signature"],
                    "hook_style": row["hook_style"],
                    "cta_style": row["cta_style"],
                    "rhetorical_family": row["rhetorical_family"],
                    "title_vec": json.loads(row["title_vec_json"]),
                    "intro_vec": json.loads(row["intro_vec_json"]),
                    "outline_vec": json.loads(row["outline_vec_json"]),
                    "body_vec": json.loads(row["body_vec_json"]),
                    "body_trigrams": json.loads(row["body_trigrams_json"]),
                    "argument_flow_graph": json.loads(row["argument_flow_graph_json"] or "{}"),
                    "argument_flow_motif": row["argument_flow_motif"],
                    "concept_cluster_ids": json.loads(row["concept_cluster_ids_json"] or "[]"),
                    "narrative_archetype": row["narrative_archetype"],
                    "explanation_style": row["explanation_style"],
                    "analogy_type": row["analogy_type"],
                    "opening_archetype": row["opening_archetype"],
                    "closing_archetype": row["closing_archetype"],
                    "rhythm_signature": json.loads(row["rhythm_signature_json"] or "{}"),
                    "structure_family": row["structure_family"],
                }
            )
        return out

    def nearest_records(self, field: str, vec: list[float], k: int = 15, limit: int = 400) -> list[dict]:
        rows = self.fetch_records(limit=limit)
        scored = []
        for row in rows:
            other = row.get(field, [])
            sim = cosine_similarity(vec, other)
            row2 = dict(row)
            row2["similarity"] = sim
            scored.append(row2)
        scored.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
        return scored[:k]

    def max_cosine(self, field: str, vec: list[float], top_k: int = 20) -> tuple[float, str]:
        rows = self.nearest_records(field, vec, k=max(1, top_k), limit=max(60, top_k * 8))
        if not rows:
            return 0.0, ""
        top = rows[0]
        return round(float(top.get("similarity", 0.0)), 6), str(top.get("post_path", ""))

    def hook_reuse_count(self, hook_style: str, recent_n: int = 5) -> int:
        rows = self.conn.execute(
            "SELECT hook_style FROM novelty_posts ORDER BY created_at DESC LIMIT ?", (recent_n,)
        ).fetchall()
        return sum(1 for r in rows if r["hook_style"] == hook_style)

    def cta_repeat_risk(self, cta_style: str) -> bool:
        rows = self.conn.execute(
            "SELECT cta_style FROM novelty_posts ORDER BY created_at DESC LIMIT 2"
        ).fetchall()
        if len(rows) < 2:
            return False
        return all(r["cta_style"] == cta_style for r in rows)

    def fetch_recent_constraints(self, window: int) -> dict[str, list[str]]:
        rows = self.conn.execute(
            """
            SELECT structure_family, hook_style, argument_flow_motif, cta_style, opening_archetype
            FROM novelty_posts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (window,),
        ).fetchall()
        structure = []
        hook = []
        arg = []
        cta = []
        for r in rows:
            sf = r["structure_family"] or ""
            hk = r["hook_style"] or ""
            ag = r["argument_flow_motif"] or ""
            if sf:
                structure.append(f"{sf}|{ag}")
            if hk:
                hook.append(f"{hk}|{sf}")
            if ag:
                arg.append(ag)
            if r["cta_style"]:
                cta.append(r["cta_style"])
        return {
            "structure_family": structure,
            "hook_style": hook,
            "argument_flow_motif": arg,
            "cta_style": cta,
        }

    def compute_entropy_snapshot(self, run_id: str, now_ts: str | None = None) -> dict[str, Any]:
        now = datetime.now(timezone.utc) if now_ts is None else datetime.fromisoformat(now_ts)
        w = int(ENTROPY_CONFIG["window"])
        rows = self.fetch_records(limit=max(200, w * 3))
        window_rows = rows[:w]

        def entropy(vals: list[str]) -> float:
            if not vals:
                return 0.0
            freq: dict[str, int] = {}
            for v in vals:
                freq[v] = freq.get(v, 0) + 1
            n = len(vals)
            h = 0.0
            for c in freq.values():
                p = c / n
                h -= p * math.log(max(p, 1e-12), 2)
            max_h = math.log(max(2, len(freq)), 2)
            return round(h / max(max_h, 1e-9), 6)

        def dominant_ratio(vals: list[str]) -> float:
            if not vals:
                return 0.0
            freq: dict[str, int] = {}
            for v in vals:
                freq[v] = freq.get(v, 0) + 1
            return round(max(freq.values()) / len(vals), 6)

        structure_vals = [r.get("structure_family", "") for r in window_rows if r.get("structure_family")]
        topic_vals = [cid for r in window_rows for cid in r.get("concept_cluster_ids", [])]
        angle_vals = [r.get("argument_flow_motif", "") for r in window_rows if r.get("argument_flow_motif")]
        rhetoric_vals = [r.get("rhetorical_family", "") for r in window_rows if r.get("rhetorical_family")]
        argflow_vals = [r.get("argument_flow_motif", "") for r in window_rows if r.get("argument_flow_motif")]

        # Rhythm entropy: bucketed by avg sentence length bins.
        rhythm_bins = []
        vocab_ratio_vals = []
        for r in window_rows:
            sig = r.get("rhythm_signature", {})
            avg = float(sig.get("avg_sentence_len", 0.0) or 0.0)
            if avg < 9:
                rhythm_bins.append("short")
            elif avg < 16:
                rhythm_bins.append("medium")
            elif avg < 25:
                rhythm_bins.append("long")
            else:
                rhythm_bins.append("very_long")
            trigrams = set(r.get("body_trigrams", []))
            vocab_ratio_vals.append(min(1.0, len(trigrams) / 1200.0))

        metrics = {
            "H_structure": entropy(structure_vals),
            "H_topic": entropy(topic_vals),
            "H_angle": entropy(angle_vals),
            "H_rhetoric": entropy(rhetoric_vals),
            "H_rhythm": entropy(rhythm_bins),
            "H_vocab": round(sum(vocab_ratio_vals) / max(1, len(vocab_ratio_vals)), 6),
            "H_argflow": entropy(argflow_vals),
        }

        # Baseline from last ~6 months of entropy records.
        cutoff = (now - timedelta(days=180)).isoformat()
        hist = self.conn.execute(
            "SELECT metrics_json FROM entropy_metrics WHERE created_at >= ? ORDER BY created_at DESC LIMIT 300",
            (cutoff,),
        ).fetchall()

        def zscore(metric_key: str, value: float) -> float:
            vals = []
            for h in hist:
                try:
                    m = json.loads(h["metrics_json"])
                    vals.append(float(m.get(metric_key, 0.0)))
                except Exception:
                    continue
            if len(vals) < 5:
                return 0.0
            mu = sum(vals) / len(vals)
            var = sum((x - mu) ** 2 for x in vals) / max(1, len(vals) - 1)
            sd = math.sqrt(max(var, 1e-9))
            return round((value - mu) / sd, 6)

        zscores = {k: zscore(k, v) for k, v in metrics.items()}

        alerts = []
        if any(z < ENTROPY_CONFIG["collapse_z"] for z in zscores.values()):
            alerts.append("pattern_collapse_alert")

        if dominant_ratio(structure_vals) > ENTROPY_CONFIG["dominance_alert_ratio"]:
            alerts.append("dominance_alert")

        # Similarity drift alert approximated via body similarity trend.
        recent_runs = self.conn.execute(
            "SELECT hidden_similarity_score FROM run_telemetry ORDER BY created_at DESC LIMIT 8"
        ).fetchall()
        if len(recent_runs) >= 8:
            arr = [float(r["hidden_similarity_score"]) for r in reversed(recent_runs)]
            first = sum(arr[:4]) / 4.0
            last = sum(arr[4:]) / 4.0
            if last > first + 0.05:
                alerts.append("similarity_drift_alert")

        self.conn.execute(
            """
            INSERT INTO entropy_metrics(run_id, created_at, metrics_json, zscores_json, alerts_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                created_at=excluded.created_at,
                metrics_json=excluded.metrics_json,
                zscores_json=excluded.zscores_json,
                alerts_json=excluded.alerts_json
            """,
            (
                run_id,
                now.isoformat(),
                json.dumps(metrics, ensure_ascii=False),
                json.dumps(zscores, ensure_ascii=False),
                json.dumps(alerts, ensure_ascii=False),
            ),
        )
        self.conn.commit()
        return {"metrics": metrics, "zscores": zscores, "alerts": alerts}

    def log_run_telemetry(
        self,
        *,
        run_id: str,
        strategy_id: str,
        prompt_lineage_id: str,
        structure_family: str,
        hook_style: str,
        cta_style: str,
        argument_flow_motif: str,
        aggregate_conf: float,
        novelty_score: float,
        hidden_similarity_score: float,
        rejected_stage: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO run_telemetry(
                run_id, created_at, strategy_id, prompt_lineage_id, structure_family, hook_style, cta_style,
                argument_flow_motif, aggregate_conf, novelty_score, hidden_similarity_score, rejected_stage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                created_at=excluded.created_at,
                strategy_id=excluded.strategy_id,
                prompt_lineage_id=excluded.prompt_lineage_id,
                structure_family=excluded.structure_family,
                hook_style=excluded.hook_style,
                cta_style=excluded.cta_style,
                argument_flow_motif=excluded.argument_flow_motif,
                aggregate_conf=excluded.aggregate_conf,
                novelty_score=excluded.novelty_score,
                hidden_similarity_score=excluded.hidden_similarity_score,
                rejected_stage=excluded.rejected_stage
            """,
            (
                run_id,
                datetime.now(timezone.utc).isoformat(),
                strategy_id,
                prompt_lineage_id,
                structure_family,
                hook_style,
                cta_style,
                argument_flow_motif,
                float(aggregate_conf),
                float(novelty_score),
                float(hidden_similarity_score),
                rejected_stage,
            ),
        )
        self.conn.commit()

    def successful_publish_count(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM run_telemetry WHERE rejected_stage=''"
        ).fetchone()
        return int(row["c"]) if row else 0

    def latest_entropy_state(self) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT metrics_json, zscores_json, alerts_json FROM entropy_metrics ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return {"metrics": {}, "zscores": {}, "alerts": []}
        try:
            return {
                "metrics": json.loads(row["metrics_json"] or "{}"),
                "zscores": json.loads(row["zscores_json"] or "{}"),
                "alerts": json.loads(row["alerts_json"] or "[]"),
            }
        except Exception:
            return {"metrics": {}, "zscores": {}, "alerts": []}
