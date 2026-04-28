#!/usr/bin/env python3
"""
Blog Post Validator (strict anti-collapse edition)

Validates the latest published post in `_posts` and fails CI when:
- Structural quality is broken (front matter / code fences / required sections)
- Template-like anti-patterns dominate (weak lead-ins / title-verb collapse)
- Content shape does not meet baseline technical depth (>= 3 H2 sections)
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

# Phrases banned from prose body (case-insensitive substring checks).
BANNED_FLUFF_PHRASES = [
    "in conclusion",
    "delve into",
    "paramount",
    "in today's world",
    "in today's digital world",
    "in today's rapidly",
    "dynamic landscape",
    "ever-evolving",
    "in the realm of",
    "it is important to note",
    "it's worth noting that",
    "let's dive in",
    "without further ado",
    "in this blog post we will",
    "in this article we will",
    "has revolutionized",
    "game-changer",
    "leverage the power",
]

# Headers indicating generic templating.
BANNED_HEADERS = [
    "## introduction",
    "## conclusion",
    "## interview perspective",
    "## real-world use cases",
    "## summary",
    "# introduction",
    "# conclusion",
]

BANNED_TITLE_WORDS = [
    "unlocking",
    "mastering",
    "streamlining",
    "orchestrating",
    "empowering",
    "navigating",
    "demystifying",
    "revolutionizing",
    "supercharging",
    "turbocharging",
    "harnessing",
]

REQUIRED_FRONT_MATTER_FIELDS = [
    "layout",
    "title",
    "date",
    "categories",
    "tags",
]

# Anti-collapse defaults.
RECENT_WINDOW = 10
DOMINANCE_THRESHOLD = 0.50  # reject when >50%
MIN_H2_COUNT = 3

LEAD_IN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("we_recently", re.compile(r"^\s*we recently\b", re.I)),
    ("our_team_recently", re.compile(r"^\s*our team recently\b", re.I)),
    ("we_started", re.compile(r"^\s*we started\b", re.I)),
    ("recently_our_team", re.compile(r"^\s*recently,\s*our team\b", re.I)),
    ("team_adopted_ai", re.compile(r"^\s*(we|our team)\b.*\badopted\b.*\bai", re.I)),
]


def _extract_front_matter(content: str) -> str | None:
    if not content.startswith("---\n"):
        return None
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return None
    return parts[0][4:]


def _extract_body(content: str) -> str:
    if content.startswith("---\n"):
        parts = content.split("\n---\n", 1)
        if len(parts) == 2:
            return parts[1]
    return content


def _strip_code_blocks(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    return text


def _first_paragraph(body: str) -> str:
    for para in body.split("\n\n"):
        p = para.strip()
        if not p:
            continue
        if p.startswith("#") or p.startswith("```"):
            continue
        return p
    return ""


def _lead_in_label(para: str) -> str:
    probe = para.strip()
    for label, pat in LEAD_IN_PATTERNS:
        if pat.search(probe):
            return label
    return "other"


def _title_first_word(title: str) -> str:
    m = re.match(r"\s*([A-Za-z]+)", title)
    return (m.group(1).lower() if m else "").strip()


def _parse_title_from_front_matter(front_matter: str) -> str:
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', front_matter, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _recent_posts(posts_dir: Path, latest: Path, limit: int) -> list[Path]:
    posts = sorted(posts_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    filtered = [p for p in posts if p != latest]
    return filtered[:limit]


def validate_markdown_file(file_path: Path, posts_dir: Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"Error reading {file_path}: {exc}")
        return False

    print(f"Validating {file_path}...")
    errors: list[str] = []
    warnings: list[str] = []

    front_matter = _extract_front_matter(content)
    body = _extract_body(content)
    prose = _strip_code_blocks(body)
    prose_lower = prose.lower()

    # 1) Front matter checks
    if front_matter is None:
        errors.append("Missing or malformed front matter block")
    else:
        for field in REQUIRED_FRONT_MATTER_FIELDS:
            if f"{field}:" not in front_matter:
                errors.append(f"Missing required front matter field: '{field}'")
        title = _parse_title_from_front_matter(front_matter)
        for banned in BANNED_TITLE_WORDS:
            if banned in title.lower():
                errors.append(f"Title contains banned word: '{banned}'")

    # 2) Code block integrity
    fences = body.count("```")
    if fences % 2 != 0:
        errors.append(f"Unclosed code blocks detected (found {fences} fences, expected even number)")
    if "```" not in body:
        errors.append("No code blocks found. Technical posts must contain code.")
    in_code_block = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block and stripped == "```":
                warnings.append("Found code block without language identifier")
                break
            in_code_block = not in_code_block
    if "```markdown" in content and content.strip().startswith("```markdown"):
        errors.append("Found '```markdown' wrapper at start of file (LLM artifact)")

    # 3) Template and fluff checks (prose only)
    for phrase in BANNED_FLUFF_PHRASES:
        if phrase in prose_lower:
            errors.append(f"Found forbidden fluff phrase: '{phrase}'")
    for header in BANNED_HEADERS:
        if header in prose_lower:
            errors.append(f"Found banned template header: '{header}'")

    # 4) Link and required section checks (strict)
    internal_links = re.findall(r"\]\((/posts/[^)]+)\)", body)
    external_links = re.findall(r"\]\((https?://[^)]+)\)", body)
    if len(internal_links) < 2:
        warnings.append("Insufficient internal links (minimum: 2)")
    if len(external_links) < 2:
        warnings.append("External authoritative links are low (recommended minimum: 2)")
    if "### Evidence & References" not in body and "## Evidence & References" not in body:
        errors.append("Missing required section: 'Evidence & References'")
    if "### Operational Checklist" not in body and "## Operational Checklist" not in body:
        errors.append("Missing required section: 'Operational Checklist'")

    # 5) Anti-collapse shape checks
    h2_count = sum(1 for line in body.splitlines() if line.startswith("## "))
    if h2_count < MIN_H2_COUNT:
        errors.append(f"Insufficient H2 sections ({h2_count}); require at least {MIN_H2_COUNT}")

    if front_matter is not None:
        latest_title = _parse_title_from_front_matter(front_matter)
        latest_first_word = _title_first_word(latest_title)
        if latest_first_word:
            recent_files = _recent_posts(posts_dir, file_path, RECENT_WINDOW)
            recent_first_words = []
            for post in recent_files:
                txt = post.read_text(encoding="utf-8")
                fm = _extract_front_matter(txt)
                if not fm:
                    continue
                recent_first_words.append(_title_first_word(_parse_title_from_front_matter(fm)))
            if recent_first_words:
                same_word = sum(1 for word in recent_first_words if word == latest_first_word)
                ratio = same_word / len(recent_first_words)
                if ratio > DOMINANCE_THRESHOLD:
                    errors.append(
                        "Title opening verb/pattern is overused in recent posts "
                        f"('{latest_first_word}' appears in {same_word}/{len(recent_first_words)} recent titles)"
                    )

    latest_para = _first_paragraph(body)
    if latest_para:
        latest_label = _lead_in_label(latest_para)
        if latest_label != "other":
            recent_files = _recent_posts(posts_dir, file_path, RECENT_WINDOW)
            labels = []
            for post in recent_files:
                txt = post.read_text(encoding="utf-8")
                labels.append(_lead_in_label(_first_paragraph(_extract_body(txt))))
            same_label = sum(1 for label in labels if label == latest_label)
            ratio = same_label / len(labels) if labels else 0.0
            if labels and ratio > DOMINANCE_THRESHOLD:
                pct = math.floor(ratio * 100)
                errors.append(
                    "Lead-in archetype is overused in recent posts "
                    f"('{latest_label}' appears in {same_label}/{len(labels)} recent posts, {pct}%)"
                )

    # 6) Length diagnostics
    body_words = len(re.findall(r"[A-Za-z0-9']+", body))
    if body_words < 300:
        warnings.append(f"Post is short ({body_words} words).")
    if body_words > 5000:
        warnings.append(f"Post is very long ({body_words} words).")

    for warning in warnings:
        print(f"  [Warning] {warning}")

    if errors:
        print(f"FAILED: {file_path}")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED: {file_path}")
    return True


def main() -> int:
    posts_dir = Path("_posts")
    if not posts_dir.exists():
        print("No _posts directory found.")
        return 0

    posts = list(posts_dir.glob("*.md"))
    if not posts:
        print("No posts found to validate.")
        return 0

    posts.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest = posts[0]
    ok = validate_markdown_file(latest, posts_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
