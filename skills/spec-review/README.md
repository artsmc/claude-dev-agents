# /spec-review

> Validate, critique, and iterate on generated specifications. Use for "review this spec", "critique the FRD/FRS", "is this spec ready to build?", or folding user feedback into a spec produced by spec-plan before execution begins.

## What it does

The human feedback loop for feature specs. Runs automated structural validation (`validate_spec.py`) and quality critique (`critique_plan.py`) against a spec folder produced by `/spec-plan`, presents the findings (completeness score, critical issues, warnings), then collects your verdict — approve, request changes (re-runs the spec-writer agent with your feedback), edit manually, or focus the critique on a specific area. Iterates until the spec is approved.

Validation is tier-aware: a quick-tier spec is checked against task-list.md only, standard against FRD + TR + task-list, full against all five files.

## When it triggers

- "Review this spec" / "critique the FRD"
- "Is this spec ready to build?"
- "Fold my feedback into the spec before we start"
- After `/spec-plan` finishes — it's the designated next step
- To *generate* a spec from scratch → `/spec-plan` instead

## Usage

```
/spec-review
```

Points at the most recent `/job-queue/feature-{name}/` output. The two analysis scripts live in the sibling spec-plan skill:

```bash
python3 ~/.claude/skills/spec-plan/scripts/validate_spec.py /path/to/feature-folder [--tier standard]
python3 ~/.claude/skills/spec-plan/scripts/critique_plan.py /path/to/feature-folder [--tier standard]
```

Checks: file existence/completeness, Gherkin syntax, actionable tasks, cross-references (validation); requirement specificity, task atomicity/sequencing, API/data-model completeness, security coverage, testability (critique).

## Context cost

Description always in context (~230 chars); SKILL.md body loads on trigger (~6k chars); no references/ directory.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Validate → critique → present → feedback → iterate workflow |
| `evals/trigger-eval.json` | Trigger-accuracy eval |

The Python tools it invokes (`validate_spec.py`, `critique_plan.py`) live in `../spec-plan/scripts/`.

## Related skills

- **/spec-plan** — generates the specs this skill reviews (and hosts the scripts)
- **/feature-new** — runs spec-review automatically as Step 2 of the end-to-end workflow
- **/start-phase-plan** — the step after a spec is approved
