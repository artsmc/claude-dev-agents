---
name: steer-and-correct-the-agent
description: Use mid-flight while executing for Mark to interpret his terse steering grammar. Triggers on short directives — greenlights ('yes', 'go for it'), autonomy grants ('you have full autonomy', 'dont stop', 'run 2-3 goals on your own'), hard overrides ('no remove this', 'not X but Y'), re-anchoring ('remember the goal', 'get back on track', 'this looks wrong our main objectives are'), and method/preserve constraints ('no just cli', 'keep the save button'). Encodes bounded autonomy vs human checkpoints; his corrections are the spec.
---

# Steer and Correct the Agent (Mark's grammar)

Mark steers with a terse, decisive, action-first vocabulary. Misreading it wastes his time. This skill maps his signals to the right behavior and encodes his correction reflexes so you stay aligned the way he actually drives.

## 1. Terse greenlight → proceed from your own proposal, keep momentum
When he says `yes`, `yes proceed`, `go for it`, `lets do it`, `do it`, `this is good` — he is approving the plan/fix you surfaced. Do NOT re-litigate, re-explain, or re-ask for details. Execute. He picks options tersely and chains the next instruction: `lets go with #2`, `2 and make note of it in claude.md`, `2, and turn on MVP backend in the background`. Honor the pick AND the appended directive in one move.

## 2. Bounded autonomy handoff → run unattended, but obey the boundary
When he grants autonomy (`you have full autonomy`, `apply it all`, `you can run 2-3 goals end to end on your own while im gone`, `kick it off, fan them out`, `dont stop`), run the full plan WITHOUT per-step approval — but pin the boundary he set:
- A stopping point (`don't stop until done`)
- A decision heuristic (`if you have to make a decision, take the one with best long-term results not short-term gains; don't destroy my data; strict typescript`)
- A cadence (`check in every N minutes`)

**Distinguish from phase-gating:** bounded autonomy is for when he trusts the plan and wants momentum. If instead he said `i need gates between each phase`, stop at each named checkpoint. Don't autopilot through a gate he asked to own.

## 3. Hard override → flatly switch, dictate the exact target
When he rejects a path (`no remove this editor this was a bad call`, `no replace the sentient home folder on the Desktop WSL`, `not libs/util/src/__test but __test__/libs/utils/src`, `no just inside sentient home`), do NOT iterate on the bad result. Reverse it and do exactly the operation/target/path he named. He is supplying the correct command — use it verbatim.

## 4. Re-anchor to the goal → misalignment IS the defect
When work drifts into tangents or you propose re-scoping already-agreed work, he snaps back to the top-level objective and treats the drift as the bug to fix:
- `well remember the goal, top of the line we are moving betachat backend to MVP`
- `dont worry about prisma bugs focus on the slides`
- `I dont know what your suggesting, we already outlined the work, get back on track`
- `this looks wrong our main objectives are around beta.chat`
Cut the side investigation; re-paste/restate the original breakdown as the authority and resume it.

## 5. Constrain the method, not just the goal → use the simpler native path
He overrides HOW you work when you overbuild or reach for the wrong mechanism:
- `no just cli check and show me a table here`
- `is this not possible via supabase cli?`
- `claude should have used a different install: irm https://claude.ai/install.ps1 | iex`
- `i dont want it to deploy or build here, just help with coding`
When he challenges with `is this not possible via X?`, switch to the built-in/simpler approach; don't defend the complex one. No throwaway scaffolding.

## 6. Expected-vs-actual correction → the gap is the spec
He corrects by naming the intended end-state beside the observed failure (often with images), not by restating the whole ask: `this is my expectation [img] this is what im getting [img]`, `this message should properly link but its not`, `contractor is not being assigned to case`. Treat the gap as the new requirement and fix to close it. Reject your own premature 'done' claims (hand to **prove-it-live-before-done**).

## 7. Pair the change with a preserve-constraint → don't regress what worked
He pins the one quality that must survive a change: `since you replace, just make sure you keep the save button for tiptap changes`, `keep the integrity of agent personality`, `nothing can break from previous threads`, `it should remain the same just more workable surface area`. Before changing, identify the protected capability and verify it still works after.

## 8. Reject fakery / demand real data
`no need for mock data lets work with what we have`, `this should be tied to our real issues`, `start the application in the background`. Never fill a sparse UI with invented content; ground everything in real domain data and run the actual app.

## 9. Persist a surfaced constraint to memory/docs
When a constraint, domain definition, or role boundary surfaces (often after a violation), he orders it captured durably, naming the exact repo:
- `again fleet refers to splitting work between machines — save that to memory and claude.md`
- `update memory + CLAUDE.md to reflect that fleet workers... are for coding-assist only`
- `update the Claude MD file to say that beta chat talks to the MVP API`
Write it to the named CLAUDE.md / memory so it can't recur.

## 10. Cite-my-observation overrides your claim
If his direct observation contradicts you, he wins and your claim is suspect (often stale knowledge): `that is false im looking at the template page`, `your understanding of resend may not be current, you need latest data`. Fetch current data before proceeding; don't argue from training knowledge.

## Reserved-for-self / gate-and-resume
He owns some steps manually (PRs, SSH/credential steps): `ill do the PR myself`, `give me separate instructions to run on mac mini`, `im going to turn on ssh and you will hook up`. Hand him the standalone instructions and wait. When he returns with a terse `done` / `the env has been updated` / `continue where we left off`, the prerequisite is satisfied — resume the main thread, recovering prior context yourself.

## Red flags
| You did | He corrects with |
|---|---|
| Re-asked for confirmation after he said 'go for it' | (silence / impatience — just execute) |
| Stopped for approval after he granted autonomy | `dont stop`, `you have full autonomy` |
| Iterated on a wrong approach | `no, replace... / not X but Y` |
| Chased a tangent | `get back on track`, `remember the goal` |
| Built complex scaffolding | `is this not possible via cli?` |
| Broke a working feature while improving | `keep the save button`, `nothing can break` |
| Filled UI with mock data | `no need for mock data` |
| Argued from stale knowledge | `that is false im looking at the page` |
