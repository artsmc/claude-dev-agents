#!/usr/bin/env bash
# Aggregate logs from all failed jobs in a pipeline.
#
# Usage:
#   pipeline-failing-logs.sh                 # latest pipeline on current branch
#   pipeline-failing-logs.sh <pipeline-id>   # specific pipeline
#   pipeline-failing-logs.sh --full          # don't truncate logs
#   pipeline-failing-logs.sh --full <id>
#
# Output: for each failing job, a header line then the job's log (tail by default).
# Logs are tailed to the last 200 lines because the real error is almost always
# near the bottom; the rest is build setup noise.
set -euo pipefail

FULL=0
PIPELINE_ID=""

for arg in "$@"; do
  case "$arg" in
    --full) FULL=1 ;;
    *) PIPELINE_ID="$arg" ;;
  esac
done

if ! command -v glab >/dev/null 2>&1; then
  echo "glab not found on PATH. Install: https://gitlab.com/gitlab-org/cli" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found on PATH. Install jq (apt/brew/etc.)." >&2
  exit 2
fi

# glab subcommands (ci, mr) read GITLAB_HOST from env automatically.
# Only `glab api` needs the explicit --hostname flag.
API_HOST_FLAG=""
if [[ -n "${GITLAB_HOST:-}" ]]; then
  API_HOST_FLAG="--hostname ${GITLAB_HOST}"
fi

# Get pipeline JSON. `glab ci get` defaults to latest pipeline on current branch.
if [[ -n "$PIPELINE_ID" ]]; then
  PIPELINE_JSON=$(glab ci get --pipeline-id "$PIPELINE_ID" --output json 2>&1) || {
    echo "Failed to fetch pipeline $PIPELINE_ID: $PIPELINE_JSON" >&2
    exit 1
  }
else
  PIPELINE_JSON=$(glab ci get --output json 2>&1) || {
    echo "Failed to fetch latest pipeline. Are you in a GitLab repo? Output: $PIPELINE_JSON" >&2
    exit 1
  }
fi

PID=$(echo "$PIPELINE_JSON" | jq -r '.id // empty')
STATUS=$(echo "$PIPELINE_JSON" | jq -r '.status // empty')
URL=$(echo "$PIPELINE_JSON" | jq -r '.web_url // empty')

echo "Pipeline #${PID} — status: ${STATUS}"
echo "URL: ${URL}"
echo

FAILED_JOB_IDS=$(echo "$PIPELINE_JSON" | jq -r '.jobs[]? | select(.status=="failed") | .id')

if [[ -z "$FAILED_JOB_IDS" ]]; then
  echo "No failed jobs in this pipeline."
  exit 0
fi

while IFS= read -r JOB_ID; do
  [[ -z "$JOB_ID" ]] && continue
  JOB_NAME=$(echo "$PIPELINE_JSON" | jq -r ".jobs[] | select(.id==${JOB_ID}) | .name")
  JOB_STAGE=$(echo "$PIPELINE_JSON" | jq -r ".jobs[] | select(.id==${JOB_ID}) | .stage")
  echo "===================================================================="
  echo "FAILED JOB: ${JOB_NAME} (stage: ${JOB_STAGE}, id: ${JOB_ID})"
  echo "===================================================================="
  if [[ $FULL -eq 1 ]]; then
    glab ci trace "$JOB_ID" 2>&1 || echo "(failed to fetch log for job ${JOB_ID})"
  else
    glab ci trace "$JOB_ID" 2>&1 | tail -n 200 || echo "(failed to fetch log for job ${JOB_ID})"
  fi
  echo
done <<< "$FAILED_JOB_IDS"
