# /fleet-dispatch-and-watch

> Use when Mark wants large or mechanical work fanned out across his machine fleet, or wants long-running/background/remote agents monitored. His dispatch→snapshot→poll→escalate→checkpoint loop: fan independent work to workers (local box orchestrates), hand each a precise state snapshot, then poll on a fixed cadence with trustworthy liveness proxies, error-signature buckets, and hard stop/escalation thresholds — never blocking or assuming success.

## What it does

Encodes how Mark runs parallel work across his machines (Mac Mini, Desktop WSL, local orchestrator) — "fleet" specifically means splitting work between machines. Mechanics: sync repos to a known-good baseline and commit a checkpoint before dispatching; one tmux session + git worktree per unit of work; heavy compute on the remote boxes, local machine orchestrates only. The monitoring half is the hard-won part: judge liveness by `tmux ls` + `pgrep` + git commits, NOT log size (0 bytes = working; a tiny log ending EXIT:1 = failed); pre-classify error signatures into wait-vs-retry buckets (401 → re-auth and wait, 400 role → re-spawn); escalate only past explicit thresholds; never `git reset --hard` on a worker; close the loop with commits pushed, memory-bank/docs synced, and a stakeholder summary.

## When it triggers

- "distribute among the fleet", "delegate with tmux and worktrees"
- "kick it off, fan them out", "are we ready to delegate"
- "offload to mac-mini and desktop, just be an orchestrator"
- "check on the agents every 5 min", "add checkins every 5min"
- "is it done, its been some hours" — status of a long background run
- Any dispatch of work to background/remote workers

## Usage

Behavioral skill — auto-triggers from its description on dispatch or monitoring language; `/fleet-dispatch-and-watch` forces it. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~750 chars); SKILL.md body loads on trigger (~6.5k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The nine-step dispatch/monitor loop + red-flag table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **scope-question-and-delegate** — budgets exactly what context each delegate gets; this skill's "precise state snapshot" rule is the machine-fleet version of that brief.
- **prove-it-live-before-done** — when a poll shows pending, that skill governs the green-gate before advancing.
- **steer-and-correct-the-agent** — how Mark hands off autonomy for the run and steers it mid-flight.
