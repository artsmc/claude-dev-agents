# Mastra Dev Best Practices

> Part of the `mastra-dev` skill. DO/DON'T checklists for agent development, workflow design, tool development, MCP integration, and testing/debugging. Moved verbatim from SKILL.md.

## Best Practices

### 1. Agent Development

✅ **DO:**
- Use clear, specific instructions
- Choose appropriate models for tasks (Opus for complex reasoning, Sonnet for speed)
- Register only necessary tools (avoid tool overload)
- Test agents with `agent.generate()` before production use
- Use memory systems for conversation context

❌ **DON'T:**
- Use generic instructions like "You are a helpful assistant"
- Register all available tools (increases latency and confusion)
- Skip testing agent behavior
- Hardcode API keys or secrets in agent definitions

### 2. Workflow Design

✅ **DO:**
- Define clear input/output schemas for every step
- Use `.parallel()` for independent operations
- Implement retry policies for unstable external APIs
- Add error handling with lifecycle callbacks
- Validate schema compatibility between steps
- Use `.commit()` to finalize workflow definitions

❌ **DON'T:**
- Create circular dependencies (DAG must be acyclic)
- Skip schema definitions (causes runtime errors)
- Use `.branch()` without proper conditionals
- Forget to call `.commit()` at the end
- Ignore step execution order requirements

### 3. Tool Development

✅ **DO:**
- Write descriptive tool descriptions for agents
- Use Zod for comprehensive input validation
- Handle edge cases and errors gracefully
- Return structured data matching output schema
- Test tools independently before agent integration

❌ **DON'T:**
- Use vague descriptions (agents won't know when to call)
- Skip input validation (leads to runtime errors)
- Return inconsistent output structures
- Assume external APIs are always available
- Expose sensitive operations without safeguards

### 4. MCP Integration

✅ **DO:**
- Use stdio transport for local MCP servers
- Use HTTP transport for remote MCP servers
- Test MCP connections with `/mastra-dev mcp test`
- Document which agents use which MCP tools
- Version MCP server configurations

❌ **DON'T:**
- Mix stdio and HTTP incorrectly
- Skip connection testing
- Hardcode URLs in MCP config
- Forget to restart server after MCP changes

### 5. Testing & Debugging

✅ **DO:**
- Test workflows with representative data
- Use Mastra Studio for visual debugging
- Check logs regularly during development
- Validate configurations before committing
- Debug failed executions with execution IDs

❌ **DON'T:**
- Skip testing with real data
- Ignore workflow execution failures
- Deploy without validating configurations
- Debug in production (use staging/dev environments)

