---
name: mastra-evals
description: Mastra Evaluation and Testing guide - built-in scorers, custom scorers, datasets, experiments, and CI integration
---

# Mastra Evaluation and Testing

Comprehensive guide for evaluating AI agent quality with Mastra. Covers 17 built-in scorer factories, custom scorer creation with `createScorer()`, datasets for reproducible benchmarks, experiments for comparison, and CI pipeline integration.

## Usage

```bash
/mastra-evals
```

Provides context for:
- Scorer factory functions (e.g., `createAnswerRelevancyScorer()`)
- Import paths: `@mastra/evals/scorers/llm` and `@mastra/evals/scorers/code`
- `createScorer()` from `@mastra/core/scores`
- `runEvals({ target, scorers, data })`
- Dataset management (create, addItems, experiments)
- Experiment comparison and CI integration
- Agent-level scorer configuration with `sampling`
