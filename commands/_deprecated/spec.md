# Spec Writer Command

This command initiates the feature specification workflow, leveraging MCP tools to access the latest documentation and the spec-writer agent to generate comprehensive feature documentation.

## Workflow Overview

You are initiating a **documentation-first feature planning workflow**. This command will:

1. **Research & Documentation Gathering** - Use MCP tools to access the latest framework/library documentation
2. **Codebase Analysis** - Analyze existing system architecture via Memory Bank
3. **Specification Generation** - Launch the spec-writer agent to create comprehensive feature docs
4. **Task Breakdown** - Generate actionable development tasks

## Phase 1: Pre-Planning Research

Before engaging the spec-writer agent, gather the latest documentation and context:

### Step 1: Identify Technology Stack
Ask the user:
- "What frameworks/technologies will this feature use? (e.g., Next.js, React, specific libraries)"
- "Are there any specific patterns or APIs you want to leverage?"

### Step 2: Fetch Latest Documentation

Based on the tech stack, use MCP tools to gather current best practices:

**For Next.js projects:**
```
1. Call mcp__next-devtools__init to fetch latest Next.js docs
2. Use mcp__next-devtools__nextjs_docs with action='search' to find relevant patterns
3. Query specific areas: Server Actions, Route Handlers, Data Fetching, Caching, etc.
```

**For other frameworks/libraries:**
```
1. Use WebSearch to find latest official documentation
2. Use WebFetch to retrieve specific documentation pages
3. Focus on: API reference, best practices, recent changes/deprecations
```

**For general research:**
```
1. Use WebSearch to find latest patterns and best practices
2. Search for similar implementations or case studies
3. Identify potential pitfalls or known issues
```

### Step 3: Memory Bank Analysis

Before creating new specs, check for existing work:
```
1. Read memory-bank/systemArchitecture.md to understand current system
2. Search Memory Bank for similar features or reusable components
3. Use mcp__memory__search_nodes to find relevant entities
4. Document any existing patterns to avoid duplication
```

## Phase 2: Launch Spec-Writer Agent

Now that you have the context, launch the spec-writer agent with a comprehensive prompt:

### Agent Launch Template

Use the Task tool with subagent_type="spec-writer" and provide:

```
I need comprehensive feature specifications for: [FEATURE NAME]

**Context from Documentation Research:**
[Summarize findings from MCP tools - latest patterns, APIs, best practices]

**Current System Architecture:**
[Summarize findings from Memory Bank - existing components, patterns]

**Feature Requirements:**
- Larger Feature Context: [Epic or initiative this belongs to]
- Feature Description: [Detailed description]
- Acceptance Criteria: [List known criteria]
- Technology Stack: [Frameworks, libraries, tools]

**Documentation Requirements:**
Please generate:
1. FRD (Feature Requirement Document) - Business requirements and objectives
2. FRS (Functional Requirement Document) - Detailed functional specifications
3. GS (Gherkin Specification) - BDD scenarios for testing
4. TR (Technical Requirements) - Implementation details, APIs, data models
5. Task List - Actionable development tasks

**Special Instructions:**
- Follow the folder structure: /job-queue/feature-{name}/docs/
- Ensure .gitignore contains /job-queue
- Reference latest documentation patterns discovered
- Highlight any reusable existing components
- Note any framework-specific considerations
```

## Phase 3: Quality Assurance

After the spec-writer agent completes, verify:

### Checklist
- [ ] All documentation files created (FRD, FRS, GS, TR, task-list.md)
- [ ] Documentation references latest framework patterns
- [ ] Existing components identified for reuse
- [ ] Task list is actionable and sequenced logically
- [ ] .gitignore includes /job-queue
- [ ] Gherkin scenarios cover acceptance criteria
- [ ] Technical requirements include API contracts, data models, dependencies

## Phase 4: User Review

Present the generated specifications to the user:

1. **Show folder structure** created
2. **Summarize each document** (1-2 sentence overview)
3. **Highlight key decisions** from documentation research
4. **Present task list** for review
5. **Ask for feedback** and iterate if needed

## Example Usage

**User:** "I need specs for a user authentication feature"

**You:**
1. Ask clarifying questions about tech stack
2. Fetch latest Next.js authentication docs via MCP
3. Search Memory Bank for existing auth patterns
4. Launch spec-writer agent with comprehensive context
5. Review generated specs with user

## Important Notes

- **Documentation-First:** Always research latest patterns before spec generation
- **No Duplication:** Always check Memory Bank to avoid recreating existing work
- **Latest Practices:** Use MCP tools to ensure specs follow current best practices
- **Framework-Specific:** Tailor specs to the specific framework/library versions being used
- **Actionable Tasks:** Ensure task list is concrete and developer-ready

---

## Success Criteria

This command is successful when:
1. User has clear, comprehensive specifications
2. Specs reference latest documentation and patterns
3. Existing codebase components are identified for reuse
4. Task list provides clear development path
5. All documentation is consistent and complete
