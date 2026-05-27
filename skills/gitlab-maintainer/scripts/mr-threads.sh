#!/usr/bin/env bash
# Dump all discussion threads on an MR as structured JSON.
#
# Usage:
#   mr-threads.sh <mr-iid-or-branch>
#   mr-threads.sh                    # tries current branch's open MR
#   mr-threads.sh <mr> --unresolved  # only unresolved resolvable threads
#
# Output: JSON array, one element per discussion thread, with:
#   { id, resolved, resolvable, position (file/line or null),
#     author, created_at, notes: [ { body, author, created_at, system } ] }
set -euo pipefail

if ! command -v glab >/dev/null 2>&1; then echo "glab not found" >&2; exit 2; fi
if ! command -v jq >/dev/null 2>&1; then echo "jq not found" >&2; exit 2; fi

UNRESOLVED_ONLY=0
MR=""
for arg in "$@"; do
  case "$arg" in
    --unresolved) UNRESOLVED_ONLY=1 ;;
    *) MR="$arg" ;;
  esac
done

API_HOST_FLAG=""
if [[ -n "${GITLAB_HOST:-}" ]]; then API_HOST_FLAG="--hostname ${GITLAB_HOST}"; fi
PROJECT_PATH="${GITLAB_PROJECT_ENC:-:id}"

# Resolve MR IID
if [[ -z "$MR" ]]; then
  MR_IID=$(glab mr view --output json 2>/dev/null | jq -r '.iid // empty')
  if [[ -z "$MR_IID" ]]; then
    echo "No MR found for current branch. Pass an MR IID or branch name." >&2
    exit 1
  fi
else
  # If $MR looks numeric, use as IID; otherwise treat as branch and look it up.
  if [[ "$MR" =~ ^[0-9]+$ ]]; then
    MR_IID="$MR"
  else
    MR_IID=$(glab mr view "$MR" --output json 2>/dev/null | jq -r '.iid // empty')
    if [[ -z "$MR_IID" ]]; then
      echo "No MR found for '$MR'." >&2
      exit 1
    fi
  fi
fi

# Fetch all discussions (paginated). glab api auto-pages with --paginate.
RAW=$(glab api $API_HOST_FLAG --paginate "projects/${PROJECT_PATH}/merge_requests/${MR_IID}/discussions") || {
  echo "Failed to fetch discussions for MR !${MR_IID}" >&2
  exit 1
}

# Reshape into a cleaner structure
FILTER='
[ .[] | {
    id: .id,
    resolvable: (.notes[0].resolvable // false),
    resolved: (.notes[0].resolved // false),
    position: (.notes[0].position // null),
    author: (.notes[0].author.username // null),
    created_at: (.notes[0].created_at // null),
    notes: [ .notes[] | {
      id: .id,
      body: .body,
      author: .author.username,
      created_at: .created_at,
      system: .system
    } ]
  }
]'

if [[ $UNRESOLVED_ONLY -eq 1 ]]; then
  FILTER="${FILTER} | map(select(.resolvable == true and .resolved == false))"
fi

echo "$RAW" | jq "$FILTER"
