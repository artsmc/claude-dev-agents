---
name: research-gated-build-plan
description: Use at the START of anything sizable, BEFORE writing code — when Mark says 'lets start the planning', 'I want to do some deep research', 'what does complete look like / what tickets remain / what are our current gaps', or 'do we already have a harness for this / is there a system we can use?'. Inventory what exists, scope the gap, persist research as artifacts, gate phases on human checkpoints. Decides WHETHER and HOW to enter the execution skills (start-phase-plan, feature-new); run it first.
---

# Research-Gated Build Plan

Mark refuses to start coding on anything sizable until the approach is settled. He optimizes for the quality of the decision over the speed of shipping (`whatever option you think is best not fastest but the best`; `make the one with long term benefits not short term gain`). Run these gates before any build.

## Gate 1: Inventory existing capabilities — check before you build
Before committing to build something new, examine the foundation and ask whether it already exists. This counters the default urge to hand-roll.
- `do we have inngest workflows... first just examining the foundation`
- `do we already have a harness for this in docs?`
- `is there a system we can use?` / `I don't think raw sql is the best`
- Separate genuine build work from mere configuration: `understanding how much is just for the agent and how much we need to build`.

Also probe feasibility as an open question, not a prescribed solution: `is it possible to run task in another terminal...?`, `can you access tailscale?`, `is that setup per-change or global?`

## Gate 2: Scope assessment — what's left against the target
Open the session by asking what REMAINS, not by jumping to execution. Anchor on a reference artifact (gap analysis, planning doc, ticket cycle) or a concrete target metric, then derive a sequenced ordering.
- `what betachat tickets are still remaining?`
- `how close are we to autonomous agents — what is our current gaps?`
- `based on planning/gap-analysis what task remain inside of platform`
- `in the best order id like to execute on tickets in a order that gets us to zero betachat tickets`

## Gate 3: Research → document → ticket (persist it, no memory leakage)
For comprehensive asks, run the explicit pipeline and persist artifacts so context isn't lost.
- `this is a really comprehensive ask so im looking for deep research and planning`
- `make a folder in the docs i want to truely vet through everything`
- Pipeline: `phase 1 research, phase 2 markdown, phase 3 ticket building` — `start from markdowns... then move them into linear so we dont have memory leakage`.
- Record config decisions into project memory: `make note of it in claude.md`. Propagate shared-doc changes to every node: `ssh-machines.md will need to be updated`.

## Gate 4: Decompose into developer-sized units
Map the scope by which pieces belong to which subsystem/app, then break coarse work into smaller independently-testable chunks with a spec per unit.
- `i need to work out which parts belong to which apps`
- `SEN-209 and SEN-204 both look they should be broken down into smaller ticket`
- Prefer incremental per-item integration: `incremental — merge each as it greens`, not one big batch merge.
- When a unit is sizable/ambiguous or context-heavy, route it through **scope-question-and-delegate** to ask the decisive questions first, then delegate with minimal context.

## Gate 5: Sequence prerequisites; gate downstream on completion
Order dependent work explicitly — clear blockers first, sequence env setup, gate releases behind upstream conditions.
- `unblock first`
- `lets do this first then start them up`
- `once the database migration and update clear, ready to ship tagged version updates to all repos`
- `first thing first i need to harden what we have now`

## Gate 6: Bake quality bars + phase gates into the go-ahead
Embed non-negotiable constraints directly in the kickoff so they need not be re-stated. Mark's standing bar:
- **90%+ unit test coverage**, **strict TypeScript**, **linters with zero errors**
- **Files under ~350 lines** (especially React)
- **SRP / DRY**, **swagger/OpenAPI updated**
- **Stop-gates that validate each stage before advancing**

`each stage is back by stop gates to validate and test, we should have linters built in with no errors. unit test backed 90% or better, strict typescript`. Often ask for an assessment of current violations before refactoring.

Then phase-gate the work with human checkpoints — advance only on command, dry-run before anything destructive: `i need gates between each phase`, `I want to test each part one at a time`, `yes dry run`, `ship v1.6.2 once builds pass`.

## Gate 7: Subordinate the mechanism to the user-visible outcome
If the plan over-engineers, restate the actual goal and pick the cheaper path that achieves the visible result:
- `the api is not important what is important is that its present on the homepage`
- `it is mostly marketing lets just use the value we have as issues and keep it static`
- `could we kill the Lambda and just use it as our backend?`
Prune scope when a simpler architecture becomes viable; cut optional features by reasoning about the product's stage (`4 wont be needed because this is a small application`).

## Gate 8: Define hard architectural boundaries up front
Specify the single boundary all cross-component interaction must route through, and bake authorization/permission invariants into the spec as hard constraints:
- `the only thing unified should be that API layer... should not interact with beta chat directly`
- `I can only link a conversation to a case if the people have permission to view the case`
- Designate one source of truth and phase out the rest: `the public page is our source of truth, redirect and phase out the quiz result page`.

## After the plan: hand off
Once the plan is agreed, either phase-gate it (Gate 6) OR grant uninterrupted autonomy if Mark trusts it and wants momentum (`come up with a plan... you will execute without breaks on your own`). See **steer-and-correct-the-agent** for how he hands off, and **fleet-dispatch-and-watch** if the work fans out across machines.

## Red flags
| Anti-pattern | Mark's correction |
|---|---|
| Jumping to code before research/inventory | `first just examining the foundation`; `do we already have a harness?` |
| Hand-rolling when a system exists | `is there a system we can use?` |
| Starting without scoping the gap to a target | `what tickets are still remaining?` |
| Research that isn't persisted | `move them into linear so we dont have memory leakage` |
| Omitting quality bars from the kickoff | `unit test backed 90%... strict typescript... linters with no errors` |
| Over-engineering the plumbing | `the api is not important — it just needs to be present on the homepage` |
| One big batch merge at the end | `incremental — merge each as it greens` |
