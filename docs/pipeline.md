# AI Publishing Pipeline

Entrypoint: `python scripts/run_pipeline.py`

## Stages
1. `planner` (multi-candidate topic+angle planning + strategy rotation)
2. `outliner` (outline diversity under hard anti-repetition constraints)
3. `writer` (outline-locked generation + prompt lineage selection)
4. `technical_reviewer`
5. `seo_reviewer`
6. `editor` (style/authority)
7. `novelty_reviewer` (semantic + structural anti-repetition)
8. `red_team_reviewer` (adversarial hidden-sameness detector)
9. `publisher`

## Quality Gates
1. Structural
2. Factual
3. SEO completeness
4. Link integrity
5. Authority/readability
6. Novelty similarity
7. Red-team hidden-similarity

## Long-Horizon Anti-Collapse Features
- Strategy registry with usage/reward tracking and Thompson sampling.
- Prompt lineage (`champion` / `challenger`) with periodic mutation and rollback/promotion.
- Constraint solver over rolling window (hard exclusions for structure/hook/argflow/CTA combinations).
- Regeneration decision tree (mutate angle/structure/reasoning/topic; no text-only paraphrase).
- Entropy telemetry and alerts (`pattern_collapse_alert`, `dominance_alert`, `similarity_drift_alert`).

## Novelty Memory
Pipeline maintains `.pipeline/novelty.db` with per-post metadata:
- title/intro/outline/body embeddings
- heading signature
- hook style / CTA style / rhetorical family
- body trigram signature
- argument flow graph + motif
- concept cluster IDs
- narrative/explanation/analogy archetypes
- opening/closing archetypes
- rhythm signature

## Output Artifacts
Per run, artifacts are written to `.pipeline/runs/<run_id>/`:
- `manifest.json`
- `planner_output.json`
- `outline_output.json`
- `draft_v1.md`
- `tech_review_v1.json`
- `seo_review_v1.json`
- `editor_review_v1.json`
- `novelty_review_v1.json`
- `red_team_review_v1.json`
- `entropy_report.json`
- `gate_report.json`
- `publish_decision.json`
- `agent_traces.jsonl`

## Publish Policy
- Publish to `_posts/` only if all gates pass and confidence threshold is met.
- Otherwise route to `_drafts/` quarantine.
- Every 5th green run is forced to sampling review.

## Simulation
Run long-horizon drift simulation:

```bash
python scripts/simulate_long_horizon.py --runs 1000
```
