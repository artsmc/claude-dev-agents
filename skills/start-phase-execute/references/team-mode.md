# Team Mode — Full Procedure

Full procedure for `--team` execution (formerly the `/start-phase-execute-team` skill).
Multi-agent teams execute waves of tasks in parallel.

**Speedup:** 1.5-2x faster depending on task parallelism

> **Reference:** All TypeScript pseudocode (wave creation, TeamCreate/TaskCreate calls, the full agent spawn-prompt template, polling and shutdown loops), the complete 7-task worked example with display formats, and full error-recovery playbooks live in `references/team-mode-examples.md`. Read it before executing Part 3, and whenever you need the exact spawn prompt or a display/output format.

---

## Mode Detection

**Step 0: Determine Execution Mode**

```bash
# Check args for --team flag
if args contains "--team":
    USE_TEAM_MODE=true
    echo "⚡ Team mode: ENABLED (forced)"
elif args contains "--sequential":
    USE_TEAM_MODE=false
    echo "📝 Team mode: DISABLED (sequential)"
else:
    # Auto-detect based on task count and dependencies
    task_count=$(grep -c "^## Task" "$task_list_file")

    if [ $task_count -ge 7 ]; then
        USE_TEAM_MODE=true
        echo "⚡ Team mode: ENABLED (auto-detected $task_count tasks)"
    else:
        USE_TEAM_MODE=false
        echo "📝 Team mode: DISABLED ($task_count tasks, threshold is 7)"
    fi
fi
```

---

## Part 1: Create Directories

[Same as Phase 1 in the main SKILL.md]

## Part 2: Generate Planning Docs

[Same as Phase 2 in the main SKILL.md]

---

## Part 3: Execute Tasks (Team-Enhanced)

Full pseudocode and worked example for every step below: `references/team-mode-examples.md`.

- **3.0 Parse task list** — Read `$task_list_file`; for each `## Task N:` section extract: id, subject, agent_type, depends_on (from "Depends on:" / "Blocked by:"), estimated_time.
- **3.1 Create waves** (if USE_TEAM_MODE) — Repeatedly collect all tasks whose dependencies are already completed into the next wave; an empty wave means a circular dependency (abort with error). Display the wave analysis: per-wave tasks and timing, sequential vs parallel estimate, speedup factor.
- **3.2 Create team** — `TeamCreate({ team_name: "phase-execution", description, agent_type: "general-purpose" })`; creates `~/.claude/teams/phase-execution/config.json` and `~/.claude/tasks/phase-execution/`.
- **3.3 Create task entries** — `TaskCreate` per task; description embeds the claim → execute → quality gates → self-review → commit → mark-complete loop, metadata carries agent_type/wave/estimated_time. Wire dependencies with `TaskUpdate({ addBlockedBy })`.
- **3.4 Execute waves** — Per wave, spawn one `Task` agent per task (`subagent_type` from the task, `team_name: "phase-execution"`, `model: "sonnet"` — Haiku is too weak). Use the full spawn-prompt template from the reference file; it makes each agent: claim its task, read requirements, verify blockers complete (recheck every 30s), execute following project patterns (Memory Bank, Documentation Hub), pass quality gates (lint/build/tests — HARD BLOCKS, fix before committing), self-review, git commit co-authored by the agent, mark complete, then claim the next unblocked task or go idle. Team lead polls `TaskList` every 10s until all wave tasks are `completed`; any `failed` task aborts the wave with an error.
- **3.5 Verify all complete** — `TaskList`; if any task is not `completed`, list id/subject/status/owner and abort.
- **3.6 Shut down team** — Read the team config's members, `SendMessage` a `shutdown_request` to each, wait ~5s for confirmations, then `TeamDelete`.

---

## Part 4: Task Updates & Commits

In team mode, each agent handles its own task updates and git commit during Step 3.4. Display a git-history summary of the agent commits (format in reference file).

## Part 5: Phase Closeout

Display the closeout summary: tasks completed, duration, quality gates passed, commits, per-wave breakdown, speedup analysis, agent utilization, peer communication, quality summary, and next steps (`/pm-db dashboard`, memory bank quick save, phase-summary.md). Full example in reference file.

---

## Fallback: Sequential Execution

**If USE_TEAM_MODE == false:** execute tasks one at a time with direct `Task` calls (no team), running quality gates and committing after each task — the standard start-phase-execute logic (Phases 3-4 in the main SKILL.md).

---

## Error Handling

Full recovery playbooks with example displays: `references/team-mode-examples.md`.

- **Team creation fails** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` not enabled: add it to `settings.json` env, retry with `--team`, or fall back to `--sequential`.
- **Agent spawn fails** — check `which tmux`; reduce parallelism (sequential mode) or spawn a replacement agent manually.
- **Task deadlock** — a blocking task stuck `in_progress` too long: `SendMessage` the owning agent, mark the task complete manually if the work is done, or spawn a replacement.
- **Quality gate fails** — automatic recovery: the agent fixes the issues, re-runs the gates, retries the commit. No manual intervention needed.

---

## Best Practices

1. **Context** — teammates don't inherit conversation history; put task details, file locations, API contracts in the spawn prompt.
2. **Task size** — self-contained units (function, test file, component); too small wastes coordination, too large risks wasted effort.
3. **File conflicts** — each teammate owns different files; concurrent edits to one file can overwrite.
4. **Monitor and steer** — check progress, redirect failing approaches, synthesize findings.
5. **Gate with hooks** — `TeammateIdle` exit 2 sends feedback; `TaskCompleted` exit 2 prevents completion.

---

## Token Usage & When to Use Team Mode

Team mode (7 tasks, 7 agents): ~450k tokens / 84 min vs sequential ~150k tokens / 127 min — 3x tokens for 1.5x speed.

- ✅ Complex features (2+ hours sequential), multiple independent modules, time more valuable than cost
- ❌ Simple changes (< 1 hour sequential), routine maintenance, single-file modifications

---

## Usage Examples

```bash
/start-phase-execute ./job-queue/feature-auth/task-list.md               # auto-detect: team mode at >= 7 tasks
/start-phase-execute ./job-queue/feature-profile/task-list.md --team     # force team mode even if < 7 tasks
/start-phase-execute ./job-queue/feature-logout/task-list.md --sequential # force sequential even if 7+ tasks
```

---

## Integration with Hooks

`on-phase-run-start` (phase_run_id → spawn prompts), `on-task-run-start`/`-complete` (task_run_id, duration, exit code → PM-DB), `TeammateIdle` (exit 2 = feedback to idle agent), `TaskCompleted` (exit 2 = reject completion). Details in reference file.
