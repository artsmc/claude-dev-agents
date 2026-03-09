# Spec-Plan Run Summary: Dark Mode Toggle

**Date:** 2026-03-09
**Feature Request:** "I need to add a dark mode toggle to the settings page in the web app"
**Skill Version:** spec-plan v2 (Scope-Aware Planning & Research)

---

## Phase 0: Feature Description

**Input (from user prompt):** "I need to add a dark mode toggle to the settings page in the web app"

Used as starting point; proceeded directly to Phase 1 with context.

---

## Phase 1: Clarification Questions (Simulated)

The skill instructs asking 2-3 triage-level questions only. Below are the questions that WOULD be asked, with simulated reasonable answers:

### Q1: What problem does this solve for users? (one sentence)
**Simulated Answer:** "Users need the ability to switch between light and dark color schemes for visual comfort and reduced eye strain, especially during extended use."

### Q2: Which apps are affected? (API / Web / Mastra / Microsandbox)
**Simulated Answer:** "Web only. This is a client-side UI preference -- no API storage needed initially. The preference can be persisted in localStorage."

### Q3: Any hard constraints? (security, performance, compliance)
**Simulated Answer:** "Should meet Section 508/WCAG 2.1 AA contrast requirements in both light and dark modes. No security or performance concerns."

---

## Phase 2: Triage Gate

### Tier Selected: QUICK-SPEC

### Reasoning (matched against classification criteria):

| Signal | Match? | Evidence |
|--------|--------|----------|
| Single app affected | YES | Web app only |
| Single concern (UI-only) | YES | Pure client-side theme switching |
| Estimated < 5 implementation tasks | YES | ~6 tasks (borderline but well-understood) |
| Well-understood pattern | YES | Tailwind dark mode + next-themes is a standard pattern |
| User said "simple/quick/small" | NO | Not explicitly, but "add a toggle" is small-scope language |

**Override rules check:**
- No `--tier` flag provided
- No ambiguity between tiers (all signals point to QUICK)
- Result: **QUICK-SPEC confirmed**

**Why NOT Standard?** Only 1 app affected. No API contract changes. No schema changes. No new data models. This is a UI-only feature using a well-documented, standard pattern (Tailwind CSS `darkMode: 'class'` is already configured in the codebase).

---

## Phase 3: Scope Confirmation

```
Based on your description, I've scoped this as a **QUICK** spec:

Feature: Add dark mode toggle to the web app settings page
Affected apps: Web (apps/web)
Estimated complexity: Low

I'll generate:
  [x] task-list.md -- Implementation tasks with dependencies

Research scope:
  [x] Memory Bank -- Check existing patterns and active work
  [x] Codebase scan -- Identify target files and existing patterns

Estimated generation time: 1-3 min
Estimated tokens: ~15K

Does this scope look right, or should I adjust?
```

---

## Phase 4: Budgeted Research (Quick Tier -- ~2K tokens budget)

### Memory Bank Check (~1K budget)

**Source:** `/home/artsmc/applications/low-code/memory-bank/activeContext.md`

**Findings:**
- No active work related to dark mode or theming
- Current focus is on Microsandbox Connectors + Build Stabilization
- No conflicts or blockers for this feature
- Web frontend is on port 3500, Next.js 16.1.6, React 19

### Codebase Scan (~1K budget)

**Key findings:**

1. **Tailwind already configured for dark mode:**
   - `tailwind.config.ts` line 4: `darkMode: ['class']` -- class-based dark mode is ALREADY enabled
   - This means adding `class="dark"` to the `<html>` element activates all `dark:` prefixed utilities

2. **CSS custom properties already defined (light only):**
   - `globals.css` has `:root` variables for background, foreground, surface, text, border colors
   - No `.dark` class selector exists yet -- dark mode CSS variables must be added

3. **shadcn/ui color system in use:**
   - Tailwind config maps `background`, `foreground`, `border`, `card`, `muted`, etc. to `hsl(var(--...))` CSS variables
   - This is the standard shadcn/ui pattern -- adding a `.dark` block in `globals.css` with inverted HSL values enables dark mode for all components using these tokens

4. **Settings page exists but is a stub:**
   - `/apps/web/src/app/(auth)/settings/page.tsx` -- contains only `<h1>Settings</h1>`
   - The toggle needs to be added to this page

5. **Providers component exists:**
   - `/apps/web/src/app/providers.tsx` -- wraps app with `QueryClientProvider`
   - ThemeProvider (from `next-themes`) would be added here

6. **`next-themes` not installed:**
   - Not in `package.json` dependencies
   - Must be installed as a new dependency

7. **Root layout uses Providers wrapper:**
   - `layout.tsx` wraps children in `<Providers>`, which is the correct integration point

8. **No existing theme/dark mode files:**
   - No `*theme*` or `*dark*` files found in the web app
   - Clean slate for implementation

---

## Phase 5: Deliverables Generated

### Files Generated

| File | Purpose | Tier Requirement |
|------|---------|-----------------|
| `task-list.md` | Implementation tasks with dependencies | Required (QUICK tier) |
| `run_summary.md` | This file -- evaluation artifact | Evaluation requirement |
| `structured-brief.json` | JSON brief for spec-writer agent | Skill workflow artifact |

### Structured Brief (JSON)

The following JSON brief would be passed to the spec-writer agent:

```json
{
  "feature": {
    "name": "dark-mode-toggle",
    "description": "Add a dark mode toggle to the settings page in the web app",
    "problem_statement": "Users need the ability to switch between light and dark color schemes for visual comfort and reduced eye strain during extended platform use",
    "affected_apps": ["web"],
    "complexity": "low",
    "tier": "quick"
  },
  "deliverables": [
    "task-list.md"
  ],
  "constraints": {
    "security": "None",
    "performance": "Theme toggle must be instantaneous with no flash of unstyled content (FOUC)",
    "compliance": "WCAG 2.1 AA contrast ratios must be maintained in both light and dark modes (Section 508 requirement)",
    "deadline": "None specified"
  },
  "research_findings": {
    "existing_patterns": "Tailwind darkMode: ['class'] already configured. shadcn/ui HSL CSS variable system in use. No active work conflicts (current focus: Microsandbox connectors).",
    "reusable_components": "Existing Providers component at src/app/providers.tsx for ThemeProvider integration. Existing settings page stub at src/app/(auth)/settings/page.tsx. shadcn/ui color token system (background, foreground, card, muted, border, etc.) already mapped to CSS variables.",
    "framework_patterns": "next-themes library for Next.js theme management (handles SSR, localStorage, system preference detection, FOUC prevention). Tailwind class-based dark mode with CSS custom properties.",
    "integration_points": "Root layout (layout.tsx) -> Providers -> ThemeProvider wrapping. globals.css :root variables need .dark counterpart. Settings page needs toggle UI component.",
    "pitfalls_to_avoid": "Flash of unstyled content (FOUC) on page load -- next-themes handles this with a script tag. Must set suppressHydrationWarning on <html> element. Dark mode colors must maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)."
  },
  "output_path": "/home/artsmc/.claude/skills/spec-plan-workspace/iteration-1/dark-mode-quick-with-skill/outputs/"
}
```

---

## Agent Prompt (Quick Tier)

The spec-writer agent would be launched with this prompt:

```
Generate a focused implementation task list for: dark-mode-toggle

CONTEXT BRIEF:
{structured_brief_json}

DELIVERABLE: task-list.md ONLY

Requirements for task-list.md:
- Start with a 3-5 line feature summary (inline requirements -- no separate FRD)
- Break down into numbered, atomic tasks
- Each task: what to do, which file(s), what pattern to follow
- Include task dependencies (e.g., "depends on Task 2")
- Group into logical phases (setup -> implementation -> testing)
- Target: 3-8 tasks (if you need more than 8, flag that this may need a higher tier)

DO NOT generate FRD.md, FRS.md, GS.md, or TR.md.
Output: /home/artsmc/.claude/skills/spec-plan-workspace/iteration-1/dark-mode-quick-with-skill/outputs/task-list.md
```

---

## Evaluation Notes

### What the Skill Did Well
1. **Triage was clear-cut** -- All QUICK signals matched; no ambiguity
2. **Research was focused** -- Memory Bank confirmed no conflicts; codebase scan identified the exact integration points and the key finding that `darkMode: ['class']` is already configured
3. **Budget was respected** -- Research stayed well within the ~2K token budget for QUICK tier
4. **Existing infrastructure leveraged** -- Found that the shadcn/ui CSS variable system makes dark mode a matter of adding a `.dark` selector block, not refactoring components

### Key Codebase Findings for Implementation
- **Already done:** `darkMode: ['class']` in `tailwind.config.ts`
- **Already done:** HSL CSS variable system in `globals.css` and `tailwind.config.ts`
- **Needs doing:** Install `next-themes`, add `.dark` CSS variables, wrap in `ThemeProvider`, build toggle UI, add `suppressHydrationWarning` to `<html>`
- **Settings page is a stub:** Only contains `<h1>Settings</h1>` -- needs full page layout with the toggle
