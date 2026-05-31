<!--
========================================================================
  DESIGN.md  —  Per-Project Design System (TEMPLATE)
  ------------------------------------------------------------------------
  Author of this file: the `ui-developer` agent.
  When: on the FIRST UI task for a project when no DESIGN.md exists.
  How:  run the frontend-design skill's Design Thinking gate
        (Purpose / Tone / Constraints / Differentiation), commit to ONE
        named aesthetic direction, then fill EVERY `<...>` marker below
        and delete the guidance comments you no longer need.
  Read: every UI task thereafter, alongside the doc-hub files.

  PRECEDENCE (read this first):
    This DESIGN.md is BINDING BRAND TRUTH. It WINS where it specifies.
    Any token pinned here (font, color, spacing, radius, shadow, motion)
    OVERRIDES the frontend-design skill. The skill only fills the
    UNSPECIFIED degrees of freedom (composition, depth, micro-detail,
    page-load orchestration) and raises polish. It must NEVER override a
    value committed here.

  HARD BANS (apply to every choice below, no exceptions):
    - Fonts:  NO Inter, Roboto, Arial, system-ui/system fonts, Space Grotesk.
    - Color:  NO timid evenly-distributed greys; NO purple/indigo gradient
              on a white background (the canonical AI-slop tell —
              specifically avoid #6366f1, #4f46e5, Tailwind indigo-*).
    - Layout: NO cookie-cutter 3-identical-icon-card grids, no perfect
              symmetry as a default, no swap-the-logo-and-it's-any-startup.
  ========================================================================
-->

# DESIGN.md — `<Project / Brand Name>`

> **Status:** `<draft | committed>`  ·  **Version:** `<0.1.0>`  ·  **Last updated:** `<YYYY-MM-DD>`
> **Authored by:** `ui-developer` (frontend-design skill Design Thinking gate)
> **Source of truth:** `<this file | reverse-engineered from Figma URL | reverse-engineered from live site>`

<!-- One-paragraph north star. Who uses this, what feeling it must leave, and
     the ONE thing someone remembers. Write the brand personality in 1-2 lines
     so it can drive type/color/motion — this is what makes a generic output
     "visibly wrong" for this brand. -->

**North star:** `<e.g. "A high-end Japanese kitchen-knife brand for professional chefs — precise, restrained, a little severe. Mastery and patience, never buy-now urgency.">`

**Design Thinking gate (from frontend-design skill):**
- **Purpose:** `<what problem this interface solves; who uses it>`
- **Tone (pick an extreme, name it):** `<brutally minimal | maximalist | retro-futuristic | organic/natural | luxury/refined | playful/toy-like | editorial/magazine | brutalist/raw | art-deco/geometric | soft/pastel | industrial/utilitarian | ...>`
- **Constraints:** `<framework, performance budget, accessibility target, brand locks>`
- **Differentiation (the unforgettable detail):** `<the one memorable, context-specific move>`

---

# PART 1 — TOKENS (structured, machine-fillable)

<!-- These are the binding values. Implement them as CSS custom properties
     and/or a Tailwind theme so every component pulls from the same source.
     Every token below OVERRIDES the frontend-design skill. -->

## 1. Color Palette & Roles

<!-- Commit to a DOMINANT color with SHARP accents — not a timid, evenly
     distributed palette. Derive the palette from the brand personality,
     e.g. severe artisan = mineral + ink; warm heritage = ochre + leather;
     calm finance = soft sage + sand. Every color needs a hex AND a usage
     role so an agent knows WHEN to reach for it. Light/dark is a choice —
     do not default to light. -->

| Token | Hex | Usage role |
|---|---|---|
| `--color-bg` | `<#______>` | Page background / canvas |
| `--color-surface` | `<#______>` | Cards, panels, raised surfaces |
| `--color-surface-alt` | `<#______>` | Alternate / sunken sections, zebra bands |
| `--color-fg` | `<#______>` | Primary text |
| `--color-fg-muted` | `<#______>` | Secondary / supporting text |
| `--color-dominant` | `<#______>` | Brand dominant — the color the page is "about" |
| `--color-accent` | `<#______>` | Sharp accent — CTAs, focus, key highlights (NOT #6366f1 / #4f46e5 / indigo) |
| `--color-accent-2` | `<#______>` | Secondary accent (optional; leave blank to keep restraint) |
| `--color-border` | `<#______>` | Hairlines, dividers, input borders |
| `--color-success` | `<#______>` | Positive / confirm states |
| `--color-warning` | `<#______>` | Caution states |
| `--color-danger` | `<#______>` | Destructive / error states |
| `--color-focus-ring` | `<#______>` | Visible focus indicator (must meet 3:1 vs adjacent) |

**Theme:** `<light | dark | both — if both, state how the tokens flip>`
**Palette intent (1 line, why these colors fit the brand):** `<...>`

## 2. Typography

<!-- Pair a DISTINCTIVE display font with a refined body font.
     BANNED: Inter, Roboto, Arial, system-ui/system, Space Grotesk.
     State the actual @font-face / next/font / CDN source for each. -->

**Font pair (REQUIRED — display + body, must be different):**
- **Display / headings:** `<font family>` — `<source: Google Fonts / Fontshare / local woff2 / ...>`
- **Body / UI:** `<font family>` — `<source>`
- **Mono (optional, code/data):** `<font family or "none">`

**Why this pairing fits the brand (1 line):** `<...>`

**Type scale** (≥ 3 distinct sizes; commit to a ratio, e.g. 1.25 major-third):

| Token | Size | Line-height | Weight | Used for |
|---|---|---|---|---|
| `--text-display` | `<3.5rem / clamp(...)>` | `<1.05>` | `<700>` | Hero / page title |
| `--text-h1` | `<2.5rem>` | `<1.1>` | `<700>` | Section headings |
| `--text-h2` | `<1.75rem>` | `<1.2>` | `<600>` | Sub-headings |
| `--text-h3` | `<1.25rem>` | `<1.3>` | `<600>` | Card / block titles |
| `--text-body` | `<1rem>` | `<1.6>` | `<400>` | Body copy |
| `--text-small` | `<0.875rem>` | `<1.5>` | `<400>` | Captions, labels |
| `--text-eyebrow` | `<0.75rem>` | `<1.4>` | `<600 / uppercase / tracked>` | Eyebrows, overlines (≤ 1 per 3 sections) |

**Weights available:** `<e.g. 400 / 500 / 600 / 700>`
**Letter-spacing rules:** `<e.g. -0.02em on display; +0.08em uppercase on eyebrows>`

## 3. Spacing Scale

<!-- One consistent rhythm. Pick a base step and stick to it everywhere so
     spacing reads as deliberate, not arbitrary. Whitespace is structure,
     not filler. -->

**Base unit:** `<4px | 8px>`

| Token | Value | Typical use |
|---|---|---|
| `--space-2xs` | `<4px>` | Icon gaps, tight inline |
| `--space-xs` | `<8px>` | Within-component padding |
| `--space-sm` | `<12px>` | Compact stacks |
| `--space-md` | `<16px>` | Default element gap |
| `--space-lg` | `<24px>` | Card padding, group spacing |
| `--space-xl` | `<40px>` | Between sub-sections |
| `--space-2xl` | `<64px>` | Between major sections |
| `--space-3xl` | `<96px+>` | Hero breathing room, section bands |

**Container max-width:** `<e.g. 1200px>`  ·  **Content measure (reading width):** `<60–75ch>`  ·  **Gutter:** `<...>`

## 4. Radii

| Token | Value | Used for |
|---|---|---|
| `--radius-none` | `0` | Sharp / brutalist / editorial edges |
| `--radius-sm` | `<2–4px>` | Inputs, tags, small controls |
| `--radius-md` | `<8px>` | Buttons, cards |
| `--radius-lg` | `<16px>` | Modals, large surfaces |
| `--radius-full` | `9999px` | Pills, avatars |

**Radius personality (1 line):** `<e.g. "sharp corners throughout — softness would undercut the severe tone">`

## 5. Shadow / Elevation

<!-- Depth and elevation are an intentional language, not an afterthought.
     Decide whether depth comes from shadows, borders, layered transparency,
     or flat color separation — and be consistent. Define an elevation ladder. -->

| Token | Value | Elevation level / use |
|---|---|---|
| `--shadow-none` | `none` | Flat surfaces, on-brand flat aesthetics |
| `--shadow-sm` | `<0 1px 2px rgba(...)>` | Resting cards, inputs |
| `--shadow-md` | `<0 4px 12px rgba(...)>` | Hover lift, dropdowns |
| `--shadow-lg` | `<0 12px 32px rgba(...)>` | Modals, popovers |
| `--shadow-inset` | `<inset 0 1px 0 rgba(...)>` | Pressed / sunken states (optional) |

**Elevation strategy (1 line):** `<e.g. "depth via hairline borders + subtle shadow, never glossy drop-shadows">`

## 6. Motion

<!-- Per assessment §4.6. These durations/easings are the COMMITTED token set.
     One well-orchestrated entrance with staggered reveals beats scattered
     micro-interactions. Easing is directional: ease-out on enter, ease-in
     on exit. prefers-reduced-motion is MANDATORY, not optional. -->

**Duration tokens:**

| Token | Value | Use |
|---|---|---|
| `--motion-fast` | `150ms` | Hover, focus, small state changes |
| `--motion-normal` | `300ms` | Default transitions, reveals, dropdowns |
| `--motion-slow` | `500ms` | Page-load orchestration, large/hero motion |

**Easing tokens (directional):**

| Token | Value | Use |
|---|---|---|
| `--ease-out-enter` | `<cubic-bezier(0.16, 1, 0.3, 1)>` | Elements ENTERING (ease-out) |
| `--ease-in-exit` | `<cubic-bezier(0.7, 0, 0.84, 0)>` | Elements EXITING (ease-in) |
| `--ease-spring` | `<spring(stiffness, damping, mass) or cubic-bezier>` | Interactive feedback (optional) |

**Stagger:** secondary/sequential elements offset by `<50–100ms>` for hierarchy on reveal.
**Signature motion moment (the one orchestrated entrance):** `<describe it, e.g. "hero headline rises with staggered word reveal, 60ms apart">`

**`prefers-reduced-motion` (REQUIRED):**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
<!-- Keep the FINAL visual state reachable without motion — never hide content
     behind an animation that no longer plays. -->

---

# PART 2 — PHILOSOPHY (natural language)

<!-- The "why/when" a token file can't carry. Keep it specific to THIS brand.
     An agent reads this to make the hundreds of unspecified micro-decisions
     in the same spirit. -->

## 7. Visual Theme & Atmosphere

<!-- The overall feeling and the named aesthetic direction. Atmosphere comes
     from backgrounds, texture, and depth — not flat solid fills by default.
     Name the conceptual lane and describe the world it lives in. -->

`<Named direction (editorial / brutalist / refined-minimal / retro-futuristic / warm-organic / ...). Describe the atmosphere: what the surfaces feel like, the texture/grain/gradient-mesh/pattern strategy, the overall density (generous negative space OR controlled density), and the one memorable detail that makes it unforgettable.>`

## 8. Layout Principles

<!-- How structure is built. Favor intentional composition over the AI-default
     centered-everything symmetry. Whitespace is structure. State the grid
     and the deliberate grid-breaking moves allowed. -->

- **Grid:** `<e.g. 12-col, asymmetric; type-led single column; editorial split>`
- **Composition stance:** `<asymmetry / overlap / diagonal flow / generous negative space / controlled density — pick and explain>`
- **Hero:** `<e.g. "hero need not fit one viewport; one clear focal point, unambiguous CTA priority">`
- **Navigation:** `<e.g. "single-line nav; no overflow wrapping">`
- **Eyebrows / overlines:** `<≤ 1 per 3 sections>`
- **Rhythm:** `<how sections alternate surface/surface-alt, where the page breathes>`

## 9. Depth & Elevation

<!-- The philosophy behind Token §5. WHEN something lifts, and why. -->

`<Describe the depth language in prose: does the UI feel flat-and-confident, or layered? When do surfaces lift (hover, active, modal)? Is depth expressed through shadow, hairline borders, layered transparency, or color separation? Keep it consistent with the brand — e.g. a severe artisan brand earns its depth from precise borders, not glossy shadows.>`

## 10. Responsive Behavior

<!-- Breakpoints + what reflows. Must hold at the eval viewports 390/768/1440
     with no horizontal scroll, no overflow/overlap, readable type, and
     tap-friendly targets (≥ 44px). -->

| Breakpoint | Width | Behavior |
|---|---|---|
| Mobile | `<≤ 390px>` | `<single column; stack; collapse nav to ...; type scales to ...>` |
| Tablet | `<768px>` | `<2-col where it helps; ...>` |
| Desktop | `<≥ 1440px>` | `<full grid; max-width container; ...>` |

- No horizontal scroll at 390px (`scrollWidth ≤ clientWidth`).
- No element wider than its viewport at 390 / 768 / 1440.
- Tap targets ≥ `<44px>`; type stays readable (body ≥ 16px on mobile).
- `<which elements reflow vs. hide vs. reorder>`

## 11. Accessibility Requirements

<!-- The frontend-design skill is purely aesthetic and can HURT a11y if left
     unchecked. These floors are non-negotiable and survive every aesthetic
     choice. Defer deep WCAG audits to the accessibility-specialist agent. -->

- **Contrast:** body text ≥ **4.5:1**, large text (≥ 24px or 18.66px bold) ≥ **3:1**, UI/focus indicators ≥ **3:1** against adjacent colors. Verify every pairing in Token §1.
- **Focus:** every interactive element has a **visible focus ring** (`--color-focus-ring`); never `outline: none` without a stronger replacement. Logical focus order; visible focus on keyboard nav.
- **Reduced motion:** the Token §6 `prefers-reduced-motion` block ships in every build; the final visual state is reachable with motion disabled.
- **Semantics:** semantic landmarks/headings; labels on inputs; alt text on meaningful images; ARIA only where native semantics fall short.
- **States:** every component defines hover / focus / active / disabled / loading / empty / error states.
- **Target:** WCAG `<2.1 AA | AAA>`. For full audits, screen-reader testing, or contrast remediation beyond the build, hand off to `accessibility-specialist`.

## 12. Do's and Don'ts

**Do**
- `<Commit to the ONE named aesthetic direction above and execute it precisely.>`
- `<Use the dominant color with sharp accents; let one color carry the page.>`
- `<Pair the committed display + body fonts; honor the type scale and ≥ 3 distinct sizes.>`
- `<Build one well-orchestrated, staggered entrance; respect prefers-reduced-motion.>`
- `<Use whitespace as structure; favor intentional / asymmetric composition.>`
- `<Add at least one memorable, context-specific detail per view.>`
- `<Derive every color from brand personality, with a stated role.>`

**Don't**
- **No** Inter, Roboto, Arial, system-ui/system fonts, or Space Grotesk.
- **No** purple/indigo gradient on white; **no** `#6366f1` / `#4f46e5` / Tailwind `indigo-*` as the brand accent.
- **No** timid, evenly-distributed grey palette.
- **No** cookie-cutter 3-identical-icon-card grid; **no** default perfect symmetry; **no** swap-the-logo generic SaaS template.
- **No** linear easing on enter/exit; **no** motion without a reduced-motion fallback.
- **No** `outline: none` without a stronger visible focus replacement.
- **No** emoji bullets as a layout crutch; **no** more than one eyebrow per 3 sections.

## 13. Agent Prompt Guide

<!-- The precedence contract. This is what a coding agent reads to know how
     this file and the frontend-design skill cooperate. Keep verbatim. -->

> **DESIGN.md WINS where it specifies.** This file is binding brand truth. Any token it pins — fonts, colors, spacing, radii, shadows, motion — **overrides** the `frontend-design` skill; the skill must never "creatively" replace a value committed here. Invoke `frontend-design:frontend-design` only to fill the **unspecified degrees of freedom** (composition, depth, background atmosphere, micro-detail, page-load orchestration) and to raise polish. If a requirement is silent in this file, the skill's taste decides — and once decided, **persist the new choice back into the relevant token/section here** so the project stays cohesive. Keep the accessibility floor (contrast, focus, reduced-motion) active regardless of any aesthetic choice.

<!--
  ========================================================================
  FILL-IN CHECKLIST (delete before committing):
    [ ] Named ONE aesthetic direction (not generic defaults)
    [ ] Display + body font PAIR chosen, both sourced, neither banned
    [ ] Dominant + sharp accent committed; accent is NOT indigo/#6366f1/#4f46e5
    [ ] Full color table has hex + role for every row; contrast verified
    [ ] Type scale has ≥ 3 distinct sizes with line-heights and weights
    [ ] Spacing scale, radii, and elevation ladder all filled
    [ ] Motion: 150/300/500ms + ease-out-enter / ease-in-exit + reduced-motion block
    [ ] All 7 philosophy sections (7–13) written specific to THIS brand
    [ ] Responsive holds at 390 / 768 / 1440 with no horizontal scroll
    [ ] Do's / Don'ts reflect the brand; bans intact
    [ ] Agent Prompt Guide precedence paragraph kept verbatim
  ========================================================================
-->
