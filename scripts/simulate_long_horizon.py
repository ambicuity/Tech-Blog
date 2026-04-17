#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.config import NOVELTY_DB_FILE
from pipeline.novelty.memory import NoveltyMemory


def run_sim(memory: NoveltyMemory, runs: int, seed: int = 7) -> dict:
    rng = random.Random(seed)
    snapshot_points = [50, 200, 1000]
    rows = memory.fetch_records(limit=400)
    if not rows:
        return {"error": "no_history"}

    failures = 0
    hidden_scores = []
    strategy_freq: dict[str, int] = {}

    for i in range(1, runs + 1):
        chosen = rows[rng.randrange(0, len(rows))]
        sf = chosen.get("structure_family", "deep_dive")
        hk = chosen.get("hook_style", "problem_hook")
        arg = chosen.get("argument_flow_motif", "")
        cta = chosen.get("cta_style", "neutral_cta")
        key = f"{sf}|{hk}|{arg}|{cta}"
        strategy_freq[key] = strategy_freq.get(key, 0) + 1

        sim = min(0.99, 0.45 + (strategy_freq[key] / max(1, i)) + rng.random() * 0.1)
        hidden_scores.append(sim)
        if sim > 0.85:
            failures += 1

    out = {
        "runs": runs,
        "failure_rate": round(failures / max(1, runs), 6),
        "hidden_similarity_p50": round(sorted(hidden_scores)[len(hidden_scores) // 2], 6),
        "hidden_similarity_p90": round(sorted(hidden_scores)[int(len(hidden_scores) * 0.9)], 6),
        "dominant_pattern_ratio": round(max(strategy_freq.values()) / max(1, runs), 6),
        "top_patterns": sorted(strategy_freq.items(), key=lambda x: (-x[1], x[0]))[:10],
        "snapshots": {},
    }

    for n in snapshot_points:
        if runs >= n:
            p = hidden_scores[:n]
            out["snapshots"][str(n)] = {
                "p50": round(sorted(p)[len(p) // 2], 6),
                "p90": round(sorted(p)[int(len(p) * 0.9)], 6),
            }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Long-horizon repetition simulation")
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    memory = NoveltyMemory(NOVELTY_DB_FILE)
    try:
        result = run_sim(memory, runs=args.runs, seed=args.seed)
        print(json.dumps(result, indent=2))
    finally:
        memory.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
