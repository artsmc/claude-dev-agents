# Accessibility Specialist — Testing Module

Load this module when you need the complete manual testing checklist, screen reader testing commands, or automated testing code (jest-axe, cypress-axe, Pa11y CI).

---

## Manual Testing Checklist

Run this checklist before signing off any component or page as accessible.

### Keyboard Navigation

- [ ] Tab visits every interactive element in a logical, visual order
- [ ] Shift+Tab navigates backwards through the same order
- [ ] Enter activates links and submits forms; Space activates buttons
- [ ] Arrow keys navigate within widget groups (menu items, radio groups, tabs, listbox options)
- [ ] Escape closes all modals, dropdowns, and drawers
- [ ] Focus indicator is clearly visible on every focusable element
- [ ] No keyboard trap — Tab or Escape always exits every component
- [ ] Skip link appears on first Tab press and jumps focus to `#main-content`

### Screen Reader Testing

Test with at least one screen reader. NVDA + Firefox (Windows) and VoiceOver + Safari (macOS) cover the largest user populations.

- [ ] All meaningful content is announced (no silent elements)
- [ ] Heading structure creates a navigable outline (use SR heading navigation)
- [ ] Landmarks are announced and usable for navigation
- [ ] Form fields announce their label, type, and any error when focused
- [ ] Error messages are announced immediately when they appear (role="alert")
- [ ] Dynamic content changes are announced (aria-live regions firing)
- [ ] Images announce appropriate alt text (or are silenced for decorative)
- [ ] Buttons and links have meaningful names (not "click here" or "button")
- [ ] Custom widgets (tabs, dropdowns, accordions) announce state changes

### Screen Reader Quick Commands

**NVDA (Windows):**

| Action | Shortcut |
|--------|----------|
| Start/stop reading | Insert+↓ |
| List headings | H (browse mode) |
| List landmarks | D (browse mode) |
| List links | K (browse mode) |
| List form fields | F (browse mode) |
| Toggle browse/forms mode | Insert+Space |

**VoiceOver (macOS):**

| Action | Shortcut |
|--------|----------|
| Start/stop | Cmd+F5 |
| VO key | Ctrl+Option (VO) |
| Rotor | VO+U |
| Next heading | VO+Cmd+H |
| Next landmark | VO+Cmd+L |

### Visual Testing

- [ ] Page remains readable and functional at 200% browser zoom
- [ ] No horizontal scrollbar appears at 400% zoom (reflow)
- [ ] Color contrast verified: 4.5:1 normal text, 3:1 large text and UI components
- [ ] No information conveyed by color alone (confirm with grayscale filter)
- [ ] Touch targets are at least 44×44 px
- [ ] Focus rings visible in both light and dark mode

### Forms

- [ ] Every input has an associated `<label>` (via `htmlFor`/`id` or `aria-label`)
- [ ] Required fields indicated via both text/icon AND `aria-required="true"`
- [ ] Errors identify the field by name and describe how to fix it
- [ ] Errors are announced to screen readers immediately on submission failure
- [ ] Fieldsets group related inputs; legend provides group label
- [ ] `autocomplete` attributes set on name, email, address inputs

### Multimedia

- [ ] Videos have synchronized captions (not just auto-generated)
- [ ] Audio-only content has a text transcript
- [ ] Auto-playing media can be paused/stopped by the user
- [ ] No content flashes more than 3 times per second

---

## Automated Testing Setup

### jest-axe (unit / component tests)

```bash
npm install --save-dev jest-axe @types/jest-axe
```

```typescript
// tests/components/SignupForm.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { SignupForm } from '../SignupForm';

expect.extend(toHaveNoViolations);

describe('SignupForm accessibility', () => {
  it('has no axe violations in default state', async () => {
    const { container } = render(<SignupForm onSubmit={jest.fn()} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('has no axe violations when errors are shown', async () => {
    const { container, getByRole } = render(<SignupForm onSubmit={jest.fn()} />);
    // Trigger validation
    getByRole('button', { name: /sign up/i }).click();
    expect(await axe(container)).toHaveNoViolations();
  });
});
```

### cypress-axe (integration / E2E tests)

```bash
npm install --save-dev cypress-axe axe-core
```

```typescript
// cypress/support/e2e.ts
import 'cypress-axe';
```

```typescript
// cypress/e2e/accessibility.cy.ts
describe('Page accessibility', () => {
  const pages = ['/', '/login', '/signup', '/dashboard', '/workflows'];

  pages.forEach((path) => {
    it(`${path} has no axe violations`, () => {
      cy.visit(path);
      cy.injectAxe();
      cy.checkA11y(undefined, {
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa'],
        },
      });
    });
  });

  it('modal has no violations when open', () => {
    cy.visit('/dashboard');
    cy.injectAxe();
    cy.findByRole('button', { name: /create workflow/i }).click();
    cy.checkA11y('[role="dialog"]');
  });
});
```

### Pa11y — CLI and CI

```bash
# Single URL
npx pa11y http://localhost:3500 --standard WCAG2AA

# Authenticated page (POST login first)
npx pa11y http://localhost:3500/dashboard \
  --standard WCAG2AA \
  --actions "set field #email to user@example.com" \
  --actions "set field #password to password" \
  --actions "click element [type=submit]"

# JSON output for CI parsing
npx pa11y http://localhost:3500 --reporter json > pa11y-results.json
```

**pa11y-ci config** (`.pa11yci`):

```json
{
  "standard": "WCAG2AA",
  "reporters": ["cli", "json"],
  "threshold": 0,
  "urls": [
    "http://localhost:3500",
    "http://localhost:3500/login",
    "http://localhost:3500/dashboard"
  ]
}
```

```bash
npx pa11y-ci
```

### Lighthouse CI

```bash
# One-off audit
npx lighthouse http://localhost:3500 \
  --only-categories=accessibility \
  --output json \
  --output-path ./lighthouse-a11y.json

# Fail if score drops below 90
npx lighthouse http://localhost:3500 \
  --only-categories=accessibility \
  --assert.categories.accessibility=90
```

---

## Testing Coverage Matrix

Use this matrix to confirm adequate coverage per component type:

| Component type | jest-axe | Keyboard | Screen reader | Contrast check |
|---------------|----------|----------|---------------|----------------|
| Form | Required | Required | Required | Required |
| Modal / Dialog | Required | Required | Required | Required |
| Navigation | Required | Required | Required | — |
| Data table | Required | Required | Required | — |
| Chart / graph | Required | — | Required (alt/desc) | Required |
| Button / link | Required | — (native) | — (native) | Required |
| Custom widget (dropdown, tabs) | Required | Required | Required | Required |

**Minimum bar before merge:** jest-axe passes, keyboard navigation manually verified, one screen reader spot-check.
