---
name: scope-question-and-delegate
description: Use when work is genuinely ambiguous in a way that changes the plan, big/multi-part/underspecified enough to balloon context, or when the orchestrator's window nears the ~200k cliff. Fires when Mark says 'this is a big one', 'what do you need from me before you start', 'dont drag the whole context through this', 'should we split this up' — or when one thread does both the planning AND the execution. Triage fast, ask only the few DECISIVE questions, treat the window as a finite budget, and hand each worker a minimal scoped snapshot. Not a hard gate — small clear tasks just proceed.
---

# Scope, Question, and Delegate

Two failure modes bracket every sizable task: plowing ahead on guessed requirements, and dragging one bloated context through all of it until quality craters. This skill is the cheap triage that catches both — but it is NOT a ceremony you run on everything. The win is sharper DETECTION of when to stop, not asking more questions everywhere. Most tasks are small and clear; just do them.

## 1. Triage first — ~10 seconds, then usually proceed
Before anything, ask two questions and answer them fast:
- **Is the requirement genuinely ambiguous IN A WAY THAT CHANGES THE PLAN?** Not "could I imagine an edge case" — would a reasonable reading lead you to build the wrong thing? If the ambiguity doesn't fork the plan, it's not decisive; proceed.
- **Will this balloon context?** Sizable, multi-part, multi-file, or open-ended work that will accrete a long transcript as it runs.

If neither is true, there is nothing to do here — build it. No menu, no preamble. Manufacturing questions for a clear task is its own failure (see Red flags). This gate earns its keep only on real ambiguity or real cost.

## 2. Ask the DECISIVE questions — not all questions
When triage trips on ambiguity, surface ONLY the few unknowns that change what you'd build. The test for each candidate question: *does a different answer produce a different artifact?* If not, drop it — decide it yourself with a sensible default and move on. Never interrogate the obvious.
- Present them as a numbered menu so a bare reply resolves cleanly — hand off to **enumerated-menu-pick-and-sweep** for the format and for reading Mark's terse picks (`go with B`, `1. yes 2. thats fine 3. just aws`).
- Two or three sharp questions beats a ten-item questionnaire every time. Each extra trivial question spends Mark's attention and trains him to skim.

## 3. Budget the context — the ~200k cliff
Treat the context window as a finite budget, not free space. Quality and cost degrade as it fills, and there is a cliff near ~200k tokens where reasoning gets mushy and spend balloons. Mark measured this across a company — the teams that dragged a full, ever-growing context through execution went off the rails; the ones that kept threads lean stayed sharp. So:
- Don't pull the entire transcript, every file read, and every tool result forward into the part of the work that does the building.
- The expensive thinking (planning, synthesis) deserves headroom. Spend the budget on judgment, not on re-carrying raw material the orchestrator no longer needs.

## 4. Delegate with a MINIMAL scoped snapshot
When you do fan work out, each subagent or team gets a hand-built brief — never the whole context. This extends **fleet-dispatch-and-watch**'s "precise state snapshot" rule to context budgeting: the snapshot is also how you keep the worker's window small. A scoped brief is exactly four things:
- **Goal** — the one outcome this worker owns, stated as a result.
- **Inputs** — the specific files, IDs, branch, or data it needs (paths/IDs, not pasted blobs where a pointer will do).
- **Constraints** — the hard bars that apply (quality bars, boundaries, "don't touch X").
- **Acceptance criteria** — how the worker proves it's done, so it returns a verdict, not a transcript.

If you can't write those four lines, the task isn't scoped yet — go back to step 1 or 2. A vague "continue this" forces the worker to reconstruct context you should have handed it.

## 5. Pick the substrate by task shape
Match the delegation mechanism to the work, don't default to one:
- **Workflow subagents** — bounded fan-out, each gets a fresh context and returns once. Right for independent, well-scoped units you'll synthesize.
- **Agent teams / TeamCreate** — persistent, parallel, multi-domain work where workers coordinate over time across different specialties.
- **Fleet** — work that spans machines (Mac Mini, Desktop, local orchestrator). See **fleet-dispatch-and-watch** for the dispatch→poll→escalate loop.

In every case the orchestrator's job is the same: **plan → dispatch → synthesize.** It does NOT accumulate execution detail. The moment the main thread starts doing the file-by-file building itself, you've collapsed orchestrator and worker into one bloated context — the exact thing this skill exists to prevent.

## 6. Return conclusions, not raw context
Workers hand back artifacts and verdicts — "done, branch pushed, tests green", "found the root cause: X", the finished file — not their full working transcript. That's what keeps the orchestrator lean across rounds: each round adds a conclusion, not a context dump. Across many rounds this is the difference between a thread that stays sharp and one that hits the cliff mid-task.

## When this hands off
**research-gated-build-plan**'s Gate 4 (decompose into developer-sized units) hands directly here — once the work is broken into units, this skill decides what to ask, what to budget, and how to dispatch each unit. For reading Mark's answers to your menu, **enumerated-menu-pick-and-sweep**. For the snapshot discipline and the poll/escalate loop once workers are running, **fleet-dispatch-and-watch**.

## Red flags
| Anti-pattern | The rule |
|---|---|
| Dragging the full window into execution | Treat the window as a budget; pull forward only what the step needs |
| Plowing ahead on unstated assumptions | If a reading forks the plan, ask the decisive question first |
| One giant context for everything | Orchestrator plans and synthesizes; workers build in scoped windows |
| Interrogating a trivial task | Triage says proceed — manufacturing questions is its own failure |
| The orchestrator doing the execution work itself | Plan → dispatch → synthesize; don't collapse into one bloated thread |
| A ten-item questionnaire | Two or three DECISIVE questions; default the rest yourself |
| "Continue this" with no brief | Hand goal + inputs + constraints + acceptance criteria |
| Workers returning their whole transcript | Return artifacts and verdicts so the orchestrator stays lean |
