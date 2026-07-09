# /steer-and-correct-the-agent

> Use mid-flight while executing for Mark to interpret his terse steering grammar — greenlights ("yes", "go for it"), autonomy grants ("you have full autonomy", "dont stop"), hard overrides ("no remove this", "not X but Y"), re-anchoring ("remember the goal", "get back on track"), and method/preserve constraints ("no just cli", "keep the save button"). His corrections are the spec.

## What it does

A decoder for Mark's terse, action-first steering vocabulary while work is already in motion. It maps each signal class to the right behavior: a terse greenlight means execute without re-litigating; an autonomy grant means run unattended but pin the boundary he set (stopping point, decision heuristic, check-in cadence) — and is distinct from phase-gating, where he owns each checkpoint; a hard override means reverse course and use his named target verbatim; re-anchoring means the drift itself is the defect — cut the tangent and resume the agreed breakdown. It also covers method constraints ("is this not possible via X?" → switch to the simpler path), expected-vs-actual corrections (the gap is the new requirement), preserve-constraints (verify the protected capability survives the change), rejecting mock data, persisting surfaced constraints to the named CLAUDE.md/memory, his direct observation beating your stale claim, and the gate-and-resume pattern for steps he reserves for himself (PRs, SSH/credentials).

## When it triggers

- "yes", "go for it", "lets do it" after you surfaced a plan
- "you have full autonomy", "dont stop", "run 2-3 goals on your own"
- "no remove this, this was a bad call", "not X but Y"
- "remember the goal", "get back on track", "this looks wrong our main objectives are..."
- "no just cli", "keep the save button", "no need for mock data"
- "that is false im looking at the page" — his observation contradicts your claim

## Usage

Behavioral skill — auto-triggers from its description whenever a short directive arrives mid-execution; `/steer-and-correct-the-agent` forces it. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~530 chars); SKILL.md body loads on trigger (~6.9k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The ten signal classes + gate-and-resume + red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **enumerated-menu-pick-and-sweep** — handles picks that only resolve against a labeled list you offered; this skill handles free-standing directives once work is moving.
- **prove-it-live-before-done** — where expected-vs-actual corrections and rejected done-claims get verified.
- **research-gated-build-plan** — sets up the plan and quality bars that these steering signals then drive.
