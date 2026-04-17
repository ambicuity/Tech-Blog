"""Novelty memory and anti-repetition utilities."""

from .dedup import check_title_duplicate
from .memory import (
    NoveltyMemory,
    NoveltyRecord,
    build_body_trigrams,
    classify_cta_style,
    classify_hook_style,
    classify_rhetorical_family,
    extract_headings,
    extract_intro,
    normalized_levenshtein_similarity,
)
from .similarity import cosine_similarity, embed_text

__all__ = [
    "NoveltyMemory",
    "NoveltyRecord",
    "check_title_duplicate",
    "embed_text",
    "cosine_similarity",
    "extract_intro",
    "extract_headings",
    "classify_hook_style",
    "classify_cta_style",
    "classify_rhetorical_family",
    "build_body_trigrams",
    "normalized_levenshtein_similarity",
]
