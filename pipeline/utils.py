from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import RUNS_DIR


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_run_id() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def slugify(value: str) -> str:
    slug = value.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-") or "untitled"


def parse_front_matter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    raw = content[4:end]
    body = content[end + 5:]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = strip_stray_front_matter(body)
    return meta, body


def strip_stray_front_matter(body: str) -> str:
    if "---" not in body:
        return body
    fm_key_pattern = re.compile(
        r"^(?:layout|title|date|categories|tags|description|author)\s*:",
        re.MULTILINE,
    )
    lines = body.split("\n")
    cleaned: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped == "---":
            block_start = i
            i += 1
            fm_key_count = 0
            found_closing = False
            while i < len(lines):
                if lines[i].strip() == "---":
                    found_closing = True
                    break
                if fm_key_pattern.match(lines[i].strip()):
                    fm_key_count += 1
                i += 1
            if found_closing and fm_key_count >= 2:
                i += 1
                continue
            else:
                cleaned.append(line)
                i = block_start + 1
                continue
        cleaned.append(line)
        i += 1
    return "\n".join(cleaned)


def build_front_matter(meta: dict[str, str], body: str) -> str:
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.strip() + "\n"


def default_run_paths(run_id: str) -> dict[str, Path]:
    run_dir = RUNS_DIR / run_id
    return {
        "run_dir": run_dir,
        "manifest": run_dir / "manifest.json",
        "gate_report": run_dir / "gate_report.json",
        "traces": run_dir / "agent_traces.jsonl",
        "planner": run_dir / "planner_output.json",
        "outline": run_dir / "outline_output.json",
        "draft": run_dir / "draft_v1.md",
        "tech_review": run_dir / "tech_review_v1.json",
        "seo_review": run_dir / "seo_review_v1.json",
        "editor_review": run_dir / "editor_review_v1.json",
        "novelty_review": run_dir / "novelty_review_v1.json",
        "red_team_review": run_dir / "red_team_review_v1.json",
        "entropy_report": run_dir / "entropy_report.json",
        "publish_decision": run_dir / "publish_decision.json",
    }


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)
