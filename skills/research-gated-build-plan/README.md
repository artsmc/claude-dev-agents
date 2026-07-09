# /research-gated-build-plan

> Use at the START of anything sizable, BEFORE writing code — inventory what exists, scope the gap, persist research as artifacts, gate phases on human checkpoints. Decides WHETHER and HOW to enter the execution skills (start-phase-plan, feature-new); run it first.

## What it does

Encodes Mark's refusal to start coding on anything sizable until the approach is settled ("not fastest but the best"). Eight gates run before any build: inventory existing capabilities before hand-rolling ("do we already have a harness for this?"); scope what REMAINS against a target artifact or metric; persist research as docs → tickets so nothing lives only in a chat thread ("no memory leakage"); decompose into developer-sized, independently-testable units; sequence prerequisites and gate downstream work on their completion; bake Mark's standing quality bars into the kickoff (90%+ coverage, strict TypeScript, zero lint errors, files under ~350 lines, stop-gates per stage); subordinate mechanism to the user-visible outcome; and fix hard architectural boundaries and the single source of truth up front.

## When it triggers

- "lets start the planning", "I want to do some deep research"
- "what does complete look like", "what tickets remain", "what are our current gaps?"
- "do we already have a harness for this?", "is there a system we can use?"
- Any sizable ask arriving before an approach is settled — run this before jumping to execution
- "this is a really comprehensive ask so im looking for deep research and planning"

## Usage

Behavioral skill — auto-triggers from its description at the start of sizable work; `/research-gated-build-plan` forces it. It is the entry point that decides whether to route into `/start-phase-plan`, `/feature-new`, or nothing at all. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~500 chars); SKILL.md body loads on trigger (~7k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The eight gates + hand-off rules + red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **scope-question-and-delegate** — Gate 4 hands decomposed units here for question-triage and context-budgeted delegation.
- **reference-as-executable-spec** — fires instead when the requirement is a concrete named product/subsystem rather than a gap against a planning artifact.
- **steer-and-correct-the-agent** — governs the hand-off once the plan is agreed (phase gates vs. bounded autonomy).
- **fleet-dispatch-and-watch** — if the agreed plan fans out across machines.
- **spec-plan / start-phase-plan / feature-new** — the execution-side skills this one gates entry into.
