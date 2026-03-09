#!/usr/bin/env bash
# mastra-evals - Mastra Evaluation and Testing Skill
# Provides comprehensive guidance for evaluation-driven AI development with Mastra
cat << 'SKILL_EOF'

# Mastra Scorers: Evaluation-Driven AI Development

## Overview

Mastra Scorers enable evaluation-driven development for AI applications. Use scorers to
grade agent outputs against quality metrics, track quality over time with datasets, and
run experiments to compare model/prompt changes. Think of scorers as "unit tests for AI."

Key concepts:
- **Scorers** - Factory-created functions that grade agent output on specific dimensions (relevancy, faithfulness, tone, etc.)
- **Datasets** - Reusable collections of test cases (input/groundTruth pairs) managed via Mastra Studio or API
- **Experiments** - Named evaluation runs against a dataset, enabling A/B comparison of agents or prompts

---

## Architecture: The Scorer Pipeline

All scorers follow a four-step evaluation pipeline (only `generateScore` is required):

```
preprocess (optional) → analyze (optional) → generateScore (required) → generateReason (optional)
```

Each step can be a **function** (deterministic logic) or an **LLM prompt** (nuanced evaluation).

---

## Built-in Scorers

Install `@mastra/evals` to access built-in scorers. They come in two categories:

### LLM Scorers (require a judge model)
Import from `@mastra/evals/scorers/llm`:

```typescript
import {
  createAnswerRelevancyScorer,
  createAnswerSimilarityScorer,
  createBiasScorer,
  createCompletenessScorerLLM,
  createContextPrecisionScorer,
  createContextRelevanceScorerLLM,
  createFaithfulnessScorer,
  createHallucinationScorer,
  createNoiseSensitivityScorerLLM,
  createPromptAlignmentScorerLLM,
  createToneConsistencyScorerLLM,
  createToolCallAccuracyScorerLLM,
  createToxicityScorer,
} from '@mastra/evals/scorers/llm';
```

### Code/NLP Scorers (deterministic, no LLM needed)
Import from `@mastra/evals/scorers/code`:

```typescript
import {
  createContentSimilarityScorer,
  createKeywordCoverageScorer,
  createTextualDifferenceScorer,
  createToolCallAccuracyScorerCode,
} from '@mastra/evals/scorers/code';
```

### Scorer Reference

| Scorer | Category | Purpose | Scale |
|--------|----------|---------|-------|
| `createAnswerRelevancyScorer` | LLM | Measures query-answer alignment, completeness, detail level | 0-1 higher=better |
| `createAnswerSimilarityScorer` | LLM | Compares output to ground truth answers semantically | 0-1 higher=better |
| `createBiasScorer` | LLM | Detects biased language or viewpoints | 0-1 lower=better |
| `createCompletenessScorerLLM` | LLM | Checks if all aspects of the question are addressed | 0-1 higher=better |
| `createContextPrecisionScorer` | LLM | Evaluates context relevance ranking via MAP | 0-1 higher=better |
| `createContextRelevanceScorerLLM` | LLM | Measures context utility with weighted relevance levels | 0-1 higher=better |
| `createFaithfulnessScorer` | LLM | Verifies claims are grounded in provided context | 0-1 higher=better |
| `createHallucinationScorer` | LLM | Detects factual contradictions vs. context | 0-1 lower=better |
| `createNoiseSensitivityScorerLLM` | LLM | Tests robustness to noisy/irrelevant input (CI only) | 0-1 higher=better |
| `createPromptAlignmentScorerLLM` | LLM | Checks if output follows prompt instructions | 0-1 higher=better |
| `createToneConsistencyScorerLLM` | LLM | Measures consistency of tone across outputs | 0-1 higher=better |
| `createToolCallAccuracyScorerLLM` | LLM | Validates tool call appropriateness (semantic) | 0-1 higher=better |
| `createToxicityScorer` | LLM | Detects toxic or harmful content | 0-1 lower=better |
| `createContentSimilarityScorer` | Code | Character-level textual similarity with normalization | 0-1 higher=better |
| `createKeywordCoverageScorer` | Code | Measures keyword coverage ignoring stop words | 0-1 higher=better |
| `createTextualDifferenceScorer` | Code | Computes edit distance between strings | 0-1 higher=similar |
| `createToolCallAccuracyScorerCode` | Code | Exact-match tool call validation | 0-1 higher=better |

---

## Scorer Examples

### 1. AnswerRelevancyScorer (LLM)
```typescript
import { createAnswerRelevancyScorer } from '@mastra/evals/scorers/llm';
import { openai } from '@ai-sdk/openai';

const relevancyScorer = createAnswerRelevancyScorer({
  model: openai('gpt-4o-mini'),
  uncertaintyWeight: 0.3,  // Weight for partially relevant statements
});

const result = await relevancyScorer.run({
  input: 'What are the benefits of TypeScript?',
  output: 'TypeScript provides static typing, better IDE support, and catches errors at compile time.',
});
// result: { score: 0.95, reason: 'Answer directly addresses the question...' }
```

### 2. FaithfulnessScorer (LLM)
```typescript
import { createFaithfulnessScorer } from '@mastra/evals/scorers/llm';
import { openai } from '@ai-sdk/openai';

const faithfulnessScorer = createFaithfulnessScorer({
  model: openai('gpt-4o-mini'),
});

const result = await faithfulnessScorer.run({
  input: 'What is the company revenue?',
  output: 'The company revenue was $5M in 2024.',
  context: ['Annual report shows revenue of $5M for fiscal year 2024.'],
});
// result: { score: 1.0, reason: 'All claims are supported by context' }
```

### 3. ContentSimilarityScorer (Code)
```typescript
import { createContentSimilarityScorer } from '@mastra/evals/scorers/code';

const similarityScorer = createContentSimilarityScorer({
  caseSensitive: false,
  ignoreWhitespace: true,
});

const result = await similarityScorer.run({
  input: 'Original text content',
  output: 'original  text  content',
});
// result: { score: 1.0, reason: 'Texts match after normalization' }
```

### 4. ToolCallAccuracyScorer (LLM)
```typescript
import { createToolCallAccuracyScorerLLM } from '@mastra/evals/scorers/llm';
import { openai } from '@ai-sdk/openai';

const toolScorer = createToolCallAccuracyScorerLLM({
  model: openai('gpt-4o-mini'),
});

// Evaluates whether the tools called are semantically appropriate
// for the given user request (not just exact match)
```

---

## Custom Scorer Creation

### Using createScorer (Recommended)

Import from `@mastra/core/scores`:

```typescript
import { createScorer } from '@mastra/core/scores';
```

### Simple Code Scorer (no LLM)
```typescript
import { createScorer } from '@mastra/core/scores';

const jsonValidityScorer = createScorer({
  name: 'json-validity',
  description: 'Checks if the output is valid JSON',
})
.generateScore(({ run }) => {
  try {
    JSON.parse(run.output);
    return 1.0;
  } catch {
    return 0.0;
  }
})
.generateReason(({ score }) => {
  return score === 1.0 ? 'Output is valid JSON' : 'Output is not valid JSON';
});
```

### Full Pipeline Scorer
```typescript
import { createScorer } from '@mastra/core/scores';

const wordCountScorer = createScorer({
  name: 'word-count-check',
  description: 'Ensures output is between 50 and 200 words',
})
.preprocess(({ run }) => {
  const { output } = run;
  const wordCount = output.split(/\s+/).length;
  return { wordCount };
})
.analyze(({ results }) => {
  const { wordCount } = results.preprocessStepResult;
  const inRange = wordCount >= 50 && wordCount <= 200;
  return { wordCount, inRange };
})
.generateScore(({ results }) => {
  const { wordCount, inRange } = results.analyzeStepResult;
  if (inRange) return 1.0;
  return Math.max(0, 1 - Math.abs(wordCount - 125) / 125);
})
.generateReason(({ score, results }) => {
  const { wordCount } = results.analyzeStepResult;
  return `Word count ${wordCount} scored ${score.toFixed(2)} (target: 50-200 words)`;
});
```

### LLM-Judged Scorer
```typescript
import { createScorer } from '@mastra/core/scores';
import { openai } from '@ai-sdk/openai';

const domainAccuracyScorer = createScorer({
  name: 'domain-accuracy',
  description: 'Checks domain-specific accuracy using an LLM judge',
  model: openai('gpt-4o-mini'),  // Judge model
})
.analyze({
  // LLM prompt for analysis step
  prompt: `Analyze the following output for domain accuracy:
Input: {{input}}
Output: {{output}}
List any factual errors or inaccuracies.`,
})
.generateScore(({ results }) => {
  const { analyzeStepResult } = results;
  // Score based on LLM analysis
  return analyzeStepResult.includes('no errors') ? 1.0 : 0.5;
})
.generateReason(({ score, results }) => {
  return `Domain accuracy: ${score}. Analysis: ${results.analyzeStepResult}`;
});
```

---

## Adding Scorers to Agents (Live Evaluation)

Agents accept a `scorers` property for automatic real-time scoring of outputs:

```typescript
import { Agent } from '@mastra/core/agent';
import { createAnswerRelevancyScorer, createBiasScorer } from '@mastra/evals/scorers/llm';
import { openai } from '@ai-sdk/openai';

export const customerSupportAgent = new Agent({
  name: 'CustomerSupport',
  instructions: 'You are a helpful customer support agent',
  model: openai('gpt-4o'),
  scorers: {
    relevancy: {
      scorer: createAnswerRelevancyScorer({ model: openai('gpt-4o-mini') }),
      sampling: { type: 'ratio', rate: 0.5 }, // Score 50% of outputs
    },
    bias: {
      scorer: createBiasScorer({ model: openai('gpt-4o-mini') }),
      sampling: { type: 'ratio', rate: 1 },   // Score all outputs
    },
  },
});
```

Scoring results automatically persist to the `mastra_scorers` database table and are
visible in Mastra Studio's Playground "Scorers" tab.

---

## Running Evaluations in CI

### runEvals Function

```typescript
import { runEvals } from '@mastra/evals';

const result = await runEvals({
  data: [
    {
      input: 'weather in Berlin',
      groundTruth: { expectedLocation: 'Berlin', expectedCountry: 'DE' },
    },
    {
      input: 'weather in Berlin, Maryland',
      groundTruth: { expectedLocation: 'Berlin', expectedCountry: 'US' },
    },
  ],
  target: weatherAgent,
  scorers: [locationScorer, relevancyScorer],
});

// result.scores: { 'location-accuracy': 1.0, 'answer-relevancy': 0.95 }
// result.summary: { totalItems: 2 }
```

### Vitest Integration
```typescript
// evals/agent.eval.test.ts
import { describe, it, expect } from 'vitest';
import { runEvals } from '@mastra/evals';
import { createAnswerRelevancyScorer, createFaithfulnessScorer } from '@mastra/evals/scorers/llm';
import { openai } from '@ai-sdk/openai';
import { myAgent } from '../src/agents/my-agent';

describe('Agent Evals', () => {
  it('should score above 0.8 on answer relevancy', async () => {
    const result = await runEvals({
      data: [
        {
          input: 'What is TypeScript?',
          groundTruth: { expected: 'TypeScript is a typed superset of JavaScript.' },
        },
      ],
      target: myAgent,
      scorers: [
        createAnswerRelevancyScorer({ model: openai('gpt-4o-mini') }),
      ],
    });

    expect(result.scores['answer-relevancy']).toBeGreaterThan(0.8);
  }, 30000);

  it('should not hallucinate beyond context', async () => {
    const result = await runEvals({
      data: [
        {
          input: 'What features does the product have?',
          groundTruth: {
            expected: 'The product has feature A and feature B.',
            context: ['Product features: A - data sync, B - real-time alerts.'],
          },
        },
      ],
      target: myAgent,
      scorers: [
        createFaithfulnessScorer({ model: openai('gpt-4o-mini') }),
      ],
    });

    expect(result.scores['faithfulness']).toBeGreaterThan(0.9);
  }, 30000);
});
```

### GitHub Actions Example
```yaml
name: AI Eval Suite
on:
  pull_request:
    paths:
      - 'src/agents/**'
      - 'src/prompts/**'

jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx vitest run evals/
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Datasets

Datasets are versioned collections of test cases. Create them in Mastra Studio or via API.

### Create a Dataset
```typescript
const dataset = await mastra.datasets.create({
  name: 'my-test-suite',
  description: 'Agent quality test cases for customer support bot',
});
```

### Add Items to a Dataset
```typescript
await dataset.addItems([
  {
    input: 'How do I cancel my subscription?',
    groundTruth: {
      expected: 'To cancel, go to Settings > Billing > Cancel Subscription.',
      context: ['Cancellation is available in Settings under Billing section.'],
    },
  },
  {
    input: 'What are your business hours?',
    groundTruth: {
      expected: 'We are open Monday-Friday, 9 AM to 5 PM EST.',
      context: ['Business hours: Mon-Fri 9:00-17:00 Eastern Time.'],
    },
  },
]);
```

---

## Experiments

Experiments run each dataset item through a target (agent, workflow, or function) and
score the output, giving you a consistent and repeatable measure of performance.

### Run an Experiment (Synchronous - for CI)
```typescript
const experiment = await dataset.startExperiment({
  name: 'v2-gpt4o-test',
  targetType: 'agent',
  targetId: 'customer-support',
  scorers: [
    createAnswerRelevancyScorer({ model: openai('gpt-4o-mini') }),
    createFaithfulnessScorer({ model: openai('gpt-4o-mini') }),
  ],
  description: 'Testing GPT-4o model upgrade',
});

// experiment includes summary with per-item scores and outputs
```

### Run an Experiment (Async - for large datasets)
```typescript
const experiment = await dataset.startExperimentAsync({
  name: 'large-scale-eval',
  targetType: 'agent',
  targetId: 'customer-support',
  scorers: [relevancyScorer, faithfulnessScorer],
});
// Runs in background; check status in Mastra Studio
```

---

## Scorer Utilities

Import from `@mastra/evals/scorers/utils`:

```typescript
import {
  getAssistantMessageFromRunOutput,
  getReasoningFromRunOutput,
  getUserMessageFromRunInput,
  getSystemMessagesFromRunInput,
  getCombinedSystemPrompt,
  extractToolCalls,
  extractInputMessages,
  extractAgentResponseMessages,
} from '@mastra/evals/scorers/utils';
```

These utilities help extract and process data from scorer run inputs and outputs,
particularly useful in the `preprocess` step of custom scorers.

---

## Best Practices

1. **Start with AnswerRelevancy + Faithfulness** - These two scorers cover the most common quality issues and provide a solid baseline.

2. **Use LLM scorers for nuance, code scorers for speed** - LLM scorers (from `scorers/llm`) provide semantic evaluation; code scorers (from `scorers/code`) are fast and deterministic.

3. **Add domain-specific custom scorers** - Build custom scorers with `createScorer` that validate your specific business rules and output formats.

4. **Run evals in CI for every PR** - Use `runEvals()` with Vitest or Jest. Treat eval regressions like test failures.

5. **Add live scoring to agents in production** - Use the `scorers` property on Agent with `sampling` config to monitor quality without scoring every request.

6. **Use datasets for reproducible benchmarks** - Build curated datasets that represent real usage patterns. Datasets are versioned automatically.

7. **Compare experiments when changing models or prompts** - Never change a model or prompt without running a comparative experiment.

8. **Separate fast evals from slow evals** - Run code scorers (keyword coverage, content similarity) on every commit. Run LLM scorers on PRs.

---

## Documentation Links

- Scorers Overview: https://mastra.ai/docs/scorers/overview
- Built-in Scorers: https://mastra.ai/docs/scorers/built-in-scorers
- Custom Scorers: https://mastra.ai/docs/scorers/custom-scorers
- Running in CI: https://mastra.ai/docs/evals/running-in-ci
- createScorer API: https://mastra.ai/reference/scorers/create-scorer
- MastraScorer API: https://mastra.ai/reference/scorers/mastra-scorer
- Datasets: https://mastra.ai/docs/observability/datasets/overview
- Experiments: https://mastra.ai/docs/observability/datasets/running-experiments

SKILL_EOF
