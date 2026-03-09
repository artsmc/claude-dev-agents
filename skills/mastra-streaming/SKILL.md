---
name: mastra-streaming
description: Mastra Streaming patterns - agent streams, workflow streams, tool streaming, SSE events, and AI SDK integration for React/Next.js UIs
---

# Mastra Streaming Patterns

Comprehensive guide for real-time streaming with Mastra. Covers agent streaming (textStream, fullStream), workflow streaming, tool streaming with context.writer, SSE events, and AI SDK integration (chatRoute, toAISdkStream, handleChatStream) for React and Next.js UIs.

## Usage

```bash
/mastra-streaming
```

Provides context for:
- `agent.stream()` returning `MastraModelOutput` with `textStream`, `fullStream`
- Workflow `run.stream()` with event types
- Tool streaming via `context.writer.custom()`
- AI SDK: `toAISdkStream()`, `chatRoute()`, `handleChatStream()`
- `networkRoute()`, `workflowRoute()`
- React `useChat` hook integration
- `streamLegacy()` for v1 model compatibility
