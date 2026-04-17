#!/usr/bin/env python3
"""
Title Similarity Deduplication Gate
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.novelty.dedup import SIMILARITY_THRESHOLD, check_title_duplicate


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python check_duplicates.py <path_to_new_post.md>")
        raise SystemExit(2)

    new_post_path = Path(sys.argv[1])
    if not new_post_path.exists():
        print(f"Error: File not found: {new_post_path}")
        raise SystemExit(2)

    is_dup, closest, sim = check_title_duplicate(new_post_path, ROOT / "_posts")
    if is_dup:
        print(f"DUPLICATE DETECTED (similarity: {sim:.2f})")
        print(f"  New post is too similar to: {closest}")
        print(f"  Threshold: {SIMILARITY_THRESHOLD}")
        print("  Action: Reject this post and regenerate with a different topic.")
        raise SystemExit(1)

    if closest:
        print(f"PASSED: Title is sufficiently unique (closest match: {closest}, similarity: {sim:.2f})")
    else:
        print("PASSED: No existing posts to compare against.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
