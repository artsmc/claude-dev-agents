---
name: mastra-agents
description: Mastra Agent development guide - creation, tools, memory, networks, processors, guardrails, voice, and structured output patterns
---

# Mastra Agent Development

Comprehensive guide for building Mastra agents with LLM integration, tool binding, memory configuration, agent networks, processors, guardrails, and voice capabilities. Loads validated API patterns from official Mastra documentation.

## Usage

```bash
/mastra-agents
```

Provides context for:
- Agent class constructor and configuration
- Model string format (`'provider/model-name'`)
- Tool integration with `createTool()`
- Memory integration with options-based config
- Structured output with `structuredOutput: { schema }`
- Agent networks via `.network()`
- Input/output processors
- Voice integration (TTS/STT)
