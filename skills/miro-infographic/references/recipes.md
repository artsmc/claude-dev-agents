# Miro Infographic — Building Blocks, Layout Templates & Recipes

Companion reference for the `miro-infographic` skill. Read this before creating any elements: pick the layout template and recipe that match the infographic type, then follow the element order.

## Available Building Blocks

| Block | Miro Tool | Best For |
|-------|-----------|----------|
| **Diagrams** | `diagram_create` | Process flows, architecture maps, relationship visuals |
| **Documents** | `doc_create` | Rich text sections — headers, stats callouts, narratives, legends |
| **Tables** | `table_create` + `table_sync_rows` | Data grids, feature comparisons, metrics tables |

Each block is positioned on the board using x/y coordinates. Your job is to plan the layout, create each block, and position them so they read as one cohesive visual.

## Layout Templates

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
