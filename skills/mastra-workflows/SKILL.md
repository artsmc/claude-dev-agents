---
name: mastra-workflows
description: Mastra Workflow development guide - DAG composition, control flow, suspend/resume, HITL, time travel, state management, and streaming
---

# Mastra Workflow Development

Comprehensive guide for building DAG-based workflows with Mastra. Covers step creation, control flow patterns (.then, .parallel, .branch, .foreach, .map, loops, sleep), suspend/resume, human-in-the-loop, time travel debugging, workflow state, and streaming.

## Usage

```bash
/mastra-workflows
```

Provides context for:
- `createWorkflow()` and `createStep()` APIs
- DAG composition with `.commit()`
- Run management (`createRun()`, `start()`, `cancel()`, `restart()`)
- Suspend/resume with `resumeSchema`
- Human-in-the-loop approval patterns
- Workflow state (`stateSchema`, `setState`)
- Data mapping between steps
- Error handling strategies
