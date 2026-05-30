---
name: prove-it-live-before-done
description: Use whenever an agent (or you) is about to claim work is done/fixed/shipped/passing, or when Mark says 'ready?', 'done?', 'did it work?', 'still failing', 'is the live URL responding?', 'check the deploy status', or wants to confirm a fix before pushing. Treat every completion claim, green CI, and passing test as UNPROVEN until the real artifact is exercised end-to-end — drive the actual running app at its real URL/UI/API, confirm the deployed revision is actually live, verify the mutating side-effect (email/queue/DB row) truly fired, gate every forward step on an explicit green signal, audit coverage across the whole surface, and reconcile against the system of record. Then name the specific residual defect with expected-vs-actual.
---

# Prove It Live Before Done

Mark's strongest reflex: he refuses to accept 'done/fixed/shipped/tests pass' on your word. He drives the real product himself and names what's still broken (`that worked but now the skills path dont reflect the calls properly`; `got the confirmation but no email sent`). Adopt his skepticism as the default — your job is to DISPROVE the completion claim, not announce it.

## Core rule: a claim is not proof. Exercise the real thing.
A UI confirmation toast is NOT proof the email sent. A green workflow is NOT proof the new revision is live. A passing unit test is NOT proof the feature works through its real path. Map each claim to the right proxy and check THAT:

| Claim being made | What you must actually do to prove it |
|---|---|
| "The fix works" | Re-run the real user action / construct a deliberate failing case; confirm the exact prior symptom is gone |
| "Feature is built" | Drive it at its real URL/UI/API as a user would — `start the application in the background` and use it |
| "Email/notification sent" | Check the actual inbox/provider, not the success toast — `got the confirmation but no email sent: artsmc88@gmail.com` |
| "Uploaded / queued / saved" | Inspect the queue depth / the DB row — `i uploaded 3 and they are all sitting in the queue` |
| "Deployed / shipped" | Hit the live URL AND confirm the new ECS taskDef revision / Render dashboard shows the running version by exact version number |
| "Migration done" | Confirm the migration actually RAN, not just that code changed — `run the migration` |
| "Tests pass / CI green" | Confirm the gate ran on a machine that actually has node_modules; check coverage hits the bar |
| "PR is done" | Read the actual diff, not the PR summary — `is the code inside the PR...`; check it hasn't drifted from main |

## Step 1: Gate every forward step on a green, machine-checkable signal
Never merge, deploy, scale, or advance a phase on red or pending. Always specify the branch for both outcomes — Mark does this reflexively:
- `merge it if green` / `merge the green ones`
- `Gate PASS → mark done, write next brief. Gate FAIL → write fixup, dispatch on desktop main, schedule wake`
- `If all 5 checks are green: stop the loop, then gh pr merge. Else resolve and re-run.`

If the signal is pending, do not proceed — poll (see **fleet-dispatch-and-watch**) or report and wait.

## Step 2: Require a multi-signal definition of done
One signal is never enough. Mark defines done by the end-to-end outcome:
- Report file exists **AND** commits present **AND** gate passes on a real machine
- Agent says DONE **AND** its branch is on origin (`when sen-259 shows DONE and its branch is on origin`)
- Code changed **AND** migration actually run
- Feature exists **AND** it exercises the intended mechanism (the right path, not a stub)
- Coverage meets the numeric bar (`we need at least 90%`)

## Step 3: Confirm the deploy is actually LIVE
A release is incomplete until the deployed artifact is confirmed in production — not when the workflow says success.
- `https://chat.beta.sentienthome.ai/ live?` — hit it.
- `check the v1.5.11 deploy status` — by exact version, across iterations.
- Confirm the new ECS taskDef revision is running / the Render dashboard shows the version.
- If passive polling stalls, switch to the authoritative dashboard (`check the render dashboard`).

## Step 4: Confirm a mutating command actually took effect
After any script/command/correction that changes external state, do not assume success. `did it work?` — paste the actual execution output and verify it. Cross-check deployment integrity against an external source (the commit URL) to confirm the specific changes shipped. `did we confirm the change when we ran the script?`

## Step 5: Confirm the chain actually advanced
A completion signal does not imply the next stage fired. Probe it: `does that mean the deploy started?`, `have we pushed a tagged version of the code?`, `is that pino work already merged in?`. When multiple actors did work, demand explicit confirmation: `i had another runner doing work — can you absolutely confirm nothing is live?`

## Step 6: Audit coverage across the WHOLE surface
Don't accept that a concern exists 'somewhere'. Sweep it:
- `do we have pino log coverage across the app?` — all apps, all containers.
- `i need that 100% resolved across apps before moving to the next thing`
- After fixing one layer, check downstream holds separate state: `luke is unable to login to the monorepo — can we confirm they are also the same in RDS?`
- Check adjacent/parallel categories that may have been missed.

## Step 7: Reconcile against the system of record
Distrust secondary tracking state. Before accepting a 'completed' list, cross-check against git / Linear / the real machines:
- `are they accounted for in linear?` / `did we track all the platform tickets?`
- Backfill tickets from actual commits; enumerate exactly which commits/features are missing rather than asking open-endedly: `its missing a lot of commits — the updated message ui, the conversation api logic... its all missing`
- `is the code on desktop wsl?` — confirm committed code landed on the specific machine.
- Cross-check the rendered UI against the source artifact: `check the html folder, you are not properly reflecting the conversation ui`.

## Step 8: Report the residual defect in expected-vs-actual terms
Close with what's still wrong, stated as `this is my expectation / this is what im getting` — never 'works for me'. If it's truly clean, say which real action you ran and what you observed.

## Red flags
| Anti-pattern | Why it fails Mark |
|---|---|
| Declaring done after making the change | He'll disprove it by hand — `still failing to fetch` |
| Trusting a UI confirmation as proof of the side-effect | `got the confirmation but no email sent` |
| Trusting a green workflow as proof of live deploy | He checks the ECS revision / live URL |
| Advancing on pending/red CI | He gates strictly on green with a fallback branch |
| One signal = done | He requires report AND commits AND gate, or DONE AND branch-on-origin |
| Using mock/placeholder data to fake a result | `no need for mock data lets work with what we have` |
| Trusting the ticket tracker over git/real machines | He reconciles against the source of record |
