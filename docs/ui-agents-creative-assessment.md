# UI Agents' Creative Abilities — Assessment & Improvement Plan

**Date:** 2026-05-30
**Author:** Claude Code (examination/recommendation only — no agent files were modified)
**Scope:** `ui-developer`, `frontend-developer`, `accessibility-specialist`, the installed `frontend-design` skill, and a runnable creativity-eval plan built on `skill-creator`.

**Files referenced:**
- `/home/mark/.claude/agents/ui-developer.md`
- `/home/mark/.claude/agents/frontend-developer.md`
- `/home/mark/.claude/agents/accessibility-specialist.md`
- `/home/mark/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
- `/home/mark/.claude/skills/skill-creator/` (agents/comparator.md, agents/grader.md, agents/analyzer.md, scripts/aggregate_benchmark.py, eval-viewer/generate_review.py)

---

## 1. Executive Summary

### Core finding

The fleet's UI agents are **strong, provable implementers but weak creative originators.** `ui-developer` — the only agent that touches the visible surface — is built end-to-end around *discipline and verification* (Gherkin-first plan → implement → Playwright proof → confidence gate → self-verification checklist). That spine guarantees the UI *behaves* correctly. It says **nothing** about whether the UI *looks* good. The agent:

- has **zero aesthetic point-of-view** — its only styling guidance is "consistent with the project's design system" (`ui-developer.md` line 69, checklist line 93), and per Mark's MEMORY **that design system does not exist**, so the instruction is a no-op and the model defaults to its training-distribution average: Inter/Tailwind defaults, evenly-distributed palettes, predictable card grids — the exact "AI slop" the installed `frontend-design` skill exists to prevent;
- **never references the `frontend-design` skill**, which is the single most relevant capability in the whole system and is sitting installed and unused;
- has a starved toolset — `tools: [Read, Grep, Glob, Write, Edit]` (line 5). It has **no eyes** (no screenshot/Playwright-visual MCP) and **no inspiration channel** (no WebSearch/WebFetch/Context7/Figma). Ironically `frontend-developer.md`, which by its own description does **not** do visual work, carries a whole "MCP Tools for Latest Documentation" section (lines 25–58) the visual agent lacks — though note this is a *prompt-body* asymmetry: both agents share the identical `tools: [Read, Grep, Glob, Write, Edit]` frontmatter, and even `frontend-developer`'s WebSearch/WebFetch/MCP references aren't granted in its own frontmatter, so porting the block into `ui-developer` must also add those tools to frontmatter (Rec 2 does this);
- **verifies behavior but never looks at pixels** — a green Playwright run proves a dropdown opens; it proves nothing about hierarchy, contrast, or distinctiveness;
- caps interaction at "basic user interactions (e.g., dropdowns, modals)" (description line 3) — no motion, micro-interaction, or page-load orchestration layer at all.

Net: a competent, behavior-correct, on-the-rails implementer that will reliably ship generic UI. The good news is the *plumbing for taste already exists* — the doc-hub read protocol (lines 14–19) is a ready intake for a design system; it is simply being fed nothing.

### Top 3 recommendations

1. **Wire in the already-installed `frontend-design` skill + add a "Phase 0: Aesthetic Direction" step before Gherkin.** This is the highest-leverage change. It forces a committed, named aesthetic direction (and an anti-AI-slop guardrail) *before* the agent inherits a nonexistent design system and free-generates generic output. It requires adding `Skill` to the agent's `tools` array (currently absent) and naming the exact skill id `frontend-design:frontend-design` in the prompt, because subagents do not auto-surface skills. Source: Anthropic's own canonical anti-slop guidance the skill is derived from ([Claude Cookbook — Frontend Aesthetics](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics); [Anthropic blog — Improving frontend design through skills](https://claude.com/blog/improving-frontend-design-through-skills)).

2. **Give the visual agent eyes and inspiration channels — port `frontend-developer`'s MCP pattern into `ui-developer`, with an even richer version.** Add `WebSearch`, `WebFetch`, `chrome-devtools` (screenshot/resize/lighthouse), and reference `Context7` (Tailwind v4, Radix, shadcn/ui, Motion) and `Figma` MCP. Then add a **Visual Self-Critique loop** that parallels the Playwright loop: render → screenshot at 390/768/1440 → critique craft → fix. This converts behavior-only verification into behavior-plus-craft verification ([OneRedOak design-review workflow](https://github.com/OneRedOak/claude-code-workflows/tree/main/design-review)).

3. **Adopt a dual taste model: general taste via the skill, brand truth via a per-project `DESIGN.md`.** Make `ui-developer` author and persist a `DESIGN.md` (token + philosophy) on first UI task when none exists, read it every task alongside the doc-hub files, and treat it as overriding the skill on any token it specifies. This makes taste *durable project state* instead of per-task improvisation ([BetterStack — DESIGN.md for AI](https://betterstack.com/community/guides/ai/design-md-ai/); [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/blob/main/README.md)).

---

## 2. Per-Agent Findings

### 2.1 `ui-developer` — the designated visual agent (the main subject)

**Role.** The team's visual-implementation specialist: writes TSX, applies Tailwind/CSS/SCSS, builds responsive layouts and basic interactions. Its identity is built around discipline and verification, not origination — a Gherkin-first plan, a Playwright proof, a doc-hub read protocol, a confidence gate, a self-verification checklist. It assumes a design already exists and "translate[s] static designs and user flow documents into interactive components" (line 70). It is effectively a frontend QA/implementer that happens to write components.

**Creative strengths (real assets to build on):**
- **Execution rigor as a foundation.** Gherkin → implement → Playwright proof means whatever it builds is functional and behavior-verified. That is the right place to *layer craft on top of* — the loop just needs a craft analogue.
- **Accessibility + responsiveness already in the checklist** (lines 94, 98) — keyboard nav and mobile/tablet/desktop breakpoints are genuine craft dimensions most generic agents skip.
- **Doc-hub intake plumbing exists** (lines 14–19). If tokens / a `design.md` / brand guidance existed in the hub, the agent already ingests it every task. The intake for taste is wired; it is fed nothing.
- **Confidence protocol** (lines 75–82) gives it a natural place to STOP and ask when a design direction is ambiguous, instead of silently inventing generic defaults.

**Creative gaps:**
- **No aesthetic point-of-view / taste rubric.** Nothing on typography pairing, color/contrast hierarchy, spacing rhythm, visual density, depth/shadow, or motion language. "Consistent with the project's design system" is the *only* styling guidance — and that system does not exist.
- **No anti-generic guardrail.** No instruction to avoid the cliches the `frontend-design` skill bans (Inter/Roboto/Arial/system fonts, purple-gradient-on-white, cookie-cutter layouts).
- **No reference-driven design step.** It never gathers references, competitor screenshots, or a named aesthetic before building. It treats design as an input handed to it, never as something it can research or originate.
- **Zero creative tooling.** `[Read, Grep, Glob, Write, Edit]` — no inspiration channel, no docs channel, no eyes on its own pixels.
- **Never references `frontend-design`.** The most relevant capability in the system is invisible to this agent.
- **No motion/micro-interaction layer.** "Basic interactions" is the ceiling.
- **No design-token authorship.** It consumes a (nonexistent) system but is never told to CREATE one, so output drifts token-by-token across components.
- **No visual self-critique loop.** Playwright proves Gherkin passes, never that the result looks good.
- **Gherkin-first framing structurally biases behavior over beauty** — the plan artifact has slots for click/type/assert but none for aesthetic direction, so craft is never planned, only behavior.

**Specific prompt-level improvements (concrete snippets to add):**

*(a) Add a Phase 0 before the Gherkin plan:*
```markdown
## 🎨 Phase 0: Aesthetic Direction (run BEFORE Gherkin)
Before specifying behavior, commit to a visual point-of-view.
1. If the project has a DESIGN.md / design tokens / brand guidance in the Documentation
   Hub, adopt it VERBATIM — it overrides everything below.
2. If none exists (common), invoke the frontend-design skill
   (Skill tool, skill id `frontend-design:frontend-design`) and complete its
   Design Thinking gate: Purpose / Tone / Constraints / Differentiation.
3. Name ONE conceptual direction (editorial, brutalist, refined-minimal,
   retro-futuristic, warm-organic...) and state it in your plan.
4. Define tokens: a display+body font PAIR (never Inter/Roboto/Arial/system),
   a dominant color + sharp accent (never timid greys or purple-on-white gradient),
   a spacing scale, radii, and an elevation/shadow language.
5. Gather 1–3 concrete references via WebSearch/WebFetch and extract WHAT makes
   them feel crafted. Treat the reference as an executable spec for the look.
State the chosen direction + token set as the first part of your plan, alongside the Gherkin.
```

*(b) Grant creative/inspection tools (frontmatter + body):*
```yaml
tools: [Read, Grep, Glob, Write, Edit, Skill, WebSearch, WebFetch,
        mcp__chrome-devtools__navigate_page,
        mcp__chrome-devtools__take_screenshot,
        mcp__chrome-devtools__resize_page,
        mcp__chrome-devtools__lighthouse_audit]
```
```markdown
### Design Resources (use every task)
- frontend-design skill: load for the craft rubric and anti-generic guardrails.
- WebSearch/WebFetch: pull current references, type pairings, palette + motion patterns.
- Context7 (resolve-library-id + query-docs): fetch CURRENT docs for Tailwind v4,
  Motion/Framer-Motion, Radix, shadcn/ui before using their APIs.
- Figma MCP (get_design_context, get_variable_defs, get_screenshot): when a Figma URL
  or design system exists, read the REAL design and pull its tokens instead of guessing.
```

*(c) Add a Visual Self-Critique loop after Playwright passes:*
```markdown
### Visual Verification (in addition to Playwright)
After the behavior test passes:
1. Render and screenshot at mobile(390)/tablet(768)/desktop(1440) via chrome-devtools.
2. Critique against the rubric: typographic hierarchy & contrast, spacing rhythm,
   intentional color (dominant + accent), depth/shadow, alignment, ONE memorable detail.
3. Flag generic-AI tells (default fonts, timid palette, predictable card grid, no motion)
   and FIX them before continuing.
4. Not done until the result is behavior-correct AND visibly crafted — attach a
   screenshot to the task-update report.
```

*(d) Motion mandate replacing the "basic interactions" ceiling:*
```markdown
### Motion & Interaction Polish
- One well-orchestrated entrance (staggered reveal via animation-delay or Motion)
  beats scattered micro-interactions.
- Hover/focus/active with deliberate easing (no linear; custom cubic-bezier).
  ALWAYS respect prefers-reduced-motion.
- Tokenize: fast 150ms / normal 300ms / slow 500ms; ease-out on enter, ease-in on exit;
  secondary elements offset 50–100ms.
- Add at least one surprising-but-tasteful detail per view, appropriate to the aesthetic.
```

*(e) Reframe the design-system line from "consume" to "author + persist":*
```markdown
* Styling & Design Tokens: If the project has a DESIGN.md / token system, follow it
  exactly. If none exists, AUTHOR one on the first UI task — color/type/spacing/radius/
  shadow/motion as CSS variables or a Tailwind theme — persist it to the Documentation
  Hub (DESIGN.md), and reuse it across every component so the project stays cohesive.
```

*(f) Anti-generic self-verification additions:*
```markdown
- [ ] Committed to a named aesthetic direction (not generic defaults)
- [ ] Display+body font pair is distinctive (NOT Inter/Roboto/Arial/system/Space Grotesk)
- [ ] Color is intentional: dominant + sharp accent (NOT timid greys or purple-on-white)
- [ ] At least one memorable, context-specific detail present
- [ ] Intentional motion with prefers-reduced-motion respected
- [ ] Screenshots reviewed at 390/768/1440 and attached to the task-update report
```

*(g) Update the `description` frontmatter so the orchestrator routes real design work here:*
```yaml
description: "Designs AND implements distinctive, high-craft React UI. Originates an
  aesthetic direction and design tokens when none exist, builds polished TSX/Tailwind
  with intentional typography, color, motion and micro-interactions, then proves
  behavior with Playwright and reviews craft via screenshots. Use for any task involving
  what the user sees — from greenfield visual design to refining generic UI into
  something memorable."
```

### 2.2 `frontend-developer` — logic/data/state (non-visual by design)

**Role.** Application logic and data management: state (Zustand), data fetching (TanStack Query), routing, business logic. Explicitly *not* visual presentation. Not a creative agent, and shouldn't be.

**Strengths (the reusable infrastructure pattern):**
- It carries the **strongest, most portable pattern in the trio**: the "MCP Tools for Latest Documentation" + WebFetch/WebSearch section (lines 25–58) that compensates for knowledge cutoff. This is the exact muscle `ui-developer` lacks.
- Disciplined engineering rails (DRY/SRP/strict typing/file-size/lint gates, lines 84–91) and a documentation-update protocol.

**Creative gaps:** None that need fixing here — it should stay non-visual. The risk is *ownership leakage*: its "Styling & Design Systems" expertise line (line 120) implies it can do visual work, which muddies routing. Keep it logic-focused.

**Specific prompt-level improvement:** Do **not** add design origination here. Instead, (a) sharpen the boundary so layout-adjacent work that needs taste is handed to `ui-developer`, and (b) treat its MCP section as the **template to copy into `ui-developer`** (pointed at design libraries instead of data libraries):
```markdown
### Latest Docs & Design Resources  (PORT THIS BLOCK INTO ui-developer, RETARGETED)
Before implementing, fetch current docs — your knowledge cutoff means component-library
APIs may have evolved.
- Context7 (resolve-library-id → query-docs) or WebFetch/WebSearch for current APIs of:
  Tailwind v4, shadcn/ui, Radix UI, Framer Motion / Motion, React Aria.
- For Next.js UI concerns (next/font, next/image, Suspense streaming), use
  mcp__next-devtools__init then mcp__next-devtools__nextjs_docs.
- Verify current prop/API signatures BEFORE writing component code; never assume from memory.
```

### 2.3 `accessibility-specialist` — WCAG/a11y compliance (non-creative by design)

**Role.** WCAG 2.1 AA/AAA, screen-reader compatibility, keyboard nav, color contrast, ARIA, focus management, automated a11y testing. Deep, correct, and rightly non-creative.

**Strengths:** Thorough manual + automated checklists (axe, Lighthouse, Pa11y, jest-axe, cypress-axe), strong focus-management and ARIA patterns, severity triage. It owns the contrast/focus/reduced-motion knowledge the `frontend-design` skill explicitly **does not** cover (the skill is purely aesthetic and can actually *hurt* contrast and `prefers-reduced-motion` users with heavy grain/motion).

**Creative gap (a collaboration gap, not a taste gap):** Accessibility is currently **half-owned**. `ui-developer` mentions a single "keyboard accessibility" checklist line (line 94); `accessibility-specialist` owns the full depth but *separately*, with **no defined handoff**. During creative work, a11y falls through the cracks — and the more distinctive/animated the UI gets, the bigger the risk.

**Specific prompt-level improvement — define an explicit handoff and fold a11y into `ui-developer`'s existing Playwright loop:**
```markdown
(in ui-developer) Bake accessibility into your Gherkin: every `Then` step must include
focus, keyboard, and screen-reader-visible outcomes. Assert it in Playwright via
@axe-core/playwright. For full WCAG AA/AAA audits, screen-reader testing, or contrast
remediation beyond your build, hand off to the accessibility-specialist agent and cite
what you've already covered (axe-clean, focus order, reduced-motion fallback present).
```
This makes `ui-developer` cover the baseline inline (axe in Playwright) and escalate the deep audit, without duplicating the specialist's depth or dropping it.

---

## 3. THE KEY DECISION — `DESIGN.md` vs. Leveraging System Logic (the `frontend-design` skill)

This is the central architectural choice. The two options are **not mutually exclusive** — they operate at different altitudes and pull in opposite directions *by design*.

### Option A — `DESIGN.md` (project-specific ground truth)

A committed plain-Markdown design-system file at the repo root that any coding agent reads as context to keep generated UI on-brand. The community-converged structure is **two-part**: (1) **structured tokens** — colors (hex + usage role), typography (families/sizes/weights/line-height), spacing scale, component styles (radius/shadow/input), motion (durations + easing); (2) **natural-language philosophy** — overall aesthetic, usage guidelines, accessibility requirements, explicit Do's/Don'ts. VoltAgent's collection uses a 9-section format (Visual Theme & Atmosphere, Color Palette & Roles, Typography Rules, Component Stylings, Layout Principles, Depth & Elevation, Do's and Don'ts, Responsive Behavior, Agent Prompt Guide).

- **Why it beats the alternatives for *consistency*:** a JSON token file gives explicit rules but no "why/when"; a prompt gives philosophy but must be re-pasted every session. `DESIGN.md` gives **both, persistently**, and Markdown is the format LLMs parse best. Ready-made files reverse-engineered from real brands (Linear, Stripe, Vercel, Anthropic, 70+) exist to drop in.
- **It dovetails with the existing plumbing:** `ui-developer` already reads `systemArchitecture.md` / `keyPairResponsibility.md` / `glossary.md` / `techStack.md` every task (lines 14–19). A `DESIGN.md` slots right in as one more mandatory read, making taste *durable project state*.
- Sources: [BetterStack](https://betterstack.com/community/guides/ai/design-md-ai/); [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/blob/main/README.md); [v0 persistent Context/Knowledge field](https://medium.com/design-bootcamp/prompting-ai-like-a-designer-why-most-ai-generated-ui-designs-look-generic-945eccd35b7f).

### Option B — Leverage system logic (the installed `frontend-design` skill)

The official Anthropic skill is **already installed** at `/home/mark/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`. It is **general taste**: a pre-coding Design Thinking gate (Purpose/Tone/Constraints/Differentiation), guidance across four/five aesthetic axes (typography, color, motion, spatial composition, backgrounds), an explicit anti-AI-slop blocklist (no Inter/Roboto/Arial/system fonts, no purple-gradient-on-white, no Space-Grotesk convergence), a complexity-matching rule, and a **non-convergence mandate** (vary fonts/themes/flavor every generation so no two outputs look alike).

- **Why it's the cheapest high-leverage win:** it already exists, is purpose-built for distinctiveness, and is exactly the missing piece in `ui-developer`. It's derived from Anthropic's own canonical [`<frontend_aesthetics>` cookbook prompt](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics) and [blog](https://claude.com/blog/improving-frontend-design-through-skills) — skills are "prompts and contextual resources that activate on demand," keeping the context window lean.
- **Two blockers to wire it (from the skill study):** (1) `ui-developer`'s `tools` array has **no `Skill` tool** — invoke-mode silently fails until `Skill` is added; (2) **subagents don't auto-surface skills**, so the exact id `frontend-design:frontend-design` must be named in the prompt. Mitigation: also **inline a 6–8 line condensed fallback** ("## Aesthetic Standard (anti-AI-slop)") so the standard survives even when the Skill tool isn't reachable.

### The conflict — and why it makes BOTH necessary

These two **pull in opposite directions on purpose**: the skill *maximizes novel variation* and bans common fonts/palettes; a `DESIGN.md` *enforces consistency* with an established identity. On a real product with a fixed brand (say, Inter is the brand font, or a specific token palette is locked), blindly applying the skill will **fight the brand** and "creatively" override locked tokens. So you cannot pick one and call it done.

### RECOMMENDATION — **Do BOTH, with an explicit precedence rule**

Layer them at their natural altitudes and encode precedence so they never collide:

> **`DESIGN.md` WINS where it specifies.** If a project `DESIGN.md` / design system exists, it overrides the `frontend-design` skill on any token it pins (fonts, colors, spacing). Apply the skill only to fill the *unspecified* degrees of freedom (motion, composition, backgrounds, depth, micro-detail, page-load orchestration) and to raise polish. **If no `DESIGN.md` exists, use the skill's Design Thinking gate to establish the aesthetic direction and propose it AS the project's first `DESIGN.md`.**

Justification straight from the inputs:
- The skill study explicitly concludes "do (A) invoke + (B) inline fallback" and that the skill **complements, not replaces** a per-project `DESIGN.md` — "design.md WINS where it specifies."
- Mark's MEMORY confirms there is **no design system today**, so most projects start in the "no `DESIGN.md`" branch: the skill supplies the taste to *generate the first one*. After that, `DESIGN.md` keeps the project cohesive — directly fixing the "output drifts token-by-token" gap.
- The online research's "most applicable" list ranks "wire DESIGN.md as always-read context" and "invoke/inline the frontend-design skill" as the **two cheapest, highest-leverage changes** — they are complementary, not competing.
- Keep `accessibility-specialist`'s contrast/focus/reduced-motion checks active on top, because the skill is *purely aesthetic* and can degrade a11y if applied unchecked.

**One-paragraph version for the agent prompt:**
> Read `DESIGN.md` (if present) with the doc-hub files every task; it is binding brand truth and overrides the `frontend-design` skill on any token it specifies. Invoke `frontend-design:frontend-design` for general taste on the unspecified degrees of freedom and to raise polish. If no `DESIGN.md` exists, run the skill's Design Thinking gate, build the UI, and persist the resulting tokens + philosophy as the project's first `DESIGN.md`. Always keep the accessibility checks (contrast, focus, reduced-motion) regardless of aesthetic.

---

## 4. Leveraging Online Resources (MCP / WebSearch / Context7)

The visual agent is the *most starved* of visual resources yet renders the most visual output. The fix is to port `frontend-developer`'s proven in-repo pattern into `ui-developer` and make it richer.

**4.1 Port `frontend-developer`'s MCP/WebSearch muscle (retargeted to design).** `frontend-developer.md` lines 25–58 are a working template. Retarget from data libraries to design libraries (Tailwind v4, shadcn/ui, Radix, Framer Motion/Motion, React Aria) and add WebSearch/WebFetch for live references, type pairings, palette and motion inspiration. The agent that doesn't render UI shouldn't have a richer resource section than the one that does. (Snippet in §2.2.)

**4.2 Context7 for current design-system docs.** Use `resolve-library-id` → `query-docs` to fetch **current** APIs before writing component code, instead of guessing from a stale cutoff. Highest value for fast-moving libs: **Tailwind v4** (new config/utilities), **shadcn/ui**, **Radix UI** primitives, **Motion/Framer-Motion**. The Context7 MCP is already available in this environment.

**4.3 Figma MCP — the legitimate "design handed to me" path.** `ui-developer` currently *assumes* a design is handed to it but cannot actually consume one. `get_design_context`, `get_variable_defs`, `get_screenshot`, `search_design_system` let it read a real Figma design and pull **actual tokens** rather than inventing them. This is the proper source for a `DESIGN.md` when a Figma source of truth exists.

**4.4 chrome-devtools MCP — give the agent eyes.** `navigate_page`, `take_screenshot`, `resize_page`, `emulate`, `lighthouse_audit`, `performance_start_trace` are already available here. This turns behavior-only verification into **behavior + craft + a11y/perf** verification: screenshot at 390/768/1440, run a Lighthouse pass (a11y ≥ 90, perf ≥ 85), and self-critique. Model: [OneRedOak claude-code-workflows design-review](https://github.com/OneRedOak/claude-code-workflows/tree/main/design-review), which drives the **live** UI with the Playwright MCP across a 7-phase review and reports findings with a `[Blocker]/[High]/[Medium]/[Nit]` triage matrix plus screenshot evidence.

**4.5 next-devtools MCP.** The same `init` + `nextjs_docs` tools `frontend-developer` already uses, reusable in `ui-developer` for Next.js-specific UI (next/font, next/image, Suspense streaming UI).

**4.6 Motion tokens to put in `DESIGN.md`** (so "Tailwind consistent with the design system" actually carries craft): durations fast 150ms / normal 300ms / slow 500ms; **ease-out on enter, ease-in on exit**; springs (stiffness/damping/mass) for interactive feedback; **staggered** sequential reveals for hierarchy; always honor `prefers-reduced-motion`. Source: motion choreography, staggering, and enter/exit easing *principles* from [Microsoft Fluent 2 Motion](https://fluent2.microsoft.design/motion) — the literal 150/300/500ms + ease-out/in values are this report's recommended token set, not lifted from Fluent 2 — corroborated by Motion.dev/Mockplus and Anthropic's "one orchestrated staggered page-load > scattered micro-interactions."

**Additional grounded references for the taste rubric:**
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — taste as 3 tunable dials (DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY, baseline 8/6/4) with a brief→dial inference table, a "Design Read" one-liner step, an anti-default blocklist, and HARD pre-flight rules that fail the build (hero fits viewport, single-line nav, ≤1 eyebrow per 3 sections, no layout family repeated, WCAG-AA contrast, full loading/empty/error states).
- [rohitg00/awesome-claude-design](https://github.com/rohitg00/awesome-claude-design) — 9 aesthetic families as a "pick a lane" menu, remix recipes, and an anti-slop fingerprint table mapping each Claude default tic to a counter-rule.

---

## 5. The `skill-creator` Creativity-Eval Plan (concrete & runnable)

**Goal.** *Measure* the creative lift of the changes (skill + `DESIGN.md` + Phase 0 + visual loop) and *improve* iteratively, using `skill-creator`'s eval loop. Creativity is subjective, so the grader is a **blind 3-judge panel** (extends `agents/comparator.md` from one judge to three) plus a **thin objective floor** (`agents/grader.md`).

**Key adaptation — screenshots are mandatory.** The eval-viewer renders PNG/SVG inline but renders HTML as plain text. Every run must emit **both** the built `index.html` (code craft) **and** rendered screenshots at desktop **1440×900** and mobile **390×844** (visual craft). Screenshots are what make distinctiveness legible to a blind judge and to Mark in the viewer.

### 5.1 Test prompts (6 brand-rich, style-underspecified briefs)

Each brief is rich on **brand personality** but deliberately under-specified on style, so a generic output is *visibly wrong for that brand* (the genericness detector). Each says "make the call and own it."

1. **Cleave** — hero + primary CTA for a high-end Japanese kitchen-knife brand selling to professional chefs. Voice: precise, restrained, a little severe (mastery/patience, not buy-now urgency). *A centered indigo-gradient hero is visibly wrong for a severe artisanal brand.*
2. **Loophole** — pricing page for a playful no-code automation tool for solo founders/indie hackers. Three tiers (Free / Pro $19 / Team $49), monthly–annual toggle, fun and a bit irreverent. *Tests breaking the generic 3-column-card template while keeping tiers scannable: hierarchy vs distinctiveness in tension.*
3. **Tidewatch** — landing hero + how-it-works for a coastal-flooding early-warning service for town emergency managers. Mood: calm authority, trust under pressure (data-dense, never alarmist). 3-step explanation + one stat band. *Tests restraint on a serious civic product — confident and quiet, the opposite failure mode from Loophole.*
4. **Resonance** — product feature section for a boutique analog-synth plugin, 3 signature features, strong motion + texture. Include tasteful animation AND a `prefers-reduced-motion` fallback. *Explicitly invites motion so the motion/restraint dimensions get signal; tests bold-without-noisy + shipping the reduced-motion fallback.*
5. **Meridian** — single-screen onboarding/welcome for a calm personal-finance app for people anxious about money. Headline + reassuring subhead + email capture + a trust element. Safe, warm, unhurried. *Minimal surface area forces craft into micro-decisions (spacing rhythm, type pairing, single accent, palette warmth) where genericness hides.*
6. **Forge & Field** — hero + testimonial strip for a premium artisan leather-goods workshop. Heritage, hand-made, warm, tactile; should feel like a physical catalog, not a tech startup. One customer quote with attribution. *Editorial/print sensibility is the distinctive answer; the SaaS template is the generic failure.*

Every brief: single self-contained `index.html` (Tailwind CDN ok), responsive at 390/1440. (Guard against overfitting: every couple of iterations swap in 2–3 fresh held-out brands; if gains hold there, the improvement is real.)

### 5.2 Judging dimensions (1–5 each)

1. **Visual hierarchy** — clear focal point, deliberate type scale (≥3 distinct sizes), intentional whitespace/grouping, scannable structure, unambiguous CTA priority.
2. **Distinctiveness / non-genericness** *(primary signal)* — distance from the AI default (centered hero, indigo/violet gradient, 3 identical icon cards, generic sans, emoji bullets, perfect symmetry). HIGH = committed brand-specific choices; LOW = swap-the-logo-and-it's-any-startup.
3. **Motion & interaction** — purposeful motion that guides attention, executed smoothly, with a working `prefers-reduced-motion` fallback. On prompts that don't call for motion, judge *restraint* instead of presence.
4. **Restraint & polish** — craft discipline: consistent spacing rhythm, aligned grid, confident limited palette, finished states/focus rings/optical alignment.
5. **Brand fit & tone** — does it read as the right personality (severe artisan vs playful indie vs calm civic vs warm heritage)? A beautiful-but-tonally-wrong page scores low.
6. **Responsiveness & robustness** *(objective-leaning floor)* — holds at 390/768/1440, no horizontal scroll, no overflow/overlap, readable type, tap-friendly targets. Gates the beauty score so a stunning-but-broken page can't win.

### 5.3 How to run

Run from the `skill-creator` dir so `python -m scripts.aggregate_benchmark` resolves. Workspace follows `skill-creator` convention: `creative-eval-workspace/iteration-N/<eval-name>/<config>/run-{1..3}/outputs/`.

- **STEP 0 — Snapshot (only when comparing new prompt vs old):** `cp -r` the skill/`DESIGN.md` into `creative-eval-workspace/skill-snapshot` and point `old_agent` at it to measure the *prompt change*, not skill-vs-nothing.
- **STEP 1 — Spawn all runs in one turn.** For each of the 6 prompts spawn **both** configs: `with_agent` (subagent gets the UI-agent skill + `DESIGN.md` path) and `without_agent` (vanilla Claude, identical prompt, no skill). **3 runs per config** to expose creative variance (18 + 18 = 36 subagents). Identical instructions to every run: build one self-contained `index.html`, then render with the **same** headless tooling at 1440×900 and 390×844, saving `desktop.png` + `mobile.png` + `index.html` to the run's `outputs/`. Use chrome-devtools `take_screenshot` at a fixed viewport, or a tiny Playwright/puppeteer script loading the `file://` URL — same tooling/viewport for both configs.
- **STEP 2 — `eval_metadata.json` per eval** (`eval_id`, descriptive `eval_name` e.g. `cleave-knife-hero`, the prompt, the objective assertions). Capture each subagent's `total_tokens` + `duration_ms` into `timing.json` — a marginally-prettier page at 3× tokens/latency is a real tradeoff.
- **STEP 3 — Objective grade via `agents/grader.md`** producing `grading.json` (`text`, `passed`, `evidence`), as **scripts not eyeballing**:
  a) no horizontal scroll at 390 (`scrollWidth ≤ clientWidth` via headless eval);
  b) layout intact at 390/768/1440 (no element wider than viewport);
  c) `prefers-reduced-motion` block present in CSS (grep) on motion prompts;
  d) Lighthouse a11y ≥ 90 and perf ≥ 85 via chrome-devtools `lighthouse_audit`;
  e) ≥ 3 distinct font sizes in computed styles;
  f) palette is **not** the default indigo/system-blue tell (scan for `6366f1`, `4f46e5`, Tailwind `indigo-*` class names).
  These **gate** the panel — a page failing the floor can't win regardless of beauty.
- **STEP 4 — Blind 3-judge panel** (extends `agents/comparator.md`). Present the `with_agent` and baseline runs as **A and B with provenance stripped and A/B order randomized per judge per eval**. Spawn 3 independent judge subagents; each reads `comparator.md` + the 6 dimensions, views both screenshots (desktop + mobile), skims both `index.html`, scores 1–5 per dimension, and names a winner citing specific elements. **Majority vote** across 3 judges = eval winner. `with_agent`'s aggregate win-rate across the 6 evals = headline creativity metric. A tie-heavy/split panel means the prompt isn't yet producing a legible distinctive difference.
- **STEP 5 — Aggregate:** `python -m scripts.aggregate_benchmark creative-eval-workspace/iteration-N --skill-name ui-creative-agent` (put `with_agent` before baseline so the delta is signed intuitively). Produces `benchmark.json` / `benchmark.md` with pass-rate (objective floor), time, tokens, mean/stddev, delta. Then `agents/analyzer.md` flags non-discriminating assertions (floors both configs always pass — fine, they're floors), high-variance evals, and the token/latency cost of the creative lift.
- **STEP 6 — View (non-negotiable, before any rewrite):** run `/home/mark/.claude/skills/skill-creator/eval-viewer/generate_review.py` with `creative-eval-workspace/iteration-N`, `--skill-name ui-creative-agent`, `--benchmark .../benchmark.json`, and from iteration 2 on `--previous-workspace creative-eval-workspace/iteration-(N-1)`. The Outputs tab renders `desktop.png`/`mobile.png` inline per eval so **Mark eyeballs craft and leaves per-eval feedback**; the Benchmark tab shows panel win-rate, objective pass-rates, and cost. On a headless box use `--static` with an output HTML path and hand Mark the file; Submit downloads `feedback.json` to copy back for the next iteration.

### 5.4 Feedback loop (turn judgments into prompt edits)

Per iteration gather three signals: (1) the 3-judge panel reasoning, (2) Mark's per-eval `feedback.json` (empty = looked fine), (3) failed objective assertions. Pattern-match recurring weaknesses across evals and map each to a **specific, explained** addition to `DESIGN.md` / the skill (explain-the-why over all-caps MUSTs), generalized so it's not overfit to these six brands:

- *Recurring "both centered/symmetrical" or "couldn't tell A from B"* → section on committing to an editorial/asymmetric grid and *why* perfect symmetry reads as the generic AI default (show the move — offset hero, type-led column, deliberate negative space — without prescribing one layout).
- *Recurring indigo/violet gradient or a failing palette-tell assertion* → a derive-the-palette-from-brand-personality pattern (severe artisan = mineral + ink; warm heritage = ochre + leather; calm finance = soft sage + sand), naming the indigo-gradient default as the tell to avoid.
- *Low Motion or missing reduced-motion* → motion-with-restraint pattern: 1–2 purposeful, attention-guiding animations + a mandatory `prefers-reduced-motion` fallback.
- *Low Visual-hierarchy* → real type scale (≥3 committed sizes), one unambiguous focal point, whitespace as structure not filler.
- *Low Brand-fit but high Restraint (pretty-but-generic)* → strengthen the brief-reading step: articulate brand personality in 1–2 lines first and let it drive type/color/motion.

Then **re-run the same six prompts** into iteration-N+1 with `--previous-workspace` so Mark sees before/after side-by-side and watches the win-rate-vs-baseline delta move while objective floors stay passed and token/latency cost stays reasonable. **STOP** when the panel margin is stable and positive and Mark's feedback goes empty (`skill-creator`'s stopping rule). For a rigorous "is the new prompt actually better" checkpoint, run the blind panel with `old_agent` (the snapshot) as baseline to measure the prompt change directly.

---

## 6. Sequenced, Gated Implementation Plan

Mark wants human checkpoints before building. Each phase has a quality bar and a hard gate. **No edits to agent files happen until Gate 1 is explicitly approved.**

### Phase 0 — This assessment (DONE)
- **Deliverable:** this document.
- **Gate 0 (human):** Mark reviews and confirms direction. → *waiting on approval before any file edits.*

### Phase 1 — Decide scope & precedence (no code)
- **Do:** Mark confirms (a) do-BOTH (skill + per-project `DESIGN.md`) with `DESIGN.md`-wins precedence; (b) which agent edits are in scope (recommend: `ui-developer` Phase 0 + tools + visual loop + motion + `DESIGN.md` authorship + anti-generic checklist; the `accessibility-specialist` handoff; the `frontend-developer` boundary clarification — *not* origination); (c) whether to grant the `Skill` + MCP tools or stay inline-only.
- **Quality bar:** every proposed edit traces to a named gap in §2.
- **Gate 1 (human):** explicit go/no-go on the exact edit list. **Building starts only after this.**

### Phase 2 — Author the canonical assets (low risk, reversible)
- **Do:** (1) write a `DESIGN.md` **template** (9-section: tokens + philosophy) for `ui-developer` to instantiate per project; (2) draft the 6–8 line inlined "Aesthetic Standard" fallback; (3) draft the retargeted "Latest Docs & Design Resources" block.
- **Quality bar:** template covers color (hex + role), type (display+body pair, scale, weights), spacing, radius, shadow, motion tokens (150/300/500, ease-out/in), Do's/Don'ts, responsive, a11y. Inline fallback names the bans (no Inter/Roboto/Arial/system/Space-Grotesk, no purple-on-white).
- **Gate 2 (human):** approve assets before they're wired into the agent.

### Phase 3 — Wire `ui-developer` (the core edit) on a branch
- **Do:** add `Skill` + creative/inspection tools to frontmatter; add Phase 0; add the Design Resources block; add the Visual Self-Critique loop; add the Motion mandate; reframe the design-token line to author+persist; add the anti-generic checklist items; update the `description`; add the `accessibility-specialist` handoff line.
- **Quality bar:** agent still passes its own self-verification; Phase 0 runs *before* Gherkin; `DESIGN.md`-wins precedence stated; a11y line preserved.
- **Gate 3 (human):** diff review of `ui-developer.md` before merge. (Do **not** edit on `main` — branch first.)

### Phase 4 — Stand up the creativity eval (§5) and run iteration-1
- **Do:** build the harness (`with_agent` = new `ui-developer`/skill+`DESIGN.md`, `without_agent` = vanilla), screenshot tooling, 3-judge panel, objective grader, viewer. Run the 6 prompts × 2 configs × 3 runs. Snapshot the *old* prompt as `old_agent` for a true before/after.
- **Quality bar:** every run emits `index.html` + `desktop.png` + `mobile.png`; objective floor scripted (not eyeballed); panel is blind + randomized.
- **Gate 4 (human):** Mark reviews the eval-viewer (Outputs tab inline screenshots + Benchmark win-rate) and leaves per-eval feedback **before** any prompt rewrite.

### Phase 5 — Iterate to a stable positive margin
- **Do:** apply §5.4 feedback loop, re-run with `--previous-workspace`, watch win-rate-vs-baseline climb while objective floors stay green and cost stays reasonable. Swap in held-out brands every couple of iterations to guard against overfitting.
- **Quality bar:** `with_agent` blind-panel win-rate over baseline trends up and stabilizes; objective pass-rate stays high; token/latency lift is justified.
- **Gate 5 (human):** STOP when margin is stable + positive and Mark's feedback goes empty (the `skill-creator` stopping rule). Final diff + benchmark approved → merge.

### Phase 6 — Roll out & document
- **Do:** merge to `main`; add a short note to the team-skills docs on the new `ui-developer` contract, the `DESIGN.md` convention, and the precedence rule; optionally drop the `DESIGN.md` template into `docs/designs/`.
- **Gate 6 (human):** final sign-off.

**Overarching quality bars (apply at every gate):** (1) behavior verification (Playwright) stays intact — craft is *added*, never traded for behavior; (2) accessibility floor (contrast, focus, reduced-motion) never regresses; (3) `DESIGN.md` overrides the skill on any pinned token; (4) every claimed improvement is backed by the blind-panel delta + objective grading, not assertion.

---

## Sources cited
- Anthropic Claude Cookbook — Coding/Prompting for Frontend Aesthetics: https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics
- Anthropic blog — Improving frontend design through skills: https://claude.com/blog/improving-frontend-design-through-skills
- BetterStack — DESIGN.md for AI: https://betterstack.com/community/guides/ai/design-md-ai/
- VoltAgent/awesome-design-md: https://github.com/VoltAgent/awesome-design-md/blob/main/README.md
- Leonxlnx/taste-skill (3-dial taste rubric + pre-flight rules): https://github.com/Leonxlnx/taste-skill
- rohitg00/awesome-claude-design (aesthetic families + anti-slop fingerprints): https://github.com/rohitg00/awesome-claude-design
- OneRedOak/claude-code-workflows — design-review (live-UI scored review): https://github.com/OneRedOak/claude-code-workflows/tree/main/design-review
- Microsoft Fluent 2 — Motion choreography/staggering/easing *principles* (literal ms values are this report's recommendation): https://fluent2.microsoft.design/motion
- Design Bootcamp — Prompting AI like a designer (articulation + persistent context): https://medium.com/design-bootcamp/prompting-ai-like-a-designer-why-most-ai-generated-ui-designs-look-generic-945eccd35b7f
