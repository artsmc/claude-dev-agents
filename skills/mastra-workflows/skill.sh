#!/usr/bin/env bash
################################################################################
# mastra-workflows - Mastra Workflow Development Skill
#
# Outputs comprehensive guidance for building workflows with the Mastra framework.
# Usage: bash skill.sh
################################################################################

cat << 'SKILL_EOF'
# Mastra Workflow Development Guide

## Table of Contents
1. Workflow Basics
2. Creating Steps
3. Control Flow Patterns
4. Input Data Mapping
5. Workflow State
6. Using Agents in Workflows
7. Suspend and Resume
8. Human-in-the-Loop
9. Error Handling
10. Workflow Streaming
11. Run Management
12. Common Patterns
13. Anti-Patterns
14. Debugging Tips

---

## 1. Workflow Basics

Workflows are DAG-based execution pipelines with typed steps, control flow, and state management.

```typescript
import { createWorkflow, createStep } from '@mastra/core/workflows';
import { z } from 'zod';

const greetStep = createStep({
  id: 'greet',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
  execute: async ({ inputData }) => {
    return { formatted: inputData.message.toUpperCase() };
  },
});

const workflow = createWorkflow({
  id: 'greeting-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
})
  .then(greetStep)
  .commit();  // CRITICAL: Always end with .commit()
```

### Registering Workflows with Mastra

```typescript
import { Mastra } from '@mastra/core';

const mastra = new Mastra({
  workflows: { greetingWorkflow: workflow },
});
```

### Running a Workflow

```typescript
// Get reference (preferred over direct import)
const testWorkflow = mastra.getWorkflow('greetingWorkflow');

// Create a run and start it
const run = await testWorkflow.createRun();

const result = await run.start({
  inputData: { message: 'Hello world' },
});

if (result.status === 'success') {
  console.log(result.result);    // Final output
}
console.log(result.steps);       // All step results
console.log(result.input);       // Original input
```

### Workflow Result Status (Discriminated Union)

| Status      | Unique Properties                   | Description                           |
|-------------|--------------------------------------|---------------------------------------|
| `success`   | `result`                            | Workflow output data                  |
| `failed`    | `error`                             | Error that caused failure             |
| `suspended` | `suspendPayload`, `suspended`       | Suspension data and step paths        |
| `tripwire`  | `tripwire`                          | Contains reason, metadata, processorId|
| `paused`    | _(none)_                            | Only common properties                |

```typescript
const result = await run.start({ inputData: { message: 'Hello' } });

if (result.status === 'success') {
  console.log(result.result);
} else if (result.status === 'failed') {
  console.error(result.error.message);
} else if (result.status === 'suspended') {
  console.log(result.suspendPayload);
  console.log(result.suspended);  // Array of suspended step paths
}
```

Docs: https://mastra.ai/docs/workflows/overview

---

## 2. Creating Steps

Steps are the atomic units of work. Each step has typed input/output schemas and an execute function.

### Basic Step

```typescript
const processStep = createStep({
  id: 'process-data',
  description: 'Processes and formats data',
  inputSchema: z.object({
    data: z.string(),
    format: z.enum(['json', 'csv', 'xml']),
  }),
  outputSchema: z.object({
    processed: z.any(),
    recordCount: z.number(),
  }),
  execute: async ({ inputData }) => {
    const parsed = parseData(inputData.data, inputData.format);
    return {
      processed: parsed,
      recordCount: parsed.length,
    };
  },
});
```

### Step with Agent Access

```typescript
const analyzeStep = createStep({
  id: 'analyze-with-agent',
  inputSchema: z.object({ document: z.string() }),
  outputSchema: z.object({ analysis: z.string(), sentiment: z.string() }),
  execute: async ({ inputData, mastra }) => {
    const agent = mastra.getAgent('analyzer');
    const result = await agent.generate(
      `Analyze this document: ${inputData.document}`,
      {
        structuredOutput: {
          schema: z.object({
            analysis: z.string(),
            sentiment: z.enum(['positive', 'neutral', 'negative']),
          }),
        },
      },
    );
    return {
      analysis: result.object.analysis,
      sentiment: result.object.sentiment,
    };
  },
});
```

### Creating Steps from Agents

```typescript
import { testAgent } from '../agents/test-agent';

// Basic agent step
const agentStep = createStep(testAgent);
// inputSchema: { prompt: string }
// outputSchema: { text: string }

// Agent step with structured output
const structuredAgentStep = createStep(testAgent, {
  structuredOutput: {
    schema: z.object({
      title: z.string(),
      summary: z.string(),
      tags: z.array(z.string()),
    }),
  },
});
```

### Execute Context Parameters

| Parameter        | Type              | Description                                           |
|-----------------|-------------------|-------------------------------------------------------|
| `inputData`     | Typed input       | Validated input matching `inputSchema`                |
| `mastra`        | `Mastra`          | Access to Mastra services (agents, tools, etc.)       |
| `resumeData`    | Typed resume      | Data from resume (only when resuming from suspend)    |
| `suspendData`   | Typed suspend     | Data from original suspend() call                     |
| `suspend`       | `Function`        | Function to pause workflow execution                  |
| `bail`          | `Function`        | Function to stop execution without error              |
| `state`         | Typed state       | Current workflow state (from stateSchema)             |
| `setState`      | `Function`        | Update workflow state                                 |
| `getStepResult` | `Function`        | Access results from other steps                       |
| `getInitData`   | `Function`        | Access workflow's initial input data                  |
| `runId`         | `string`          | Current workflow run identifier                       |
| `requestContext`| `RequestContext`   | Request-scoped context                                |
| `retryCount`    | `number`          | Retry count for this step                             |

Docs: https://mastra.ai/reference/workflows/step

---

## 3. Control Flow Patterns

### Core Schema Rules

- First step's `inputSchema` must match workflow's `inputSchema`
- Last step's `outputSchema` must match workflow's `outputSchema`
- Each step's `outputSchema` must match the next step's `inputSchema`
- If schemas don't match, use `.map()` to transform data

### Sequential: `.then(step)`

Steps execute one after another. Output of step N becomes input of step N+1.

```typescript
const workflow = createWorkflow({
  id: 'sequential-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ emphasized: z.string() }),
})
  .then(formatStep)    // output: { formatted: string }
  .then(emphasizeStep) // input: { formatted: string }
  .commit();
```

### Parallel: `.parallel([steps])`

Steps execute concurrently. Output is an object keyed by each step's `id`:

```typescript
const step3 = createStep({
  id: 'step-3',
  inputSchema: z.object({
    'step-1': z.object({ formatted: z.string() }),
    'step-2': z.object({ emphasized: z.string() }),
  }),
  outputSchema: z.object({ combined: z.string() }),
  execute: async ({ inputData }) => {
    const { formatted } = inputData['step-1'];
    const { emphasized } = inputData['step-2'];
    return { combined: `${formatted} | ${emphasized}` };
  },
});

const workflow = createWorkflow({
  id: 'parallel-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ combined: z.string() }),
})
  .parallel([step1, step2])
  .then(step3)
  .commit();
```

### Branching: `.branch([conditions])`

Conditional execution. All branch steps must have the same `inputSchema` and `outputSchema`:

```typescript
const workflow = createWorkflow({
  id: 'branch-workflow',
  inputSchema: z.object({ value: z.number() }),
  outputSchema: z.object({ message: z.string() }),
})
  .then(step1)
  .branch([
    [async ({ inputData: { value } }) => value > 10, highValueStep],
    [async ({ inputData: { value } }) => value <= 10, lowValueStep],
  ])
  .commit();
```

Branch output is keyed by the executed step's `id`. The next step should handle all possible branches with optional fields:

```typescript
const finalStep = createStep({
  id: 'final-step',
  inputSchema: z.object({
    'high-value-step': z.object({ result: z.string() }).optional(),
    'low-value-step': z.object({ result: z.string() }).optional(),
  }),
  outputSchema: z.object({ message: z.string() }),
  execute: async ({ inputData }) => {
    const result = inputData['high-value-step']?.result
      || inputData['low-value-step']?.result;
    return { message: result };
  },
});
```

### Do-Until Loop: `.dountil(step, condition)`

Repeats a step until the condition returns true:

```typescript
const workflow = createWorkflow({
  id: 'retry-workflow',
  inputSchema: z.object({ number: z.number() }),
  outputSchema: z.object({ number: z.number() }),
})
  .then(step1)
  .dountil(incrementStep, async ({ inputData: { number } }) => number > 10)
  .commit();
```

### Do-While Loop: `.dowhile(step, condition)`

Repeats a step while the condition remains true:

```typescript
const workflow = createWorkflow({
  id: 'polling-workflow',
  inputSchema: z.object({ number: z.number() }),
  outputSchema: z.object({ number: z.number() }),
})
  .then(step1)
  .dowhile(incrementStep, async ({ inputData: { number } }) => number < 10)
  .commit();
```

### Loop Abort with `iterationCount`

```typescript
const workflow = createWorkflow({ ... })
  .dountil(step1, async ({ inputData: { userResponse, iterationCount } }) => {
    if (iterationCount >= 10) {
      throw new Error('Maximum iterations reached');
    }
    return userResponse === 'yes';
  })
  .commit();
```

### ForEach: `.foreach(step, options?)`

Iterates over an array, executing the step for each item:

```typescript
const addTenStep = createStep({
  id: 'add-ten',
  inputSchema: z.object({ value: z.number() }),
  outputSchema: z.object({ value: z.number() }),
  execute: async ({ inputData }) => ({ value: inputData.value + 10 }),
});

const workflow = createWorkflow({
  id: 'batch-workflow',
  inputSchema: z.array(z.object({ value: z.number() })),
  outputSchema: z.array(z.object({ value: z.number() })),
})
  .foreach(addTenStep)
  .commit();

// Input:  [{ value: 1 }, { value: 22 }]
// Output: [{ value: 11 }, { value: 32 }]
```

#### ForEach with Concurrency

```typescript
.foreach(processStep, { concurrency: 4 })  // Process 4 items at once
```

#### Aggregating ForEach Results

```typescript
const aggregateStep = createStep({
  id: 'aggregate',
  inputSchema: z.array(z.object({ processed: z.number() })),
  outputSchema: z.object({ total: z.number() }),
  execute: async ({ inputData }) => ({
    total: inputData.reduce((sum, item) => sum + item.processed, 0),
  }),
});

const workflow = createWorkflow({ ... })
  .foreach(processItemStep)
  .then(aggregateStep)  // Receives the full array from foreach
  .commit();
```

### Sleep / SleepUntil

```typescript
const workflow = createWorkflow({ ... })
  .then(submitStep)
  .sleep(5000)                  // Wait 5 seconds
  .then(checkResultStep)
  .commit();

// Or sleep until a specific date
const workflow2 = createWorkflow({ ... })
  .then(prepareStep)
  .sleepUntil(new Date('2026-03-01T00:00:00Z'))
  .then(executeStep)
  .commit();
```

### Workflows as Steps (Nested)

```typescript
const childWorkflow = createWorkflow({
  id: 'child-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ emphasized: z.string() }),
})
  .then(step1)
  .then(step2)
  .commit();

const parentWorkflow = createWorkflow({
  id: 'parent-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ emphasized: z.string() }),
})
  .then(childWorkflow)  // Use workflow as a step
  .commit();
```

### Combining Control Flow

```typescript
const workflow = createWorkflow({
  id: 'complex-workflow',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ report: z.string() }),
})
  .then(parseQueryStep)
  .parallel([searchStep, cacheStep, historyStep])
  .map(async ({ inputData }) => ({
    combined: `${inputData['search'].value} - ${inputData['cache'].value}`,
  }))
  .branch([
    [async ({ inputData }) => inputData.confidence > 0.8, directAnswerStep],
    [async () => true, deepAnalysisStep],
  ])
  .then(formatReportStep)
  .commit();
```

Docs: https://mastra.ai/docs/workflows/control-flow

---

## 4. Input Data Mapping

When step schemas don't align, use `.map()` to transform data:

### Basic Map

```typescript
const workflow = createWorkflow({ ... })
  .then(step1)
  .map(async ({ inputData }) => {
    const { foo } = inputData;
    return { bar: `new ${foo}` };
  })
  .then(step2)
  .commit();
```

### Map Helper Functions

```typescript
.map(async ({ inputData, getStepResult, getInitData, mapVariable }) => {
  // Access specific step results
  const step1Result = getStepResult('step-1');

  // Access workflow's initial input data
  const initData = getInitData();

  return {
    combined: `${step1Result.value} from ${initData.message}`,
  };
})
```

### Map After Parallel/Branch

```typescript
const workflow = createWorkflow({ ... })
  .parallel([step1, step2])
  .map(async ({ inputData }) => ({
    combined: `${inputData['step-1'].value} - ${inputData['step-2'].value}`,
  }))
  .then(nextStep)
  .commit();
```

Docs: https://mastra.ai/docs/workflows/control-flow#input-data-mapping

---

## 5. Workflow State

Share values across steps without passing them through every step's schemas.

### Defining State Schemas

```typescript
const step1 = createStep({
  id: 'step-1',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
  stateSchema: z.object({ counter: z.number() }),
  execute: async ({ inputData, state, setState }) => {
    // Read from state
    console.log(state.counter);

    // Update state for subsequent steps
    await setState({ ...state, counter: state.counter + 1 });

    return { formatted: inputData.message.toUpperCase() };
  },
});

const workflow = createWorkflow({
  id: 'stateful-workflow',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
  stateSchema: z.object({
    counter: z.number(),
    items: z.array(z.string()),
  }),
})
  .then(step1)
  .commit();
```

### Setting Initial State

```typescript
const run = await workflow.createRun();

const result = await run.start({
  inputData: { message: 'Hello' },
  initialState: {
    counter: 0,
    items: [],
  },
});
```

### State Persists Across Suspend/Resume

State automatically persists when a workflow suspends and resumes.

Docs: https://mastra.ai/docs/workflows/workflow-state

---

## 6. Using Agents in Workflows

### Agent as a Workflow Step

```typescript
const agentAnalysisStep = createStep({
  id: 'agent-analysis',
  inputSchema: z.object({ document: z.string() }),
  outputSchema: z.object({
    analysis: z.string(),
    confidence: z.number(),
    categories: z.array(z.string()),
  }),
  execute: async ({ inputData, mastra }) => {
    const agent = mastra.getAgent('analyzer');
    const result = await agent.generate(
      `Analyze this document:\n\n${inputData.document}`,
      {
        structuredOutput: {
          schema: z.object({
            analysis: z.string(),
            confidence: z.number().min(0).max(1),
            categories: z.array(z.string()),
          }),
        },
      },
    );
    return result.object;
  },
});
```

### Create Step Directly from Agent

```typescript
import { testAgent } from '../agents/test-agent';

const agentStep = createStep(testAgent);
// Automatically: inputSchema: { prompt: string }, outputSchema: { text: string }
```

### Multiple Agents in a Workflow

```typescript
const researchStep = createStep({
  id: 'research',
  inputSchema: z.object({ topic: z.string() }),
  outputSchema: z.object({ findings: z.string() }),
  execute: async ({ inputData, mastra }) => {
    const researcher = mastra.getAgent('researcher');
    const result = await researcher.generate(`Research: ${inputData.topic}`);
    return { findings: result.text };
  },
});

const writeStep = createStep({
  id: 'write',
  inputSchema: z.object({ findings: z.string() }),
  outputSchema: z.object({ article: z.string() }),
  execute: async ({ inputData, mastra }) => {
    const writer = mastra.getAgent('writer');
    const result = await writer.generate(
      `Write an article based on:\n${inputData.findings}`
    );
    return { article: result.text };
  },
});

const workflow = createWorkflow({
  id: 'content-pipeline',
  inputSchema: z.object({ topic: z.string() }),
  outputSchema: z.object({ article: z.string() }),
})
  .then(researchStep)
  .then(writeStep)
  .commit();
```

Docs: https://mastra.ai/docs/workflows/agents-and-tools

---

## 7. Suspend and Resume

Workflows can be paused at any step and resumed later.

### Suspending a Workflow

Define `resumeSchema` (and optionally `suspendSchema`) on the step:

```typescript
const approvalStep = createStep({
  id: 'wait-for-approval',
  inputSchema: z.object({ userEmail: z.string() }),
  outputSchema: z.object({ output: z.string() }),
  resumeSchema: z.object({
    approved: z.boolean(),
  }),
  suspendSchema: z.object({
    reason: z.string(),
  }),
  execute: async ({ inputData, resumeData, suspend }) => {
    const { userEmail } = inputData;
    const { approved } = resumeData ?? {};

    if (!approved) {
      return await suspend({
        reason: 'Human approval required.',
      });
    }

    return { output: `Email sent to ${userEmail}` };
  },
});

const workflow = createWorkflow({
  id: 'approval-workflow',
  inputSchema: z.object({ userEmail: z.string() }),
  outputSchema: z.object({ output: z.string() }),
})
  .then(approvalStep)
  .commit();
```

### Resuming a Suspended Workflow

```typescript
import { approvalStep } from './workflows/approval-workflow';

const workflow = mastra.getWorkflow('approvalWorkflow');
const run = await workflow.createRun();

// Start - will suspend
const result = await run.start({
  inputData: { userEmail: 'alex@example.com' },
});
// result.status === 'suspended'

// Resume with type-safe step reference
const resumed = await run.resume({
  step: approvalStep,           // Full type safety for resumeData
  resumeData: { approved: true },
});

// Or resume with step ID string
const resumed2 = await run.resume({
  step: 'wait-for-approval',
  resumeData: { approved: true },
});

// Or omit step to resume last suspended step
const resumed3 = await run.resume({
  resumeData: { approved: true },
});
```

### Resuming with a Known runId

```typescript
const workflow = mastra.getWorkflow('approvalWorkflow');
const run = await workflow.createRun({ runId: '123' });

const result = await run.resume({
  resumeData: { approved: true },
});
```

### Accessing Suspend Data on Resume

```typescript
const approvalStep = createStep({
  id: 'user-approval',
  inputSchema: z.object({ requestId: z.string() }),
  resumeSchema: z.object({ approved: z.boolean() }),
  suspendSchema: z.object({ reason: z.string(), requestDetails: z.string() }),
  outputSchema: z.object({ result: z.string() }),
  execute: async ({ inputData, resumeData, suspend, suspendData }) => {
    if (!resumeData?.approved) {
      return await suspend({
        reason: 'User approval required',
        requestDetails: `Request ${inputData.requestId} pending review`,
      });
    }
    // suspendData contains original suspend() payload
    const reason = suspendData?.reason || 'Unknown';
    return { result: `Approved - ${reason}` };
  },
});
```

### Identifying Suspended Steps

```typescript
const result = await run.start({ inputData: { userEmail: 'alex@example.com' } });

if (result.status === 'suspended') {
  console.log(result.suspended);     // e.g., ['wait-for-approval']
  // or for nested: ['nested-workflow', 'step-1']

  const suspendStep = result.suspended[0];
  const payload = result.steps[suspendStep[0]].suspendPayload;
  console.log(payload);
}
```

### Bail (Stop Without Error)

```typescript
const step = createStep({
  execute: async ({ inputData, resumeData, suspend, bail }) => {
    const { approved } = resumeData ?? {};

    if (approved === false) {
      return bail({ reason: 'User rejected the request.' });
    }

    if (!approved) {
      return await suspend({ reason: 'Human approval required.' });
    }

    return { message: `Approved` };
  },
});
```

Docs: https://mastra.ai/docs/workflows/suspend-and-resume

---

## 8. Human-in-the-Loop

Combine suspend/resume with UI interactions for human approval workflows.

```typescript
import { createWorkflow, createStep } from '@mastra/core/workflows';
import { z } from 'zod';

const humanReviewStep = createStep({
  id: 'human-review',
  inputSchema: z.object({
    content: z.string(),
    aiAnalysis: z.string(),
  }),
  outputSchema: z.object({
    approved: z.boolean(),
    feedback: z.string(),
  }),
  resumeSchema: z.object({
    approved: z.boolean(),
    feedback: z.string().optional(),
  }),
  suspendSchema: z.object({
    reason: z.string(),
  }),
  execute: async ({ inputData, resumeData, suspend }) => {
    if (!resumeData) {
      return await suspend({
        reason: 'Please review this content and provide feedback.',
      });
    }
    return {
      approved: resumeData.approved,
      feedback: resumeData.feedback || '',
    };
  },
});

// API endpoint to handle human response
app.post('/api/workflow/:runId/review', async (req, res) => {
  const { runId } = req.params;
  const { approved, feedback } = req.body;

  const workflow = mastra.getWorkflow('reviewWorkflow');
  const run = await workflow.createRun({ runId });

  const result = await run.resume({
    step: 'human-review',
    resumeData: { approved, feedback },
  });

  res.json(result);
});
```

### Multi-Turn Human Input

Each step must be resumed separately:

```typescript
const handleStep1Resume = async () => {
  const result = await run.resume({
    step: 'step-1',
    resumeData: { approved: true },
  });
};

const handleStep2Resume = async () => {
  const result = await run.resume({
    step: 'step-2',
    resumeData: { approved: true },
  });
};
```

Docs: https://mastra.ai/docs/workflows/human-in-the-loop

---

## 9. Error Handling

### Step-Level Error Handling

```typescript
const riskyStep = createStep({
  id: 'risky-operation',
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ data: z.string(), error: z.string().optional() }),
  execute: async ({ inputData }) => {
    try {
      const response = await fetch(inputData.url);
      if (!response.ok) {
        return { data: '', error: `HTTP ${response.status}` };
      }
      return { data: await response.text() };
    } catch (err) {
      return { data: '', error: err.message };
    }
  },
});
```

### Workflow-Level Error Handling

```typescript
const run = await workflow.createRun();

const result = await run.start({
  inputData: { url: 'https://example.com' },
});

if (result.status === 'failed') {
  console.error('Workflow failed:', result.error);
} else if (result.status === 'suspended') {
  console.log('Suspended at:', result.suspended);
} else if (result.status === 'tripwire') {
  console.log('Tripwire:', result.tripwire?.reason);
} else if (result.status === 'success') {
  console.log('Result:', result.result);
}
```

### Workflow Callbacks (onFinish, onError)

```typescript
const workflow = createWorkflow({
  id: 'callback-workflow',
  inputSchema: z.object({ value: z.string() }),
  outputSchema: z.object({ value: z.string() }),
  options: {
    onFinish: (result) => {
      console.log('Workflow finished with status:', result.status);
    },
    onError: (errorInfo) => {
      console.error('Workflow error:', errorInfo.error);
    },
  },
})
  .then(step1)
  .commit();
```

### Retry Pattern with Do-While

```typescript
const retryableStep = createStep({
  id: 'retryable',
  inputSchema: z.object({
    url: z.string(),
    attempt: z.number().default(0),
  }),
  outputSchema: z.object({
    data: z.string().optional(),
    status: z.enum(['success', 'retry', 'failed']),
    attempt: z.number(),
  }),
  execute: async ({ inputData }) => {
    try {
      const data = await fetch(inputData.url).then(r => r.text());
      return { data, status: 'success', attempt: inputData.attempt + 1 };
    } catch (err) {
      const attempt = inputData.attempt + 1;
      if (attempt >= 3) {
        return { status: 'failed', attempt };
      }
      return { status: 'retry', attempt };
    }
  },
});

const workflow = createWorkflow({ ... })
  .dowhile(
    retryableStep,
    async ({ inputData }) => inputData.status === 'retry',
  )
  .commit();
```

Docs: https://mastra.ai/docs/workflows/error-handling

---

## 10. Workflow Streaming

Stream workflow execution events in real-time.

```typescript
const run = await workflow.createRun();

const stream = run.stream({
  inputData: { message: 'Hello world' },
});

for await (const chunk of stream.fullStream) {
  console.log(chunk);
}

// Get the final result (same type as run.start())
const result = await stream.result;

if (result.status === 'success') {
  console.log(result.result);
}
```

Docs: https://mastra.ai/docs/workflows/overview#running-workflows

---

## 11. Run Management

### Creating and Starting Runs

```typescript
const testWorkflow = mastra.getWorkflow('testWorkflow');
const run = await testWorkflow.createRun();

const result = await run.start({
  inputData: { message: 'Hello world' },
});
```

### Restarting Active Runs

```typescript
// Restart a specific run from last active step
const restartedResult = await run.restart();

// Restart all active runs of a workflow
workflow.restartAllActiveWorkflowRuns();
```

### Listing Active Runs

```typescript
const activeRuns = await workflow.listActiveWorkflowRuns();
if (activeRuns.runs.length > 0) {
  console.log(activeRuns.runs);
}
```

### Cloning Workflows

```typescript
import { cloneWorkflow } from '@mastra/core/workflows';

const clonedWorkflow = cloneWorkflow(parentWorkflow, { id: 'cloned-workflow' });
```

Docs: https://mastra.ai/docs/workflows/overview

---

## 12. Common Patterns

### ETL Pipeline

```typescript
const etlWorkflow = createWorkflow({
  id: 'etl-pipeline',
  inputSchema: z.object({ source: z.string() }),
  outputSchema: z.object({ inserted: z.number() }),
})
  .then(extractStep)
  .then(transformStep)
  .then(loadStep)
  .commit();
```

### Fan-Out / Fan-In

```typescript
const fanOutFanIn = createWorkflow({
  id: 'fan-out-fan-in',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ combinedResult: z.string() }),
})
  .parallel([searchGoogleStep, searchBingStep, searchInternalStep])
  .map(async ({ inputData }) => ({
    allResults: Object.values(inputData).flat(),
  }))
  .then(rankResultsStep)
  .commit();
```

### RAG Pipeline with ForEach

```typescript
const ragWorkflow = createWorkflow({
  id: 'rag-pipeline',
  inputSchema: z.object({ content: z.string() }),
  outputSchema: z.array(z.object({ embedding: z.array(z.number()) })),
})
  .then(chunkStep)           // Returns array of chunks
  .foreach(embedStep)        // Process each chunk
  .commit();
```

### Multi-Document Processing with Nested Workflows

```typescript
const processDocWorkflow = createWorkflow({
  id: 'process-document',
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ embeddings: z.array(z.array(z.number())) }),
})
  .then(downloadStep)
  .then(chunkStep)
  .then(embedChunksStep)
  .commit();

const batchWorkflow = createWorkflow({
  id: 'batch-process',
  inputSchema: z.array(z.object({ url: z.string() })),
  outputSchema: z.array(z.object({ embeddings: z.array(z.array(z.number())) })),
})
  .foreach(processDocWorkflow, { concurrency: 3 })
  .commit();
```

### Approval Pipeline

```typescript
const approvalPipeline = createWorkflow({
  id: 'approval-pipeline',
  inputSchema: z.object({ request: z.string(), amount: z.number() }),
  outputSchema: z.object({ status: z.string() }),
})
  .then(validateRequestStep)
  .then(riskAssessmentStep)
  .branch([
    [async ({ inputData }) => inputData.riskLevel === 'low', autoApproveStep],
    [async ({ inputData }) => inputData.riskLevel === 'medium', managerApprovalStep],
    [async () => true, executiveApprovalStep],
  ])
  .then(notifyRequesterStep)
  .commit();
```

### Iterative Refinement

```typescript
const refinementWorkflow = createWorkflow({
  id: 'iterative-refinement',
  inputSchema: z.object({ prompt: z.string() }),
  outputSchema: z.object({ finalDraft: z.string() }),
})
  .then(generateDraftStep)
  .dowhile(
    refineStep,
    async ({ inputData }) => inputData.qualityScore < 0.9,
  )
  .then(finalizeStep)
  .commit();
```

---

## 13. Anti-Patterns

### NEVER forget `.commit()`

```typescript
// BAD - workflow will not work
const workflow = createWorkflow({ ... })
  .then(step1)
  .then(step2);

// GOOD - always end with .commit()
const workflow = createWorkflow({ ... })
  .then(step1)
  .then(step2)
  .commit();
```

### NEVER use untyped data

```typescript
// BAD - no schema validation
const step = createStep({
  id: 'bad-step',
  inputSchema: z.any(),
  outputSchema: z.any(),
  execute: async ({ inputData }) => inputData,
});

// GOOD - explicit schemas
const step = createStep({
  id: 'good-step',
  inputSchema: z.object({ text: z.string() }),
  outputSchema: z.object({ result: z.string() }),
  execute: async ({ inputData }) => ({ result: inputData.text.toUpperCase() }),
});
```

### NEVER ignore workflow result status

```typescript
// BAD - assumes success
const result = await run.start({ inputData });
console.log(result.result); // Might be undefined!

// GOOD - check status
const result = await run.start({ inputData });
if (result.status === 'success') {
  console.log(result.result);
} else if (result.status === 'suspended') {
  console.log('Suspended at:', result.suspended);
} else if (result.status === 'failed') {
  console.error('Failed:', result.error);
}
```

### NEVER chain .foreach().foreach() without flattening

```typescript
// BAD - creates nested arrays, hard to work with
workflow
  .foreach(downloadStep)
  .foreach(chunkStep)  // Creates array of arrays

// GOOD - use nested workflow or flatten with .map()
workflow
  .foreach(processDocWorkflow)  // Nested workflow handles full pipeline
  .commit();

// or
workflow
  .foreach(downloadStep)
  .foreach(chunkStep)
  .map(async ({ inputData }) => inputData.flat())
  .commit();
```

---

## 14. Debugging Tips

### Enable Verbose Logging

```typescript
const mastra = new Mastra({
  workflows: { myWorkflow },
  logger: { level: 'debug' },
});
```

### Inspect Step Input/Output via Result

```typescript
const result = await run.start({ inputData: { message: 'test' } });

// Inspect each step's result
for (const [stepId, stepResult] of Object.entries(result.steps)) {
  console.log(`Step: ${stepId}`);
  console.log(`  Status: ${stepResult.status}`);
  console.log(`  Input:`, stepResult.payload);
  console.log(`  Output:`, stepResult.output);
}
```

### Common Issues

1. **"Cannot read property of undefined" in step**
   - Check that previous step's outputSchema matches current step's inputSchema
   - Use `.map()` to transform data between incompatible schemas

2. **Workflow hangs indefinitely**
   - Check for infinite loops in dowhile/dountil conditions
   - Verify `suspend()` is called with `await` and `return`
   - Use `iterationCount` to limit loops

3. **Schema validation errors**
   - Use `schema.safeParse(data)` to test schemas independently
   - Ensure numbers aren't strings (common with form data)
   - Check optional fields use `.optional()` in Zod

4. **Steps execute in wrong order**
   - Verify .then(), .parallel(), .branch() chaining
   - Check .commit() is called at the end
   - Use streaming to observe execution order

5. **Resume not working**
   - Ensure `run` instance is the same (or recreated with same `runId`)
   - Verify step ID matches the suspended step
   - Check resumeData matches the step's `resumeSchema`
   - Try omitting `step` to auto-resume last suspended step

6. **Parallel output structure confusion**
   - Output is keyed by step `id`: `{ 'step-1': {...}, 'step-2': {...} }`
   - Next step's inputSchema must match this structure

---

## Quick Reference Links

- Workflows Overview: https://mastra.ai/docs/workflows/overview
- Control Flow: https://mastra.ai/docs/workflows/control-flow
- Workflow State: https://mastra.ai/docs/workflows/workflow-state
- Suspend & Resume: https://mastra.ai/docs/workflows/suspend-and-resume
- Human-in-the-Loop: https://mastra.ai/docs/workflows/human-in-the-loop
- Error Handling: https://mastra.ai/docs/workflows/error-handling
- Agents & Tools: https://mastra.ai/docs/workflows/agents-and-tools
- API Reference - Workflow: https://mastra.ai/reference/workflows/workflow
- API Reference - Step: https://mastra.ai/reference/workflows/step

SKILL_EOF
