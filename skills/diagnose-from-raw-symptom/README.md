# /diagnose-from-raw-symptom

> Use when Mark reports a bug by pasting a raw artifact with little or no prose — a stack trace, an HTTP trace (URL + method + status like 500/403/404/502), a console/React/Prisma error, a ChunkLoadError, a shell error, or a screenshot of a visual defect. The front-to-back debugging procedure: extract trigger and reproduction from terse input, probe whether the plumbing even exists, localize by contrast, and drive to a durable root cause. Reach for this BEFORE proposing any fix.

## What it does

Encodes Mark's debugging discipline as a procedure the agent runs before touching a fix. The pasted artifact (error string, status code, screenshot) is treated as the literal spec — never paraphrased away. The procedure: pin the exact trigger and a real reproduction, check the foundational wiring first (does the API/DB/service behind the failing UI even exist?), localize by contrasting a known-good case against the broken one, walk the error chain forward (502 → 404 → 403 is progress, not regression), and reject easy explanations until the root cause is verified end-to-end. It also covers distrusting known-lying signals (e.g. a tee'd log that's empty while work proceeds).

## When it triggers

- A bare stack trace or error string pasted with no prose ("Invalid `prisma.profiles.create()` invocation...")
- An HTTP trace: URL + method + `Status Code 403 Forbidden` / 500 / 502
- "still failing", "clicking X does nothing", "identify the true error"
- A screenshot of a visual defect with a terse caption ("message position weird on chat")
- Plumbing questions mid-bug: "do we have local postgres/pgvector?"
- "no inline editor on the rendered page" — a missing-element symptom at a URL

## Usage

This is a behavioral skill: it auto-triggers from its description when a raw symptom lands; there is no flag or mode to pass. It can be forced with `/diagnose-from-raw-symptom` if the agent starts proposing fixes without diagnosis. A cue-matching hook lives at `hooks/reasoning-skills/` but is not currently wired — triggering relies on the description alone.

## Context cost

Description always in context (~750 chars); SKILL.md body loads on trigger (~6k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The six-step diagnosis procedure + red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **prove-it-live-before-done** — the explicit hand-off target: once you believe it's fixed, that skill disproves the claim against the live app.
- **reference-as-executable-spec** — shares the "divergence from an agreed source of truth IS the bug" invariant.
