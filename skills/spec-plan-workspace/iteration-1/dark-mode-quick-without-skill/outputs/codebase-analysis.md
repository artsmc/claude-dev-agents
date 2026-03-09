# Codebase Analysis: Dark Mode Readiness

**Date:** 2026-03-09
**Scope:** `/home/artsmc/applications/low-code/apps/web`

---

## 1. Files Examined

| File Path | Relevance |
|-----------|-----------|
| `apps/web/tailwind.config.ts` | Dark mode strategy configuration |
| `apps/web/src/app/globals.css` | CSS custom properties (light mode only) |
| `apps/web/src/app/layout.tsx` | Root layout, `<html>` element |
| `apps/web/src/app/providers.tsx` | Client providers (QueryClient only) |
| `apps/web/src/app/page.tsx` | Landing page (uses dark: variants) |
| `apps/web/src/app/(auth)/settings/page.tsx` | Settings page (stub) |
| `apps/web/src/app/login/page.tsx` | Login page (hardcoded light colors) |
| `apps/web/src/components/navigation/app-header.tsx` | Main nav (hardcoded light colors) |
| `apps/web/src/components/layouts/app-shell.tsx` | Placeholder |
| `apps/web/src/components/layouts/header.tsx` | Placeholder |
| `apps/web/src/components/layouts/sidebar.tsx` | Placeholder |
| `apps/web/src/store/auth.store.ts` | Auth store (stub) |
| `apps/web/src/middleware.ts` | Auth middleware (no theme impact) |
| `apps/web/src/types/api.types.ts` | API types (no theme field) |
| `apps/web/src/types/next-auth.d.ts` | Session types (no theme field) |
| `apps/web/src/lib/schemas/users.schema.ts` | User schema (no theme field) |
| `apps/web/package.json` | Dependencies (no next-themes) |
| `apps/api/prisma/schema.prisma` | Database schema (no user preferences) |
| `apps/api/src/schemas/organization.schema.ts` | Org schema (has branding, no theme) |
| `job-queue/product-forge/screens/08-settings.md` | Product spec for settings |

---

## 2. Dark Mode Infrastructure Status

### Already In Place

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| Tailwind darkMode config | Configured | `tailwind.config.ts` line 4 | `darkMode: ['class']` |
| CSS custom properties (light) | Defined | `globals.css` lines 5-35 | All shadcn/ui vars present |
| shadcn/ui color references | Used | `tailwind.config.ts` lines 103-119 | `hsl(var(--x))` pattern |
| dark: variant usage | Partial | `page.tsx` | Default Next.js landing page only |
| Body styled via CSS vars | Yes | `globals.css` lines 37-43 | `background`, `color`, `font-family` |

### Missing

| Item | Impact | Effort |
|------|--------|--------|
| `.dark` CSS variable block | Blocking -- no dark colors defined | 1-2 hours |
| `next-themes` package | Blocking -- no theme switching mechanism | 15 minutes |
| ThemeProvider in providers | Blocking -- no way to propagate theme | 30 minutes |
| `suppressHydrationWarning` on `<html>` | Blocking -- hydration errors without it | 5 minutes |
| ThemeToggle component | Blocking -- no UI to change theme | 2-3 hours |
| Settings page UI | Blocking -- current page is a stub | 1-2 hours |
| User.themePreference in Prisma | Non-blocking (Phase 2) | 1 hour |
| API preference endpoint | Non-blocking (Phase 2) | 2-3 hours |

---

## 3. Component-Level Dark Mode Readiness

### Color Strategy Analysis

The codebase uses three distinct color strategies:

**Strategy 1: CSS Custom Properties (Best for dark mode)**
Used in: `globals.css`, components referencing `bg-background`, `text-foreground`, `border-border`, etc.
Dark mode ready: Yes, once `.dark` block is added.

**Strategy 2: Tailwind Direct Color Classes (Needs migration)**
Used in: `app-header.tsx` (`bg-white`, `text-neutral-600`, `border-neutral-200`)
Dark mode ready: No -- requires `dark:` variants or migration to Strategy 1.

**Strategy 3: Custom Design Token Classes (Partially ready)**
Used in: `app-header.tsx` (`bg-cui`, `text-primary-700`, `bg-accent-blue`)
Dark mode ready: Depends on the token -- `bg-cui` should stay constant, others need `dark:` variants.

### Per-Component Status

| Component | Color Strategy | dark: variants | CSS vars | Migration Needed |
|-----------|---------------|----------------|----------|-----------------|
| Root Layout | CSS vars | N/A | Yes | No (add `suppressHydrationWarning`) |
| Home Page | Mixed | Yes (extensive) | Partial | Minimal |
| Login Page | Direct classes | None | None | Yes (add dark: variants) |
| AppHeader | Direct + tokens | None | None | Yes (high priority) |
| CUI Banner | Direct | None | None | No (keep as-is, government req) |
| AppShell | N/A | N/A | N/A | No (placeholder) |
| Header | N/A | N/A | N/A | No (placeholder) |
| Sidebar | N/A | N/A | N/A | No (placeholder) |
| Settings | N/A | N/A | N/A | No (being rebuilt) |

---

## 4. Product Spec Alignment

The product specification at `job-queue/product-forge/screens/08-settings.md` defines:

**Settings Navigation Hierarchy:**
```
Personal
  |- Profile
  |- Preferences (theme, notifications)  <-- Dark mode goes here
  |- Notifications

Organization (Admin only)
  |- General
  |- Team
  |- Security
  |- Billing

Platform (Admin only)
  |- API Keys
  |- Audit Logs
  |- Compliance
```

The "Preferences" section is explicitly listed with "theme" as a sub-item, confirming this feature aligns with the existing product specification.

---

## 5. Dependency Analysis

### Direct Dependencies (web app)

| Package | Current Version | Dark Mode Relevance |
|---------|----------------|-------------------|
| next | 16.1.6 | `next-themes` v0.4+ compatible |
| react | 19.2.3 | Full support |
| tailwindcss | ^3.4.19 | `darkMode: ['class']` already set |
| tailwindcss-animate | ^1.0.7 | Works with dark mode |
| zustand | ^5.0.11 | Not needed (next-themes handles state) |

### New Dependency Required

| Package | Version | Size | Weekly Downloads |
|---------|---------|------|-----------------|
| next-themes | ^0.4.4 | 6.5 KB (gzip) | ~4.5M |

---

## 6. Risk Assessment

| Risk | Severity | Probability | Notes |
|------|----------|-------------|-------|
| AppHeader looks broken in dark mode | Medium | High | Hardcoded white/neutral colors will look wrong |
| Login page looks broken in dark mode | Medium | Medium | Hardcoded light colors, but user may not notice immediately (login is before settings) |
| FOUC on first load | Low | Low | `next-themes` handles this well |
| Hydration mismatch errors | Low | Low | `suppressHydrationWarning` prevents this |
| WCAG contrast violations in dark mode | Medium | Medium | Need to verify all dark color combinations |
| Future components forget dark mode | Low | High | Establish a convention/checklist for new components |
