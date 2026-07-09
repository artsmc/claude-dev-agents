# /mastra-streaming

> Mastra Streaming patterns - agent streams, workflow streams, tool streaming, SSE events, and AI SDK integration for React/Next.js UIs

## What it does

Loads validated patterns for real-time streaming with Mastra: `agent.stream()` returning `MastraModelOutput` (`textStream`, `fullStream`), workflow `run.stream()` event types, tool streaming via `context.writer.custom()`, SSE, and AI SDK integration (`toAISdkStream()`, `chatRoute()`, `handleChatStream()`, `networkRoute()`, `workflowRoute()`) with the React `useChat` hook, plus `streamLegacy()` for v1 models. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Stream agent responses to my Next.js UI"
- "Hook Mastra up to useChat / the AI SDK"
- "Stream progress from inside a tool"
- "Consume workflow stream events"
- "SSE endpoint for a Mastra agent"

## Usage

```bash
/mastra-streaming
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~150 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~18k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full streaming patterns guide (~18k chars) |

## Related skills

- `/mastra-dev` — CLI hub that routes here for streaming concepts
- `/mastra-deploy` — the server/routes the streams are served from
- `/mastra-workflows` — workflow-side streaming and event semantics
