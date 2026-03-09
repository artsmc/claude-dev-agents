# Spec-Plan Team Enhancement

## Overview

Team mode for **full-tier specs only**. Parallelizes generation of 5 deliverables across specialized agents.

**Availability:** Full tier only (`--tier full --team` or auto-triggered for very complex features)
**Speedup:** ~1.7x faster (15 min → 9 min)
**Token cost:** ~1.5x more tokens than single-agent full tier

---

## When Team Mode Activates

Team mode is used when ALL of these are true:
1. Tier is `full` (5 deliverables)
2. Either `--team` flag is set, OR auto-detected as very complex (3+ apps, 20+ estimated tasks)

**Team mode is NEVER used for quick or standard tiers.** Those tiers generate 1-3 files — parallelization adds overhead without meaningful speedup.

---

## Wave Structure

```
Wave 1 (parallel):     FRD, FRS+TR       ← 2 agents, independent
Wave 2 (after Wave 1): GS                ← needs FRD for scope
Wave 3 (after all):    task-list          ← needs all specs for breakdown
```

### Why These Dependencies

- FRD and FRS+TR are independent (business vs technical perspective)
- GS needs FRD to understand feature scope and write scenarios
- task-list needs all specs to create accurate implementation breakdown

---

## Team Setup

### Step 1: Create Team

```typescript
TeamCreate({
  team_name: "spec-generation",
  description: "Parallel spec generation for {{feature.name}}"
});
```

### Step 2: Create Tasks with Dependencies

```typescript
// Task 1: FRD (no dependencies)
TaskCreate({
  subject: "Generate FRD.md",
  description: "Feature Requirements Document from structured brief",
  activeForm: "Generating FRD"
});

// Task 2: FRS + TR (no dependencies)
TaskCreate({
  subject: "Generate FRS.md and TR.md",
  description: "Functional spec + Technical requirements from structured brief",
  activeForm: "Generating FRS and TR"
});

// Task 3: GS (blocked by Task 1)
TaskCreate({
  subject: "Generate GS.md",
  description: "Gherkin scenarios covering FRD requirements",
  activeForm: "Generating Gherkin scenarios"
});
TaskUpdate({ taskId: "3", addBlockedBy: ["1"] });

// Task 4: task-list (blocked by all)
TaskCreate({
  subject: "Generate task-list.md",
  description: "Implementation tasks derived from all specs",
  activeForm: "Generating task list"
});
TaskUpdate({ taskId: "4", addBlockedBy: ["1", "2", "3"] });
```

### Step 3: Spawn Agents

All agents receive the **same structured brief** from Phase 5 of SKILL.md.

```typescript
// Agent 1: FRD Writer
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "frd-writer",
  prompt: `
You are generating FRD.md for: {{feature.name}}

STRUCTURED BRIEF:
{{brief_json}}

1. Claim task: TaskUpdate({ taskId: "1", owner: "frd-writer", status: "in_progress" })
2. Generate FRD.md (feature requirements, user stories, acceptance criteria, edge cases)
3. Write to: {{output_path}}/FRD.md
4. Mark complete: TaskUpdate({ taskId: "1", status: "completed" })
`,
  description: "Generate FRD"
});

// Agent 2: FRS + TR Writer
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "frs-tr-writer",
  prompt: `
You are generating FRS.md and TR.md for: {{feature.name}}

STRUCTURED BRIEF:
{{brief_json}}

1. Claim task: TaskUpdate({ taskId: "2", owner: "frs-tr-writer", status: "in_progress" })
2. Generate FRS.md (detailed functional requirements, component breakdown)
3. Generate TR.md (API contracts, data models, architecture decisions)
4. Write to: {{output_path}}/FRS.md and {{output_path}}/TR.md
5. Mark complete: TaskUpdate({ taskId: "2", status: "completed" })
`,
  description: "Generate FRS and TR"
});

// Agent 3: Scenario Writer (waits for FRD)
Task({
  subagent_type: "qa-engineer",
  team_name: "spec-generation",
  name: "scenario-writer",
  prompt: `
You are generating GS.md for: {{feature.name}}

STRUCTURED BRIEF:
{{brief_json}}

Your task is BLOCKED by Task 1 (FRD). Wait for it.

1. Check TaskList() — proceed only when Task 1 is completed
2. Read {{output_path}}/FRD.md for feature scope
3. Claim task: TaskUpdate({ taskId: "3", owner: "scenario-writer", status: "in_progress" })
4. Generate GS.md (Gherkin scenarios covering all FRD requirements)
5. Write to: {{output_path}}/GS.md
6. Mark complete: TaskUpdate({ taskId: "3", status: "completed" })
`,
  description: "Generate Gherkin scenarios"
});

// Agent 4: Task List Writer (waits for all)
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "task-writer",
  prompt: `
You are generating task-list.md for: {{feature.name}}

STRUCTURED BRIEF:
{{brief_json}}

Your task is BLOCKED by Tasks 1, 2, 3. Wait for all.

1. Check TaskList() — proceed only when Tasks 1, 2, 3 are all completed
2. Read all specs from {{output_path}}/
3. Claim task: TaskUpdate({ taskId: "4", owner: "task-writer", status: "in_progress" })
4. Generate task-list.md (phased tasks, dependencies, agent assignments, complexity estimates)
5. Write to: {{output_path}}/task-list.md
6. Mark complete: TaskUpdate({ taskId: "4", status: "completed" })
`,
  description: "Generate task list"
});
```

### Step 4: Validate and Shut Down

After all tasks complete:

```typescript
// Validate deliverables
Bash("python /home/artsmc/.claude/skills/spec-plan/scripts/validate_spec.py {{feature_path}} --tier full");

// Shut down agents
for (const name of ["frd-writer", "frs-tr-writer", "scenario-writer", "task-writer"]) {
  SendMessage({ type: "shutdown_request", recipient: name, content: "Done" });
}

TeamDelete();
```

---

## Error Recovery

If an agent fails:

```
1. Check agent output for error details
2. Spawn a replacement agent for the failed task only
3. Or fallback: re-run /spec-plan without --team flag (sequential)
```

---

## Token and Time Estimates

| Mode | Files | Time | Tokens | When |
|------|-------|------|--------|------|
| Full (single) | 5 | 8-15 min | ~80K | Default for full tier |
| Full (team) | 5 | 5-10 min | ~120K | `--team` flag or auto for very complex |

**Use team mode when** time matters more than tokens and the feature is genuinely complex (3+ apps, security-sensitive, 20+ estimated tasks).
