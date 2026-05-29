# Accessibility Specialist — Techniques Module

Load this module for the full ARIA patterns reference, color contrast specifics, alt text guidance for complex images, and keyboard interaction patterns for custom controls (dropdowns, comboboxes, tabs).

---

## ARIA Role and State Reference

### Landmark Roles

Prefer native HTML elements (they carry the implicit ARIA role automatically). Use explicit `role` only on non-semantic elements:

| ARIA role | Preferred native element | Notes |
|-----------|--------------------------|-------|
| `banner` | `<header>` | Top-level page header only |
| `navigation` | `<nav>` | Add `aria-label` when multiple navs exist |
| `main` | `<main>` | One per page |
| `complementary` | `<aside>` | Sidebar or related content |
| `contentinfo` | `<footer>` | Top-level page footer only |
| `search` | `<search>` (or `<form role="search">`) | Search form wrapper |

### Widget Roles

```tsx
// Tabs
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected={activeTab === 'general'} aria-controls="panel-general" id="tab-general">
    General
  </button>
  <button role="tab" aria-selected={activeTab === 'security'} aria-controls="panel-security" id="tab-security">
    Security
  </button>
</div>
<div role="tabpanel" id="panel-general" aria-labelledby="tab-general" hidden={activeTab !== 'general'}>
  General settings content
</div>

// Listbox (single select)
<ul role="listbox" aria-label="Options" aria-activedescendant={selectedId}>
  {options.map(opt => (
    <li
      key={opt.id}
      id={opt.id}
      role="option"
      aria-selected={opt.id === selectedId}
    >
      {opt.label}
    </li>
  ))}
</ul>

// Status / alert
<div role="status" aria-live="polite">Operation successful</div>  // polite — doesn't interrupt
<div role="alert"  aria-live="assertive">Error: required field</div> // assertive — interrupts
```

### aria-describedby vs aria-labelledby

- `aria-labelledby`: replaces the element's accessible name (the "what is this" announcement)
- `aria-describedby`: appends additional context after the name ("email field, must be a valid address")

Both accept space-separated IDs to compose from multiple elements:
```tsx
<input aria-describedby="hint-1 hint-2" />
```

---

## Custom Dropdown / Combobox

The full keyboard pattern for a custom dropdown (the abbreviated version is in the core file):

```tsx
function Dropdown({ label, options, onSelect }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) { setIsOpen(true); setActiveIndex(0); }
        else setActiveIndex(i => Math.min(i + 1, options.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen && activeIndex >= 0) {
          onSelect(options[activeIndex]);
          setIsOpen(false);
          buttonRef.current?.focus();
        } else {
          setIsOpen(!isOpen);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
      case 'Home':
        e.preventDefault();
        setActiveIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveIndex(options.length - 1);
        break;
    }
  };

  return (
    <div onKeyDown={handleKeyDown}>
      <button
        ref={buttonRef}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls="dropdown-list"
        onClick={() => setIsOpen(!isOpen)}
      >
        {label}
      </button>
      {isOpen && (
        <ul
          ref={listRef}
          id="dropdown-list"
          role="listbox"
          aria-label={label}
          aria-activedescendant={activeIndex >= 0 ? `option-${activeIndex}` : undefined}
        >
          {options.map((opt, i) => (
            <li
              key={opt.value}
              id={`option-${i}`}
              role="option"
              aria-selected={i === activeIndex}
              onClick={() => { onSelect(opt); setIsOpen(false); buttonRef.current?.focus(); }}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## Color Contrast Reference

### WCAG 2.1 Requirements (AA)

| Text type | Minimum contrast ratio |
|-----------|----------------------|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 |
| Large text (≥ 18pt / ≥ 14pt bold) | 3:1 |
| UI components and graphical objects | 3:1 |
| Focus indicators | 3:1 against adjacent colors |
| Disabled elements | Exempt |

### AAA Targets

| Text type | Target ratio |
|-----------|-------------|
| Normal text | 7:1 |
| Large text | 4.5:1 |

### Common Safe Combinations (white background #fff)

| Text color | Ratio | Level |
|------------|-------|-------|
| `#595959` | 7:1 | AAA |
| `#767676` | 4.5:1 | AA |
| `#949494` | 3:1 | AA large only |
| `#333333` | 12.6:1 | AAA |

```css
/* Focus indicator — must contrast 3:1 against both the element and adjacent background */
:focus-visible {
  outline: 2px solid #005fcc;   /* 5.9:1 against white */
  outline-offset: 2px;
}

/* High-contrast mode support */
@media (forced-colors: active) {
  :focus-visible {
    outline: 2px solid ButtonText;
  }
}
```

Tools for checking: WebAIM Contrast Checker, browser DevTools color picker, `@storybook/addon-a11y`.

---

## Alternative Text Guidance

### Decision tree

1. Is the image purely decorative? → `alt=""`
2. Does the image convey information used in surrounding text? → `alt=""` (text already covers it)
3. Is the image a functional control (button icon)? → Describe the function: `alt="Search"`
4. Is the image informative? → Describe what it shows, concisely
5. Is the image complex (chart, diagram)? → Short alt + long description via `aria-describedby`

```tsx
// Decorative
<img src="/divider.svg" alt="" />

// Informative
<img src="/warning-icon.svg" alt="Warning" />

// Functional (inside button)
<button>
  <img src="/send-icon.svg" alt="Send message" />
</button>

// Complex — chart
<figure>
  <img
    src="/sales-chart.png"
    alt="Monthly sales chart, Q1 2026"
    aria-describedby="chart-desc"
  />
  <figcaption id="chart-desc">
    Sales grew from $100k in January to $150k in June, peaking in May at $160k
    before a slight decline.
  </figcaption>
</figure>

// SVG inline — use title + aria-labelledby
<svg role="img" aria-labelledby="svg-title">
  <title id="svg-title">Workflow status: Running</title>
  {/* paths */}
</svg>
```

---

## Reduced Motion

Users with vestibular disorders may be harmed by animations. Respect the OS preference:

```css
/* Only animate when the user hasn't requested reduced motion */
@media (prefers-reduced-motion: no-preference) {
  .slide-in {
    animation: slideIn 0.3s ease-out;
  }
}

/* Provide a safe fallback — fade is less likely to cause issues */
@media (prefers-reduced-motion: reduce) {
  .slide-in {
    animation: fadeIn 0.1s ease-out;
  }
}
```

```tsx
// React: read the preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

Never auto-play video or audio. Always provide pause controls. No content that flashes more than 3 times per second.
