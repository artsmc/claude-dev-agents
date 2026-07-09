---
description: |
  Use when Mark wants large or mechanical work fanned out across his machine fleet, or wants long-running/background/remote agents monitored. Triggers on 'distribute among the fleet', 'delegate with tmux and worktrees', 'kick it off fan them out', 'offload to mac-mini, desktop just orchestrate', 'check on the agents every 5 min', 'is it done its been some hours', 'are we ready to delegate', or any dispatch to background workers. This is Mark's dispatch→snapshot→poll→escalate→checkpoint loop — fan independent work to workers (local box orchestrates), hand each a precise state snapshot, then poll on a fixed cadence with trustworthy liveness proxies, error-signature buckets, and hard stop/escalation thresholds — never blocking or assuming success.
---

# fleet-dispatch-and-watch

This skill handles: Use when Mark wants large or mechanical work fanned out across his machine fleet, or wants long-running/background/remote agents monitored. Triggers on 'distribute among the fleet', 'delegate with tmux and worktrees', 'kick it off fan them out', 'offload to mac-mini, desktop just orchestrate', 'check on the agents every 5 min', 'is it done its been some hours', 'are we ready to delegate', or any dispatch to background workers. This is Mark's dispatch→snapshot→poll→escalate→checkpoint loop — fan independent work to workers (local box orchestrates), hand each a precise state snapshot, then poll on a fixed cadence with trustworthy liveness proxies, error-signature buckets, and hard stop/escalation thresholds — never blocking or assuming success.
