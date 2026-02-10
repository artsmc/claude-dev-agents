# Spec-Plan Team Enhancement

## Overview

Add `--team` flag support to `/spec-plan` for parallel specification generation.

**Speedup:** 1.7x faster (19 min → 11 min)

---

## Integration Point

Add this section to `/home/artsmc/.claude/skills/spec-plan/SKILL.md` after the research phase:

---

## Step 5: Generate Specifications (Enhanced with Teams)

### Mode Detection

```bash
# Check args for --team flag
if args contains "--team":
    USE_TEAM_MODE=true
elif args contains "--sequential":
    USE_TEAM_MODE=false
else:
    # Auto-detect: Use teams if 4+ deliverables
    deliverable_count=4  # FRD, FRS, GS, TR
    if deliverable_count >= 4:
        USE_TEAM_MODE=true
    else:
        USE_TEAM_MODE=false
fi
```

### Option A: Team-Based Parallel Generation

**If USE_TEAM_MODE == true:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Parallel Spec Generation (Team Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating team: spec-generation
```

#### Step 5.1: Create Team

```typescript
TeamCreate({
  team_name: "spec-generation",
  description: "Parallel specification generation for {{feature_description}}",
  agent_type: "spec-writer"  // Team lead role
});
```

**Creates:**
- Team config: `~/.claude/teams/spec-generation/config.json`
- Task list: `~/.claude/tasks/spec-generation/`

#### Step 5.2: Create Task Entries

```typescript
// Task 1: Generate FRD
TaskCreate({
  subject: "Generate Functional Requirements Document (FRD)",
  description: `
Create FRD.md with:
- Feature overview
- User stories
- Business requirements
- Success criteria

Use research context from:
- Memory Bank: systemPatterns.md, activeContext.md
- Documentation Hub: systemArchitecture.md
- Codebase analysis results

Output: ./job-queue/feature-{name}/docs/FRD.md
`,
  activeForm: "Generating FRD"
});

// Task 2: Generate FRS + TR
TaskCreate({
  subject: "Generate FRS and Technical Requirements",
  description: `
Create FRS.md and TR.md with:

FRS.md:
- Detailed functional specifications
- Component breakdown
- API contracts
- Data models

TR.md:
- Technical requirements
- Architecture decisions
- Technology stack
- Performance requirements
- Security requirements

Output:
  - ./job-queue/feature-{name}/docs/FRS.md
  - ./job-queue/feature-{name}/docs/TR.md
`,
  activeForm: "Generating FRS and TR"
});

// Task 3: Generate Gherkin Scenarios
TaskCreate({
  subject: "Generate Gherkin Scenarios (GS)",
  description: `
Create GS.md with:
- Gherkin-formatted scenarios
- Given-When-Then structure
- Acceptance criteria
- Edge cases

Use FRD for feature context (will be available from Task 1)

Output: ./job-queue/feature-{name}/docs/GS.md
`,
  activeForm: "Generating Gherkin scenarios"
});

// Set dependency: GS depends on FRD
TaskUpdate({
  taskId: "3",
  addBlockedBy: ["1"]  // GS needs FRD context
});

// Task 4: Generate Task List
TaskCreate({
  subject: "Generate implementation task list",
  description: `
Create task-list.md with:
- Breakdown of implementation tasks
- Task dependencies
- Agent assignments
- Time estimates

Use all specs (FRD, FRS, TR, GS) for context

Output: ./job-queue/feature-{name}/docs/task-list.md
`,
  activeForm: "Generating task list"
});

// Set dependencies: task-list depends on all specs
TaskUpdate({
  taskId: "4",
  addBlockedBy: ["1", "2", "3"]
});
```

#### Step 5.3: Spawn Specialized Agents

```typescript
// Agent 1: FRD Writer (business analyst persona)
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "frd-writer",
  prompt: `
You are responsible for generating the Functional Requirements Document (FRD).

Context available:
- Memory Bank: {{read memory-bank files}}
- Documentation Hub: {{read docs}}
- Feature description: "{{feature_description}}"

1. Claim your task:
   TaskUpdate({ taskId: "1", owner: "frd-writer", status: "in_progress" })

2. Generate FRD.md focusing on:
   - Business value and user needs
   - High-level functionality
   - Success metrics

3. Save to: ./job-queue/feature-{name}/docs/FRD.md

4. Mark complete:
   TaskUpdate({ taskId: "1", status: "completed" })

5. Go idle (you're done)
`,
  description: "Generate FRD"
});

// Agent 2: FRS + TR Writer (technical architect persona)
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "frs-tr-writer",
  prompt: `
You are responsible for generating FRS and TR documents.

Context available:
- Memory Bank: {{read memory-bank files}}
- Documentation Hub: {{read docs}}
- Codebase patterns: {{analyze existing code}}

1. Claim your task:
   TaskUpdate({ taskId: "2", owner: "frs-tr-writer", status: "in_progress" })

2. Generate FRS.md (detailed functional specs)
3. Generate TR.md (technical requirements)

4. Save to:
   - ./job-queue/feature-{name}/docs/FRS.md
   - ./job-queue/feature-{name}/docs/TR.md

5. Mark complete:
   TaskUpdate({ taskId: "2", status: "completed" })

6. Go idle
`,
  description: "Generate FRS and TR"
});

// Agent 3: Scenario Writer (QA persona)
Task({
  subagent_type: "qa-engineer",
  team_name: "spec-generation",
  name: "scenario-writer",
  prompt: `
You are responsible for generating Gherkin scenarios (GS).

⚠️ IMPORTANT: Your task is blocked by Task 1 (FRD generation).

1. Wait for Task 1 to complete:
   TaskList()  // Check if Task 1 is completed

2. Once Task 1 complete, claim your task:
   TaskUpdate({ taskId: "3", owner: "scenario-writer", status: "in_progress" })

3. Read FRD for context:
   Read("./job-queue/feature-{name}/docs/FRD.md")

4. Generate GS.md with Gherkin scenarios

5. Save to: ./job-queue/feature-{name}/docs/GS.md

6. Mark complete:
   TaskUpdate({ taskId: "3", status: "completed" })

7. Go idle
`,
  description: "Generate Gherkin scenarios"
});

// Agent 4: Task List Writer (project manager persona)
Task({
  subagent_type: "spec-writer",
  team_name: "spec-generation",
  name: "task-writer",
  prompt: `
You are responsible for generating the implementation task list.

⚠️ IMPORTANT: Your task is blocked by Tasks 1, 2, 3 (all specs).

1. Wait for all specs to complete:
   TaskList()  // Check if Tasks 1, 2, 3 are completed

2. Once all complete, claim your task:
   TaskUpdate({ taskId: "4", owner: "task-writer", status: "in_progress" })

3. Read all specs for context:
   Read("./job-queue/feature-{name}/docs/FRD.md")
   Read("./job-queue/feature-{name}/docs/FRS.md")
   Read("./job-queue/feature-{name}/docs/TR.md")
   Read("./job-queue/feature-{name}/docs/GS.md")

4. Generate task-list.md with:
   - Implementation tasks
   - Dependencies
   - Agent assignments
   - Time estimates

5. Save to: ./job-queue/feature-{name}/docs/task-list.md

6. Mark complete:
   TaskUpdate({ taskId: "4", status: "completed" })

7. Go idle
`,
  description: "Generate task list"
});
```

#### Step 5.4: Monitor Wave Execution

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave 1 (Parallel - 2 agents)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[frd-writer] Generating FRD.md...
[frs-tr-writer] Generating FRS.md and TR.md...

[frd-writer] FRD complete! (4 min)
[frs-tr-writer] FRS and TR complete! (4 min)

✅ Wave 1 complete in 4 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave 2 (Sequential - 1 agent, waits for FRD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[scenario-writer] Checking dependencies...
  ✓ Task 1 (FRD): completed
[scenario-writer] Generating GS.md...
[scenario-writer] GS complete! (2 min)

✅ Wave 2 complete in 2 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave 3 (Sequential - 1 agent, waits for all specs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[task-writer] Checking dependencies...
  ✓ Task 1 (FRD): completed
  ✓ Task 2 (FRS, TR): completed
  ✓ Task 3 (GS): completed
[task-writer] Generating task-list.md...
[task-writer] Task list complete! (2 min)

✅ Wave 3 complete in 2 minutes
```

#### Step 5.5: Validate All Deliverables

```typescript
// Check all files exist
const requiredFiles = [
  "./job-queue/feature-{name}/docs/FRD.md",
  "./job-queue/feature-{name}/docs/FRS.md",
  "./job-queue/feature-{name}/docs/TR.md",
  "./job-queue/feature-{name}/docs/GS.md",
  "./job-queue/feature-{name}/docs/task-list.md"
];

for (const file of requiredFiles) {
  if (!Read(file)) {
    throw new Error(`Missing deliverable: ${file}`);
  }
}

console.log("✅ All deliverables present");
```

#### Step 5.6: Cross-Reference Validation

```typescript
// Validate spec consistency
const frd = Read("./job-queue/feature-{name}/docs/FRD.md");
const frs = Read("./job-queue/feature-{name}/docs/FRS.md");
const gs = Read("./job-queue/feature-{name}/docs/GS.md");
const tr = Read("./job-queue/feature-{name}/docs/TR.md");

// Check that FRS references match FRD
// Check that GS scenarios cover FRD requirements
// Check that TR covers FRS technical needs

console.log("✅ Cross-reference validation passed");
```

#### Step 5.7: Shut Down Team

```typescript
// Request shutdown for all agents
const teammates = ["frd-writer", "frs-tr-writer", "scenario-writer", "task-writer"];

for (const teammate of teammates) {
  SendMessage({
    type: "shutdown_request",
    recipient: teammate,
    content: "Spec generation complete, shutting down"
  });
}

// Wait for confirmations...

// Clean up team
TeamDelete();

console.log("✅ Team shutdown complete");
```

#### Step 5.8: Display Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Parallel Spec Generation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Duration: 11 minutes
Sequential estimate: 19 minutes
Speedup: 1.7x (42% faster)

Deliverables:
  ✓ FRD.md (Functional Requirements)
  ✓ FRS.md (Functional Specification)
  ✓ TR.md (Technical Requirements)
  ✓ GS.md (Gherkin Scenarios)
  ✓ task-list.md (Implementation Tasks)

Wave Breakdown:
  Wave 1: 4 min (2 agents: FRD, FRS+TR)
  Wave 2: 2 min (1 agent: GS, waited for FRD)
  Wave 3: 2 min (1 agent: task-list, waited for all)
  Setup/Teardown: 3 min

Agent Utilization:
  frd-writer: 4 min (Wave 1)
  frs-tr-writer: 4 min (Wave 1)
  scenario-writer: 2 min (Wave 2)
  task-writer: 2 min (Wave 3)

Validation:
  ✓ All files present
  ✓ Cross-references validated
  ✓ Task list has 7 tasks

Next step: /spec-review
```

---

### Option B: Sequential Generation

**If USE_TEAM_MODE == false:**

```
[Use existing sequential spec generation logic]
```

---

## Implementation Notes

### Dependency Management

**Wave structure:**
```
Wave 1 (parallel):     FRD, FRS+TR
Wave 2 (after Wave 1): GS (needs FRD context)
Wave 3 (after Wave 2): task-list (needs all specs)
```

**Why these dependencies:**
- FRD and FRS+TR are independent (can run in parallel)
- GS needs FRD to understand feature scope
- task-list needs all specs to break down implementation

### Error Handling

```
❌ Spec generation failed: frd-writer did not complete

Recovery:
  1. Check frd-writer output for errors
  2. Spawn replacement agent:
     Task({
       subagent_type: "spec-writer",
       team_name: "spec-generation",
       name: "frd-writer-2",
       prompt: "Generate FRD.md (retry after failure)"
     })
  3. Or fallback to sequential mode:
     /spec-plan "{{feature_description}}" --sequential
```

### Token Usage

**Sequential mode:**
- ~50k tokens (single agent, 19 min)

**Team mode:**
- ~120k tokens (4 agents, 11 min)
- 2.4x more tokens
- 1.7x faster execution

**When to use team mode:**
- ✅ Complex features requiring detailed specs
- ✅ Time is more valuable than tokens
- ❌ Simple features (< 5 tasks)
- ❌ Routine spec updates

---

## Testing

### Test Case 1: Simple Feature (Auto-Detect → Sequential)

```bash
/spec-plan "add logout button"

Expected:
  - Auto-detect: 1-2 tasks estimated
  - Mode: Sequential
  - Duration: ~8 minutes
  - Deliverables: All 5 files
```

### Test Case 2: Complex Feature (Auto-Detect → Team)

```bash
/spec-plan "add user authentication with OAuth, JWT, and MFA"

Expected:
  - Auto-detect: 10+ tasks estimated
  - Mode: Team (parallel)
  - Duration: ~11 minutes
  - Deliverables: All 5 files
  - Speedup: 1.7x vs sequential
```

### Test Case 3: Force Team Mode

```bash
/spec-plan "add profile page" --team

Expected:
  - Mode: Team (forced)
  - Duration: ~11 minutes
  - Even if feature is simple
```

### Test Case 4: Force Sequential Mode

```bash
/spec-plan "migrate to Next.js 16" --sequential

Expected:
  - Mode: Sequential (forced)
  - Duration: ~19 minutes
  - Even if feature is complex
```

---

## Migration Path

### Phase 1: Add Team Support (Week 1)
1. Add team mode detection to SKILL.md
2. Implement parallel generation logic
3. Test with simple features

### Phase 2: Refine Dependencies (Week 2)
1. Optimize wave structure
2. Test with complex features
3. Measure real speedups

### Phase 3: Make Default (Week 3)
1. Set auto-detect as default
2. Use team mode for 4+ deliverables
3. Document in README
