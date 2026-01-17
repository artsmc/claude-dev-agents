# Document Hub Refactoring Plan

## Executive Summary

This plan outlines how to refactor the `commands/document-hub.md` into a modular architecture leveraging Claude Code best practices: **Skills**, **Hooks**, and **Custom Agents**.

**Current State:** Monolithic command file that combines persona instructions, workflow procedures, and command definitions.

**Target State:** Modular system with:
- 4 user-invocable skills
- 4 event-driven hooks
- 4 specialized agents
- Clear separation of concerns

---

## Analysis of Current Structure

### Current Components

1. **Persona Definition** - "Brain" character with memory-reset behavior
2. **Documentation Hub Structure** - 4 core markdown files
3. **Commands** - `/document-hub initialize` and `/document-hub update`
4. **Standard Operating Procedure** - Read-Plan-Execute-Document loop
5. **Complexity Management** - `/arch` subfolder creation logic

### Identified Patterns

- **Repetitive read operations** → Can be automated via hooks
- **Manual update proposals** → Can be agent-driven
- **Complexity assessment** → Specialized agent task
- **Initialization** → One-time skill
- **Update workflow** → Multi-step agent workflow

---

## Proposed Architecture

### 1. Skills (User-Invocable Commands)

Skills are explicit commands users invoke when they want to interact with the Documentation Hub.

#### Skill: `/document-hub initialize`
**Location:** `skills/document-hub-initialize.md`

**Purpose:** Bootstrap a new project's documentation hub

**Behavior:**
- Creates `/cline-docs` directory if not exists
- Creates 4 core files with templates:
  - `systemArchitecture.md`
  - `keyPairResponsibility.md`
  - `glossary.md`
  - `techStack.md`
- Prompts user for initial project details
- Uses interactive questions to gather context

**Implementation Notes:**
- Should be idempotent (safe to run multiple times)
- Validates existing files before overwriting
- Could invoke `documentation-analyst` agent for initial population

---

#### Skill: `/document-hub update`
**Location:** `skills/document-hub-update.md`

**Purpose:** Comprehensive review and update of all documentation

**Behavior:**
- Announces: "Initiating full review and update of Documentation Hub"
- Invokes `documentation-analyst` agent to:
  - Read all hub files
  - Analyze recent code changes
  - Propose specific updates
- Invokes `complexity-assessor` agent to check if `/arch` split needed
- Presents summary of proposed changes
- Waits for user confirmation before applying

**Implementation Notes:**
- This should orchestrate agents rather than do the work itself
- Can accept optional parameters: `--auto-apply`, `--scope=architecture`

---

#### Skill: `/document-hub read`
**Location:** `skills/document-hub-read.md`

**Purpose:** Explicitly read and summarize current documentation state

**Behavior:**
- Reads all files in `/cline-docs`
- Presents structured summary:
  - System architecture overview
  - Key modules and responsibilities
  - Tech stack summary
  - Glossary term count
- Identifies gaps or outdated information
- Suggests areas needing attention

**Implementation Notes:**
- Fast, read-only operation
- Useful for manual checks or debugging
- Could be invoked before complex tasks

---

#### Skill: `/document-hub analyze`
**Location:** `skills/document-hub-analyze.md`

**Purpose:** Deep analysis of codebase vs. documentation alignment

**Behavior:**
- Invokes `documentation-analyst` agent in analysis-only mode
- Scans codebase for:
  - New modules not documented
  - Changed responsibilities
  - New technologies not in tech stack
  - Domain terms not in glossary
- Reports discrepancies without making changes
- Recommends specific updates

**Implementation Notes:**
- Should be fast and non-destructive
- Useful before making updates
- Could run on schedule via CI/CD

---

### 2. Hooks (Event-Driven Automation)

Hooks automatically trigger actions based on system events, reducing manual overhead.

#### Hook: `on-conversation-start`
**Location:** `hooks/document-hub-session-start.md`

**Trigger:** At the beginning of every Claude Code session

**Behavior:**
- Automatically reads entire Documentation Hub
- Displays brief summary to Claude (not user)
- Sets context for session
- Equivalent to automatic "memory loading"

**Configuration:**
```json
{
  "hookType": "on-conversation-start",
  "name": "document-hub-session-start",
  "enabled": true,
  "silent": true
}
```

**Implementation Notes:**
- Should be fast (< 2 seconds)
- Silent execution (no user notification unless errors)
- Critical for "Brain" persona behavior

---

#### Hook: `on-task-complete`
**Location:** `hooks/document-hub-task-complete.md`

**Trigger:** After any task is marked complete via TodoWrite

**Behavior:**
- Analyzes completed task type:
  - Architecture change → Suggest architecture update
  - New module → Suggest responsibility update
  - New technology → Suggest tech stack update
- If significant change detected:
  - Presents quick prompt: "This task modified the architecture. Run `/document-hub update`?"
  - User can accept/decline

**Configuration:**
```json
{
  "hookType": "on-task-complete",
  "name": "document-hub-task-complete",
  "enabled": true,
  "severity": "medium",
  "conditions": {
    "significantChange": true
  }
}
```

**Implementation Notes:**
- Should be intelligent about when to trigger
- Avoid notification fatigue
- Could batch suggestions (e.g., after 3+ tasks)

---

#### Hook: `on-file-write`
**Location:** `hooks/document-hub-file-watch.md`

**Trigger:** When specific files are written/modified

**Watch Patterns:**
- `/cline-docs/**/*.md` - Documentation hub files
- `src/**/index.ts` - New modules
- `package.json` - Tech stack changes
- `*.config.js` - Configuration changes

**Behavior:**
- For hub file changes: Validate structure and links
- For new modules: Flag for responsibility documentation
- For package.json: Check if tech stack needs update
- For config changes: Check if architecture diagram needs update

**Configuration:**
```json
{
  "hookType": "on-file-write",
  "name": "document-hub-file-watch",
  "enabled": true,
  "patterns": [
    "/cline-docs/**/*.md",
    "src/**/index.ts",
    "package.json"
  ]
}
```

**Implementation Notes:**
- Should debounce (wait 5s after last change)
- Avoid triggering during batch operations
- Can be disabled during large refactors

---

#### Hook: `on-module-added`
**Location:** `hooks/document-hub-module-tracker.md`

**Trigger:** When a new module/directory is created in `src/`

**Behavior:**
- Invokes `glossary-builder` agent to scan new files
- Extracts new domain-specific terms
- Proposes glossary additions
- Checks if `keyPairResponsibility.md` needs update

**Configuration:**
```json
{
  "hookType": "on-directory-create",
  "name": "document-hub-module-tracker",
  "enabled": true,
  "patterns": ["src/**"]
}
```

**Implementation Notes:**
- Should run in background (non-blocking)
- Results presented as suggestion, not auto-applied
- Useful for large codebases

---

### 3. Custom Agents (Specialized Autonomous Agents)

Agents are specialized workers that handle complex, multi-step tasks autonomously.

#### Agent: `documentation-analyst`
**Location:** `agents/documentation-analyst.md`

**Specialization:** Comprehensive documentation analysis and updates

**Tools Available:**
- All tools (Read, Write, Edit, Glob, Grep, etc.)

**Responsibilities:**
1. **Analyze Phase:**
   - Read all `/cline-docs` files
   - Scan codebase structure via Glob/Grep
   - Compare documentation vs. actual code
   - Identify discrepancies

2. **Propose Phase:**
   - Generate specific update recommendations
   - Create updated Mermaid diagrams
   - Draft new glossary entries
   - Suggest responsibility changes

3. **Apply Phase:**
   - Update markdown files
   - Maintain formatting consistency
   - Cross-reference between files
   - Validate links and structure

**Invocation Examples:**
- From `/document-hub update` skill
- From hooks when significant changes detected
- Direct via Task tool: `Task(subagent_type="documentation-analyst", prompt="Analyze recent auth changes")`

**Key Behaviors:**
- Always reads entire hub before proposing changes
- Presents diff/preview before applying
- Maintains Mermaid diagram syntax correctness
- Follows hub file structure conventions

---

#### Agent: `architecture-diagrammer`
**Location:** `agents/architecture-diagrammer.md`

**Specialization:** Creating and maintaining Mermaid architecture diagrams

**Tools Available:**
- Read, Write, Edit (for markdown files)
- Glob, Grep (for code analysis)

**Responsibilities:**
1. **Generate Diagrams:**
   - Flowcharts for system architecture
   - ER diagrams for database schemas
   - Sequence diagrams for processes
   - Component diagrams for modules

2. **Maintain Existing:**
   - Update diagrams when architecture changes
   - Ensure consistency across related diagrams
   - Validate Mermaid syntax

3. **Complexity Management:**
   - Detect when single diagram becomes too complex
   - Recommend splitting into `/arch` subfolder
   - Create granular diagrams (auth_flow, data_pipeline, etc.)

**Invocation Examples:**
- From `documentation-analyst` agent
- From `/document-hub initialize` for initial diagrams
- Direct: `Task(subagent_type="architecture-diagrammer", prompt="Create sequence diagram for payment flow")`

**Key Behaviors:**
- Produces valid Mermaid syntax (v10+)
- Follows consistent styling conventions
- Includes descriptive comments in diagrams
- Tests diagrams if possible

---

#### Agent: `glossary-builder`
**Location:** `agents/glossary-builder.md`

**Specialization:** Building and maintaining domain-specific glossaries

**Tools Available:**
- Glob, Grep (for code scanning)
- Read, Edit (for glossary.md)

**Responsibilities:**
1. **Term Extraction:**
   - Scan variable names, function names, class names
   - Identify domain-specific terms (non-generic)
   - Extract context from comments and usage

2. **Definition Generation:**
   - Analyze term usage across codebase
   - Infer meaning from context
   - Generate clear, concise definitions

3. **Maintenance:**
   - Remove obsolete terms
   - Update definitions when usage changes
   - Organize alphabetically
   - Link related terms

**Invocation Examples:**
- From `/document-hub initialize` for initial glossary
- From hooks when new modules added
- From `/document-hub analyze` for gap detection

**Key Behaviors:**
- Focuses on domain-specific terms only (not generic tech terms)
- Provides examples of term usage
- Flags ambiguous terms for human review
- Avoids circular definitions

---

#### Agent: `complexity-assessor`
**Location:** `agents/complexity-assessor.md`

**Specialization:** Evaluating documentation complexity and structure

**Tools Available:**
- Read (for analyzing files)
- Glob (for directory structure)

**Responsibilities:**
1. **Complexity Metrics:**
   - Line count of `systemArchitecture.md`
   - Number of Mermaid diagrams per file
   - Diagram node/edge counts
   - Depth of nested sections

2. **Assessment:**
   - Determine if single-file architecture is too complex
   - Identify logical split points
   - Recommend `/arch` subfolder structure

3. **Recommendations:**
   - Propose specific files to create in `/arch`
   - Suggest diagram refactoring
   - Recommend index/navigation structure

**Invocation Examples:**
- From `/document-hub update` (automatic check)
- Periodic reviews (monthly)
- When architecture doc exceeds thresholds

**Key Behaviors:**
- Uses quantitative metrics (line count > 500 = complex)
- Considers conceptual cohesion
- Balances granularity vs. fragmentation
- Presents clear split recommendations

---

## Migration Strategy

### Phase 1: Create Skills (Week 1)
1. Extract `/document-hub initialize` → `skills/document-hub-initialize.md`
2. Extract `/document-hub update` → `skills/document-hub-update.md`
3. Create new `skills/document-hub-read.md`
4. Create new `skills/document-hub-analyze.md`
5. Test each skill independently

### Phase 2: Create Agents (Week 2)
1. Create `agents/documentation-analyst.md` (most complex)
2. Create `agents/architecture-diagrammer.md`
3. Create `agents/glossary-builder.md`
4. Create `agents/complexity-assessor.md`
5. Test agents via Task tool

### Phase 3: Integrate Skills + Agents (Week 3)
1. Update skills to invoke agents
2. Verify skill → agent communication
3. Test end-to-end workflows
4. Refine agent prompts based on results

### Phase 4: Create Hooks (Week 4)
1. Create `hooks/document-hub-session-start.md`
2. Create `hooks/document-hub-task-complete.md`
3. Create `hooks/document-hub-file-watch.md`
4. Create `hooks/document-hub-module-tracker.md`
5. Configure hook settings in Claude config

### Phase 5: Testing & Refinement (Week 5)
1. Test complete workflows on real projects
2. Gather feedback on automation levels
3. Tune hook sensitivity
4. Optimize agent performance
5. Document usage patterns

### Phase 6: Deprecate Original (Week 6)
1. Archive `commands/document-hub.md`
2. Create migration guide
3. Update documentation
4. Announce new structure

---

## File Structure (Post-Migration)

```
.claude/
├── skills/
│   ├── document-hub-initialize.md
│   ├── document-hub-update.md
│   ├── document-hub-read.md
│   └── document-hub-analyze.md
├── hooks/
│   ├── document-hub-session-start.md
│   ├── document-hub-task-complete.md
│   ├── document-hub-file-watch.md
│   └── document-hub-module-tracker.md
├── agents/
│   ├── documentation-analyst.md
│   ├── architecture-diagrammer.md
│   ├── glossary-builder.md
│   └── complexity-assessor.md
└── commands/
    └── document-hub.md  [DEPRECATED - keep for reference]
```

---

## Benefits of Refactoring

### Modularity
- Each component has single responsibility
- Easier to maintain and update
- Components can be reused independently

### Automation
- Hooks reduce manual overhead
- Automatic context loading
- Proactive documentation suggestions

### Specialization
- Agents become experts in their domain
- Better quality outputs
- Focused, optimized prompts

### Flexibility
- Users can disable/enable hooks
- Skills can be invoked independently
- Agents can be used in other contexts

### Scalability
- Easy to add new skills/hooks/agents
- Can extend without modifying existing
- Clear patterns for future development

---

## Potential Challenges

### Challenge 1: Hook Notification Fatigue
**Issue:** Too many hooks triggering suggestions
**Solution:**
- Implement debouncing
- Batch notifications
- Allow per-hook enable/disable
- Smart detection of "significant" changes

### Challenge 2: Agent Performance
**Issue:** Agents might be slow for large codebases
**Solution:**
- Implement caching mechanisms
- Scope analysis to changed files only
- Provide progress indicators
- Allow partial updates

### Challenge 3: Maintaining "Brain" Persona
**Issue:** Splitting might lose cohesive persona
**Solution:**
- Include persona instructions in each component
- Session-start hook maintains memory metaphor
- Skills reference "Brain" in descriptions
- Agents act as "Brain's assistants"

### Challenge 4: Backward Compatibility
**Issue:** Existing users accustomed to current command
**Solution:**
- Keep original file as deprecated
- Provide migration guide
- Support both during transition period
- Auto-suggest migration when old command used

---

## Success Metrics

### User Experience
- Reduced manual documentation overhead by 70%
- Faster onboarding to new projects
- More consistent documentation quality

### Technical
- Documentation accuracy > 95%
- Hook false positive rate < 10%
- Agent task completion > 90%

### Adoption
- Users actively using 3+ skills
- At least 2 hooks enabled per user
- Positive feedback on automation

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize components** (which skills/agents/hooks are MVP?)
3. **Create prototypes** for 1 skill + 1 agent + 1 hook
4. **Test prototype** on real project
5. **Iterate** based on feedback
6. **Full implementation** following migration strategy

---

## Appendix: Component Dependency Graph

```mermaid
graph TD
    U[User] -->|invokes| S1[/document-hub initialize]
    U -->|invokes| S2[/document-hub update]
    U -->|invokes| S3[/document-hub read]
    U -->|invokes| S4[/document-hub analyze]

    S1 -->|invokes| A1[documentation-analyst]
    S1 -->|invokes| A2[architecture-diagrammer]

    S2 -->|invokes| A1
    S2 -->|invokes| A4[complexity-assessor]

    S4 -->|invokes| A1

    H1[on-conversation-start] -->|reads| DC[/cline-docs]
    H2[on-task-complete] -->|suggests| S2
    H3[on-file-write] -->|validates| DC
    H4[on-module-added] -->|invokes| A3[glossary-builder]

    A1 -->|creates/updates| DC
    A2 -->|generates| DC
    A3 -->|maintains| DC
    A4 -->|analyzes| DC
```

---

## Appendix: Example Workflows

### Workflow 1: New Project Setup
1. User: `/document-hub initialize`
2. Skill prompts for project details
3. Skill invokes `documentation-analyst` agent
4. Agent creates 4 core files with initial content
5. Skill invokes `architecture-diagrammer` agent
6. Agent generates initial system architecture diagram
7. User reviews and confirms
8. Hook `on-conversation-start` enabled for future sessions

### Workflow 2: After Significant Refactoring
1. User completes large refactoring task
2. Hook `on-task-complete` triggers
3. Hook detects architectural changes
4. Hook suggests: "Run `/document-hub update`?"
5. User accepts
6. Skill `/document-hub update` invokes `documentation-analyst`
7. Agent analyzes changes, proposes updates
8. Skill invokes `complexity-assessor`
9. Assessor recommends creating `/arch` subfolder
10. User reviews proposed changes
11. User confirms, agents apply updates

### Workflow 3: Daily Development Flow
1. User starts new session
2. Hook `on-conversation-start` auto-reads hub (silent)
3. User works on feature, adds new module
4. Hook `on-module-added` triggers
5. Hook invokes `glossary-builder` agent (background)
6. Agent finds 3 new domain terms
7. User sees notification: "New glossary entries suggested"
8. User reviews and accepts
9. Session ends with up-to-date documentation

---

## Conclusion

This refactoring transforms the monolithic `document-hub.md` command into a modern, modular system that aligns with Claude Code best practices. By separating concerns into Skills, Hooks, and Agents, we achieve better maintainability, automation, and user experience while preserving the core "Brain" persona and documentation philosophy.

The phased migration strategy ensures smooth transition with minimal disruption to existing users, while the comprehensive testing plan validates functionality before full deployment.
