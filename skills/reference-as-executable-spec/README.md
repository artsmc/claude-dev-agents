# /reference-as-executable-spec

> Use when Mark points at a concrete reference as the feature spec instead of describing behavior — a live product ("an inline editor like editor.js"), an internal subsystem ("the OTP from sentient-monorepo is the pattern we should match"), or a library's structure ("setups similar to CASL"). On "build it like THAT": the named reference IS the executable spec — go observe it and let its real behavior define correct.

## What it does

Mark rarely enumerates requirements — he names something that already exists and says build it like that. This skill makes the agent treat that reference as the literal spec: actually go open the URL / read the internal subsystem's code (never reconstruct it from memory), pin down WHICH property of the reference is the target (Monaco's dark-theme raw-HTML editing surface, not the whole IDE; Editor.js's inline on-page editing, not its whole product), and when two references are offered as alternatives, extract the property they share. Internal references are designations of authority — match the named subsystem's contract exactly and never stand up a second source of truth. "Done" means behaves-like-the-reference on the property that mattered, and scope stops there: don't over-clone.

## When it triggers

- "an inline editor on the page like https://editorjs.io/ or quil"
- "like a monaco-editor dark theme", "much like openclaw.ai"
- "the OTP from sentient-monorepo is the pattern we should match"
- "use sentient-monorepo as its api source of truth"
- "are there setups similar to CASL?" — a library named as the structural model
- "build it like THAT", "same as X", "mimic/replicate X"

## Usage

Behavioral skill — auto-triggers from its description when a feature is framed by analogy to a named artifact; `/reference-as-executable-spec` forces it. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~480 chars); SKILL.md body loads on trigger (~7.4k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The seven-step reference-extraction procedure + red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **research-gated-build-plan** — the deliberate sibling: that skill scopes a gap against a planning artifact; this one fires only on a real named anchor (`monaco`, `editorjs`, `sentient-monorepo`, `casl`). A gap-analysis doc called a "source of truth" is that skill, not this one.
- **prove-it-live-before-done** — verification hand-off: check reference-vs-actual, not "works for me".
- **diagnose-from-raw-symptom** — shares the invariant that divergence from an agreed source of truth IS the bug.
