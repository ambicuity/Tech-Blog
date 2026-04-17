from __future__ import annotations

import re
from pathlib import Path

from pipeline.config import AGENT_VERSION, POSTS_DIR
from pipeline.models import AgentResult
from pipeline.utils import build_front_matter, parse_front_matter

CLUSTER_INDEX_FILE = Path(__file__).resolve().parents[2] / "_data" / "topic_clusters.yml"
CLUSTER_EXTERNAL_REFERENCES = {
    "ai_code_in_production": [
        "https://platform.openai.com/docs/guides/production-best-practices",
        "https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning",
    ],
    "kubernetes_failure_forensics": [
        "https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/",
        "https://kubernetes.io/docs/tasks/debug/debug-cluster/",
    ],
    "python_runtime_performance": [
        "https://docs.python.org/3/library/profile.html",
        "https://docs.python.org/3/library/asyncio.html",
    ],
    "cloud_cost_reliability": [
        "https://sre.google/sre-book/table-of-contents/",
        "https://aws.amazon.com/architecture/well-architected/",
    ],
}


def _parse_cluster_index() -> dict[str, dict[str, list[str] | str]]:
    if not CLUSTER_INDEX_FILE.exists():
        return {}
    content = CLUSTER_INDEX_FILE.read_text(encoding="utf-8", errors="ignore")
    clusters: dict[str, dict[str, list[str] | str]] = {}
    current = None
    list_key = None
    for raw in content.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1].strip()
            clusters[current] = {"keywords": [], "pillar": "", "deep_dives": [], "runbooks": []}
            list_key = None
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.endswith(":"):
            key = stripped[:-1]
            if key in {"keywords", "deep_dives", "runbooks"}:
                list_key = key
            else:
                list_key = None
            continue
        if stripped.startswith("- "):
            value = stripped[2:].strip().strip('"')
            if list_key in {"keywords", "deep_dives", "runbooks"}:
                clusters[current][list_key].append(value)
            continue
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"')
            if k == "pillar":
                clusters[current][k] = v
    return clusters


def _extract_post_links(limit: int = 200) -> list[str]:
    links: list[str] = []
    files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files[:limit]:
        slug = p.stem
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
        links.append(f"/posts/{slug}/")
    return links


def _ensure_front_matter(meta: dict[str, str], title: str) -> dict[str, str]:
    if "layout" not in meta:
        meta["layout"] = "post"
    if "title" not in meta:
        meta["title"] = f'"{title}"'
    if "description" not in meta:
        meta["description"] = '"Production-grade incident analysis with concrete root-cause and mitigation guidance."'
    if "author" not in meta:
        meta["author"] = "ritesh"
    if "categories" not in meta:
        meta["categories"] = "[Engineering, Reliability]"
    if "tags" not in meta:
        meta["tags"] = "[engineering, production, reliability]"
    return meta


def _infer_cluster(draft: str, clusters: dict[str, dict[str, list[str] | str]]) -> str:
    lowered = draft.lower()
    best_cluster = ""
    best_score = 0
    for cluster_name, cfg in clusters.items():
        kws = cfg.get("keywords", []) if isinstance(cfg.get("keywords"), list) else []
        score = sum(1 for kw in kws if str(kw).lower() in lowered)
        if score > best_score:
            best_score = score
            best_cluster = cluster_name
    return best_cluster


def _cluster_suggestions(
    cluster: str,
    clusters: dict[str, dict[str, list[str] | str]],
) -> list[str]:
    if not cluster or cluster not in clusters:
        return []
    cfg = clusters[cluster]
    links: list[str] = []
    pillar = cfg.get("pillar", "")
    if isinstance(pillar, str) and pillar:
        links.append(pillar)
    for key in ("deep_dives", "runbooks"):
        vals = cfg.get(key, [])
        if isinstance(vals, list):
            for v in vals:
                if isinstance(v, str) and v:
                    links.append(v)
                    break
    # Deduplicate while preserving order.
    deduped = []
    seen = set()
    for link in links:
        if link not in seen:
            deduped.append(link)
            seen.add(link)
    return deduped


def review(draft: str, title_hint: str = "", cluster_hint: str = "") -> AgentResult:
    meta, body = parse_front_matter(draft)
    title = title_hint or meta.get("title", "Production Engineering Post").strip('"')
    meta = _ensure_front_matter(meta, title)
    clusters = _parse_cluster_index()
    cluster = cluster_hint or _infer_cluster(draft, clusters)
    if cluster:
        meta["cluster"] = f'"{cluster}"'

    internal = re.findall(r"\]\((/posts/[^)]+)\)", body)
    external = re.findall(r"\]\((https?://[^)]+)\)", body)

    suggested_internal: list[str] = []
    if len(internal) < 3:
        cluster_links = _cluster_suggestions(cluster, clusters)
        for link in cluster_links:
            if link not in internal and len(suggested_internal) < 3:
                suggested_internal.append(link)

    if len(suggested_internal) < 3:
        pool = _extract_post_links()
        for link in pool:
            if link not in internal and len(suggested_internal) < 3:
                suggested_internal.append(link)

    suggested_external: list[str] = []
    cluster_refs = CLUSTER_EXTERNAL_REFERENCES.get(cluster, [])
    for ref in cluster_refs:
        if ref not in external and len(suggested_external) < 2:
            suggested_external.append(ref)

    # Auto-append related links when needed.
    if suggested_internal:
        body = body.rstrip() + "\n\n### Related\n"
        labels = ["Pillar", "Deep Dive", "Runbook"]
        for idx, l in enumerate(suggested_internal[:3]):
            label = labels[idx] if idx < len(labels) else "Related Engineering Note"
            body += f"- [{label}]({l})\n"
    if suggested_external:
        if "### Evidence & References" not in body and "## Evidence & References" not in body:
            body = body.rstrip() + "\n\n### Evidence & References\n"
        for ref in suggested_external:
            body += f"- [Primary Source]({ref})\n"

    internal_after = re.findall(r"\]\((/posts/[^)]+)\)", body)
    external_after = re.findall(r"\]\((https?://[^)]+)\)", body)

    warnings: list[str] = []
    if len(internal_after) < 2:
        warnings.append("internal_links_below_min")
    if len(external_after) < 2:
        warnings.append("external_links_below_min")
    if not cluster:
        warnings.append("missing_cluster_assignment")

    seo_score = 0.95
    if warnings:
        seo_score -= 0.1 * len(warnings)
    seo_score = max(0.0, round(seo_score, 3))

    patched = build_front_matter(meta, body)

    status = "passed" if seo_score >= 0.8 else "failed"
    return AgentResult(
        name="seo_reviewer",
        version=AGENT_VERSION,
        status=status,
        confidence=seo_score,
        artifacts={
            "seo_score": seo_score,
            "missing_metadata": [w for w in warnings if w.startswith("metadata")],
            "internal_links": internal_after,
            "external_links": external_after,
            "suggested_internal_links": suggested_internal[:3],
            "suggested_external_links": suggested_external[:2],
            "patched_draft": patched,
            "warnings": warnings,
        },
        errors=[] if status == "passed" else ["seo_score_below_threshold"],
    )
