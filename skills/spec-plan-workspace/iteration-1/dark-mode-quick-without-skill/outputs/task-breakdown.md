# Task Breakdown: Dark Mode Toggle

**Feature ID:** FEAT-DM-001
**Date:** 2026-03-09
**Total Estimated Effort:** 2-3 days

---

## Task Dependency Graph

```
T1 (Install next-themes)
 |
 +---> T2 (Dark CSS variables)
 |       |
 +---> T3 (ThemeProvider + layout)
         |
         +---> T4 (ThemeToggle component)
         |       |
         |       +---> T5 (Settings page integration)
         |
         +---> T6 (AppHeader dark mode migration)
                |
                +---> T7 (Testing)
                        |
                        +---> T8 (Accessibility audit)
```

---

## Tasks

### T1: Install `next-themes` dependency

**Estimated Effort:** 15 minutes
**Agent:** frontend-developer
**Files Modified:**
- `/home/artsmc/applications/low-code/apps/web/package.json`

**Description:**
Install the `next-themes` package in the web app workspace.

**Acceptance Criteria:**
- [ ] `next-themes` appears in `dependencies` in `apps/web/package.json`
- [ ] `npm install` completes without errors
- [ ] No version conflicts with existing dependencies

**Command:**
```bash
cd /home/artsmc/applications/low-code && npm install next-themes --workspace=apps/web
```

---

### T2: Define dark mode CSS variables

**Estimated Effort:** 1-2 hours
**Agent:** ui-developer
**Depends On:** T1
**Files Modified:**
- `/home/artsmc/applications/low-code/apps/web/src/app/globals.css`

**Description:**
Add a `.dark` CSS class block to `globals.css` that defines all the dark mode values for the existing CSS custom properties. Also add a smooth transition on `body` for background-color and color.

**Subtasks:**
1. Define dark values for all existing `:root` variables (`--background`, `--foreground`, `--surface-primary`, `--surface-secondary`, `--text-primary`, `--text-secondary`, `--text-muted`, `--border`, `--border-input`)
2. Define dark values for all shadcn/ui variables (`--card`, `--card-foreground`, `--muted`, `--muted-foreground`, `--popover`, `--popover-foreground`, `--input`, `--ring`)
3. Add 150ms transition for `background-color` and `color` on `body`
4. Verify all HSL values produce WCAG AA compliant contrast ratios

**Acceptance Criteria:**
- [ ] `.dark` block contains all variables from `:root`
- [ ] All dark text-on-background combinations meet 4.5:1 contrast ratio
- [ ] Body transitions smoothly between light and dark

---

### T3: Integrate ThemeProvider and update root layout

**Estimated Effort:** 30 minutes
**Agent:** frontend-developer
**Depends On:** T1
**Files Modified:**
- `/home/artsmc/applications/low-code/apps/web/src/app/providers.tsx`
- `/home/artsmc/applications/low-code/apps/web/src/app/layout.tsx`

**Description:**
Wrap the application with `next-themes` `ThemeProvider` and add `suppressHydrationWarning` to the root `<html>` element.

**Subtasks:**
1. Import `ThemeProvider` from `next-themes` in `providers.tsx`
2. Wrap existing `QueryClientProvider` with `ThemeProvider` configured for:
   - `attribute="class"` (matches Tailwind `darkMode: ['class']`)
   - `defaultTheme="system"`
   - `enableSystem={true}`
3. Add `suppressHydrationWarning` to `<html>` in `layout.tsx`

**Acceptance Criteria:**
- [ ] `ThemeProvider` wraps all children in `providers.tsx`
- [ ] `<html>` tag has `suppressHydrationWarning`
- [ ] No hydration mismatch console warnings
- [ ] Default theme is "system"

---

### T4: Build ThemeToggle component

**Estimated Effort:** 2-3 hours
**Agent:** ui-developer
**Depends On:** T3
**Files Created:**
- `/home/artsmc/applications/low-code/apps/web/src/components/settings/theme-toggle.tsx`

**Description:**
Create a segmented control component that allows users to switch between Light, System, and Dark themes. Must handle SSR hydration gracefully (render skeleton until mounted).

**Subtasks:**
1. Create component with `useTheme` hook from `next-themes`
2. Implement 3-option segmented control with Sun, Monitor, Moon icons
3. Use `role="radiogroup"` with `role="radio"` buttons for a11y
4. Handle SSR with `mounted` state check (render skeleton placeholder until client-side)
5. Style with Tailwind using CSS variable references (not hardcoded colors)
6. Add focus ring, hover states, and selected state styling

**Acceptance Criteria:**
- [ ] Three options displayed: Light, System, Dark
- [ ] Clicking an option changes the theme immediately
- [ ] Selected option is visually distinct
- [ ] No flash or layout shift on initial render
- [ ] Proper ARIA roles and labels

---

### T5: Build out Settings page with Preferences section

**Estimated Effort:** 1-2 hours
**Agent:** ui-developer
**Depends On:** T4
**Files Modified:**
- `/home/artsmc/applications/low-code/apps/web/src/app/(auth)/settings/page.tsx`

**Description:**
Replace the stub Settings page with a proper Preferences section containing the Appearance subsection and ThemeToggle component. Follow the existing product spec layout pattern.

**Subtasks:**
1. Add page metadata (title, description)
2. Create section structure with heading hierarchy (h1 > h2 > h3)
3. Add Appearance card with description text and ThemeToggle
4. Add helper text explaining "System" mode
5. Style using CSS variable-based classes (dark-mode-ready)
6. Use proper `aria-labelledby` for section landmarks

**Acceptance Criteria:**
- [ ] Settings page shows "Preferences > Appearance" section
- [ ] ThemeToggle is rendered within a card-style container
- [ ] Page uses semantic heading hierarchy
- [ ] All text uses CSS variable colors (works in both themes)
- [ ] Descriptive text explains each mode option

---

### T6: Migrate AppHeader to support dark mode

**Estimated Effort:** 1-2 hours
**Agent:** ui-developer
**Depends On:** T3
**Files Modified:**
- `/home/artsmc/applications/low-code/apps/web/src/components/navigation/app-header.tsx`

**Description:**
Update the AppHeader component to work correctly in dark mode by either replacing hardcoded color classes with CSS variable references or adding `dark:` variant classes.

**Subtasks:**
1. Replace `bg-white` with `bg-card` on the `<header>` element
2. Replace `border-neutral-200` with `border-border`
3. Replace `text-neutral-*` classes with `text-foreground` / `text-muted-foreground` or add `dark:` variants
4. Keep CUI banner colors unchanged (`bg-cui text-white`)
5. Update icon button hover states for dark mode
6. Verify branding section (FORGE logo area) works in both modes

**Acceptance Criteria:**
- [ ] AppHeader looks correct in light mode (regression check)
- [ ] AppHeader looks correct in dark mode
- [ ] CUI banner remains green with white text in both modes
- [ ] Navigation links have proper contrast in both modes
- [ ] Icon buttons have visible hover states in both modes

---

### T7: Write tests for dark mode feature

**Estimated Effort:** 2-3 hours
**Agent:** nextjs-qa-developer
**Depends On:** T4, T5, T6
**Files Created:**
- `/home/artsmc/applications/low-code/apps/web/__test__/components/settings/theme-toggle.test.tsx`
- `/home/artsmc/applications/low-code/apps/web/__test__/app/settings/page.test.tsx`

**Description:**
Write unit tests for the ThemeToggle component and integration tests for the Settings page.

**Subtasks:**
1. Mock `next-themes` `useTheme` hook
2. Test ThemeToggle renders three options
3. Test clicking each option calls `setTheme` with correct value
4. Test ARIA roles and attributes
5. Test SSR skeleton rendering (before mount)
6. Test Settings page renders Appearance section
7. Test Settings page includes ThemeToggle

**Acceptance Criteria:**
- [ ] All tests pass
- [ ] ThemeToggle has >= 90% code coverage
- [ ] Settings page integration test covers theme toggle presence
- [ ] No console warnings during test execution

---

### T8: Accessibility audit

**Estimated Effort:** 1-2 hours
**Agent:** accessibility-specialist
**Depends On:** T7
**Files Modified:** (varies based on findings)

**Description:**
Perform a comprehensive accessibility audit of the dark mode implementation, including both light and dark theme states.

**Subtasks:**
1. Run axe-core on Settings page in light mode
2. Run axe-core on Settings page in dark mode
3. Verify keyboard navigation of ThemeToggle (Tab, Enter, Space, Arrow keys)
4. Verify screen reader announcements for theme changes
5. Check all color contrast ratios in dark mode against WCAG AA
6. Verify focus indicators are visible in both modes
7. Fix any issues found

**Acceptance Criteria:**
- [ ] Zero axe-core violations in both light and dark modes
- [ ] All interactive elements keyboard-accessible
- [ ] Screen reader correctly announces theme selections
- [ ] All text meets WCAG AA contrast (4.5:1) in both modes
- [ ] All interactive elements meet WCAG AA contrast (3:1) in both modes
- [ ] Focus indicators visible in both modes

---

## Summary Table

| Task | Title | Effort | Agent | Depends On |
|------|-------|--------|-------|------------|
| T1 | Install next-themes | 15 min | frontend-developer | -- |
| T2 | Dark CSS variables | 1-2 hrs | ui-developer | T1 |
| T3 | ThemeProvider + layout | 30 min | frontend-developer | T1 |
| T4 | ThemeToggle component | 2-3 hrs | ui-developer | T3 |
| T5 | Settings page integration | 1-2 hrs | ui-developer | T4 |
| T6 | AppHeader dark mode | 1-2 hrs | ui-developer | T3 |
| T7 | Write tests | 2-3 hrs | nextjs-qa-developer | T4, T5, T6 |
| T8 | Accessibility audit | 1-2 hrs | accessibility-specialist | T7 |

**Critical Path:** T1 -> T3 -> T4 -> T5 -> T7 -> T8
**Parallelizable:** T2 and T3 can run in parallel after T1. T5 and T6 can run in parallel after T4/T3.

---

## Phase 2 Tasks (Future)

| Task | Title | Effort | Description |
|------|-------|--------|-------------|
| T9 | Add themePreference to User model | 1 hr | Add field to Prisma schema, create migration |
| T10 | API preferences endpoint | 2-3 hrs | Create PATCH /api/users/me/preferences |
| T11 | Sync theme with API | 1-2 hrs | On theme change, persist to API; on login, load from API |
| T12 | Header quick-toggle | 1-2 hrs | Sun/moon icon in AppHeader for quick theme switch |
| T13 | Login page dark mode | 1-2 hrs | Add dark: variants to login page |
| T14 | Full component audit | 3-4 hrs | Audit and migrate all components to support dark mode |
