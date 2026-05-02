#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:?Set GOOGLE_API_KEY}"

DATES_TOPICS=(
    "2026-01-26|database connection pool exhaustion under sustained load in Kubernetes"
    "2026-02-23|debugging slow container startup probes in production Kubernetes clusters"
    "2026-04-20|eliminating zombie processes in AI-generated Python services on Kubernetes"
    "2026-04-27|tracing cascading timeout failures across microservice boundaries"
)

for entry in "${DATES_TOPICS[@]}"; do
    IFS='|' read -r date topic <<< "$entry"
    echo "=== Generating blog for $date (topic: $topic) ==="
    POST_DATE="$date" TOPIC_HINT="$topic" python3 "$SCRIPT_DIR/run_pipeline.py"
    echo "=== Sleeping 120s to avoid rate limits ==="
    sleep 120
done

echo "=== All missed blogs generated ==="