#!/usr/bin/env bash
# Build a compact context bundle for an MR: metadata + pipeline status + unresolved threads.
# Useful as the first call when starting MR review or response work — one command, full picture.
#
# Usage:
#   mr-context.sh <mr-iid-or-branch>
#   mr-context.sh                    # current branch's open MR
#
# Output: JSON object:
#   { mr: { iid, title, author, source_branch, target_branch, state, web_url, approvals_left, draft },
#     pipeline: { status, web_url, failed_jobs: [...] } | null,
#     unresolved_threads: [...]   # same shape as mr-threads.sh --unresolved
#   }
set -euo pipefail

if ! command -v glab >/dev/null 2>&1; then echo "glab not found" >&2; exit 2; fi
if ! command -v jq >/dev/null 2>&1; then echo "jq not found" >&2; exit 2; fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MR_ARG="${1:-}"

API_HOST_FLAG=""
if [[ -n "${GITLAB_HOST:-}" ]]; then API_HOST_FLAG="--hostname ${GITLAB_HOST}"; fi
PROJECT_PATH="${GITLAB_PROJECT_ENC:-:id}"

# Resolve MR
if [[ -z "$MR_ARG" ]]; then
  MR_JSON=$(glab mr view --output json 2>/dev/null) || {
    echo "No MR found for current branch." >&2; exit 1;
  }
else
  MR_JSON=$(glab mr view "$MR_ARG" --output json 2>/dev/null) || {
    echo "No MR found for '$MR_ARG'." >&2; exit 1;
  }
fi

MR_IID=$(echo "$MR_JSON" | jq -r '.iid')

MR_SUMMARY=$(echo "$MR_JSON" | jq '{
  iid: .iid,
  title: .title,
  author: .author.username,
  source_branch: .source_branch,
  target_branch: .target_branch,
  state: .state,
  web_url: .web_url,
  approvals_left: (.approvals_left // null),
  draft: (.draft // .work_in_progress // false)
}')

# Pipeline for the MR's HEAD pipeline (may be null for draft MRs without pipelines)
PIPELINE_RAW=$(echo "$MR_JSON" | jq '.head_pipeline // .pipeline // null')
if [[ "$PIPELINE_RAW" == "null" ]]; then
  PIPELINE_OUT="null"
else
  PID=$(echo "$PIPELINE_RAW" | jq -r '.id')
  FULL_PIPELINE=$(glab api $API_HOST_FLAG "projects/${PROJECT_PATH}/pipelines/${PID}" 2>/dev/null || echo 'null')
  JOBS=$(glab api $API_HOST_FLAG --paginate "projects/${PROJECT_PATH}/pipelines/${PID}/jobs" 2>/dev/null || echo '[]')
  FAILED_JOBS=$(echo "$JOBS" | jq '[.[] | select(.status=="failed") | {id, name, stage, web_url}]')
  PIPELINE_OUT=$(jq -n \
    --argjson p "$FULL_PIPELINE" \
    --argjson f "$FAILED_JOBS" \
    '{status: $p.status, web_url: $p.web_url, failed_jobs: $f}')
fi

UNRESOLVED=$(bash "${SCRIPT_DIR}/mr-threads.sh" "$MR_IID" --unresolved 2>/dev/null || echo '[]')

jq -n \
  --argjson mr "$MR_SUMMARY" \
  --argjson pipeline "$PIPELINE_OUT" \
  --argjson threads "$UNRESOLVED" \
  '{mr: $mr, pipeline: $pipeline, unresolved_threads: $threads}'
