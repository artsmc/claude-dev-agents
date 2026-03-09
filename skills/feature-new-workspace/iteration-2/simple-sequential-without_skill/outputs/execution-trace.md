# Execution Plan: Dark Mode Toggle for AIForge Web App

**Task:** Add a dark mode toggle to the AIForge web app
**Date:** 2026-03-09
**Approach:** Simple sequential (no skill invoked)

---

## 1. First Action

Before writing a single line of code, do a focused codebase reconnaissance to understand what already exists and what constraints apply.

Specifically:

- Read `tailwind.config.ts` to check if `darkMode` is configured. (Finding: `darkMode: ['class']` is already set — Tailwind's class-based dark mode is enabled.)
- Read `src/app/globals.css` to see if dark-mode CSS variables are defined. (Finding: Only light-mode CSS custom properties are defined under `:root`. No `.dark {}` block exists.)
- Read `src/app/layout.tsx` to understand how the `<html>` element is managed. (Finding: Static `<html lang="en">`, no `suppressHydrationWarning`, no theme class applied.)
- Read `src/app/providers.tsx` to understand the provider tree. (Finding: Only `QueryClientProvider` is present — no theme provider.)
- Read `src/components/navigation/app-header.tsx` to identify where a toggle button would live. (Finding: Header has user controls area with bell, settings, and avatar buttons — ideal location for a mode toggle button.)
- Read `src/store/auth.store.ts` to understand the Zustand pattern used. (Finding: Minimal stub — a new theme store using the same Zustand v5 pattern would be clean and consistent.)
- Check `package.json` for `next-themes`. (Finding: Not installed — must either install it or build a lightweight custom solution using Zustand + `localStorage`.)

This reconnaissance takes approximately 10 minutes and produces a clear picture of the gap: Tailwind is ready, but the persistence layer, CSS variables, and UI component are all missing.

---

## 2. Steps to Plan and Build

### Phase 1 — Architecture Decision (10 min)

Decide between two approaches before touching any file:

**Option A: Install `next-themes`**
- Pros: Handles SSR hydration flash, `localStorage` persistence, and system preference detection automatically. Widely adopted with Next.js App Router.
- Cons: Adds a dependency; requires wrapping providers with `ThemeProvider`.

**Option B: Custom Zustand store + `useEffect`**
- Pros: No extra dependency, consistent with existing Zustand v5 pattern in `auth.store.ts`.
- Cons: Requires manually handling the hydration flash (flicker on page load), system preference media query, and `localStorage` sync. More code, more edge cases.

**Decision:** Use `next-themes`. The hydration flash problem in Next.js App Router is non-trivial and `next-themes` solves it correctly. The project already uses external libraries for other concerns (TanStack Query, Zustand, shadcn/ui). A single focused dependency is appropriate.

---

### Phase 2 — Implementation (ordered task list)

Each step is a discrete, reviewable change. No step should be combined with another.

#### Step 1: Install `next-themes`

```bash
cd /home/artsmc/applications/low-code
npm install next-themes --workspace=apps/web
```

Verify: `apps/web/package.json` lists `next-themes` in `dependencies`.

#### Step 2: Add dark-mode CSS variables to `globals.css`

File: `/home/artsmc/applications/low-code/apps/web/src/app/globals.css`

Add a `.dark` block after the `:root` block that overrides all CSS custom properties:

```css
.dark {
  /* Background colors */
  --background: 222 47% 11%;   /* deep slate, maps to primary-900 */
  --foreground: 210 40% 98%;   /* near-white text */

  /* Surface colors */
  --surface-primary: 215 28% 17%;   /* dark card surface */
  --surface-secondary: 215 25% 14%; /* subtler dark background */

  /* Text colors */
  --text-primary: 210 40% 96%;
  --text-secondary: 214 32% 75%;
  --text-muted: 215 20% 60%;

  /* Border colors */
  --border: 215 25% 25%;
  --border-input: 215 20% 32%;

  /* shadcn/ui compatibility */
  --card: 215 28% 17%;
  --card-foreground: 210 40% 98%;
  --muted: 215 25% 20%;
  --muted-foreground: 214 32% 75%;
  --popover: 215 28% 17%;
  --popover-foreground: 210 40% 98%;
  --input: 215 20% 32%;
  --ring: 217 91% 60%;
}
```

Rationale: Only CSS variables need to change. Components already use `bg-background`, `text-foreground`, `border`, etc. from `tailwind.config.ts`, which all reference these variables. No component-level class changes are needed for base colors.

Special case: Hard-coded color classes like `bg-white`, `bg-primary-50`, `text-neutral-900` in existing components will need manual `dark:` variants added in Step 6.

#### Step 3: Update `layout.tsx` to add `ThemeProvider` and `suppressHydrationWarning`

File: `/home/artsmc/applications/low-code/apps/web/src/app/layout.tsx`

```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AIForge",
  description: "AI Agent Builder Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

The `suppressHydrationWarning` on `<html>` is required by `next-themes` to prevent React hydration mismatch warnings when the class is injected before hydration.

#### Step 4: Add `ThemeProvider` to `providers.tsx`

File: `/home/artsmc/applications/low-code/apps/web/src/app/providers.tsx`

```tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from 'next-themes';
import { useState } from 'react';
import type { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            gcTime: 300_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryClientProvider client={queryClient}>
        {children}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
```

Key props:
- `attribute="class"` — tells `next-themes` to toggle the `dark` class on `<html>`, which is what Tailwind's `darkMode: ['class']` expects.
- `defaultTheme="system"` — respects OS preference on first visit.
- `enableSystem` — allows the "system" theme option.
- `disableTransitionOnChange` — prevents color flash during transition, appropriate for a government/enterprise app.

#### Step 5: Create the `DarkModeToggle` component

File to create: `/home/artsmc/applications/low-code/apps/web/src/components/navigation/dark-mode-toggle.tsx`

```tsx
'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

/**
 * DarkModeToggle
 *
 * Renders a sun/moon icon button that cycles: light → dark → system.
 * Uses next-themes for SSR-safe hydration.
 * Accessible: includes aria-label and aria-pressed.
 */
export function DarkModeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch — render nothing until mounted
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button
        className="w-8 h-8 rounded flex items-center justify-center text-neutral-600"
        aria-label="Toggle color theme"
        disabled
      >
        <PlaceholderIcon />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  const handleToggle = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  return (
    <button
      onClick={handleToggle}
      className="w-8 h-8 rounded flex items-center justify-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-pressed={isDark}
      title={theme === 'system' ? 'System theme (click for light)' : isDark ? 'Dark mode (click for system)' : 'Light mode (click for dark)'}
    >
      {isDark ? <MoonIcon /> : <SunIcon />}
    </button>
  );
}

function SunIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  );
}

function PlaceholderIcon() {
  return <span className="w-5 h-5 block" aria-hidden="true" />;
}
```

The `mounted` guard is the standard pattern for `next-themes` in Next.js App Router to prevent hydration mismatch. Before mount, a disabled placeholder button is rendered at the same size to avoid layout shift.

#### Step 6: Add the toggle to `AppHeader`

File: `/home/artsmc/applications/low-code/apps/web/src/components/navigation/app-header.tsx`

Insert `<DarkModeToggle />` into the "User Controls" div, between the notifications bell and the settings icon. Also add `dark:` variants to the hard-coded light-only classes:

Changes:
1. Import `DarkModeToggle`.
2. Add `dark:bg-neutral-900 dark:border-neutral-700` to the header element.
3. Insert `<DarkModeToggle />` in the user controls section.
4. Add `dark:text-neutral-400 dark:hover:text-neutral-100` to bell and settings buttons.

#### Step 7: Audit hard-coded color classes across all pages

Run a targeted search for classes that will not respond to the `.dark` selector:

```bash
grep -r "bg-white\|bg-primary-50\|text-neutral-900\|bg-neutral-200\|border-neutral-200" \
  /home/artsmc/applications/low-code/apps/web/src --include="*.tsx" -l
```

Affected files from reconnaissance:
- `app/(auth)/dashboard/page.tsx` — `bg-primary-50`, `text-neutral-900`, `text-neutral-600`
- `app/(auth)/agents/new/page.tsx` — `bg-primary-50`, `bg-white`, `border-neutral-200`
- `components/navigation/app-header.tsx` — `bg-white`, `border-neutral-200`
- `components/dashboard/AgentCard.tsx` — card surface colors
- `components/dashboard/StatCard.tsx` — card surface colors

For each, add `dark:` prefixed equivalents. Example:
```
bg-primary-50 → bg-primary-50 dark:bg-primary-900
bg-white → bg-white dark:bg-primary-800
text-neutral-900 → text-neutral-900 dark:text-neutral-100
border-neutral-200 → border-neutral-200 dark:border-primary-700
```

#### Step 8: Handle CUI banner in dark mode

The CUI banner (`bg-cui text-white`) is a government compliance element. It must remain visually prominent in dark mode. The existing `bg-cui` (`#2F7C31`) is acceptable on dark backgrounds. No change needed, but explicitly document this decision.

---

### Phase 3 — Testing (30 min)

Manual verification checklist:
1. Start the dev server: `cd /home/artsmc/applications/low-code && npm run dev:web`
2. Navigate to `http://localhost:3500/dashboard`
3. Click the toggle button: verify dark mode activates (`.dark` class on `<html>`)
4. Refresh the page: verify preference persists (no flash, correct theme on load)
5. Click through: light → dark → system and back
6. Set OS to dark mode, set app to "system": verify it matches OS
7. Navigate to `/agents/new` and `/login`: verify no unstyled white surfaces bleed through
8. Open browser devtools, inspect `<html>` class attribute as you toggle
9. Check `localStorage`: `theme` key should be `"light"`, `"dark"`, or `"system"`
10. Accessibility: tab to the toggle, press Enter, verify aria-label updates

Automated tests to write (deferred, not blocking):
- Unit test `DarkModeToggle` with `next-themes` mocked: verify correct `setTheme` calls
- Snapshot tests for header in light and dark modes

---

## 3. How the Work is Organized

This is a **single-app, frontend-only** change confined entirely to `apps/web`. No API changes are needed. No Mastra or Microsandbox changes are needed.

Work is organized as a sequential set of 8 discrete steps, each touching one concern:

| Step | Concern | Files Changed | Estimated Time |
|------|---------|---------------|----------------|
| 1 | Dependency | `package.json`, `package-lock.json` | 2 min |
| 2 | CSS variables | `globals.css` | 10 min |
| 3 | HTML root hydration | `layout.tsx` | 3 min |
| 4 | Theme provider | `providers.tsx` | 5 min |
| 5 | Toggle component | `dark-mode-toggle.tsx` (new file) | 15 min |
| 6 | Header integration | `app-header.tsx` | 10 min |
| 7 | Hard-coded color audit | multiple `.tsx` files | 30 min |
| 8 | Manual testing | — | 30 min |

**Total estimated time:** ~1.5 hours

The ordering is deliberate: infrastructure before UI, UI before integration, integration before audit. Steps 1-4 are reversible without UI regression. Step 5 can be developed and tested in isolation. Step 7 is the widest step and can be batched as a single PR or split per-page.

---

## 4. What Skills/Tools Would Be Used

No special skills are available for this task per the task instruction. Working with general tools only.

**If skills were available**, the ideal invocation would be:

- `spec-plan` skill (quick tier) — confirm scope: single app, <5 tasks, known pattern. Produces a task list only, skips FRD/TR. Saves ~45% tokens on planning overhead.
- `feature-new` skill — orchestrates full feature workflow with PM-DB tracking, phase gates, and execution.
- `start-phase-execute` skill — structures the implementation with quality gates (lint, typecheck, build) between phases.

**Agents that would be spawned (per CLAUDE.md):**

Since this task touches only `apps/web` and is a single concern (frontend UI + state), a **single specialized agent** is appropriate rather than a team:

- `ui-developer` agent — handles React component creation (`DarkModeToggle`), TSX, Tailwind dark mode classes, and visual integration into the header.
- `frontend-developer` agent — optionally in parallel: handles the Zustand/provider changes and hydration concerns.

The `security-auditor` agent would NOT be needed — this feature has no authentication, RBAC, or data access implications. The `database-schema-specialist` would NOT be needed — no database changes.

**Tools used during reconnaissance (already done):**
- `Read` — for direct file reads of known paths
- `Bash` — for `find` to discover TSX file locations, `grep` to locate hard-coded color classes, `cat` as needed
- `Glob` — for pattern-based file discovery

---

## 5. What to Do If Something Failed

### Failure: Hydration flash / flicker on page load

**Symptom:** Page briefly shows light mode before switching to dark on load.
**Diagnosis:** `next-themes` requires `suppressHydrationWarning` on `<html>`. Missing it, or missing the `mounted` guard in `DarkModeToggle`, causes the flash.
**Fix:** Ensure `suppressHydrationWarning` is on `<html>` in `layout.tsx`. Ensure the toggle renders a neutral placeholder (not theme-specific icons) before `mounted === true`.
**Fallback:** If the flash persists, add a blocking script in `<head>` that reads `localStorage` and sets the class before React hydrates — this is the `next-themes` standard recommendation and is handled automatically when the library is configured correctly.

---

### Failure: TypeScript errors after installing `next-themes`

**Symptom:** `Cannot find module 'next-themes'` or type errors on `useTheme`.
**Diagnosis:** Types may not be included in the package or tsconfig path resolution may be wrong in the monorepo.
**Fix:**
```bash
npm install --save-dev @types/next-themes --workspace=apps/web
# If types are bundled (they are in next-themes 0.3+), check tsconfig.json includes:
# "moduleResolution": "bundler" or "node16"
```
Also verify `tsconfig.json` in `apps/web` does not exclude `node_modules/next-themes`.

---

### Failure: Dark mode classes not applying (components stay light)

**Symptom:** Toggle works (class appears on `<html>`), but components don't change color.
**Diagnosis 1:** The component uses hard-coded Tailwind classes (`bg-white`) instead of semantic variables (`bg-background`). These do not respond to `.dark` automatically.
**Fix 1:** Complete Step 7 audit — add `dark:` variants to all hard-coded classes.
**Diagnosis 2:** Tailwind's JIT engine did not scan the component for `dark:` classes because the file is outside the `content` globs in `tailwind.config.ts`.
**Fix 2:** Verify `tailwind.config.ts` content array includes `'./src/components/**/*.{ts,tsx}'` — it does (confirmed in reconnaissance). No change needed.
**Diagnosis 3:** CSS variable `.dark {}` block was added incorrectly (wrong selector, typo).
**Fix 3:** Use browser devtools to inspect `<html class="dark">` and verify CSS variables are overridden under `Computed` styles.

---

### Failure: Preference does not persist across page refreshes

**Symptom:** User sets dark mode, refreshes, returns to light mode.
**Diagnosis:** `localStorage` is blocked (private browsing, browser policy) or `next-themes` is not configured with `storageKey`.
**Fix:** Check `localStorage.getItem('theme')` in browser devtools. If blocked, gracefully degrade — the toggle still works per-session. If not blocked, verify `ThemeProvider` is not being unmounted and remounted on navigation (should not happen with App Router `providers.tsx` placement).

---

### Failure: CUI banner or compliance elements look wrong in dark mode

**Symptom:** The green CUI banner (`bg-cui`) appears washed out or inaccessible against dark backgrounds.
**Diagnosis:** Dark background reduces contrast ratio against `#2F7C31`.
**Fix:** Add `dark:bg-cui-dark` class to the CUI banner div (the `.dark` variant `#1F5521` is already defined in `tailwind.config.ts`). Re-verify WCAG AA contrast ratio with a tool like `https://webaim.org/resources/contrastchecker/`.
**Compliance note:** For a FedRAMP-scoped app, document this decision in the relevant screen spec under `/home/artsmc/applications/low-code/job-queue/product-forge/`.

---

### Failure: Build fails after changes

**Symptom:** `npm run build:web` fails with TypeScript or Next.js errors.
**Diagnosis:** Likely a missing import, incorrect type, or JSX error in the new component.
**Fix procedure:**
1. Run `nx run web:typecheck` first — faster than a full build, surfaces type errors immediately.
2. Run `nx run web:lint` — catches import issues and unused variables.
3. Fix reported errors, then re-run build.
4. If build fails on `next-themes` server import: ensure the `DarkModeToggle` component has `'use client'` directive (it does — it uses `useTheme` and `useState`).

---

### Failure: Test suite breaks

**Symptom:** Existing Jest tests fail after changes to `providers.tsx` or `layout.tsx`.
**Diagnosis:** Tests that render `Providers` directly may not mock `next-themes`.
**Fix:** Add a mock in `apps/web/__mocks__/next-themes.ts`:
```ts
export const useTheme = () => ({
  theme: 'light',
  setTheme: jest.fn(),
  resolvedTheme: 'light',
});
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return children;
}
```
Register in `jest.setup.ts`:
```ts
jest.mock('next-themes');
```

---

## Summary

The dark mode toggle is a well-scoped, single-app feature. The hardest part is not the toggle button itself — it is ensuring no hard-coded color classes bleed through in dark mode (Step 7) and that the hydration experience is correct on first load. Both are solvable with established patterns. The work is sequential, reviewable step-by-step, and estimated at 1.5 hours of focused implementation.
