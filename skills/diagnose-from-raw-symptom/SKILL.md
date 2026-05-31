---
name: diagnose-from-raw-symptom
description: Use when Mark reports a bug by pasting a raw artifact with little or no prose — a stack trace, an HTTP request/response trace (URL + method + status like 500/403/404/502), a console/React/Prisma error, a ChunkLoadError, a shell error, or a screenshot of a visual defect — or when he says things like 'still failing', 'clicking X does nothing', 'no inline editor on the rendered page', 'do we have local postgres/pgvector?', or 'identify the true error'. This is the front-to-back debugging procedure — extract the trigger and reproduction from terse input, probe whether the underlying plumbing even exists, localize by contrasting known-good vs broken, and drive to a durable root cause rather than a workaround. Reach for this BEFORE proposing any fix.
---

# Diagnose From the Raw Symptom

Mark debugs by dropping the literal evidence and expecting the symptom itself to drive diagnosis. He reasons from a mental model of correctness, distrusts easy explanations, and wants the root cause fixed — not papered over. Run this procedure top to bottom; do not jump to a fix.

## 0. Read the literal artifact — do not paraphrase it away
Mark pastes the exact thing: `Invalid prisma.profiles.create() invocation: User was denied access on the database`, `Status Code 403 Forbidden`, `ChunkLoadError: Failed to load chunk`, or a screenshot with a terse caption (`message position weird on chat`). The artifact is the spec. Extract from it, verbatim:
- The exact status code / error class / error string
- The URL, method, and which layer emitted it
- The on-screen symptom in his words (missing element, stuck loading, wrong count, weird position)

Never soften or re-interpret the symptom. If he gave a screenshot + URL, the defect is visual and lives at that URL.

## 1. Pin the trigger and a concrete reproduction
Narrow the search space before touching anything. Establish:
- **Exact action that triggers it** — `i get the 502 when i submit the email address in the form of the login`
- **A real recent instance** — the literal running URL, a specific account, a real example. Anchor to `http://localhost:3000/...`, not a hypothetical.
- **A volunteered hypothesis** linking a preceding event — `i left the app sitting overnight and had a token issue now it runs too many request`. Take these seriously; he often already knows.

If the trigger is ambiguous, ask ONE blunt question to pin it. Don't fix on a guess.

## 2. Probe the plumbing FIRST (before guessing at a fix)
Mark's signature move: reframe a surface symptom as a yes/no interrogation of foundational wiring. Ask and ACTUALLY CHECK, don't assume:
- `clicking the left navigation does nothing — are the pages built and connected?`
- `do we have local postgres and pgvector?`
- `still seeing failed to fetch — do we have proper logging for you to watch (pino/winston)?`
- `do we have COMPOSIO self-hosted?`

**Decision rule:** if a UI element "does nothing" or a call fails to fetch, verify the API/DB/service behind it EXISTS and is reachable before debugging the front end. A button wired to a route that was never built is not a front-end bug.

## 3. Localize by contrast
Isolate the fault by comparing a known-good reference against the broken one. Find what differs:
- **Deployed vs local** — `my local chat.beta has a button to the login page, this url does not`
- **One working surface vs the failing one** — `platform login is fine so lets get this one in order on chat`
- **Parent vs child scope** — `its highlighting the parent but not the child`
- **Account that succeeds vs one that fails** — `why is the otp reject within seconds of being created for sahil@... but not mark@...`

The difference between the two cases is the bug's address.

## 4. Walk the error chain forward — treat each new error as progress
When a fix changes the symptom, that is forward motion, not failure. `502 → 404 → 403 → business-logic error` means you are peeling layers correctly. Feed each new code back as evidence about which layer now works. An ambiguous non-2xx (`Cannot link: 3 channel members cannot view this case`) often proves the proxy/route works and the failure moved inward.

## 5. Drive to ROOT CAUSE, reject the easy explanation
Mark pushes past symptoms and demands a durable fix:
- Reject default explanations using observed timing/domain reasoning: `cant be stale it happens right away — why is the otp rejected within seconds of being created?`
- Generalize repeated incidents to one systemic cause: `both incidents have the same root cause: neither backend runs DB migrations on deploy`
- Reason from architectural invariants when his mental model is contradicted: `but a user should always be found — why is a user not found in any case?`, `Users are all inside cognito... everyone is first a cognito user`. If your fix would violate a decision already agreed (`why is it hitting monorepo, we talked about this`), stop — that inconsistency IS the bug.
- Verify the full causal chain end-to-end, not just that the symptom moved.

## 6. Distrust misleading signals
If a monitoring/liveness signal is unreliable, name the failure mode and substitute a trustworthy proxy. Mark's rule: `log file empty (tee+claude TUI quirk — ignore the log, rely on git state)`. Don't trust a signal you've seen lie.

## Red flags — you are doing it wrong if:
| Anti-pattern | Mark's correction |
|---|---|
| Proposing a fix before checking the service/DB exists | `are the pages built and connected?` |
| Paraphrasing the error instead of reading it literally | He re-pastes the exact string |
| Accepting the easy/stale explanation | `cant be stale it happens right away` |
| Treating a new error code as a regression | It's the next layer — walk the chain forward |
| Fixing the symptom with a workaround | He wants the durable root-cause fix |
| Guessing without a reproduction | `for clarity i get the 502 when i submit the email` |

Hand off to **prove-it-live-before-done** once you believe it's fixed — Mark will not accept a fix on your word.
