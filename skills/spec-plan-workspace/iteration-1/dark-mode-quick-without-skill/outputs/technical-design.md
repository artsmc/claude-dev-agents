# Technical Design: Dark Mode Toggle

**Feature ID:** FEAT-DM-001
**Date:** 2026-03-09

---

## 1. Implementation Architecture

### 1.1 Dependency: `next-themes`

```bash
cd /home/artsmc/applications/low-code
npm install next-themes --workspace=apps/web
```

`next-themes` (v0.4+) provides:
- Automatic `class` or `data-theme` attribute on `<html>`
- FOUC prevention via inline script injection
- localStorage persistence (key: `theme`)
- System preference detection via `prefers-color-scheme`
- SSR-safe with `suppressHydrationWarning`

### 1.2 Provider Integration

**File:** `/home/artsmc/applications/low-code/apps/web/src/app/providers.tsx`

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
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
    >
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

### 1.3 Root Layout Update

**File:** `/home/artsmc/applications/low-code/apps/web/src/app/layout.tsx`

Add `suppressHydrationWarning` to `<html>` to prevent React hydration mismatch warnings from `next-themes` injecting the theme class before React hydrates:

```tsx
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### 1.4 Dark Mode CSS Variables

**File:** `/home/artsmc/applications/low-code/apps/web/src/app/globals.css`

Append after the existing `:root` block:

```css
.dark {
  /* Background colors */
  --background: 222 47% 11%;       /* primary-900 #0F172A */
  --foreground: 210 40% 98%;       /* primary-50  #F8FAFC */

  /* Surface colors */
  --surface-primary: 217 33% 17%;  /* #1E293B dark card */
  --surface-secondary: 222 47% 13%; /* slightly lighter than bg */

  /* Text colors */
  --text-primary: 210 40% 98%;     /* primary-50 for headings */
  --text-secondary: 215 20% 65%;   /* lightened body text */
  --text-muted: 215 16% 57%;       /* lightened muted text */

  /* Border colors */
  --border: 217 33% 25%;           /* darkened borders */
  --border-input: 217 33% 30%;     /* darkened input borders */

  /* shadcn/ui compatibility */
  --card: 217 33% 17%;
  --card-foreground: 210 40% 98%;
  --muted: 217 33% 20%;
  --muted-foreground: 215 20% 65%;
  --popover: 217 33% 17%;
  --popover-foreground: 210 40% 98%;
  --input: 217 33% 30%;
  --ring: 217 91% 60%;             /* accent-blue stays for focus */

  --radius: 6px;
}
```

Add a smooth transition to body:

```css
body {
  background: hsl(var(--background));
  color: hsl(var(--foreground));
  font-family: 'Public Sans', Arial, Helvetica, sans-serif;
  font-size: 0.875rem;
  line-height: 1.5;
  transition: background-color 0.15s ease, color 0.15s ease;
}
```

---

## 2. Component Design

### 2.1 ThemeToggle Component

**File:** `/home/artsmc/applications/low-code/apps/web/src/components/settings/theme-toggle.tsx`

```tsx
'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

type ThemeOption = 'light' | 'system' | 'dark';

interface ThemeOptionConfig {
  value: ThemeOption;
  label: string;
  icon: React.ReactNode;
}

const themeOptions: ThemeOptionConfig[] = [
  {
    value: 'light',
    label: 'Light',
    icon: <SunIcon />,
  },
  {
    value: 'system',
    label: 'System',
    icon: <MonitorIcon />,
  },
  {
    value: 'dark',
    label: 'Dark',
    icon: <MoonIcon />,
  },
];

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch -- only render after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Render a placeholder with same dimensions to avoid CLS
    return (
      <div className="flex gap-1 rounded-lg bg-muted p-1 h-10 w-[280px]" />
    );
  }

  return (
    <div
      role="radiogroup"
      aria-label="Theme preference"
      className="flex gap-1 rounded-lg bg-muted p-1"
    >
      {themeOptions.map((option) => {
        const isSelected = theme === option.value;
        return (
          <button
            key={option.value}
            role="radio"
            aria-checked={isSelected}
            aria-label={`${option.label} mode`}
            onClick={() => setTheme(option.value)}
            className={`
              flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium
              transition-all duration-150 focus:outline-none focus:ring-2
              focus:ring-ring focus:ring-offset-2 focus:ring-offset-background
              ${isSelected
                ? 'bg-background text-foreground shadow-soft-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
              }
            `}
          >
            {option.icon}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

// --- Icon Components ---

function SunIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  );
}

function MonitorIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
      />
    </svg>
  );
}
```

### 2.2 Updated Settings Page

**File:** `/home/artsmc/applications/low-code/apps/web/src/app/(auth)/settings/page.tsx`

```tsx
import { Metadata } from 'next';
import { ThemeToggle } from '@/components/settings/theme-toggle';

export const metadata: Metadata = {
  title: 'Settings | FORGE',
  description: 'Manage your FORGE preferences and account settings',
};

export default function SettingsPage() {
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-h2 font-bold text-foreground mb-8">Settings</h1>

      {/* Preferences Section */}
      <section aria-labelledby="preferences-heading" className="mb-10">
        <h2
          id="preferences-heading"
          className="text-h3 font-semibold text-foreground mb-6"
        >
          Preferences
        </h2>

        {/* Appearance */}
        <div className="bg-card rounded-lg border border-border p-6">
          <h3 className="text-base font-medium text-foreground mb-2">
            Appearance
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            Choose how FORGE looks to you. Select a theme or sync with your
            operating system setting.
          </p>

          <ThemeToggle />

          <p className="text-xs text-muted-foreground mt-3">
            &ldquo;System&rdquo; follows your device&rsquo;s appearance setting.
          </p>
        </div>
      </section>
    </div>
  );
}
```

---

## 3. Component Dark Mode Audit

The following existing components need `dark:` variant additions or CSS variable migration:

### 3.1 High Priority (Visible in core layout)

| Component | File | Current Issue | Fix |
|-----------|------|---------------|-----|
| AppHeader | `src/components/navigation/app-header.tsx` | Hardcoded `bg-white`, `text-neutral-*`, `border-neutral-200` | Replace with `bg-card`, `text-foreground`, `border-border` or add `dark:` variants |
| CUI Banner | `app-header.tsx` line 25 | `bg-cui text-white` | **Keep as-is** -- government branding must remain unchanged |
| Settings page | `settings/page.tsx` | Stub | Replaced in this feature |

### 3.2 Medium Priority (Login and standalone pages)

| Component | File | Current Issue | Fix |
|-----------|------|---------------|-----|
| LoginPage | `src/app/login/page.tsx` | Hardcoded `bg-primary-50`, `bg-white`, `text-neutral-*` | Add `dark:` variants |
| LoginButtons | `src/components/auth/login-buttons.tsx` | Unknown (needs audit) | Add `dark:` variants |

### 3.3 Low Priority (Placeholder components)

| Component | File | Current Issue |
|-----------|------|---------------|
| AppShell | `layouts/app-shell.tsx` | Placeholder -- no real content |
| Header | `layouts/header.tsx` | Placeholder -- no real content |
| Sidebar | `layouts/sidebar.tsx` | Placeholder -- no real content |

---

## 4. Testing Strategy

### 4.1 Unit Tests

```typescript
// __test__/components/settings/theme-toggle.test.tsx

describe('ThemeToggle', () => {
  it('renders three theme options (Light, System, Dark)');
  it('marks the current theme as selected (aria-checked)');
  it('calls setTheme when an option is clicked');
  it('has proper radiogroup role and aria-label');
  it('renders placeholder skeleton before mount (SSR safety)');
});
```

### 4.2 Integration Tests

```typescript
describe('Settings > Preferences', () => {
  it('renders the Appearance section with ThemeToggle');
  it('changing theme adds/removes .dark class on <html>');
  it('theme persists in localStorage after selection');
  it('System mode resolves to dark when OS prefers dark');
});
```

### 4.3 Accessibility Tests

```typescript
describe('ThemeToggle a11y', () => {
  it('passes axe accessibility audit');
  it('is keyboard navigable (Tab focuses, Enter/Space selects)');
  it('announces selected state to screen reader');
  it('maintains WCAG AA contrast in both light and dark modes');
});
```

### 4.4 Visual Regression

- Screenshot comparison in light mode vs dark mode for:
  - Settings page
  - AppHeader
  - Login page
  - Dashboard (when implemented)

---

## 5. Migration Path for Existing Components

For components that use hardcoded colors (not CSS variables), the recommended migration approach is:

### Pattern A: Replace with semantic CSS variables (Preferred)

```tsx
// Before:
<header className="bg-white border-b border-neutral-200">

// After:
<header className="bg-card border-b border-border">
```

### Pattern B: Add dark: variants (For custom colors)

```tsx
// Before:
<div className="bg-primary-50 text-neutral-900">

// After:
<div className="bg-primary-50 dark:bg-primary-900 text-neutral-900 dark:text-neutral-50">
```

### Pattern C: Keep unchanged (Government/compliance elements)

```tsx
// CUI banner -- never changes
<div className="bg-cui text-white">CUI</div>
```

---

## 6. Rollout Strategy

### Phase 1 (This Feature)

1. Install `next-themes`
2. Add dark CSS variables to `globals.css`
3. Integrate `ThemeProvider` in `providers.tsx`
4. Add `suppressHydrationWarning` to root `<html>`
5. Build `ThemeToggle` component
6. Update Settings page with Preferences section
7. Migrate `AppHeader` to use CSS variables / dark variants
8. localStorage persistence (automatic via `next-themes`)

### Phase 2 (Follow-up)

1. Add `themePreference` field to User model in Prisma schema
2. Create `PATCH /api/users/me/preferences` endpoint
3. Sync localStorage with API on login/change
4. Add quick-toggle icon in AppHeader
5. Migrate remaining components (Login, Dashboard) to dark mode
6. Dark mode color audit with WCAG contrast checker
