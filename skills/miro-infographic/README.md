# /miro-infographic

> Create visual infographics on Miro boards by composing diagrams, documents, and tables into cohesive layouts — stats dashboards, comparison layouts, process overviews with data, executive summaries. For a single diagram (flowchart, ERD, sequence), use miro-diagram.

## What it does

Builds multi-element layouts on a Miro board: it plans a grid, then places each block using the right MCP tool — `doc_create` for text panels and executive summaries, `table_create`/`table_sync_rows` for data tables, `diagram_create` for embedded diagrams. The SKILL.md carries the design rules that make the result read as one piece: grid-based layout planning, visual hierarchy, consistent heading levels, and density limits, with a pre-create checklist.

## When it triggers

- "make an infographic of the Q3 results on Miro"
- "build a dashboard / metrics overview on my board"
- "one-pager comparing these two architectures"
- "executive summary with the numbers, visually"
- Any request to present data visually on a Miro board that needs more than one element type

## Usage

Invoke with `/miro-infographic` or ask for a dashboard/one-pager/visual summary with the Miro MCP connected (may require `mcp__miro__authenticate` first). No flags.

## Context cost

Description always in context (~0.6k chars); SKILL.md body loads on trigger (~7k chars); references load on demand: `recipes.md` (~4k).

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Grid system, per-block creation (docs/tables/diagrams), design principles, checklist |
| `references/recipes.md` | Ready-made layout recipes (dashboard, comparison, process overview) |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **miro-diagram** — when the ask is one diagram (flowchart, ERD, sequence); use THIS skill when diagrams + text + tables + metrics compose together into a layout.
- **dataviz** — charts in code/HTML artifacts rather than on a Miro board.
