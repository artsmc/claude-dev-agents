# Fix 2: Shadow Git Snapshots

## Problem

The Claude Dev Agents framework has no per-step rollback. When an agent writes bad code during
a Write or Edit operation, recovery requires manual git operations with no clear checkpoint to
return to. Agents can corrupt multiple files across a session before the damage is noticed.

## Solution

A PreToolUse hook intercepts every Write and Edit call and creates a lightweight git snapshot
branch before the operation executes. Recovery is a single `git checkout` command.

---

### Hook Script

Save as `/home/artsmc/.claude/hooks/shadow-snapshot.sh`

```bash
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

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BRANCH="shadow/${TIMESTAMP}"

# Create branch pointing at current HEAD (no working-tree changes)
git branch "$BRANCH" HEAD 2>/dev/null || true

# Cleanup: delete shadow branches older than MAX_AGE_HOURS
git for-each-ref --format='%(refname:short) %(creatordate:unix)' 'refs/heads/shadow/*' \
  | while read -r branch epoch; do
      AGE=$(( $(date +%s) - epoch ))
      if (( AGE > MAX_AGE_HOURS * 3600 )); then
        git branch -D "$branch" 2>/dev/null || true
      fi
    done

exit 0
```

---

### Hook Configuration

Add to `/home/artsmc/.claude/settings.json` inside the `"hooks"` object:

```json
"PreToolUse": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "bash /home/artsmc/.claude/hooks/shadow-snapshot.sh"
      }
    ]
  }
]
```

---

### Cleanup Script

Save as `/home/artsmc/.claude/hooks/shadow-cleanup.sh` for manual or cron use:

```bash
#!/usr/bin/env bash
# Delete all shadow/* branches older than 24 hours
cd /home/artsmc/.claude
git for-each-ref --format='%(refname:short) %(creatordate:unix)' 'refs/heads/shadow/*' \
  | while read -r branch epoch; do
      AGE=$(( $(date +%s) - epoch ))
      if (( AGE > 86400 )); then
        git branch -D "$branch"
        echo "Deleted $branch"
      fi
    done
```

---

### Rollback Commands

```bash
# List all available snapshots
git -C ~/.claude branch --list 'shadow/*' --sort=-creatordate

# See what changed between a snapshot and now
git -C ~/.claude diff shadow/20260309_143022 HEAD

# Restore a specific file from a snapshot
git -C ~/.claude checkout shadow/20260309_143022 -- path/to/file.md

# Full rollback to a snapshot (resets working tree)
git -C ~/.claude reset --hard shadow/20260309_143022

# Delete a specific snapshot after you're done with it
git -C ~/.claude branch -D shadow/20260309_143022
```

---

## Task List

1. Create `/home/artsmc/.claude/hooks/` directory
2. Write `hooks/shadow-snapshot.sh` with the script above; `chmod +x` it
3. Write `hooks/shadow-cleanup.sh`; `chmod +x` it
4. Add the `PreToolUse` block to `settings.json`
5. Smoke-test: trigger a Write operation and verify `git branch --list 'shadow/*'` shows a new branch
6. Verify cleanup: manually create an old-dated test branch, run the cleanup script, confirm deletion
7. Verify exit-0 passthrough: confirm the hooked Write/Edit still executes normally after the snapshot
