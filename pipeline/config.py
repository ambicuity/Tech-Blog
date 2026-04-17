from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
DRAFTS_DIR = ROOT / "_drafts"
PIPELINE_DIR = ROOT / ".pipeline"
RUNS_DIR = PIPELINE_DIR / "runs"
SAMPLE_COUNTER_FILE = PIPELINE_DIR / "sample_counter.txt"
NOVELTY_DB_FILE = PIPELINE_DIR / "novelty.db"

AGENT_VERSION = "v3"

THRESHOLDS = {
    "factual": 0.85,
    "seo": 0.80,
    "authority": 0.80,
    "novelty": 0.80,
    "red_team": 0.65,
    "aggregate": 0.82,
}

NOVELTY_THRESHOLDS = {
    # Pre-draft outline gate
    "outline_embedding_cosine": 0.84,
    "heading_similarity_max": 0.72,
    "hook_reuse_last5_max": 2,
    # Post-draft gate
    "intro_embedding_cosine": 0.88,
    "title_embedding_cosine": 0.86,
    "body_embedding_cosine": 0.90,
    "body_trigram_overlap": 0.18,
}

FORBIDDEN_HEADERS = {
    "## introduction",
    "## conclusion",
    "## summary",
    "## interview perspective",
    "## real-world use cases",
}

PRIMARY_CONTENT_TYPES = [
    "Incident Reports",
    "Deep Technical Breakdowns",
    "Architecture Teardowns",
    "How It Actually Works",
]

STARTER_CLUSTERS = [
    "AI Code in Production",
    "Kubernetes Failure Forensics",
    "Python Runtime Performance",
    "Cloud Cost + Reliability Engineering",
]

STAGE_MODEL_SETTINGS = {
    "planner": {"temperature": 0.9, "top_p": 0.95},
    "outline": {"temperature": 0.8, "top_p": 0.9},
    "writer": {"temperature": 0.7, "top_p": 0.9},
    "critic": {"temperature": 0.2, "top_p": 0.7},
    "red_team": {"temperature": 0.1, "top_p": 0.6},
}

ENTROPY_CONFIG = {
    "window": 40,
    "constraint_window": 20,
    "mutation_interval_successes": 8,
    "dominance_alert_ratio": 0.25,
    "warning_z": -0.5,
    "collapse_z": -1.0,
}

STRATEGY_CATALOG = [
    {
        "strategy_id": "incident_forensics_v1",
        "format_family": "incident_report",
        "hook_style": "incident_hook",
        "cta_style": "reflective_question",
        "argument_flow_motif": "symptom->telemetry->root_cause->mitigation->checklist",
        "reasoning_path": "causal_diagnosis",
    },
    {
        "strategy_id": "counterfactual_analysis_v1",
        "format_family": "analysis",
        "hook_style": "contrarian_hook",
        "cta_style": "measurement_cta",
        "argument_flow_motif": "claim->counterfactual->evidence->tradeoff->decision",
        "reasoning_path": "counterfactual",
    },
    {
        "strategy_id": "timeline_postmortem_v1",
        "format_family": "postmortem",
        "hook_style": "story_hook",
        "cta_style": "action_cta",
        "argument_flow_motif": "timeline->branch_point->root_cause->prevention",
        "reasoning_path": "temporal",
    },
    {
        "strategy_id": "teardown_mechanistic_v1",
        "format_family": "teardown",
        "hook_style": "metric_hook",
        "cta_style": "checklist_cta",
        "argument_flow_motif": "surface->mechanism->failure_mode->redesign",
        "reasoning_path": "mechanistic",
    },
    {
        "strategy_id": "faq_inversion_v1",
        "format_family": "playbook",
        "hook_style": "question_hook",
        "cta_style": "action_cta",
        "argument_flow_motif": "myth->evidence->inversion->practice",
        "reasoning_path": "inversion",
    },
]
