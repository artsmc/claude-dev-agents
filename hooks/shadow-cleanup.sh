#!/usr/bin/env bash
# Delete all shadow/* branches older than 24 hours
# Uses epoch embedded in branch name (shadow/<epoch>_<timestamp>)
cd /home/artsmc/.claude
NOW=$(date +%s)
git for-each-ref --format='%(refname:short)' 'refs/heads/shadow/*' \
  | while read -r branch; do
      BRANCH_EPOCH=$(echo "$branch" | sed 's|shadow/||' | cut -d'_' -f1)
      if [[ "$BRANCH_EPOCH" =~ ^[0-9]+$ ]]; then
        AGE=$(( NOW - BRANCH_EPOCH ))
        if (( AGE > 86400 )); then
          git branch -D "$branch"
          echo "Deleted $branch"
        fi
      fi
    done
