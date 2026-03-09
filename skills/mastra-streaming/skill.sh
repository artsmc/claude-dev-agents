#!/usr/bin/env bash
# mastra-streaming - Mastra Streaming Patterns Skill
# Provides comprehensive guidance for real-time streaming with Mastra agents, workflows, and AI SDK integration
cat << 'SKILL_EOF'

# Mastra Streaming: Real-Time Token & Event Streaming

## Overview

Mastra provides multiple streaming patterns for building responsive AI applications.
Streaming delivers tokens and events in real-time instead of waiting for complete responses,
enabling snappy UIs and live progress indicators.

Streaming patterns available:
- **Agent Streaming** - Token-by-token output from AI agents via `agent.stream()`
- **Workflow Streaming** - Step-by-step execution events from workflows via `run.stream()`
- **Resume Stream** - Continue suspended workflows with streaming output via `run.resumeStream()`
- **Time Travel Stream** - Replay workflow execution from a specific step via `run.timeTravelStream()`
- **Tool Streaming** - Progressive output from long-running tools via `context.writer`
- **AI SDK Integration** - Bridge to Vercel AI SDK for React/Next.js UIs via `@mastra/ai-sdk`

---

## Agent Streaming

Stream agent responses token-by-token for responsive chat UIs.
`agent.stream()` returns a `MastraModelOutput` object with streaming and promise-based properties.

### Basic Agent Stream (textStream)
```typescript
const stream = await agent.stream('Tell me about TypeScript');

// Iterate over incremental text chunks
for await (const text of stream.textStream) {
  process.stdout.write(text);
}
```

### With Messages Array
```typescript
const stream = await agent.stream({
  messages: [
    { role: 'user', content: 'What is Mastra?' },
  ],
});

for await (const text of stream.textStream) {
  process.stdout.write(text);
}
```

### Collecting Full Response
```typescript
const stream = await agent.stream('Summarize this document');

// Option 1: Await the text promise
const fullText = await stream.text;
console.log('Complete response:', fullText);

// Option 2: Accumulate from textStream
let accumulated = '';
for await (const text of stream.textStream) {
  accumulated += text;
}
```

### fullStream (All Event Types)
```typescript
const stream = await agent.stream('What is the weather?');

// fullStream includes text, tool calls, reasoning, metadata, and control chunks
for await (const chunk of stream.fullStream) {
  switch (chunk.type) {
    case 'text-delta':
      process.stdout.write(chunk.textDelta);
      break;

    case 'tool-call':
      console.log(`\nTool called: ${chunk.toolName}(${JSON.stringify(chunk.args)})`);
      break;

    case 'tool-result':
      console.log(`Tool result: ${JSON.stringify(chunk.result)}`);
      break;

    case 'step-finish':
      console.log(`Step finished: ${chunk.finishReason}`);
      break;

    case 'finish':
      console.log('\nStream complete. Usage:', chunk.usage);
      break;

    case 'error':
      console.error('Stream error:', chunk.error);
      break;
  }
}
```

---

## MastraModelOutput Reference

The return type of `agent.stream()`. Provides both streaming and promise-based access.

| Property | Type | Description |
|----------|------|-------------|
| `textStream` | `AsyncIterable<string>` | Incremental text chunks only (filters out metadata, tool calls, control chunks) |
| `fullStream` | `AsyncIterable<StreamChunk>` | Complete stream of ALL chunk types (text, tools, reasoning, metadata) |
| `text` | `Promise<string>` | Resolves to the full text response |
| `toolCalls` | `Promise<ToolCall[]>` | Array of all tool calls made during execution |
| `usage` | `Promise<Usage>` | Token usage: `{ inputTokens, outputTokens, totalTokens, reasoningTokens }` |
| `reasoning` | `Promise<string>` | Reasoning text for models that support it (e.g., o1 series) |

---

## Stream Event Types (fullStream)

| Event Type | Description | Key Properties |
|------------|-------------|----------------|
| `text-delta` | Incremental text token from the model | `textDelta: string` |
| `tool-call` | Agent decided to call a tool | `toolName: string`, `args: object`, `toolCallId: string` |
| `tool-result` | Tool execution returned a result | `toolCallId: string`, `result: any` |
| `step-finish` | A step has fully finalized | `finishReason: string` |
| `finish` | Stream completed successfully | `usage: { inputTokens, outputTokens }` |
| `error` | An error occurred during streaming | `error: Error` |

### Complete Event Handler
```typescript
const stream = await agent.stream('Complex query with tools');

for await (const chunk of stream.fullStream) {
  switch (chunk.type) {
    case 'text-delta':
      appendToChat(chunk.textDelta);
      break;

    case 'tool-call':
      showToolLoading(chunk.toolName, chunk.args);
      break;

    case 'tool-result':
      hideToolLoading(chunk.toolCallId);
      displayToolResult(chunk.result);
      break;

    case 'step-finish':
      // Step finalized with metadata
      break;

    case 'finish':
      finalizeMessage();
      updateTokenUsage(await stream.usage);
      break;

    case 'error':
      showError(chunk.error.message);
      break;
  }
}
```

---

## agent.stream() Parameters

```typescript
const stream = await agent.stream(messages, options?);
```

### Messages Parameter
- `string` - Single user message
- `string[]` - Array of user messages
- `{ messages: Message[] }` - Structured message objects with roles

### Options Parameter
| Option | Type | Description |
|--------|------|-------------|
| `threadId` | `string` | Conversation thread ID (for memory) |
| `resourceId` | `string` | User/resource ID (required if threadId set) |
| `temperature` | `number` | Controls randomness (0.0-1.0) |
| `maxOutputTokens` | `number` | Max tokens to generate (NOT maxTokens) |
| `toolChoice` | `'auto' \| 'none' \| 'required' \| { type: 'tool', toolName: string }` | Tool use control |
| `toolsets` | `Record<string, Toolset>` | Additional toolsets for this stream |
| `maxSteps` | `number` | Max steps allowed during streaming |
| `abortSignal` | `AbortSignal` | Cancellation signal |
| `structuredOutput` | `Schema` | Schema for structured output generation |
| `context` | `Message[]` | Additional context messages |

### Model Compatibility
- `agent.stream()` - For AI SDK v5+ models (LanguageModelV2)
- `agent.streamLegacy()` - For AI SDK v4 models (LanguageModelV1)

---

## Workflow Streaming

Stream events from workflow execution for real-time progress tracking.
Workflow streaming returns structured events (not text chunks).

### Basic Workflow Stream
```typescript
const run = workflow.createRun();
const stream = await run.stream({ inputData: { query: 'process this data' } });

for await (const event of stream) {
  console.log(`[${event.type}]`, event.payload);
}
```

### Workflow Event Types
```typescript
const run = workflow.createRun();
const stream = await run.stream({ inputData: myInput });

for await (const event of stream) {
  switch (event.type) {
    case 'workflow-step-start':
      console.log(`Step "${event.payload.stepName}" started at ${event.payload.startedAt}`);
      break;

    case 'step-finish':
      console.log(`Step completed:`, event.payload);
      break;

    case 'workflow-complete':
      console.log('Workflow finished:', event.payload);
      break;

    case 'workflow-error':
      console.error('Workflow failed:', event.payload.error);
      break;
  }
}
```

---

## Resume Stream (Suspended Workflows)

When a workflow suspends (e.g., waiting for human approval), resume it with streaming output.

```typescript
// Workflow suspends at an approval step
const run = workflow.createRun();
await run.start({ inputData: { query: 'process data' } });
// run suspends at approval step...

// Later, after human approval:
const resumeStream = await run.resumeStream({
  stepId: 'approval',
  data: { approved: true, approverNotes: 'Looks good' },
});

for await (const event of resumeStream) {
  console.log(`Resumed workflow event: ${event.type}`, event.payload);
}
```

---

## Time Travel Stream

Replay workflow execution from a specific step for debugging and "what-if" analysis.

```typescript
const ttStream = await run.timeTravelStream({
  toStepId: 'step-2',
});

for await (const event of ttStream) {
  console.log('Time travel event:', event.type, event.payload);
}
```

### Use Cases
- Debug a failing step by replaying from the step before it
- Test alternative inputs to a specific step without re-running the entire workflow
- Replay execution for audit/compliance logging

---

## Tool Streaming

Tools can emit progressive output during execution using `context.writer`.

```typescript
import { createTool } from '@mastra/core';

const researchTool = createTool({
  name: 'deep-research',
  description: 'Performs multi-step research with progress updates',
  execute: async ({ input, context }) => {
    // Emit custom progress events into the active stream
    await context?.writer?.custom('data-tool-progress', {
      status: 'pending',
      message: 'Searching databases...',
    });
    const dbResults = await searchDatabases(input.query);

    await context?.writer?.custom('data-tool-progress', {
      status: 'pending',
      message: 'Analyzing results...',
    });
    const analysis = await analyzeResults(dbResults);

    await context?.writer?.custom('data-tool-progress', {
      status: 'success',
      message: 'Research complete',
    });

    return { summary: analysis.summary, sources: dbResults.length };
  },
});
```

**Important:** You must `await` the call to `writer.custom()` or you will get a
"WritableStream is locked" error.

### Tool Lifecycle Hooks
Tools support lifecycle hooks for monitoring during streaming:
- `onInputStart` - Tool input begins arriving
- `onInputDelta` - Incremental tool input chunk
- `onInputAvailable` - Full tool input ready
- `onOutput` - Tool execution complete

---

## Event Streaming (Server-Sent Events)

Use SSE for browser-based real-time streaming over HTTP.

### Server-Side (Express)
```typescript
import express from 'express';

app.get('/api/stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const stream = await agent.stream(req.query.prompt as string);

  for await (const text of stream.textStream) {
    res.write(`data: ${JSON.stringify({ type: 'text', content: text })}\n\n`);
  }

  res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);
  res.end();
});
```

### Client-Side (Browser)
```typescript
const eventSource = new EventSource('/api/stream?prompt=Tell+me+about+AI');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'text') {
    appendToChat(data.content);
  } else if (data.type === 'done') {
    eventSource.close();
  }
};

eventSource.onerror = () => {
  eventSource.close();
  showReconnectButton();
};
```

---

## AI SDK Integration (React/Next.js)

Bridge Mastra streams to Vercel AI SDK for seamless React integration via `@mastra/ai-sdk`.

### Key Imports
```typescript
import { toAISdkStream } from '@mastra/ai-sdk';
import { handleChatStream } from '@mastra/ai-sdk';
import { chatRoute } from '@mastra/ai-sdk';
import { createUIMessageStreamResponse } from 'ai';
```

### handleChatStream - Framework-Agnostic Chat Handler

The primary way to stream agent chat in AI SDK-compatible format.
Returns a ReadableStream that you wrap with `createUIMessageStreamResponse()`.

```typescript
// Next.js App Router
import { handleChatStream } from '@mastra/ai-sdk';
import { createUIMessageStreamResponse } from 'ai';
import { mastra } from '@/lib/mastra';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const stream = await handleChatStream({
    mastra,
    agentId: 'my-agent',
    params: { messages },
  });

  return createUIMessageStreamResponse({ stream });
}
```

```typescript
// Express
import { handleChatStream } from '@mastra/ai-sdk';
import { createUIMessageStreamResponse } from 'ai';

app.post('/api/chat', async (req, res) => {
  const stream = await handleChatStream({
    mastra,
    agentId: 'my-agent',
    params: { messages: req.body.messages },
  });

  const response = createUIMessageStreamResponse({ stream });

  // Forward headers and pipe stream
  response.headers.forEach((value, key) => {
    res.setHeader(key, value);
  });
  res.status(response.status);

  const reader = response.body.getReader();
  const pump = async () => {
    const { done, value } = await reader.read();
    if (done) { res.end(); return; }
    res.write(value);
    return pump();
  };
  await pump();
});
```

### chatRoute - Declarative Route Handler

```typescript
import { chatRoute } from '@mastra/ai-sdk';

// Fixed agent route
app.post('/api/chat', chatRoute({ path: '/chat', agent: myAgent }));

// Dynamic agent routing
app.post('/api/chat/:agentId', chatRoute({ path: '/chat/:agentId' }));
```

### toAISdkStream - Manual Stream Conversion

Convert Mastra streams to AI SDK-compatible format for custom endpoints.

```typescript
import { toAISdkStream } from '@mastra/ai-sdk';
import { createUIMessageStream, createUIMessageStreamResponse } from 'ai';

const mastraStream = await agent.stream('Hello');

const aiStream = toAISdkStream(mastraStream, {
  from: 'agent',
  sendReasoning: true,
  messageMetadata: (part) => ({
    timestamp: Date.now(),
    partType: part.type,
  }),
});

return createUIMessageStreamResponse({
  stream: createUIMessageStream({ execute: (writer) => aiStream.pipeTo(writer) }),
});
```

---

## Client-Side React (AI SDK useChat)

```typescript
'use client';
import { useChat } from 'ai/react';

export function ChatUI() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  });

  return (
    <div>
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={msg.role}>
            {msg.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
}
```

### useChat with Tool Results
```typescript
'use client';
import { useChat } from 'ai/react';

export function ChatWithTools() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
    onToolCall: async ({ toolCall }) => {
      console.log('Tool called:', toolCall.toolName, toolCall.args);
    },
  });

  return (
    <div>
      {messages.map((msg) => (
        <div key={msg.id}>
          {msg.content}
          {msg.toolInvocations?.map((tool) => (
            <div key={tool.toolCallId} className="tool-result">
              <strong>{tool.toolName}</strong>: {JSON.stringify(tool.result)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

---

## Best Practices

1. **Use `textStream` for chat UIs** - Iterate over `stream.textStream` for responsive text output. Use `fullStream` only when you need tool calls and metadata.

2. **Handle ALL event types in fullStream** - Missing handlers for tool-call or error types leads to broken UIs. Always implement a complete switch statement.

3. **Use AI SDK integration for React/Next.js** - Do not build custom streaming infrastructure. `handleChatStream` + `useChat` provides battle-tested streaming with minimal code.

4. **Use `await` on writer calls in tools** - Always `await context.writer.custom()` to prevent "WritableStream is locked" errors.

5. **Handle connection drops gracefully** - Implement reconnection logic for SSE streams. Show a reconnect button rather than a silent failure.

6. **Use `maxOutputTokens` not `maxTokens`** - AI SDK v5 convention requires `maxOutputTokens` in the options parameter.

7. **Set appropriate timeouts** - Long-running agent responses need generous timeouts. Configure both client and server timeouts (60s+ for complex queries).

8. **Cancel streams when users navigate away** - Use AbortController to cancel in-flight streams:
   ```typescript
   const controller = new AbortController();
   const stream = await agent.stream('query', { abortSignal: controller.signal });
   // On unmount or new message:
   controller.abort();
   ```

9. **Use `streamLegacy()` for older models** - If using AI SDK v4 (LanguageModelV1), use `agent.streamLegacy()` instead of `agent.stream()`.

10. **Use `handleChatStream` over manual SSE** - The built-in handler manages edge cases (backpressure, error serialization, proper headers) that manual SSE implementations miss.

---

## Documentation Links

- Streaming Overview: https://mastra.ai/docs/streaming/overview
- Streaming Events: https://mastra.ai/docs/streaming/events
- Tool Streaming: https://mastra.ai/docs/streaming/tool-streaming
- Workflow Streaming: https://mastra.ai/docs/streaming/workflow-streaming
- Agent.stream() API: https://mastra.ai/reference/streaming/agents/stream
- MastraModelOutput API: https://mastra.ai/reference/streaming/agents/MastraModelOutput
- handleChatStream: https://mastra.ai/reference/ai-sdk/handle-chat-stream
- toAISdkStream: https://mastra.ai/reference/ai-sdk/to-ai-sdk-stream
- AI SDK UI Guide: https://mastra.ai/guides/build-your-ui/ai-sdk-ui
- Vercel AI SDK Docs: https://sdk.vercel.ai/docs

SKILL_EOF
