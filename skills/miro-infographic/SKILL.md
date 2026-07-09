---
name: miro-infographic
description: >
  Create visual infographics on Miro boards by composing diagrams, documents, and tables
  into cohesive layouts — stats dashboards, comparison layouts, process overviews with
  data, executive summaries. Use whenever the user wants an infographic, dashboard,
  visual summary, one-pager, comparison chart, or metrics overview on Miro, or asks to
  present data visually on their board. For a single diagram (flowchart, ERD, sequence)
  use miro-diagram; use THIS skill when multiple elements — diagrams + text + tables +
  metrics — compose together.
compatibility:
  tools:
    - mcp__miro__diagram_get_dsl
    - mcp__miro__diagram_create
    - mcp__miro__doc_create
    - mcp__miro__table_create
    - mcp__miro__table_sync_rows
    - mcp__miro__context_explore
---

# Miro Infographic Creator

Build multi-element visual layouts on Miro boards by composing **diagrams**, **documents**, and **tables** into cohesive infographics. Miro doesn't have a native infographic tool — you create them by placing multiple primitives on the board with intentional positioning.

**Read `references/recipes.md` before creating anything** — it contains the building-blocks table (which Miro tool creates which element), the layout templates, and four ready-made recipes (stats dashboard, comparison layout, process overview with data, executive one-pager) with element order and x/y coordinates.

## Layout Planning

Before creating anything, plan your layout on a grid. Think of the board as a coordinate system where (0,0) is the center.

### Grid System

Use a **column-based layout** with consistent spacing:

```
Column 1: x=0        Column 2: x=900      Column 3: x=1800
Row 1:    y=0         y=0                  y=0
Row 2:    y=600       y=600                y=600
Row 3:    y=1200      y=1200               y=1200
```

- **Column width:** ~800px per element, 100px gap = 900px column spacing
- **Row height:** varies by content, typically 400-600px per row
- **Reading order:** top-left to bottom-right (like a page)

Layout templates for the four infographic types are in `references/recipes.md` — pick one before creating.

## Creating Each Block

### Documents (doc_create)

Documents are your primary text block. They support markdown: `# headings`, `**bold**`, `*italic*`, `- lists`, `[links](url)`. They do NOT support code blocks or tables (use `table_create` for those).

**Title blocks:**
```markdown
# Project Alpha — Q4 Status Report
**Last updated:** March 2026 | **Status:** 🟢 On Track | **Owner:** Platform Team
```

**Metric callout blocks** — use bold numbers and emoji for visual impact:
```markdown
# 📊 Key Metrics

**99.9%** Uptime
**2.4M** API Calls/Day
**<200ms** P95 Latency
**40+** LLM Providers
```

**Narrative blocks:**
```markdown
## Executive Summary

The platform migration completed **2 weeks ahead of schedule**. Key wins:
- Reduced infrastructure costs by **34%**
- Improved cold-start times from 8s to **1.2s**
- Zero production incidents during migration window
```

### Tables (table_create + table_sync_rows)

Tables are great for structured data comparisons. Two column types available: **text** (freeform) and **select** (dropdown with colored options).

**Step 1 — Create the table structure:**
```
table_create(
  board_id: "...",
  table_title: "Feature Comparison",
  columns: [
    {"column_title": "Feature", "column_type": "text"},
    {"column_title": "Plan A", "column_type": "text"},
    {"column_title": "Plan B", "column_type": "text"},
    {"column_title": "Status", "column_type": "select", "options": [
      {"displayValue": "Done", "color": "#adf0c7"},
      {"displayValue": "In Progress", "color": "#fff6b6"},
      {"displayValue": "Not Started", "color": "#ffc6c6"}
    ]}
  ]
)
```

**Step 2 — Populate rows:**
```
table_sync_rows(
  board_id: "...",
  item_id: <table_id from step 1>,
  rows: [
    {"cells": [
      {"columnTitle": "Feature", "value": "SSO Authentication"},
      {"columnTitle": "Plan A", "value": "OAuth2 + SAML"},
      {"columnTitle": "Plan B", "value": "OAuth2 only"},
      {"columnTitle": "Status", "value": "Done"}
    ]}
  ]
)
```

**Use select columns** for status, priority, or any categorical data — the colored pills make tables scannable at a glance.

### Diagrams

Follow the `miro-diagram` skill patterns: fetch DSL spec first, keep nodes under 12, use emoji labels, 2-3 colors. Within an infographic, diagrams serve as the "visual anchor" — the element that draws the eye.

Position diagrams using x/y in `diagram_create`. They typically take up 1-2 columns of width.

Element-by-element recipes for the four infographic types (stats dashboard, comparison, process overview, executive one-pager) are in `references/recipes.md` — follow one when composing a full infographic.

## Design Principles

### Visual Hierarchy

The eye should flow naturally through the infographic:
1. **Title** catches attention first (top, large heading)
2. **Key metrics** deliver the headline numbers (bold, emoji)
3. **Supporting data** provides detail (tables, lists)
4. **Visuals** anchor understanding (diagrams)
5. **Narrative** adds context and recommendations (body text)

### Consistency

- Use the **same emoji style** throughout (don't mix styles)
- Use **consistent heading levels** (# for section titles, ## for subsections)
- Use **select columns** in tables for any categorical data (status, priority, risk)
- Keep the **color palette** consistent with any diagrams (reference miro-diagram's palette)

### Density

- **Don't spread things too far apart** — the viewer shouldn't have to zoom out to see everything
- **Pack related elements close together** — 100px gap between columns, 200-400px between rows
- **Use the full width** — a 3-column layout looks more professional than a single narrow column
- Each document block should be **concise** — 5-10 lines max. If you need more text, split into multiple docs.

## Before You Create — Checklist

- [ ] Identified the infographic type (dashboard, comparison, process, summary)?
- [ ] Planned the grid layout with x/y coordinates before creating anything?
- [ ] Title block has project name, date/period, and status?
- [ ] Metrics use bold numbers and emoji for scannability?
- [ ] Tables use select columns for categorical data (colored pills)?
- [ ] Diagrams follow miro-diagram patterns (emoji, 8-12 nodes, 2-3 colors)?
- [ ] Elements are spaced consistently (900px columns, 400-600px rows)?
- [ ] Reading order flows top-left to bottom-right?
