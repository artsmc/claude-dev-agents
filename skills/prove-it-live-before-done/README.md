# /prove-it-live-before-done

> Use whenever an agent (or you) is about to claim work is done/fixed/shipped/passing. Treat every completion claim, green CI, and passing test as UNPROVEN until the real artifact is exercised end-to-end — drive the actual running app, confirm the deployed revision is live, verify the mutating side-effect truly fired, gate forward steps on explicit green signals, and reconcile against the system of record.

## What it does

Mark's strongest reflex, encoded: he refuses to accept "done" on the agent's word, so the agent adopts his skepticism and tries to DISPROVE its own completion claim before announcing it. Each claim maps to a real proxy: "fix works" → re-run the exact prior failing action; "email sent" → check the inbox, not the toast; "deployed" → hit the live URL AND confirm the running revision by exact version number; "tests pass" → confirm the gate ran on a machine that actually has node_modules. Done is multi-signal (report exists AND commits present AND gate green; DONE AND branch on origin), coverage is audited across the whole surface, tracking state is reconciled against git/Linear/the real machines, and the report closes with the residual defect stated as expected-vs-actual.

## When it triggers

- The agent is about to say "done", "fixed", "shipped", or "tests pass"
- Mark asks "ready?", "done?", "did it work?", "did we confirm the change when we ran the script?"
- "still failing" — a prior done-claim just got disproven
- "is the live URL responding?", "check the v1.5.11 deploy status"
- "can you absolutely confirm nothing is live?" before a risky step
- Confirming a fix before pushing or merging

## Usage

Behavioral skill — auto-triggers from its description at completion-claim moments; `/prove-it-live-before-done` forces it. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~740 chars); SKILL.md body loads on trigger (~7.2k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Claim→proof table, the eight verification steps, red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **diagnose-from-raw-symptom** — hands off here once a fix is believed in; if this skill finds a residual defect, control goes back there.
- **fleet-dispatch-and-watch** — supplies the polling loop when the green signal is still pending.
- **reference-as-executable-spec** — when the spec was a named reference, "done" here means behaves-like-the-reference.
- The generic **verify** skill covers ordinary code changes; this one encodes Mark's specific multi-signal, system-of-record discipline.
