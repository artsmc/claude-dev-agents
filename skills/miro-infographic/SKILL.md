---
name: miro-infographic
description: >
  Create visual infographics on Miro boards by composing diagrams, documents, and tables
  into cohesive layouts. Supports stats dashboards, comparison layouts, process overviews
  with data, executive summaries, and any multi-element visual presentation.
  Use this skill whenever the user wants to create an infographic, dashboard, visual summary,
  one-pager, comparison chart, metrics overview, or any visual that combines data, text,
  and diagrams into a presentation-ready layout on Miro.
  Trigger on phrases like "create an infographic", "make a dashboard on Miro",
  "visual summary", "one-pager", "comparison chart", "metrics overview",
  "executive summary on Miro", "put together a visual report",
  or "present this data visually on my board".
  If the user just needs a single diagram (flowchart, ERD, sequence diagram), use
  miro-diagram instead. Use THIS skill when the output needs multiple visual elements
  composed together — diagrams + text + tables + metrics.
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

## Available Building Blocks

| Block | Miro Tool | Best For |
|-------|-----------|----------|
| **Diagrams** | `diagram_create` | Process flows, architecture maps, relationship visuals |
| **Documents** | `doc_create` | Rich text sections — headers, stats callouts, narratives, legends |
| **Tables** | `table_create` + `table_sync_rows` | Data grids, feature comparisons, metrics tables |

Each block is positioned on the board using x/y coordinates. Your job is to plan the layout, create each block, and position them so they read as one cohesive visual.

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

### Layout Templates

Pick the template that matches the infographic type:

**Stats Dashboard (2-3 columns, 2-3 rows):**
```
[Title Doc - spans full width]     y=0
[Metric Doc 1] [Metric Doc 2] [Metric Doc 3]  y=400
[Table or Diagram - spans 2-3 cols]            y=1000
```

**Comparison Layout (2 columns):**
```
[Title Doc - full width]           y=0
[Option A Doc]  [Option B Doc]     y=400
[Comparison Table - full width]    y=1000
[Recommendation Doc - full width]  y=1600
```

**Process Overview with Data (mixed):**
```
[Title Doc - full width]           y=0
[Process Diagram - spans 2 cols]   y=400
[KPI Table]     [Notes Doc]        y=1200
```

**Executive Summary (single column, scrolling):**
```
[Title + Context Doc]              y=0
[Key Metrics Table]                y=600
[Architecture Diagram]             y=1200
[Recommendations Doc]              y=1800
```

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

## Infographic Recipes

### Recipe 1: Stats/Metrics Dashboard

Creates a visual overview of key metrics with a supporting data table.

**Elements to create (in order):**
1. **Title doc** (x=0, y=0) — project name, date, owner, status badge
2. **Metrics doc** (x=0, y=400) — 3-6 headline numbers with emoji, bold formatting
3. **Trend table** (x=0, y=1000) — time-series or breakdown data with select columns for status
4. **Optional: Architecture diagram** (x=0, y=1600) — system overview if relevant

**Example title doc:**
```markdown
# 🚀 AIForge Platform Dashboard
**Period:** Q1 2026 | **Status:** 🟢 Healthy | **Team:** Platform Engineering
```

**Example metrics doc:**
```markdown
# 📊 Platform Health

- **99.95%** Uptime (target: 99.9%)
- **142ms** P50 Latency
- **2.4M** Daily API Calls
- **847** Active Users
- **12** Deployed Workflows
- **0** Critical Incidents (30d)
```

### Recipe 2: Comparison Layout

Creates a side-by-side comparison with recommendation.

**Elements to create:**
1. **Title doc** (x=0, y=0) — what's being compared and why
2. **Option A doc** (x=0, y=400) — summary, pros/cons for first option
3. **Option B doc** (x=900, y=400) — summary, pros/cons for second option
4. **Comparison table** (x=0, y=1000) — feature-by-feature breakdown with status columns
5. **Recommendation doc** (x=0, y=1600) — which option and why

### Recipe 3: Process Overview with Data

Creates a visual process with supporting metrics.

**Elements to create:**
1. **Title doc** (x=0, y=0) — process name and context
2. **Process diagram** (x=0, y=400) — flowchart showing the process (use miro-diagram patterns)
3. **KPI table** (x=0, y=1200) — metrics for each process stage
4. **Notes doc** (x=900, y=1200) — caveats, next steps, owner assignments

### Recipe 4: Executive Summary One-Pager

Creates a presentation-ready summary combining narrative, data, and visuals.

**Elements to create:**
1. **Header doc** (x=0, y=0) — title, executive summary paragraph, key takeaway
2. **Metrics table** (x=0, y=600) — core KPIs in a clean table
3. **Architecture/flow diagram** (x=0, y=1200) — visual showing the system or process
4. **Next steps doc** (x=0, y=1800) — action items, timeline, owners

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
