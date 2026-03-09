#!/usr/bin/env bash
# health-check.sh - Validates Claude Dev Agents foundation
# Exit non-zero on any failure

set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
DB_PATH="$CLAUDE_DIR/projects.db"
PASS=0
FAIL=0

check() {
    local name="$1"
    local result="$2"
    if [ "$result" = "0" ]; then
        echo "  [PASS] $name"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Claude Dev Agents Health Check ==="
echo ""

# 1. projects.db exists and is non-empty
echo "Database:"
if [ -f "$DB_PATH" ] && [ -s "$DB_PATH" ]; then
    check "projects.db exists and is non-empty" 0
else
    check "projects.db exists and is non-empty" 1
fi

# 2. Required tables present
REQUIRED_TABLES="projects phases tasks phase_runs"
TABLE_LIST=$(sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table'" 2>/dev/null || echo "")
ALL_TABLES_OK=0
for table in $REQUIRED_TABLES; do
    if ! echo "$TABLE_LIST" | grep -qx "$table"; then
        ALL_TABLES_OK=1
        echo "    Missing table: $table"
    fi
done
check "Required tables present (projects, phases, tasks, phase_runs)" $ALL_TABLES_OK

# 3. No phantom pm.db
if [ ! -f "$CLAUDE_DIR/pm.db" ]; then
    check "No phantom pm.db file" 0
else
    check "No phantom pm.db file" 1
fi

# 4. Python3 available and can import ProjectDatabase
echo ""
echo "Python:"
if python3 -c "import sys; sys.path.insert(0, '$CLAUDE_DIR/lib'); from project_database import ProjectDatabase; db = ProjectDatabase(); db.close()" 2>/dev/null; then
    check "Python3 can import ProjectDatabase" 0
else
    check "Python3 can import ProjectDatabase" 1
fi

# 5. Sound files for settings.json hooks
echo ""
echo "Hooks:"
if [ -f "$CLAUDE_DIR/sounds/done.wav" ]; then
    check "sounds/done.wav exists (Stop hook)" 0
else
    check "sounds/done.wav exists (Stop hook)" 1
fi

# 6. All pm-db hook scripts are executable
HOOKS_DIR="$CLAUDE_DIR/hooks/pm-db"
HOOKS_OK=0
for hook in "$HOOKS_DIR"/on-*.py; do
    if [ ! -x "$hook" ]; then
        HOOKS_OK=1
        echo "    Not executable: $(basename "$hook")"
    fi
done
check "All pm-db hook scripts are executable" $HOOKS_OK

# 7. Memory Bank directory exists
echo ""
echo "Memory Bank:"
if [ -d "$CLAUDE_DIR/memory-bank" ]; then
    check "memory-bank/ directory exists" 0
else
    check "memory-bank/ directory exists" 1
fi

# Count Memory Bank files
MB_FILES=$(ls "$CLAUDE_DIR/memory-bank/"*.md 2>/dev/null | wc -l)
if [ "$MB_FILES" -ge 4 ]; then
    check "Memory Bank has >= 4 markdown files ($MB_FILES found)" 0
else
    check "Memory Bank has >= 4 markdown files ($MB_FILES found)" 1
fi

# Summary
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
