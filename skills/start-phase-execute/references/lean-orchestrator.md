# Lean Orchestrator Protocol (--team mode)

Canonical cost-discipline protocol for team execution. Read before spawning any team agent.
The spawn-prompt mechanics (claim → gates → commit loop) live in `team-mode-examples.md`;
**this protocol governs what context flows into and out of every spawn.**

## Why this exists (30-day mined evidence, 2026-06-09 → 07-09)

The lesson from the mining is NOT "avoid fan-out." It is "fan out with a lean parent":

- Subagents were only **14.9% of total corpus cost**. Workers are cheap.
- The waste is the **orchestrator main loop**: it re-reads its ever-growing accumulated
  context on every API call, 50–100+ calls per user turn. In the worst session
  (07-07/08 max, 56 turns, 5,356 API calls, 145.7M proxy units = **7.3% of the entire
  month**), the main loop alone was **71% of cost** — not the 70 subagents it spawned.
- Fan-out sessions cost **3.4× per turn at identical effort** (xhigh fan-out 2.92M vs
  flat 0.86M proxy/turn) — driven by loop length (96.7–195 calls/turn vs 19–36 flat)
  and context carriage, not by the children.
- Cache-read per call grew 180k→251k tokens (+40%); 95.5% of all 4.75B tokens were
  cache reads. Every token of accumulated parent state is re-billed on every call.

Cost/turn = (calls/turn) × (context/call). Team mode necessarily raises calls/turn;
this protocol attacks the other factor so the product stays sane.
Source: `~/.claude/job-queue/feature-skill-efficiency/findings/effort-analysis.md` and `findings/FINAL-REPORT.md`.

---

## Rule 1 — Worker routing table

| Task profile | Model | Effort | Examples |
|---|---|---|---|
| **Default: implementation / mechanical** | **sonnet** | **medium** | CRUD endpoints, components from spec, tests, refactors with a known pattern, config, migrations, docs |
| Ambiguous requirements (spec leaves real design choices) | sonnet | high | "design the retry strategy", unclear API shape |
| Cross-cutting design (defines contracts ≥2 other tasks consume, touches 3+ modules) | opus | medium–high | shared type layer, event schema, auth middleware others build on |
| Security-sensitive (authn/authz, crypto, secrets, payment, input-validation surfaces) | opus | high | + require the worker to state its threat assumptions in its report |

- Escalate **per-task, on these criteria only** — never blanket-escalate a whole wave
  because the feature "feels big."
- Evidence for the default: controlled effort A/B on bounded tasks scored **medium 9.50/10
  vs xhigh 9.78/10 at +11% tokens** (and +27% wall time) — the dial buys ~0.3 points.
  Body A/B showed lean scoped context *helps*: mastra-dev −45% tokens with quality
  8.5→9.5; document-hub-initialize −15% tokens, tied 10/10. Same-session medium vs high
  phases produced 1,339 vs 1,098 output tokens/call. Scoping beats cranking the dial.
- Never haiku for execution (measured too weak for task completion).

## Rule 2 — Scoped snapshot (every worker spawn prompt)

Workers don't inherit conversation history — that is a feature. Hand each exactly this:

```
GOAL: <one sentence: what "done" looks like>
TASK: <task id + subject, from task-list.md>
INPUTS (paths, NOT contents):
  - Spec: {path}#{section}
  - Files to modify: {paths, from system-changes.md}
  - Patterns to follow: {path to exemplar file / memory-bank/systemPatterns.md}
CONSTRAINTS: <project rules, do-not-touch files, interface it must conform to>
ACCEPTANCE: <checkable criteria + exact gate commands (lint/build/test)>
OUTPUT CONTRACT: <the compact-return format from Rule 3 + where full artifacts go>
```

- **Paths, not payloads.** The worker reads files itself with fresh context. A pasted
  blob is billed in the parent's output AND rides in the worker's cache on every one
  of its calls.
- **Unavoidable large handoff** (log excerpt, mined dataset, generated spec that exists
  nowhere on disk): `mcp__headroom__headroom_compress` it, pass the hash + a one-line
  summary; the worker expands with `mcp__headroom__headroom_retrieve`.
- Never paste the parent's conversation history, prior worker reports, or "context so far."

## Rule 3 — Compact-return contract

Workers end their run by writing full detail to FILES, then replying with only:

```
STATUS: completed | failed | blocked
ARTIFACTS: <paths created/modified>
VERIFIED: <evidence: gate results, test counts, commit hash>
NOTES: <=2 sentences (blockers, decisions the parent must know)
```

Full detail — diffs, gate output, reasoning, alternatives considered — goes to
`{planning_folder}/task-updates/task-{n}-{slug}.md`, never into the reply.
Why: every token a worker returns becomes parent accumulated state, re-read on every
parent call for the rest of the session (30–100+ calls/turn on real work). A 5k-token
worker essay costs its size × the parent's remaining call count.

## Rule 4 — Parent hygiene

- **Accumulated-state budget: ~30k tokens.** The parent's variable context (task table,
  wave status, compact returns) stays under ~30k; the fixed ~250k/call (system, skills,
  MCP schemas) is already the floor you can't avoid — don't stack conversation fat on top.
- **Parallel dispatch in one turn:** all Task spawns for a wave in a single message.
  N sequential spawn turns ≈ N× the parent-loop overhead for zero extra parallelism.
- **Never re-read worker artifacts you don't need.** Trust STATUS/VERIFIED + pm-db.
  Open a task-update file only when a gate failed or the next wave consumes its contract.
- **Wave checkpoints:** after each wave, persist state OUTSIDE the window — tick
  task-list.md checkboxes, fire `on-task-run-complete.py` / pm-db hooks. The session can
  then `/clear` (61 uses last month — good habit) or die, and Phase 1.3 resume detection
  rebuilds from disk instead of from a 5,000-call transcript.
- **End the orchestrator at closeout.** The 7.3%-of-month session happened because one
  max session chained spec-plan → review ×4 → phase-plan ×3 → execute-team ×4. New
  phase = new session.

## Rule 5 — Failure handling

- Retry = **fresh worker + the SAME scoped snapshot + the specific failure evidence**
  (failing gate output, error signature, path to the failed attempt's task-update file).
  Never the parent's history, never "here's everything that happened so far."
- 1st retry: same routing (sonnet/medium). 2nd failure: escalate one step on the Rule 1
  table (sonnet/high or opus), still scoped. 3rd failure: stop and surface to Mark with
  the evidence trail.
- Worker context is disposable — don't resurrect or message a failed worker to "continue";
  its accumulated confusion is the thing you're paying to discard.

## Rule 6 — The Wave Gate (a wave is NOT done until proven done)

Lean dispatch makes it *cheap* to abandon workers — so this rule is hard: **the parent
never ends its turn or session while a wave is in flight.** A wave completes only when:

1. Every worker's compact return is collected (or its failure/timeout is recorded), AND
2. The wave's verification gate actually ran (quality-gate script, test suite, VERIFY
   command) with its output in hand, AND
3. Failures re-entered the Rule 5 retry loop or were surfaced.

If workers run as background processes (headless `claude -p`, tmux, remote), the parent
must actively wait: have each worker write a `DONE` marker + `RESULT.md` on exit, poll
markers in a bounded loop (e.g., every 30–60s with a hard per-wave timeout), and treat
timeout as failure with evidence. "Dispatched + checkpointed" is a *crash-recovery* state,
not a completion state — checkpoints exist so a crashed parent can resume, never so a
live parent can leave early. (Evidence: the first lean-fanout benchmark run scored 1/6 on
quality purely because the orchestrator ended with workers in flight and the gate never
ran — the code that existed was fine. Tokens −57% mean nothing if deliverables drop.)

## Anti-pattern checklist (each one observed in the corpus)

- ❌ Pasting file contents or prior worker output into spawn prompts
- ❌ Workers replying with full diffs/logs instead of paths
- ❌ Parent re-reading every artifact "to verify" when VERIFIED evidence + gates already ran
- ❌ Spawning wave agents one turn at a time
- ❌ Continuing into the next phase in the same orchestrator session
- ❌ Blanket opus/xhigh workers "because the feature is important"
- ❌ Ending the turn/session with workers in flight ("they'll notify me") — see Rule 6
