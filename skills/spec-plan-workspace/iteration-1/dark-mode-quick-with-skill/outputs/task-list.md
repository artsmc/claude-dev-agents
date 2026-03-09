# Task List: Dark Mode Toggle

## Feature Summary

Add a dark mode toggle to the web app settings page, allowing users to switch between light, dark, and system-preferred color schemes. The app already uses Tailwind CSS with `darkMode: ['class']` enabled and a shadcn/ui-style HSL CSS variable system in `globals.css`. Implementation requires installing `next-themes` for SSR-safe theme management, defining dark mode CSS variable values, wrapping the app in a `ThemeProvider`, and building a toggle component on the settings page. The preference persists in `localStorage` automatically via `next-themes`.

---

## Phase 1: Setup

### Task 1: Install `next-themes` dependency

**Action:** Add the `next-themes` package to the web app.
**File(s):** `/home/artsmc/applications/low-code/apps/web/package.json`
**Command:** `cd /home/artsmc/applications/low-code && npm install next-themes --workspace=apps/web`
**Pattern:** Standard npm dependency addition. `next-themes` is the de facto theme library for Next.js (handles SSR, FOUC prevention, localStorage, system preference detection).
**Dependencies:** None (first task).
**Agent:** `frontend-developer`

---

## Phase 2: Implementation

### Task 2: Add dark mode CSS variables to `globals.css`

**Action:** Add a `.dark` selector block in `globals.css` with inverted HSL values for all existing `:root` CSS custom properties. The dark palette should use the existing `primary` slate scale in reverse (dark backgrounds from `primary-900`/`primary-800`, light text from `primary-50`/`primary-100`).
**File(s):** `/home/artsmc/applications/low-code/apps/web/src/app/globals.css`
**Pattern:** Mirror the existing `:root` block. Each CSS variable gets a dark-mode counterpart. Example:
```css
.dark {
  --background: 222 47% 11%;      /* primary-900 (was primary-50) */
  --foreground: 210 40% 98%;      /* primary-50 (was primary-900) */
  --surface-primary: 215 28% 17%; /* dark card surface */
  --surface-secondary: 217 33% 13%; /* darker subtle bg */
  --card: 215 28% 17%;
  --card-foreground: 210 40% 98%;
  --muted: 217 33% 17%;
  --muted-foreground: 215 20% 65%;
  --popover: 215 28% 17%;
  --popover-foreground: 210 40% 98%;
  --border: 217 33% 25%;
  --input: 217 33% 25%;
  --ring: 217 91% 60%;
  /* etc. */
}
```
**Constraint:** All color combinations must meet WCAG 2.1 AA contrast ratios (4.5:1 normal text, 3:1 large text). Validate with a contrast checker tool.
**Dependencies:** None (can be done in parallel with Task 1).
**Agent:** `ui-developer`

### Task 3: Integrate `ThemeProvider` into the app Providers

**Action:** Wrap the app with `next-themes` `ThemeProvider` inside the existing `Providers` component. Configure it with `attribute="class"` (to match Tailwind's class-based dark mode), `defaultTheme="system"`, and `enableSystem={true}`.
**File(s):**
- `/home/artsmc/applications/low-code/apps/web/src/app/providers.tsx` -- Add ThemeProvider wrapping
- `/home/artsmc/applications/low-code/apps/web/src/app/layout.tsx` -- Add `suppressHydrationWarning` to `<html>` tag
**Pattern:**
```tsx
// providers.tsx - add ThemeProvider from next-themes
import { ThemeProvider } from 'next-themes';

export function Providers({ children }: { children: ReactNode }) {
  // ... existing QueryClient setup ...
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryClientProvider client={queryClient}>
        {children}
        {/* ... devtools ... */}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
```
```tsx
// layout.tsx - add suppressHydrationWarning
<html lang="en" suppressHydrationWarning>
```
**Why `suppressHydrationWarning`:** `next-themes` injects a script that sets the `class` attribute on `<html>` before React hydrates. Without this attribute, React logs a hydration mismatch warning.
**Dependencies:** Depends on Task 1 (`next-themes` must be installed).
**Agent:** `frontend-developer`

### Task 4: Build the theme toggle component

**Action:** Create a `ThemeToggle` component that allows users to select between "Light", "Dark", and "System" themes. Use `useTheme()` hook from `next-themes`.
**File(s):** `/home/artsmc/applications/low-code/apps/web/src/components/settings/theme-toggle.tsx` (new file)
**Pattern:** A simple client component (`'use client'`) with three buttons or a select/radio group. Use existing Tailwind utility classes and follow the project's component patterns. The component should:
- Show the current active theme (highlighted/selected state)
- Provide three options: Light, Dark, System
- Use `setTheme('light' | 'dark' | 'system')` from `useTheme()`
- Handle the `mounted` state to prevent hydration mismatch (standard `next-themes` pattern: don't render theme-dependent UI until `mounted` is `true`)
**Dependencies:** Depends on Task 1 (`next-themes` must be installed).
**Agent:** `ui-developer`

### Task 5: Add the toggle to the settings page

**Action:** Update the settings page to include the `ThemeToggle` component with proper page layout (heading, description, grouped settings sections).
**File(s):** `/home/artsmc/applications/low-code/apps/web/src/app/(auth)/settings/page.tsx`
**Pattern:** Replace the stub `<h1>Settings</h1>` with a structured settings page. Group the theme toggle under an "Appearance" section. Follow the app's existing page layout patterns (container widths, heading styles, spacing).
```tsx
export default function Settings() {
  return (
    <div className="container max-w-2xl py-8">
      <h1 className="text-h2 font-bold mb-6">Settings</h1>
      <section className="space-y-6">
        <div>
          <h2 className="text-h3 font-semibold mb-2">Appearance</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Customize the look and feel of the application.
          </p>
          <ThemeToggle />
        </div>
      </section>
    </div>
  );
}
```
**Dependencies:** Depends on Task 4 (ThemeToggle component must exist).
**Agent:** `ui-developer`

---

## Phase 3: Verification

### Task 6: Manual testing and contrast verification

**Action:** Test the dark mode toggle across the application:
1. Verify toggle works: Light -> Dark -> System transitions are instant (no FOUC)
2. Verify localStorage persistence: theme preference survives page reload and new tabs
3. Verify system preference: "System" mode follows OS dark/light preference
4. Verify no hydration warnings in browser console
5. Spot-check key pages (dashboard, settings, login) for contrast issues in dark mode
6. Run a contrast checker on critical text/background combinations in dark mode to confirm WCAG AA compliance
**File(s):** No file changes -- testing only.
**Dependencies:** Depends on Tasks 2, 3, 4, 5 (all implementation complete).
**Agent:** `frontend-developer` or `qa-engineer`

---

## Dependency Graph

```
Task 1 (install next-themes)
  |
  +---> Task 3 (ThemeProvider integration)
  |         |
  |         +---> Task 5 (settings page update) ---> Task 6 (testing)
  |
  +---> Task 4 (ThemeToggle component)
              |
              +---> Task 5 (settings page update) ---> Task 6 (testing)

Task 2 (dark CSS variables) --- can run in parallel with Tasks 1, 3, 4
              |
              +---> Task 6 (testing)
```

## Notes

- **Total tasks: 6** (at the upper boundary for QUICK tier; scope is well-defined and uses a standard pattern, so this remains appropriate)
- **No API changes required** -- theme preference is stored in localStorage via `next-themes`
- **Future enhancement:** If theme preference needs to sync across devices, a later sprint could add a user preferences API endpoint and store the preference server-side. That would bump this to STANDARD tier.
- **Existing Tailwind config advantage:** `darkMode: ['class']` is already configured, so all existing `dark:` utility classes will work immediately once the ThemeProvider is in place.
