#!/usr/bin/env bash
# shadow-snapshot.sh - create git checkpoint before Write/Edit operations
# Reads PreToolUse JSON from stdin; exits 0 to allow the tool call to proceed.

set -euo pipefail

REPO="/home/artsmc/.claude"
MAX_AGE_HOURS=24

# Parse tool name from stdin (PreToolUse passes JSON)
INPUT=$(cat)
TOOL=$(echo "$INPUT" | grep -o '"tool_name":"[^"]*"' | cut -d'"' -f4)

# Only snapshot for file-mutation tools
if [[ "$TOOL" != "Write" && "$TOOL" != "Edit" ]]; then
  exit 0
fi

cd "$REPO"

# Require a clean-enough repo (must be a git repo)
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

EPOCH=$(date +%s)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BRANCH="shadow/${EPOCH}_${TIMESTAMP}"

# Create branch pointing at current HEAD (no working-tree changes)
git branch "$BRANCH" HEAD 2>/dev/null || true

# Cleanup: delete shadow branches older than MAX_AGE_HOURS
# Uses epoch embedded in branch name (creatordate reflects commit date, not branch creation)
NOW=$(date +%s)
git for-each-ref --format='%(refname:short)' 'refs/heads/shadow/*' \
  | while read -r branch; do
      # Extract epoch from branch name: shadow/<epoch>_<timestamp>
      BRANCH_EPOCH=$(echo "$branch" | sed 's|shadow/||' | cut -d'_' -f1)
      if [[ "$BRANCH_EPOCH" =~ ^[0-9]+$ ]]; then
        AGE=$(( NOW - BRANCH_EPOCH ))
        if (( AGE > MAX_AGE_HOURS * 3600 )); then
          git branch -D "$branch" 2>/dev/null || true
        fi
      fi
    done

exit 0
