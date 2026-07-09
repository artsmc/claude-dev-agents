# Stage 6 Templates: Architecture Summary, Final Presentation & Error Display

Used by the orchestrator during Stage 6 (Final Review & Presentation) and on stage failure.

## ARCHITECTURE-SUMMARY.md Content Structure

File: `/job-queue/product-{name}/ARCHITECTURE-SUMMARY.md`

```markdown
# Architecture Summary: [Product Name]

## Research Completion

**Date:** [timestamp]
**Input:** [original input]
**Product Name:** [derived name]

## Recommended Architecture

### Technology Stack
- **Frontend**: [chosen technology]
- **Backend**: [chosen technology]
- **Database**: [chosen technology]
- **Deployment**: [chosen platform]

### Architectural Style
- [Monolithic/Microservices/Serverless]
- [Event-driven/Request-response]
- [SSR/CSR/SSG]

### Key Design Decisions

#### Runtime Execution
[1-2 sentence summary from runtime-execution.md]

#### Abstraction Layer
[1-2 sentence summary from abstraction-layer.md]

#### Integration Layer
[1-2 sentence summary from integration-layer.md]

#### Output Rendering
[1-2 sentence summary from output-rendering.md]

## Trade-offs & Risks

### Major Trade-offs
1. [Trade-off 1]: Chose X over Y because [reason]
2. [Trade-off 2]: Chose X over Y because [reason]

### Identified Risks
1. [Risk 1]: [Mitigation strategy]
2. [Risk 2]: [Mitigation strategy]

## Next Steps

To proceed with implementation:

1. Review detailed architecture documents:
   - `runtime-execution.md`
   - `abstraction-layer.md`
   - `integration-layer.md`
   - `output-rendering.md`

2. Set up development environment

3. Create initial project structure

4. Begin implementation with chosen tech stack

## Research Artifacts

All research is saved in:
- `/job-queue/product-{name}/`
- `/job-queue/product-{name}/research-notes/`

Total research sources consulted: [count]
```

## Completion Banner (display to user)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 PRODUCT RESEARCH COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Product: [Product Name]
Location: /job-queue/product-{name}/

Generated Documents:
  ✅ big-idea.md              - High-level vision and approach
  ✅ runtime-execution.md     - How the system executes work
  ✅ abstraction-layer.md     - How user intent becomes logic
  ✅ integration-layer.md     - How system connects externally
  ✅ output-rendering.md      - How results are delivered
  ✅ ARCHITECTURE-SUMMARY.md  - Executive summary

Recommended Stack:
  Frontend:   [technology]
  Backend:    [technology]
  Database:   [technology]
  Deployment: [platform]

Research Sources: [count] URLs consulted

Next Steps:
  1. Review detailed architecture docs in /job-queue/product-{name}/
  2. Approve or request revisions
  3. Begin implementation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Feedback Question (AskUserQuestion)

Use `AskUserQuestion`:
- **Question**: "Would you like to revise any architectural decisions?"
- **Options**:
  - "Approve - looks good" - "Proceed with this architecture"
  - "Revise runtime execution" - "Re-research execution model"
  - "Revise abstraction layer" - "Re-research abstraction approach"
  - "Revise integration layer" - "Re-research integrations"
  - "Revise output rendering" - "Re-research rendering strategy"

**If user approves:**
- Display: "✅ Architecture approved! Ready for implementation."

**If user requests revision:**
- Re-run the specific stage's research agent with feedback
- Regenerate that document
- Re-present for approval

## Stage-Failure Display (example)

```
❌ Research Failed at Stage 3/6: Abstraction Layer

Completed:
  ✓ [Stage 0] Workspace created
  ✓ [Stage 1] Big idea generated
  ✓ [Stage 2] Runtime execution researched
  ✗ [Stage 3] Abstraction layer FAILED

Error: [error message]

Partial work saved at: /job-queue/product-{name}/

Recovery:
  - Fix the issue and resume with: /new-product [input]
  - Or manually continue research
```
