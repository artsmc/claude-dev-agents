# /scope-question-and-delegate

> Use when work is genuinely ambiguous in a way that changes the plan, big/multi-part/underspecified enough to balloon context, or when the orchestrator's window nears the ~200k cliff. Triage fast, ask only the few DECISIVE questions, treat the window as a finite budget, and hand each worker a minimal scoped snapshot. Not a hard gate — small clear tasks just proceed.

## What it does

Cheap triage against two failure modes: plowing ahead on guessed requirements, and dragging one bloated context through planning AND execution until quality craters. Triage takes ~10 seconds — if the ambiguity doesn't fork the plan and the work won't balloon context, just build it (manufacturing questions for a clear task is itself a red flag). When triage trips: ask only the questions where a different answer produces a different artifact (2-3, not a questionnaire); treat the context window as a budget with a quality cliff near ~200k tokens; delegate each unit with a four-line brief (goal, inputs, constraints, acceptance criteria); pick the substrate by shape (workflow subagents, agent teams, or the machine fleet); and have workers return verdicts and artifacts, never transcripts. The orchestrator plans, dispatches, and synthesizes — it does not build.

## When it triggers

- "this is a big one", "should we split this up"
- "what do you need from me before you start"
- "dont drag the whole context through this"
- One thread is doing both the planning and the execution
- The orchestrator's window is approaching the ~200k cliff mid-task
- A unit out of research-gated-build-plan's decomposition is sizable or ambiguous

## Usage

Behavioral skill — auto-triggers from its description on ambiguity or context-cost signals; `/scope-question-and-delegate` forces it. Explicitly NOT a ceremony for every task: the win is sharper detection of when to stop, not more questions. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~590 chars); SKILL.md body loads on trigger (~6.8k chars); no references/ to load on demand.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Triage rule, decisive-question test, context budget, brief format, substrate picker |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **research-gated-build-plan** — its Gate 4 (decompose into developer-sized units) hands directly here.
- **enumerated-menu-pick-and-sweep** — formats the decisive questions as a menu and reads Mark's terse answers.
- **fleet-dispatch-and-watch** — the snapshot discipline and poll/escalate loop once workers are running across machines.
- **headroom-context-compression** — the mechanical tool for shrinking blobs that must still travel to a delegate.
