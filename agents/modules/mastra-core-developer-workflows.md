# Mastra Core Developer — Workflow Composition Module

Load this module when the task requires detailed workflow composition patterns, step orchestration examples, error handling strategies, or retry configuration.

---

## Workflow Composition Patterns

### Sequential Execution (.then)

```typescript
import { createWorkflow, createStep } from '@mastra/core/workflows';
import { z } from 'zod';

const step1 = createStep({
  id: 'fetch-data',
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ data: z.string() }),
  execute: async ({ inputData }) => {
    const response = await fetch(inputData.url);
    return { data: await response.text() };
  }
});

const step2 = createStep({
  id: 'process-data',
  inputSchema: z.object({ data: z.string() }),
  outputSchema: z.object({ result: z.string() }),
  execute: async ({ inputData }) => {
    return { result: inputData.data.toUpperCase() };
  }
});

export const sequentialWorkflow = createWorkflow({
  id: 'sequential-workflow',
  description: 'Process data sequentially',
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ result: z.string() })
})
  .then(step1)   // Runs first
  .then(step2)   // Runs after step1 completes
  .commit();     // CRITICAL: .commit() finalizes the workflow
```

### Parallel Execution (.parallel)

```typescript
const parallelWorkflow = createWorkflow({
  id: 'parallel-workflow',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ results: z.any() })
})
  .parallel([
    fetchFromSource1Step,  // Run simultaneously
    fetchFromSource2Step,  // Run simultaneously
    fetchFromSource3Step   // Run simultaneously
  ])
  .then(aggregateResultsStep)  // Runs after ALL parallel steps complete
  .commit();

// Aggregation step receives all parallel outputs
const aggregateResultsStep = createStep({
  id: 'aggregate-results',
  inputSchema: z.object({
    'fetch-from-source1': z.any(),
    'fetch-from-source2': z.any(),
    'fetch-from-source3': z.any()
  }),
  outputSchema: z.object({ results: z.any() }),
  execute: async ({ inputData }) => {
    return {
      results: {
        ...inputData['fetch-from-source1'],
        ...inputData['fetch-from-source2'],
        ...inputData['fetch-from-source3']
      }
    };
  }
});
```

### Conditional Branching (.branch)

```typescript
const branchingWorkflow = createWorkflow({
  id: 'branching-workflow',
  inputSchema: z.object({ score: z.number() }),
  outputSchema: z.object({ action: z.string() })
})
  .then(analyzeScoreStep)
  .branch({
    when: (data) => data['analyze-score'].score > 0.8,
    then: highConfidencePath,
    otherwise: lowConfidencePath
  })
  .commit();

// Sub-workflows for each branch
const highConfidencePath = createWorkflow({ id: 'high-confidence', ... })
  .then(approveStep)
  .commit();

const lowConfidencePath = createWorkflow({ id: 'low-confidence', ... })
  .then(reviewStep)
  .commit();
```

### Collection Processing (.foreach)

```typescript
const batchWorkflow = createWorkflow({
  id: 'batch-workflow',
  inputSchema: z.object({ items: z.array(z.string()) }),
  outputSchema: z.object({ processed: z.array(z.any()) })
})
  .foreach(
    (data) => data.items,  // Extract collection
    processItemStep         // Step to apply to each item
  )
  .then(summarizeStep)
  .commit();
```

### Human-in-the-Loop (HITL) with Suspend/Resume

```typescript
const approvalWorkflow = createWorkflow({
  id: 'approval-workflow',
  inputSchema: z.object({ documentId: z.string() }),
  outputSchema: z.object({ approved: z.boolean() })
})
  .then(prepareDocumentStep)
  .suspend()  // Workflow pauses here; state persisted
  .then(processApprovalStep)  // Resumes after external .resume() call
  .commit();

// Resume from external system (e.g., webhook from approval UI)
const run = await approvalWorkflow.getRunById(runId);
await run.resume({
  step: 'suspend',
  data: { approved: true, reviewerNotes: 'Looks good' }
});
```

### Long-Running Jobs (.sleep / .sleepUntil)

```typescript
const reminderWorkflow = createWorkflow({
  id: 'reminder-workflow',
  inputSchema: z.object({ userId: z.string(), taskId: z.string() }),
  outputSchema: z.object({ sent: z.boolean() })
})
  .then(sendInitialNotificationStep)
  .sleep({ hours: 24 })          // Pause 24 hours (state persisted)
  .then(checkCompletionStep)
  .branch({
    when: (data) => !data['check-completion'].completed,
    then: sendReminderWorkflow,
    otherwise: noOpWorkflow
  })
  .commit();

// Or sleep until specific time
const scheduledWorkflow = createWorkflow({ ... })
  .then(prepareStep)
  .sleepUntil((data) => new Date(data['prepare'].scheduledAt))
  .then(executeStep)
  .commit();
```

---

## Schema Management

### Schema Compatibility Rules

**CRITICAL:** Schema compatibility between steps is mandatory:
- First step's `inputSchema` must match workflow's `inputSchema`
- Last step's `outputSchema` must match workflow's `outputSchema`
- Each step's `outputSchema` must match next step's `inputSchema`
- Step outputs accessed via step ID: `inputData['step-id'].fieldName`

```typescript
const step1 = createStep({
  id: 'generate-greeting',
  inputSchema: z.object({ name: z.string() }),
  outputSchema: z.object({ greeting: z.string() }),
  execute: async ({ inputData }) => {
    return { greeting: `Hello, ${inputData.name}!` };
  }
});

const step2 = createStep({
  id: 'add-timestamp',
  inputSchema: z.object({ greeting: z.string() }),  // Matches step1 output
  outputSchema: z.object({ finalGreeting: z.string(), timestamp: z.string() }),
  execute: async ({ inputData }) => {
    return {
      finalGreeting: `${inputData.greeting} (${new Date().toISOString()})`,
      timestamp: new Date().toISOString()
    };
  }
});

// WRONG: Accessing previous step output incorrectly
const badStep = createStep({
  execute: async ({ inputData }) => {
    const data = inputData.result;  // Will be undefined
  }
});

// CORRECT: Access via step ID
const goodStep = createStep({
  execute: async ({ inputData }) => {
    const data = inputData['step-1'].result;  // Correct
  }
});
```

---

## Error Handling and Retry Patterns

### Workflow-Level Retry Policy

```typescript
const resilientWorkflow = createWorkflow({
  id: 'resilient-workflow',
  retryPolicy: {
    maxRetries: 3,
    backoff: 'exponential',
    retryableErrors: ['NETWORK_ERROR', 'TIMEOUT', '503', '429']
  },
  onError: async (error, context) => {
    await logger.error({ error, context }, 'Workflow failed');
    await sendAlert({ error, workflowId: context.workflowId });
  },
  onComplete: async (result) => {
    await logger.info({ result }, 'Workflow completed');
  }
})
  .then(unstableApiCallStep)
  .commit();
```

### Step-Level Timeout

```typescript
const step = createStep({
  id: 'fetch-with-timeout',
  timeout: 30000,  // 30 second timeout per step execution
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ data: z.any() }),
  execute: async ({ inputData }) => {
    const response = await fetch(inputData.url);
    return { data: await response.json() };
  }
});
```

### Error Handling Within Steps

```typescript
const robustStep = createStep({
  id: 'robust-api-call',
  inputSchema: z.object({ id: z.string() }),
  outputSchema: z.object({ result: z.any(), error: z.string().optional() }),
  execute: async ({ inputData }) => {
    try {
      const response = await fetch(`https://api.example.com/resource/${inputData.id}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      return { result: await response.json() };
    } catch (error) {
      // Structured error return instead of throwing
      return {
        result: null,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
});
```

---

## Workflow State Persistence

```typescript
import { db } from '../config/database.config.js';
import { workflowExecutions } from '../db/schema.js';

async function executeWorkflowWithPersistence(workflowId: string, input: any) {
  // Create execution record
  const [execution] = await db.insert(workflowExecutions).values({
    workflowId,
    status: 'running',
    state: input,
    startedAt: new Date()
  }).returning();

  try {
    const workflow = getWorkflowById(workflowId);
    const run = await workflow.createRun();
    const result = await run.start({ inputData: input });

    await db.update(workflowExecutions)
      .set({ status: 'completed', state: result, completedAt: new Date() })
      .where(eq(workflowExecutions.id, execution.id));

    return { executionId: execution.id, result };
  } catch (error) {
    await db.update(workflowExecutions)
      .set({ status: 'failed', completedAt: new Date() })
      .where(eq(workflowExecutions.id, execution.id));
    throw error;
  }
}
```

---

## Workflow Testing

```typescript
import { describe, it, expect } from 'vitest';

describe('formGenerationWorkflow', () => {
  it('should execute successfully with valid input', async () => {
    const run = await formGenerationWorkflow.createRun();
    const result = await run.start({
      inputData: { opportunityId: 'test-123' }
    });

    expect(result.status).toBe('completed');
    expect(result.formData).toBeDefined();
    expect(result.pdfUrl).toMatch(/^https:\/\//);
  });

  it('should handle missing opportunity gracefully', async () => {
    const run = await formGenerationWorkflow.createRun();

    await expect(
      run.start({ inputData: { opportunityId: 'invalid' } })
    ).rejects.toThrow('Opportunity not found');
  });

  it('should complete parallel steps independently', async () => {
    const run = await parallelWorkflow.createRun();
    const result = await run.start({ inputData: { query: 'test' } });

    expect(result.results).toHaveProperty('source1');
    expect(result.results).toHaveProperty('source2');
    expect(result.results).toHaveProperty('source3');
  });
});
```

---

## Workflow Registration

```typescript
// 1. Create workflow file: apps/mastra/src/workflows/my-workflow.ts
export const myWorkflow = createWorkflow({
  id: 'my-workflow',
  inputSchema: z.object({ ... }),
  outputSchema: z.object({ ... })
})
  .then(step1)
  .then(step2)
  .commit();

// 2. Register in mastra.config.ts
import { myWorkflow } from '../workflows/my-workflow.js';

export const mastra = new Mastra({
  storage,
  workflows: { myWorkflow }
});

// 3. Optionally expose via MCP Server
export const mastraMcpServer = new MCPServer({
  id: 'mastra-workflows',
  workflows: { myWorkflow }  // Exposes as MCP tool
});
```

---

## Workflow Checklist

- [ ] DAG structure validated (no circular dependencies)
- [ ] Input/output schemas defined with Zod for all steps
- [ ] All step schemas are compatible with each other
- [ ] Step outputs accessed via step ID (`inputData['step-id'].field`)
- [ ] Error handling configured on steps calling external services
- [ ] Timeout configured for steps with external dependencies
- [ ] Retry policy defined for unreliable operations
- [ ] `.commit()` called to finalize workflow
- [ ] Workflow registered in `mastra.config.ts`
- [ ] Tested with `workflow.createRun().start()`
