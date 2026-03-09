# Feature Specification: Dark Mode Toggle for Settings Page

**Feature ID:** FEAT-DM-001
**Date:** 2026-03-09
**Status:** Draft
**Priority:** Medium
**Effort Estimate:** 2-3 days (frontend) + 0.5 days (backend, optional persistence)

---

## 1. Executive Summary

Add a dark mode toggle to the AIForge web application Settings page under the "Preferences" section. Users will be able to switch between Light, Dark, and System (OS-preference-follows) modes. The selection persists across sessions via localStorage (Phase 1) and optionally via a user preferences API endpoint (Phase 2).

---

## 2. Current State Analysis

### What Exists

1. **Tailwind dark mode is already configured** (`tailwind.config.ts`):
   - `darkMode: ['class']` -- class-based dark mode strategy is enabled
   - The codebase already uses `dark:` Tailwind variants in `src/app/page.tsx` (the Next.js default landing page)

2. **CSS custom properties are defined** (`globals.css`):
   - Light mode CSS variables exist under `:root` for backgrounds, foregrounds, borders, cards, etc.
   - **No `.dark` class variant is defined yet** -- this is a gap that must be filled

3. **shadcn/ui color system** is wired through HSL CSS variables (`--background`, `--foreground`, `--card`, `--muted`, `--border`, `--input`, `--ring`, etc.)

4. **Settings page is a stub** (`src/app/(auth)/settings/page.tsx`):
   - Currently renders only `<h1>Settings</h1>`
   - No settings layout, no sidebar, no sub-pages (the coverage report references show `general/`, `branding/`, `permissions/`, `regional/`, `teams/` sub-routes existed at some point in test coverage but the actual source files are missing)

5. **Product spec references "Preferences" section** (`08-settings.md`):
   - Settings nav hierarchy includes "Personal > Preferences (theme, notifications)"
   - The spec already anticipates a theme/appearance preference

6. **No theme provider exists**:
   - `providers.tsx` only wraps `QueryClientProvider`
   - `next-themes` is **not** installed
   - No Zustand store for theme preference
   - The `<html>` element in `layout.tsx` has no `suppressHydrationWarning` or class toggling

7. **Organization model has branding fields** but no user-level theme preference:
   - `primaryColor`, `accentColor`, `customCss` fields exist on Organization
   - No `themePreference` field on User model

### Gaps to Fill

| Gap | Description |
|-----|-------------|
| Dark CSS variables | No `.dark` class CSS variable definitions in `globals.css` |
| Theme library | `next-themes` not installed |
| Theme provider | No `ThemeProvider` wrapping the app |
| HTML suppression | No `suppressHydrationWarning` on `<html>` tag |
| Settings UI | Settings page is a stub with no form or sections |
| Preference persistence | No localStorage or API persistence for theme |
| Component dark styles | Most components (AppHeader, LoginPage, etc.) use hardcoded light colors without `dark:` variants |

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | User can toggle between Light, Dark, and System theme modes on the Settings > Preferences page | P0 |
| FR-2 | Selected theme applies immediately without page reload (no FOUC) | P0 |
| FR-3 | Theme preference persists across browser sessions via localStorage | P0 |
| FR-4 | System mode follows the OS prefers-color-scheme media query | P0 |
| FR-5 | Dark mode applies correct colors to all semantic CSS variables | P0 |
| FR-6 | The toggle UI uses a 3-option segmented control (Light / System / Dark) or radio group | P1 |
| FR-7 | Quick-access theme toggle available in the app header (sun/moon icon) | P2 |
| FR-8 | Theme preference persists server-side on the User model via API | P2 (Phase 2) |

### 3.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | No flash of unstyled content (FOUC) on page load |
| NFR-2 | Theme transition animation (150-200ms CSS transition on background-color and color) |
| NFR-3 | WCAG 2.1 AA color contrast ratios maintained in both light and dark modes |
| NFR-4 | Section 508 compliance: dark mode toggle must be keyboard-navigable and screen-reader-announced |
| NFR-5 | Performance: theme switching must complete in under 50ms |
| NFR-6 | No CLS (Cumulative Layout Shift) when toggling themes |

### 3.3 Accessibility Requirements

| ID | Requirement |
|----|-------------|
| A11Y-1 | Toggle control has clear aria-label ("Theme preference") |
| A11Y-2 | Current selection announced by screen reader (e.g., "Light mode, selected") |
| A11Y-3 | Focus ring visible on all theme toggle options |
| A11Y-4 | Dark mode colors pass WCAG AA contrast ratios (4.5:1 for text, 3:1 for UI elements) |
| A11Y-5 | Theme change announced via aria-live region |

---

## 4. Technical Design

### 4.1 Architecture Overview

```
next-themes ThemeProvider
       |
       v
<html class="dark">  (or class="" for light)
       |
       v
globals.css   :root { --background: ... }
              .dark { --background: ... }
       |
       v
Tailwind classes: bg-background, text-foreground, etc.
       |
       v
All components inherit correct colors
```

### 4.2 Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Theme library | `next-themes` | De facto standard for Next.js, handles SSR/hydration, FOUC prevention, localStorage, system preference detection. 4.5M weekly downloads. |
| CSS strategy | CSS custom properties with `.dark` class | Already partially in place; shadcn/ui compatible; class-based strategy already configured in Tailwind |
| State management | `next-themes` internal (backed by localStorage) | No need for Zustand store; `next-themes` manages state internally |
| Persistence (Phase 1) | localStorage via `next-themes` default | Zero backend changes required |
| Persistence (Phase 2) | API endpoint `PATCH /api/users/me/preferences` | Sync across devices |

### 4.3 Dark Mode Color Palette

Based on the existing light mode CSS variables and the enterprise/government design system:

```css
.dark {
  --background: 222 47% 11%;        /* primary-900: #0F172A */
  --foreground: 210 40% 98%;        /* primary-50: #F8FAFC */

  --surface-primary: 217 33% 17%;   /* ~#1E293B dark card surface */
  --surface-secondary: 222 47% 11%; /* primary-900 subtle bg */

  --text-primary: 210 40% 98%;      /* primary-50 for headings */
  --text-secondary: 215 20% 65%;    /* lightened body text */
  --text-muted: 215 16% 57%;        /* lightened muted text */

  --border: 217 33% 25%;            /* darkened borders */
  --border-input: 217 33% 30%;      /* darkened input borders */

  --card: 217 33% 17%;              /* dark card bg */
  --card-foreground: 210 40% 98%;   /* light text on dark cards */
  --muted: 217 33% 17%;             /* dark muted surfaces */
  --muted-foreground: 215 20% 65%;  /* readable muted text */
  --popover: 217 33% 17%;           /* dark popover bg */
  --popover-foreground: 210 40% 98%;
  --input: 217 33% 30%;             /* dark input borders */
  --ring: 217 91% 60%;              /* keep accent-blue for focus */

  --radius: 6px;
}
```

### 4.4 File Changes Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `package.json` | Modify | Add `next-themes` dependency |
| `src/app/globals.css` | Modify | Add `.dark { }` CSS variable block |
| `src/app/layout.tsx` | Modify | Add `suppressHydrationWarning` to `<html>` |
| `src/app/providers.tsx` | Modify | Wrap children with `ThemeProvider` from `next-themes` |
| `src/app/(auth)/settings/page.tsx` | Modify | Build out Preferences section with theme toggle |
| `src/components/settings/theme-toggle.tsx` | **New** | Theme toggle component (segmented control) |
| `src/components/navigation/app-header.tsx` | Modify | Add dark mode variants to hardcoded colors (Phase 2: add quick toggle icon) |

---

## 5. User Interface

### 5.1 Settings > Preferences Section

```
Settings
---------

Preferences
============

Appearance
----------
Choose how FORGE looks to you. Select a theme or sync with your
operating system setting.

  [ Light ]  [ System ]  [ Dark ]
      ^          ^          ^
  Sun icon   Monitor    Moon icon

  "System" follows your device's appearance setting.


Notifications (future)
----------------------
[Coming soon placeholder]
```

### 5.2 Theme Toggle Component States

| State | Visual |
|-------|--------|
| Light selected | Sun icon highlighted, blue background on Light segment |
| System selected | Monitor icon highlighted, blue background on System segment |
| Dark selected | Moon icon highlighted, blue background on Dark segment |
| Hover (unselected) | Subtle gray background on hover |
| Focus | Blue ring outline (2px) |
| Transition | 150ms ease background-color transition |

---

## 6. Out of Scope

- Organization-level forced theme (admin forces dark/light for all users)
- Custom theme colors beyond light/dark (e.g., high contrast mode)
- Dark mode for the CUI banner (remains green per government branding requirements)
- Dark mode for Mastra Studio (separate pre-built application)
- Persistent API storage in Phase 1 (Phase 2 item)
- Email/notification dark mode templates

---

## 7. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| FOUC on initial load | Poor UX, flash of white before dark | Medium | `next-themes` handles this with script injection; `suppressHydrationWarning` prevents React mismatch |
| Contrast issues in dark mode | Accessibility violation (508/WCAG) | Medium | Audit all color combinations with contrast checker; define explicit dark palette |
| Component-level hardcoded colors | Some components won't respond to dark mode | High | Audit all components; replace hardcoded colors with CSS variable references or `dark:` variants |
| CUI banner confusion | Green banner may look odd in dark context | Low | Keep CUI banner unchanged (government requirement) -- it is a fixed-color element by design |
| SSR hydration mismatch | Console errors, broken rendering | Medium | `suppressHydrationWarning` + `next-themes` attribute handling |

---

## 8. Success Criteria

- [ ] User can select Light, Dark, or System theme on Settings > Preferences
- [ ] Theme applies immediately with no FOUC
- [ ] Theme persists after browser refresh and across sessions
- [ ] System mode correctly follows OS prefers-color-scheme
- [ ] All text passes WCAG AA contrast ratio (4.5:1) in both modes
- [ ] Theme toggle is keyboard-navigable (Tab, Enter/Space)
- [ ] Screen reader announces current theme selection
- [ ] No console hydration warnings
- [ ] CUI banner remains unchanged in both modes
