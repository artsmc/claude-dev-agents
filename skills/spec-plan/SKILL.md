---
name: spec-plan
description: Pre-planning and research for feature specs with scope-aware tiered output (quick task-list, standard FRD+TR, full FRD/FRS/Gherkin/TR). Use to spec out a feature, prep requirements/FRD, do pre-planning research, or 'plan before we build'. To critique an existing spec, use spec-review.
args:
  feature_description:
    type: string
    description: Brief description of the feature to plan (e.g., "build an auth feature")
    required: false
  tier:
    type: string
    description: Force a specific tier (quick, standard, full). Auto-detected if omitted.
    required: false
  team:
    type: boolean
    description: Force team mode for parallel generation (only applies to full tier)
    required: false
---

# Spec Plan v2: Scope-Aware Planning & Research

Research, triage scope, and generate **right-sized** specifications.

## Usage

```bash
# Auto-detect scope tier
/spec-plan build a user authentication feature

# Force a specific tier
/spec-plan add logout button --tier quick
/spec-plan add OAuth2 support --tier standard
/spec-plan build SSO with MFA --tier full

# Force team mode (full tier only)
/spec-plan build SSO with MFA --tier full --team

# Interactive mode
/spec-plan
```

## Core Principle

> **Match spec depth to requirement depth.**
> A logout button does not need an FRD. An SSO system does.

The skill auto-detects the right amount of documentation and confirms
with the user before generating anything.

---

## Workflow

```
Phase 0: Feature Description
Phase 1: Clarify Requirements (lightweight)
Phase 2: Triage Gate         ← NEW: classify scope
Phase 3: Scope Confirmation  ← NEW: user approves plan
Phase 4: Budgeted Research   ← NEW: context caps
Phase 5: Launch Agent        ← Structured brief, tier-specific
```

---

## Phase 0: Feature Description

**If argument provided:** Use as starting point, skip to Phase 1 with context.

**If no argument:** Ask: "What feature would you like to plan specifications for?"

---

## Phase 1: Clarify Requirements (Lightweight)

Ask **only what's needed to triage** — not the full requirement set. Save deep
clarification for after triage confirms the tier warrants it.

**Always ask (2-3 questions max):**

1. What problem does this solve for users? (one sentence)
2. Which apps are affected? (API / Web / Mastra / Microsandbox)
3. Any hard constraints? (security, performance, compliance)

**Do NOT ask at this stage:**
- Detailed acceptance criteria (that's for the spec-writer)
- Full tech stack inventory (infer from affected apps)
- Exhaustive integration requirements (research phase handles this)

---

## Phase 2: Triage Gate

Classify the feature into one of three tiers based on Phase 1 answers.

### Tier Classification Criteria

```
QUICK-SPEC (task-list only)
  Signal ANY of:
  - Single app affected
  - Single concern (UI-only, config-only, single endpoint)
  - Estimated < 5 implementation tasks
  - Well-understood pattern (CRUD, form, button, page)
  - User said "simple" or "quick" or "small"
  Examples: add logout button, new dashboard widget, add field to form,
            update validation rule, add API endpoint for existing model

STANDARD-SPEC (FRD + TR + task-list)
  Signal ANY of:
  - 2 apps affected
  - Moderate complexity (new data model, new API contract, new page)
  - Estimated 5-15 implementation tasks
  - Known patterns but meaningful scope
  - Requires API design or schema changes
  Examples: add user profile management, build notification system,
            add file upload feature, implement search functionality

FULL-SPEC (FRD + FRS + GS + TR + task-list)
  Signal ANY of:
  - 3+ apps affected
  - New architectural pattern or system
  - Security-sensitive (auth, RBAC, encryption, PII)
  - Estimated 15+ implementation tasks
  - Unknown patterns or significant research needed
  - Compliance implications (FedRAMP, NIST, Section 508)
  Examples: SSO with MFA, workflow execution engine, real-time
            collaboration, multi-tenant data isolation
```

### Override Rules

- `--tier quick|standard|full` overrides auto-detection
- If user disagrees with triage in Phase 3, adjust tier
- When uncertain between two tiers, pick the **lower** one
  (user can always escalate; over-production is harder to undo)

---

## Phase 3: Scope Confirmation

**MANDATORY.** Present the triage result and get user buy-in before any generation.

### Confirmation Template

```
Based on your description, I've scoped this as a **[TIER]** spec:

Feature: [one-line summary]
Affected apps: [list]
Estimated complexity: [low / moderate / high]

I'll generate:
  [x] task-list.md — Implementation tasks with dependencies
  [x if standard+] FRD.md — Feature requirements and success criteria
  [x if standard+] TR.md — Technical requirements and API contracts
  [x if full] FRS.md — Detailed functional specification
  [x if full] GS.md — Gherkin test scenarios

Research scope:
  [x] Memory Bank — Check existing patterns and active work
  [x if standard+] Documentation — Fetch latest framework patterns
  [x if full] Deep research — Case studies, pitfalls, architecture review

Estimated generation time: [1-3 min | 3-7 min | 8-15 min]
Estimated tokens: [~15K | ~35K | ~80K]

Does this scope look right, or should I adjust?
```

**If user says "more"** → bump tier up.
**If user says "less"** → bump tier down.
**If user says "looks good"** → proceed to Phase 4.

---

## Phase 4: Budgeted Research

Research depth scales with tier. Each section has a **context budget** —
max information to gather before moving on. This prevents context bloat.

### Per-Tier Budgets

Total budgets: quick ~2K tokens (Memory Bank + codebase scan), standard ~5K
(+ documentation), full ~10K (+ deep codebase analysis + external research).
The per-section budget breakdowns for each tier are in
`references/tier-prompts.md` — read the section for the confirmed tier
before starting research.

### Budget Enforcement

When a research section approaches its budget:
1. Summarize what you've found so far
2. Move to the next section
3. Do NOT keep searching for more context

**Rationale:** More context is not always better context. Focused,
relevant findings produce better specs than exhaustive dumps.

---

## Phase 5: Launch Agent with Structured Brief

### Brief Format

Replace the narrative prompt blob with a **structured brief**.
This gives the spec-writer explicit, parseable context.

```json
{
  "feature": {
    "name": "[feature name]",
    "description": "[one-line from user]",
    "problem_statement": "[what problem this solves]",
    "affected_apps": ["api", "web"],
    "complexity": "moderate",
    "tier": "standard"
  },
  "deliverables": [
    "FRD.md",
    "TR.md",
    "task-list.md"
  ],
  "constraints": {
    "security": "[any security requirements]",
    "performance": "[any performance requirements]",
    "compliance": "[any compliance requirements]",
    "deadline": "[if mentioned]"
  },
  "research_findings": {
    "existing_patterns": "[summarized from Memory Bank]",
    "reusable_components": "[list from codebase scan]",
    "framework_patterns": "[from documentation research]",
    "integration_points": "[from codebase analysis]",
    "pitfalls_to_avoid": "[from research]"
  },
  "output_path": "/job-queue/feature-{name}/docs/"
}
```

### Tier-Specific Agent Prompts

The verbatim spec-writer prompt templates for each tier (quick → task-list
only; standard → FRD + TR + task-list; full → all 5 files) are in
`references/tier-prompts.md` — read the template matching the confirmed
tier before launching the agent, and use it as-is.

**Team mode (with --team flag or auto for very complex features):**

See TEAM-ENHANCEMENT.md for parallel generation workflow.
Team mode is ONLY available for full tier.

---

## Tier Output Summary

| Tier | Files Generated | Estimated Time | Estimated Tokens | When to Use |
|------|----------------|----------------|------------------|-------------|
| **Quick** | task-list.md | 1-3 min | ~15K | Single concern, <5 tasks, known pattern |
| **Standard** | FRD + TR + task-list | 3-7 min | ~35K | Moderate scope, 5-15 tasks, API/schema changes |
| **Full** | FRD + FRS + GS + TR + task-list | 8-15 min | ~80K | Multi-app, security, 15+ tasks, new architecture |
| **Full + Team** | Same as Full (parallel) | 5-10 min | ~120K | Same as Full but time-sensitive |

---

## Expected Outcomes

After this skill completes:

1. Feature scoped to the right tier (not over-produced)
2. Research focused and budget-constrained
3. User confirmed scope before generation
4. Spec-writer launched with structured brief
5. Right-sized deliverables generated

## Next Step

Once spec-writer agent completes, use `/spec-review` to validate and critique.

The review skill is tier-aware — it validates against the expected deliverables
for the tier, not against the full 5-file set.

## Tools Used

- **AskUserQuestion** — Triage confirmation (Phase 3)
- **Memory Bank** — Existing work check
- **MCP Tools** — Documentation fetching (standard+ tiers)
- **WebSearch/WebFetch** — General research (full tier)
- **Grep/Glob** — Codebase analysis
- **Task Tool** — Spec-writer agent launch

## Design Decisions

**Why triage before research?**
Research is expensive (tokens + time). Triage determines how much research
is needed. A quick-spec needs a codebase grep, not a full documentation fetch.

**Why confirm scope with user?**
The research writeup showed that the biggest waste was generating specs for
problems that didn't need them. A 5-second confirmation prevents 10 minutes
of unnecessary generation.

**Why structured briefs over narrative prompts?**
Agents parse structured data more reliably than narrative blobs. The JSON
brief makes it explicit what the agent has to work with and what it needs
to produce.

**Why budget context?**
More context is not better context. The research showed that unbounded context
gathering leads to "context bloat" — the agent receives so much information
that it loses focus on what matters. Caps force prioritization.

**Why default to lower tier when uncertain?**
Over-production is harder to undo than under-production. If a quick-spec
turns out to be insufficient, the user can re-run at standard. But if a
full-spec was generated for a simple feature, those 80K tokens are wasted.

---

**Version:** 2.0
**Estimated skill tokens:** ~1,200 (focused on triage + structured workflow)
