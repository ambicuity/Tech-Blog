from __future__ import annotations

import re
from pathlib import Path

SIMILARITY_THRESHOLD = 0.70
MIN_TOKENS_FOR_COMPARISON = 3


def extract_title_from_file(file_path: Path) -> str | None:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")[:2000]
    except Exception:
        return None
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return m.group(1).strip() if m else None


def extract_title_from_slug(slug: str) -> str:
    stripped = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    return stripped.replace("-", " ").lower()


def tokenize(text: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "the",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "and",
        "or",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "how",
        "what",
        "why",
        "when",
        "where",
        "your",
        "my",
        "our",
    }
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in stop_words and len(w) > 1}


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_title_duplicate(new_post_path: Path, posts_dir: Path) -> tuple[bool, str | None, float]:
    if not posts_dir.exists():
        return False, None, 0.0

    new_title = extract_title_from_file(new_post_path)
    if not new_title:
        return False, None, 0.0

    new_tokens = tokenize(new_title)
    if len(new_tokens) < MIN_TOKENS_FOR_COMPARISON:
        return False, None, 0.0

    highest_sim = 0.0
    closest_match = None
    new_resolved = new_post_path.resolve()

    for existing_file in posts_dir.glob("*.md"):
        if existing_file.resolve() == new_resolved:
            continue
        existing_title = extract_title_from_file(existing_file) or extract_title_from_slug(existing_file.stem)
        existing_tokens = tokenize(existing_title)
        if len(existing_tokens) < MIN_TOKENS_FOR_COMPARISON:
            continue
        sim = jaccard_similarity(new_tokens, existing_tokens)
        if sim > highest_sim:
            highest_sim = sim
            closest_match = existing_file.stem

    return highest_sim >= SIMILARITY_THRESHOLD, closest_match, highest_sim
