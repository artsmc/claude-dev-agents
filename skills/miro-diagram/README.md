# /miro-diagram

> Create diagrams on Miro boards using the Miro MCP tools — flowcharts, UML class/sequence diagrams, and ERDs. For multi-element layouts (diagrams + text + tables + metrics), use miro-infographic instead.

## What it does

Turns a description of a system, flow, or schema into a diagram on a live Miro board via the Miro MCP (`diagram_get_dsl`, `diagram_create`, `context_explore`/`context_get`, `doc_create`). The core discipline is a two-step process — fetch the DSL grammar first, then generate clean structured input — because Miro auto-layouts everything and only produces readable results from well-formed DSL. Covers flowcharts, UML sequence diagrams, and ERDs, plus strategies for splitting complex systems across multiple diagrams and attaching companion documents for detail that doesn't belong in boxes.

## When it triggers

- "diagram this" / "visualize the architecture on Miro"
- "draw the database schema" / "make an ERD of these tables"
- "sequence diagram for the login flow"
- "map out this process on my board"
- Any diagram request while the Miro MCP is connected

## Usage

Invoke with `/miro-diagram` or just ask for a diagram with the Miro MCP connected (may require `mcp__miro__authenticate` first). No flags. One diagram per request; for a composed layout of several elements, that's miro-infographic's job.

## Context cost

Description always in context (~0.5k chars); SKILL.md body loads on trigger (~7k chars); references load on demand: `diagram-patterns.md` (~6k), `color-palette.md` (~2k).

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Two-step process, layout-engine rules, per-diagram-type golden rules, pre-create checklist |
| `references/diagram-patterns.md` | Worked DSL patterns per diagram type |
| `references/color-palette.md` | Consistent color choices for nodes/edges |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **miro-infographic** — when the deliverable composes multiple elements (diagrams + text + tables + metrics) into one layout; this skill is for a single diagram.
- **dataviz** — charts/graphs in code or artifacts, not on Miro boards.
