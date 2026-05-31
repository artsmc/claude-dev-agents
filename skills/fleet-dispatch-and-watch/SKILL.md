---
name: fleet-dispatch-and-watch
description: Use when Mark wants large or mechanical work fanned out across his machine fleet, or wants long-running/background/remote agents monitored. Triggers on 'distribute among the fleet', 'delegate with tmux and worktrees', 'kick it off fan them out', 'offload to mac-mini, desktop just orchestrate', 'check on the agents every 5 min', 'is it done its been some hours', 'are we ready to delegate', or any dispatch to background workers. This is Mark's dispatch→snapshot→poll→escalate→checkpoint loop — fan independent work to workers (local box orchestrates), hand each a precise state snapshot, then poll on a fixed cadence with trustworthy liveness proxies, error-signature buckets, and hard stop/escalation thresholds — never blocking or assuming success.
---

# Fleet Dispatch and Watch

For Mark, 'fleet' means splitting work across machines (Mac Mini, Desktop WSL, local). For any sizable or mechanical body of work he reaches for parallel execution and treats serial as a mistake. The monitoring discipline is precise and easy to get wrong — that's the whole point of this skill.

## 1. Sync to a known-good baseline before dispatching
- `pull latest from main`; `are all of my claude root folders in sync with agents and skills?`
- Confirm fleet repos are in sync and the target resource exists in the canonical registry: `do we have applications/sentient-home in our fleet repo?`
- Commit accumulated work to a clean checkpoint first: `lets get all this code commited before moving on`.

## 2. Fan out — local orchestrates, workers do the heavy compute
- `distribute the planning and effort among the fleet`
- `each process should consider delegating across machines using tmux and worktrees`
- `i think i need to offload entirely to mac-mini and desktop, just be a orchestrator for the sake of the machine battery`
- `kick it off, fan them out`

**Mechanics Mark expects:** one tmux session + git worktree per unit of work (isolation, no file conflicts), heavy jobs on Mac Mini / Desktop, local machine as orchestrator only. Respect hardware limits — a single machine can't handle it all at once, which is the reason for the fan-out.

## 3. Hand each worker a PRECISE state snapshot
Don't just kick a vague task — supply done/committed-but-unpushed/blocking-cause/hypothesis, and clean up partial state as part of recovery:
- `sen-467 work is committed on desktop WSL (commit fcb5bed) but NOT pushed — blocked because desktop sshd was closing all connections (tailnet ping worked, likely memory pressure from a 29h hung jest I tried to kill)`
- `and clean up partial sentient-monorepo node_modules`
Give each worker exact IDs/targets (run IDs, branch names, ticket IDs, SSH host), never a vague 'continue'.
The same snapshot discipline applies to subagents/teams, not just machines — see **scope-question-and-delegate** for budgeting exactly the context a delegate needs (no more, no less).

## 4. Poll on a fixed cadence — never block, never assume success
Set recurring check-ins and spell out the exact verification commands with branching outcomes:
- `check on the agents every 5 min`; `add checkins every 5min`
- `Check it now: ssh ... 'tmux ls; tail -40 ~/dispatch-logs/sen-467.log'. If done, report final summary + all 4 branches pushed. If still running, schedule another 1200s wakeup. If failed/stuck >2h total, alert.`
Probe whether work actually started and how completion is even detected: `is there a auto checker — how do you know when its ready?`

## 5. Judge liveness by TRUSTWORTHY proxies — NOT log size
This is Mark's hard-won, counter-intuitive rule. Get it right:
- `judge liveness by tmux ls + pgrep -af bypassPermissions, NOT log size (0 bytes = working; a tiny log ending EXIT:1 = failed)`
- Per cycle: `(a) tmux has-session -t s1a — is the agent still running? (b) git log --oneline stage1/shared-infra ^main` — is it producing commits?
- If liveness is very low (<3 files in 5min), do an extra probe: `tmux capture-pane` to see if it's stuck on a permission prompt or error.
Never conclude 'dead' from an empty log alone.

## 6. Pre-classify error signatures into wait-vs-retry buckets
React correctly to each known signature instead of treating all errors alike:
- `'401 Invalid authentication credentials' → user must re-auth, report + wait`
- `'400 role system is not supported' → transient, re-spawn`
Maintain this bucket list and consult it when a worker errors.

## 7. Escalate ONLY past explicit thresholds — avoid false alarms
- `Escalate only if: stuck >15 min with no commits AND CPU <2% (truly idle), repeated F-agent failures, or irrecoverable lockfile`
- If a connection keeps closing: `alert the user that manual WSL sshd recovery is needed (VNC → restart ssh) and stop polling`.
Don't panic on a single slow cycle; don't loop forever — end the loop on the defined done-state (`end the loop once Wave A is complete`).

## 8. Protect worker state — destructive ops are forbidden
- `NEVER git reset --hard on workers.`
- `Push main after every merge. Update CURRENT-STATE.md after every state change.`

## 9. Checkpoint and close the communication loop
When work passes: sweep into commits, push so work is recoverable across machines, sync persistent docs by repo name, record release status, and produce a stakeholder summary:
- `update /memory-bank && /document-hub`; `do a /memory-bank-update on MVP-backend`
- `update linear with the release status`
- `write up a description summary of what has been deployed in each app so i can tell non technical stakeholders what to look for`
Require a commit/push checkpoint BEFORE any long autonomous run so it's recoverable.

## Red flags
| Anti-pattern | Mark's rule |
|---|---|
| Running large mechanical work serially | `distribute among the fleet... tmux and worktrees` |
| Concluding an agent is dead from an empty log | `0 bytes = working; rely on tmux/pgrep + git state` |
| Treating all worker errors the same | Bucket them: 401 → wait/re-auth; 400 role → re-spawn |
| Escalating on one slow cycle | `escalate only if stuck >15min AND CPU<2%` |
| `git reset --hard` to recover a worker | `NEVER git reset --hard on workers` |
| Blocking the orchestrator waiting | Poll on cadence; schedule the next wakeup |
| Dispatching without a state snapshot | Supply done / unpushed / blocking-cause / hypothesis |
| Long run with no checkpoint | Commit + push first so it's recoverable across machines |
