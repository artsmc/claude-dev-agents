# Fix 1: Foundation (PM-DB, Hooks, Health Check)

## Problem (what's broken, with evidence)

### PM-DB: Wrong file, zero tables

`pm.db` exists at `~/.claude/pm.db` and is **0 bytes** (created 2026-01-31, empty):
```
-rw-r--r-- 1 artsmc artsmc 0 Jan 31 14:39 /home/artsmc/.claude/pm.db
```

The actual working database is `~/.claude/projects.db` (1.7MB, 25 tables including
`projects`, `phases`, `tasks`, `phase_runs`, `cached_files`, etc.).

`lib/project_database.py` line 79 defaults to `~/.claude/projects.db` — correct.
The pm-db hooks in `hooks/pm-db/` import from `lib/project_database.py` — correct.

**Root cause:** `pm.db` is a phantom file. Nothing creates it, nothing uses it.
Every skill or doc that references `pm.db` is pointing at the wrong path.

### Hooks: Wired, but only sound effects fire

`settings.json` defines two hooks:
- `Stop` → plays `done.wav`
- `Notification` → plays `loop.wav`

The 10+ Python hooks in `hooks/pm-db/` (on-job-start, on-task-complete, etc.) are
**NOT registered in any settings file**. They exist as callable scripts but no
Claude Code event triggers them. They rely on skills explicitly calling them via
`echo '...' | python3 ~/.claude/hooks/pm-db/on-task-complete.py`.

**Root cause:** The hooks are manual utilities, not event-driven. The Claude Code
hook system only fires registered commands. The pm-db hooks are undiscoverable unless
a skill explicitly invokes them by path.

### Health Check: Nonexistent

No script validates that the foundation is intact before use. When `projects.db`
is missing, hooks silently return `{"error": "...", "status": "failed"}` and
`sys.exit(0)` — zero noise, zero indication anything is wrong.

---

## Solution

### PM-DB Initialization

The database at `~/.claude/projects.db` already has all 25 required tables. No schema
work needed. The only fix is to:

1. Delete the phantom `pm.db` (or note it as safe to ignore)
2. Audit all documentation and skill files that reference `pm.db` and correct the path

The `ProjectDatabase` class already handles `projects.db` initialization correctly
via `sqlite3.connect()` — it creates the file if missing, but the schema tables must
exist. Current `projects.db` has all tables populated by prior migrations.

### Hook Validation

The pm-db Python hooks are functional utilities but not auto-triggered. Two options:

**Option A (chosen):** Document that pm-db hooks are invoked explicitly by skills, not
by Claude Code's hook system. Add a `README.md` in `hooks/pm-db/` making this clear.

**Option B (future):** Register `PreToolUse` or `PostToolUse` hooks in `settings.json`
pointing to a lightweight dispatcher script. This requires designing the event contract.

For this fix, Option A is correct. The hooks work when called. The problem is
discoverability and lack of documentation about how they are supposed to be called.

### Health Check Script

Create `~/.claude/scripts/health-check.sh` — a zero-dependency bash script that
validates the foundation and prints pass/fail per component.

Checks:
1. `projects.db` exists and is non-empty
2. Required tables present (projects, phases, tasks, phase_runs)
3. Python3 available and can import `lib/project_database.py`
4. `sounds/done.wav` exists (Stop hook dependency)
5. All pm-db hook scripts are executable

Output: clear pass/fail per check, non-zero exit on any failure.

---

## Task List

1. **Delete phantom pm.db**
   - Run: `rm /home/artsmc/.claude/pm.db`
   - Verify: `ls /home/artsmc/.claude/pm.db` returns "No such file"

2. **Audit references to pm.db in documentation and skills**
   - Search: `grep -r "pm\.db" /home/artsmc/.claude/skills /home/artsmc/.claude/memory-bank`
   - Fix: Replace any `pm.db` references with `projects.db`
   - Verify: Zero grep hits for `pm.db` in skills and memory-bank dirs

3. **Verify projects.db is intact**
   - Run: `sqlite3 ~/.claude/projects.db "SELECT name FROM sqlite_master WHERE type='table'" | wc -l`
   - Verify: Returns 25 (or >= 20 accounting for future migrations)
   - Run: `python3 -c "import sys; sys.path.insert(0, '/home/artsmc/.claude/lib'); from project_database import ProjectDatabase; db = ProjectDatabase(); print('OK')"`
   - Verify: Prints "OK" with no errors

4. **Create hooks/pm-db/README.md**
   - Document that these hooks are explicit-call utilities, not Claude Code event hooks
   - Include usage pattern: `echo '{"job_name": "..."}' | python3 ~/.claude/hooks/pm-db/on-job-start.py`
   - List all 10 hook scripts with their input/output JSON contracts
   - Verify: File created, readable, accurate

5. **Create scripts/health-check.sh**
   - Create `~/.claude/scripts/` directory if absent
   - Write script with checks listed in Solution section above
   - Make executable: `chmod +x ~/.claude/scripts/health-check.sh`
   - Run: `~/.claude/scripts/health-check.sh`
   - Verify: All checks pass, exit code 0

6. **Register health check in memory-bank/systemPatterns.md**
   - Add entry noting `scripts/health-check.sh` as the validation entry point
   - Document correct DB path (`projects.db`, not `pm.db`)
   - Verify: systemPatterns.md updated with accurate paths
