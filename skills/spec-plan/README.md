# /spec-plan

> Pre-planning and research for feature specs with scope-aware tiered output (quick task-list, standard FRD+TR, full FRD/FRS/Gherkin/TR). Use to spec out a feature, prep requirements/FRD, do pre-planning research, or "plan before we build." To critique an existing spec, use spec-review.

## What it does

Scope-aware feature specification system: it triages a feature into a tier (quick / standard / full), confirms the scope with you, does budget-capped research (Memory Bank, codebase, docs), then launches a spec-writer agent with a structured JSON brief to generate **right-sized** documentation — one file for a logout button, five for an SSO system.

> Core principle: match spec depth to requirement depth.

## When it triggers

- "Spec out a user authentication feature"
- "Plan before we build" / "let's do the pre-planning research"
- "Write an FRD for the notification system"
- "/spec-plan add file upload --tier standard"
- To critique a spec that already exists → `/spec-review` instead

## Usage

```bash
/spec-plan build a user authentication feature   # auto-detect tier
/spec-plan add logout button --tier quick
/spec-plan add OAuth2 support --tier standard
/spec-plan build SSO with MFA --tier full --team # team mode, full tier only
/spec-plan                                       # interactive
```

## Tiers

| Tier | Output | Time | Tokens | Use when |
|------|--------|------|--------|----------|
| **Quick** | task-list.md | 1-3 min | ~15K | Single concern, known pattern, <5 tasks |
| **Standard** | FRD + TR + task-list | 3-7 min | ~35K | Moderate scope, API/schema changes, 5-15 tasks |
| **Full** | FRD + FRS + GS + TR + task-list | 8-15 min | ~80K | Multi-app, security, new architecture, 15+ tasks |
| **Full + Team** | Same, generated in parallel | 5-10 min | ~120K | Full scope but time-sensitive |

When uncertain between tiers, it picks the lower one — escalating is cheap, over-production isn't. Scope confirmation is mandatory before anything is generated.

## Workflow

```
description → lightweight clarification (2-3 questions) → triage gate
→ scope confirmation (user approves) → budgeted research
→ spec-writer agent with structured JSON brief → deliverables in job-queue/feature-{name}/docs/
```

Output lands in `/job-queue/feature-{name}/docs/`. Next step: `/spec-review` (tier-aware validation + critique).

## Context cost

Description always in context (~285 chars); SKILL.md body loads on trigger (~10k chars); `references/tier-prompts.md` (~6k chars — per-tier research budgets + verbatim spec-writer prompts) loads on demand.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Core skill (v2): triage, confirmation, budgeted research, agent launch |
| `references/tier-prompts.md` | Per-tier research budgets + tier-specific spec-writer prompt templates |
| `TEAM-ENHANCEMENT.md` | Team mode workflow (parallel generation, full tier only) |
| `scripts/validate_spec.py` | Tier-aware structural validation (used by /spec-review) |
| `scripts/critique_plan.py` | Tier-aware quality critique + scope-appropriateness check |
| `scripts/README.md` | Tool documentation for the two scripts |
| `scripts/requirements.txt` | Empty — Python stdlib only |
| `evals/evals.json`, `evals/trigger-eval.json` | Skill evals + trigger-accuracy eval |

## Related skills

- **/spec-review** — validates and critiques what this skill generates; it runs the `scripts/` here. Plan with spec-plan, critique with spec-review.
- **/feature-new** — end-to-end orchestrator that runs spec-plan as Step 1
- **/start-phase-plan → /start-phase-execute** — downstream planning/execution of the generated task-list
- **/pm-db** — imports the generated specs for tracking
