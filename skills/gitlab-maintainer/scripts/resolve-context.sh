#!/usr/bin/env bash
# Resolve the GitLab host, project path, and token for the current repo.
# Prints shell-eval-able exports so the caller can use them:
#
#   eval "$(bash resolve-context.sh)"          # use 'origin' remote
#   eval "$(bash resolve-context.sh new_origin)" # use a specific remote
#
# Sets GITLAB_HOST, GITLAB_PROJECT, GITLAB_PROJECT_ENC, and (if extractable)
# GITLAB_TOKEN. Does NOT overwrite GITLAB_TOKEN if it's already set in the env.
#
# Exits 1 if not in a git repo or the named remote doesn't exist.
set -euo pipefail

REMOTE_NAME="${1:-origin}"

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "echo 'Not inside a git repository' >&2; exit 1" >&2
  exit 1
fi

URL=$(git remote get-url "$REMOTE_NAME" 2>/dev/null || true)
if [[ -z "$URL" ]]; then
  echo "Remote '$REMOTE_NAME' not found. Available remotes:" >&2
  git remote 2>&1 | sed 's/^/  /' >&2
  exit 1
fi

# Parse HTTPS or SSH URL
# HTTPS: https://[user[:token]@]host/path/to/repo.git
# SSH:   git@host:path/to/repo.git
HOST=""
PROJECT_PATH=""
URL_TOKEN=""

if [[ "$URL" =~ ^https?://([^@]*@)?([^/]+)/(.+)$ ]]; then
  USERINFO="${BASH_REMATCH[1]}"
  HOST="${BASH_REMATCH[2]}"
  PROJECT_PATH="${BASH_REMATCH[3]%.git}"
  if [[ -n "$USERINFO" && "$USERINFO" == *:* ]]; then
    URL_TOKEN="${USERINFO#*:}"
    URL_TOKEN="${URL_TOKEN%@}"
  fi
elif [[ "$URL" =~ ^[^@]+@([^:]+):(.+)$ ]]; then
  HOST="${BASH_REMATCH[1]}"
  PROJECT_PATH="${BASH_REMATCH[2]%.git}"
else
  echo "Could not parse remote URL: $URL" >&2
  exit 1
fi

# URL-encode slashes in project path (the only character that needs encoding for the
# normal case of "group/subgroup/repo"; if your project paths contain other special
# chars they'd need more encoding but that's vanishingly rare in GitLab)
PROJECT_ENC=$(echo "$PROJECT_PATH" | sed 's|/|%2F|g')

# Emit exports. Use printf so paths with special chars are quoted safely.
printf 'export GITLAB_HOST=%q\n' "$HOST"
printf 'export GITLAB_PROJECT=%q\n' "$PROJECT_PATH"
printf 'export GITLAB_PROJECT_ENC=%q\n' "$PROJECT_ENC"

# Only export GITLAB_TOKEN if it isn't already set AND we extracted one from the URL
if [[ -z "${GITLAB_TOKEN:-}" && -n "$URL_TOKEN" ]]; then
  printf 'export GITLAB_TOKEN=%q\n' "$URL_TOKEN"
fi
