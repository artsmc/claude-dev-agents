# The 200k Context Cliff — Scope & Delegate

**Skill:** `scope-question-and-delegate` · **For:** Sprinkle devs running long agent sessions

A long-running orchestrator session is a finite budget, not a free buffer. Past roughly **~200k tokens** of accumulated context, quality and cost go off the rails — observed repeatedly across teams: the sessions that dragged a full transcript through every step are exactly the ones that drifted, hallucinated stale state, and burned tokens re-reading what they already knew. The cause is not the model getting dumber on hard problems; it's the window filling with execution detail that nobody needs anymore.

This skill is the discipline that prevents that. Two moves: **front-load the few decisive questions**, then **split the work into fresh-context subagents/teams that each get a minimal scoped snapshot** — keeping the orchestrating session lean across rounds.

> **Calibration — read this first.** This is NOT a hard gate. It fires only on **genuine ambiguity** (the kind that changes the plan) OR **real cost/context-budget risk** — sizable, multi-part, or underspecified work, or when the orchestrator's context is trending toward the cliff. Small, clear tasks just proceed, no ceremony. The win is sharper *detection* of when to stop and scope — not asking more questions everywhere. Interrogating trivial work is the failure mode, not the goal.

---

## 1. Triage first (cheap, ~10s)

Before anything, two yes/no questions:

1. **Is the requirement genuinely ambiguous *in a way that changes what I'd build?*** Not "could I imagine a clarification" — would a different answer produce a materially different plan?
2. **Will this balloon the context?** Sizable, multi-part, many files, long-running, or fan-out shaped?

If **neither** → just proceed. No questions, no delegation theater. WHY: ceremony on a clear small task is pure cost and trains the human to ignore you. If **either** → continue below.

## 2. Ask the DECISIVE questions, not all the questions

Surface only the handful of questions whose answers change what you build. WHY: every obvious question you ask is friction the human pays for, and it buries the one question that actually mattered. Never interrogate the obvious — if you can infer it from the repo, the convention, or prior turns, infer it.

Hand the open questions over as a **numbered menu** so a bare reply resolves everything → see **`enumerated-menu-pick-and-sweep`** for how Mark answers (a lone `B` or `1. yes 2. just aws 3. minimal` is a full selection). One decision per line, each self-contained.

**Do:** `Before I split this, 3 things change the plan: 1) one tenant or multi? 2) reuse the existing OTP or new? 3) ship behind a flag?`
**Don't:** a 12-question intake form that includes "should I write tests?" (you know the answer).

## 3. Budget the context — the 200k cliff

Treat the window as a **finite budget you are spending**, not a log you are keeping. Quality and cost degrade as it fills; the degradation is gradual then sharp around the cliff. The orchestrator's job is to **plan → dispatch → synthesize** — it does **not** accumulate execution detail. WHY: once raw file dumps, tool spew, and dead-end exploration are in the window, they cost tokens on every subsequent turn forever and dilute the signal the model is reasoning over.

Concrete tells you're heading for the cliff: you're re-reading files you read an hour ago, the session has full diffs of code that's already merged, or you're scrolling to find the actual goal. That's the signal to delegate, not to keep going.

## 4. Delegate with a MINIMAL scoped snapshot

Each subagent / team gets a self-contained brief and **nothing else** — never the whole transcript. This extends **`fleet-dispatch-and-watch`**'s "precise state snapshot" rule to context budgeting: a snapshot is small *on purpose*. Four fields:

- **Goal** — the one outcome, in a sentence.
- **Inputs** — exact paths, IDs, branch names, the reference to mimic (not "the stuff we discussed").
- **Constraints** — what must hold (keep the save button, don't touch auth, CLI only).
- **Acceptance criteria** — how the agent knows it's done, so it can self-check before reporting.

**Do:** `Goal: add rate-limit middleware to /api/upload. Inputs: src/middleware/, mirror src/middleware/auth.ts. Constraints: no new deps. Accept: 429 after 10 req/min, existing tests green.`
**Don't:** paste the last 40k tokens of conversation and say "you have the context, continue."

If a subagent needs more, it asks — a 5-line brief that triggers one clarifying question beats a 5,000-line dump that drowns the goal.

## 5. Pick the substrate by task shape

| Shape | Substrate | Why |
|---|---|---|
| Bounded fan-out, each unit independent, fresh context each | **Workflow subagents** | Cleanest budget reset; orchestrator only sees results |
| Persistent, parallel, multi-domain (frontend + backend + infra at once) | **Agent teams / TeamCreate** | Long-lived specialists that hold their own domain context |
| Work spread across machines (Mac Mini / Desktop / local) | **Fleet** (`fleet-dispatch-and-watch`) | Hardware parallelism; local box orchestrates only |

In all three the orchestrator **plans → dispatches → synthesizes**. It must not start doing the execution work itself — the moment it does, its window fills with exactly the detail this skill exists to keep out.

## 6. Return conclusions, not raw context

Subagents hand back **artifacts and verdicts** — a diff, a file path, a pass/fail, a one-paragraph finding — not their raw working transcript. WHY: the orchestrator stays lean across rounds, so round 2, 3, 4 each start from a clean, low-token state instead of compounding. If you find yourself pasting a subagent's entire run back into the main session, you've defeated the point — extract the conclusion and drop the rest.

## 7. Red flags

| Red flag | What it causes | Do instead |
|---|---|---|
| Dragging the full window into execution | Hits the ~200k cliff; quality/cost degrade | Scoped snapshots (§4) |
| Plowing ahead on unstated assumptions | Build the wrong thing, redo it | Ask the *decisive* questions (§2) |
| One giant context for everything | No reset; every turn pays for all history | Fresh-context subagents/teams (§5) |
| Interrogating trivial, clear tasks | Friction; trains human to ignore you | Triage → just proceed (§1) |
| Orchestrator doing the execution itself | Its window fills with detail it should never hold | Plan → dispatch → synthesize (§5–6) |

---

## Where this sits

- **`research-gated-build-plan`** — Gate 4 (decompose into developer-sized units) hands *here*: once the gap is scoped into units, this skill decides the questions, the budget, and the dispatch.
- **`fleet-dispatch-and-watch`** — the snapshot discipline this extends; use it for the dispatch→poll→escalate loop once units are scoped.
- **`enumerated-menu-pick-and-sweep`** — how the decisive questions get asked and how Mark's terse picks get read.

## Checklist

- [ ] Triaged: ambiguity-that-changes-the-plan? balloon risk? If neither, just proceed.
- [ ] Asked only the decisive questions, as a numbered menu.
- [ ] Treated the window as a budget; orchestrator is planning, not accumulating.
- [ ] Each subagent got goal + inputs + constraints + acceptance — and nothing else.
- [ ] Substrate matches task shape (subagent / team / fleet).
- [ ] Subagents return conclusions/artifacts; orchestrator stays lean across rounds.
