---
name: reference-as-executable-spec
description: Use when Mark frames a feature by pointing at a concrete reference instead of describing behavior from scratch — when he names a live product as the target ('an inline editor like editor.js', 'a code editor like monaco-editor dark theme', 'much like openclaw.ai'), points at an internal subsystem as the literal spec to replicate ('the OTP from sentient-monorepo is the pattern we should match', 'use sentient-monorepo as the api source of truth'), or anchors a requirement on an external library as the structural model ('setups similar to CASL', 'building this same CASL boilerplate'). Whenever he says 'build it like THAT', 'same as X', or 'mimic/replicate X', treat the named reference as the executable spec — go observe it, extract its real behavior, and let THAT define correct rather than inventing requirements.
---

# Reference As Executable Spec

When Mark wants a feature, he usually doesn't enumerate requirements — he points at something that already exists and says build it like THAT. The named reference (a live URL, a product, an internal subsystem, a library's boilerplate) is not a vague vibe; it is the spec, and its observable behavior is the acceptance bar. Your job is to go look at the actual thing he pointed at, extract the concrete behavior, and treat any deviation from it as a defect — not to substitute your own interpretation of what he "probably" wants.

## 1. Catch the reference and treat it as the spec, not a hint
The trigger is an analogy doing the work of a requirements list: `like a https://microsoft.github.io/monaco-editor/ dark theme`, `an inline editor on the page like https://editorjs.io/ or quil`, `the idea much like https://openclaw.ai/ or https://hermes-agent.nousresearch.com/`, `are there setups similar to casl?`. When Mark frames a feature by what it should resemble, do not paraphrase the analogy into your own abstract feature description and then build to that. The reference is the source of truth for "correct." Build to the reference, not to your summary of it.

## 2. Go observe the actual reference before designing anything
The reference only constrains you if you've actually seen it. For a live URL or product, go look — open it, read its docs, identify the specific capability he's pointing at (Monaco's dark-theme raw-HTML/CSS editing surface; Editor.js's *inline*, on-page block editing; OpenClaw/Hermes-style background-running agents). For an internal subsystem named as the spec (`the OTP from sentient-monorepo`, `use sentient-monorepo as its api source of truth`), read that subsystem's real code/API — don't reconstruct the pattern from memory. The point of naming a reference is to skip re-deriving a design that already exists somewhere; honor that by extracting it from the real artifact.

## 3. Pin down WHICH property of the reference is the target
A reference carries many traits; Mark wants a specific one. Disambiguate before building:
- `like a monaco-editor dark theme` → the *raw HTML/CSS editing surface* + its theme, so he can `edit and save the raw html css` and `see the changes quicker` — not Monaco's entire IDE.
- `inline editor like editorjs.io or quil` → *on-page, inline* editing, the contrast being a separate editing screen.
- `much like openclaw or hermes-agent` → *agents that run in the background*, not those products' whole UX.
- `setups similar to casl` → CASL's *RBAC/permissions structure and boilerplate*, the structural model for multi-tenant authorization.

When two references are offered as alternatives (`editorjs.io or quil`, `openclaw or hermes-agent`), they triangulate the shared property — extract what they have in common, that's the requirement.

## 4. For an internal subsystem, replicate the existing pattern exactly — it is the source of truth
When Mark names an internal system as the spec (`the OTP from sentient-monorepo is the pattern we should match`, `the monorepo cognito pool is the source of truth for otp`, `use sentient-monorepo as its api source of truth for <feature>`), this is a designation of authority, not a loose suggestion. Match that subsystem's contract — its API shape, its auth flow, its data model — rather than designing a parallel one. Two consequences:
- If your design would diverge from the named source of truth, that divergence is the bug. Reconcile to the reference (this is the same invariant that drives **diagnose-from-raw-symptom**: `why is it hitting monorepo, we talked about this`).
- Don't introduce a second source of truth. If the monorepo cognito pool *is* the OTP authority, your feature reads from it, it doesn't stand up its own.

## 5. Anchor structure on the named library/framework
When the reference is a library (`are there setups similar to casl?`, `building this same structure... CASL boilerplate`), Mark is choosing the structural model, not just asking a question. Confirm the library actually fits the use (multi-tenant RBAC), then scaffold the feature in that library's idiom — its boilerplate, its ability/policy shape — instead of hand-rolling an equivalent. The library's conventions become the spec for how the code is organized.

## 6. Let the reference define the acceptance bar
Once the reference is established, "done" means "behaves like the reference on the property that mattered." When you verify (hand to **prove-it-live-before-done**), check against the reference's observable behavior: does the on-page editor actually edit inline like Editor.js; do agents actually run in the background like OpenClaw; does the OTP flow actually match the monorepo's. State residual gaps as reference-vs-actual: "Editor.js edits inline on the page; ours still opens a separate panel."

## 7. Don't over-clone — scope to the property Mark named
A reference is an anchor, not a mandate to reproduce the entire product. He wants Monaco's editing surface, not to rebuild VS Code; OpenClaw's background-agent idea, not its business. Pull the specific capability and leave the rest. If reproducing the whole reference would balloon scope, restate the one property that matters and build only that (the same outcome-over-mechanism instinct in **research-gated-build-plan** Gate 7).

## Distinction from research-gated-build-plan
That skill scopes the gap against a target and decides whether/how to build. This skill is upstream of the requirement itself: it's about how Mark *articulates* what to build — by naming a concrete external product/URL or internal subsystem as the literal spec. The discriminator: a real named anchor (`monaco`, `editorjs`, `sentient-monorepo`, `casl`). A generic planning artifact being called a "source of truth" (a gap-analysis, a matrix, a ticket cycle) is *not* this skill — that's research-gated-build-plan.

## Red flags
| Anti-pattern | Mark's correction |
|---|---|
| Paraphrasing the analogy into your own feature description and building to that | He named `monaco`/`editorjs` for a reason — build to the reference, not your summary |
| Designing without actually looking at the named reference | `like a https://microsoft.github.io/monaco-editor/ dark theme` — go open it |
| Cloning the entire product instead of the one property he meant | He wanted the inline editing, not the whole IDE |
| Standing up a parallel system instead of matching the named source of truth | `the OTP from sentient-monorepo is the pattern we should match` |
| Introducing a second source of truth | `the monorepo cognito pool is the source of truth for otp` |
| Hand-rolling auth structure when he named a library | `are there setups similar to casl?` — use CASL's idiom |
| Calling it done without checking it behaves like the reference | Verify reference-vs-actual, not "works for me" |
