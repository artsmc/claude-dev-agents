# Fix 4: Standardize + Modularize Agent Definitions

## Problem

The 19 agent `.md` files in `~/.claude/agents/` suffer from three compounding defects:

**1. Format Inconsistency**
Six agents lack YAML frontmatter entirely (`express-api-developer`, `mastra-core-developer`, `mastra-framework-expert`, `strategic-planner`, `team-lead`, and one unnamed file). Among the 13 with frontmatter, field coverage varies: only `api-designer` and `technical-writer` declare `tools:` restrictions; `color:` is inconsistently named (e.g., `darkred` vs `red`); and the `name:` field sometimes mismatches the filename (e.g., `nextjs-code-reviewer.md` has `name: code-reviewer`, `frontend-developer.md` has `name: front-end-developer`, `nextjs-qa-developer.md` has `name: qa-engineer`).

**2. Size Bloat**
Five agents exceed 20KB, with `security-auditor` at 41KB and `mastra-core-developer` at 35KB. The OpenDev finding is directly applicable: at 40KB+ the entire agent body must load into context on every invocation, consuming tokens for content that is rarely needed. The median small-agent size (6–10KB) is reasonable; the outliers represent 3–5x the necessary context load.

Evidence:
- `security-auditor.md` — 41,162 bytes (~40KB): OWASP checklists, CVE references, FedRAMP controls all loaded regardless of task type
- `mastra-core-developer.md` — 35,205 bytes (~34KB): Contains full code examples for every Mastra API surface
- `technical-writer.md` — 34,634 bytes (~34KB): Includes exhaustive style guides and documentation templates
- `debugger-specialist.md` / `devops-infrastructure.md` — ~29KB each: Large encyclopedic reference sections

**3. Missing Self-Check Patterns**
Only 11/19 agents have confidence-level or self-check patterns. The remaining 8 (`accessibility-specialist`, `database-schema-specialist`, `express-api-developer`, `mastra-framework-expert`, `nextjs-code-reviewer`, `spec-writer`, `strategic-planner`, `team-lead`) will proceed without stating confidence or flagging ambiguity.

**4. No Consistent Model Assignment Rationale**
Frontmatter `model:` fields are present on 13 agents, but assignments are inconsistent and unjustified. Agents doing structured output generation (api-designer, spec-writer) correctly use `sonnet`, but `ui-developer` uses `opus` despite writing predictable TSX components. `nextjs-qa-developer` and `nextjs-code-reviewer` are both assigned `opus` for tasks that Sonnet handles well. No agent uses `haiku`.

---

## Current State Audit

### Agent Inventory

| Agent File | Size | Has Frontmatter | Has Self-Check | Current Model | Filename/Name Mismatch |
|---|---|---|---|---|---|
| accessibility-specialist.md | 16,952 B (17KB) | Yes | No | opus | No |
| api-designer.md | 27,340 B (27KB) | Yes | Yes (🟢🟡🔴) | sonnet | No |
| database-schema-specialist.md | 17,255 B (17KB) | Yes | No | opus | No |
| debugger-specialist.md | 29,780 B (29KB) | Yes | Yes | opus | No |
| devops-infrastructure.md | 29,756 B (29KB) | Yes | Yes | opus | No |
| express-api-developer.md | 6,578 B (6KB) | No | No | (none) | No |
| frontend-developer.md | 8,428 B (8KB) | Yes | Yes | sonnet | Yes: name=front-end-developer |
| mastra-core-developer.md | 35,205 B (34KB) | No | Yes | (none) | No |
| mastra-framework-expert.md | 20,632 B (20KB) | No | No | (none) | No |
| nextjs-backend-developer.md | 26,666 B (26KB) | Yes | Yes | opus | No |
| nextjs-code-reviewer.md | 10,388 B (10KB) | Yes | No | opus | Yes: name=code-reviewer |
| nextjs-qa-developer.md | 7,793 B (8KB) | Yes | Yes | opus | Yes: name=qa-engineer |
| refactoring-specialist.md | 22,682 B (22KB) | Yes | Yes | sonnet | No |
| security-auditor.md | 41,162 B (40KB) | Yes | Yes | opus | No |
| spec-writer.md | 8,426 B (8KB) | Yes | No | sonnet | No |
| strategic-planner.md | 7,805 B (8KB) | No | No | (none) | No |
| team-lead.md | 9,707 B (10KB) | No | No | (none) | No |
| technical-writer.md | 34,634 B (34KB) | Yes | Yes | sonnet | No |
| ui-developer.md | 5,109 B (5KB) | Yes | No | opus | No |

**Summary stats:**
- Agents with frontmatter: 13/19
- Agents with self-check: 11/19
- Agents over 20KB (bloated): 7/19
- Agents with name/filename mismatch: 3/19
- Agents with tools restrictions: 2/19 (api-designer, technical-writer)

---

## Standard Agent Format

### Frontmatter Schema (exact YAML fields)

Every agent MUST begin with this frontmatter block:

```yaml
---
name: <filename-without-extension>  # MUST match filename exactly
description: >-
  <One or two sentences: what this agent does. When to invoke it.
  Examples of triggering phrases (kept concise — not 500-word essays).>
model: <claude-sonnet-4-6 | claude-opus-4-6 | claude-haiku-4-5-20251001>
tools: [Read, Grep, Glob, Write, Edit, Bash]  # Restrict to what agent actually needs
---
```

**Field rules:**
- `name`: lowercase, hyphenated, must exactly match filename stem. No exceptions.
- `description`: 2–4 sentences maximum. If the current description is a multi-paragraph essay, it must be condensed. The description is used for routing; it does not need to be exhaustive.
- `model`: Use full model ID string. No shorthand aliases like `opus` or `sonnet` — these may be ambiguous across Claude versions.
- `tools`: Explicitly list only what the agent uses. Read-only agents (api-designer, technical-writer, spec-writer) must be restricted to `[Read, Grep, Glob]`. Implementation agents may include `Write, Edit, Bash`.

### Required Sections (in order)

Every agent body MUST contain these sections in this order:

```markdown
## Role

One paragraph. What this agent is, what it does, what it does NOT do.

## When to Use

Bulleted list of 4–8 specific trigger scenarios. Replaces the verbose description essay.

## Confidence Protocol

[Required in every agent — see pattern below]

## Core Expertise

Domain knowledge, patterns, rules. This is the main content section.
May include subsections. Size budget: 80% of total agent budget.

## Self-Verification Checklist

[ ] Item 1
[ ] Item 2
...
```

**Sections that are FORBIDDEN** (they bloat without adding value):
- "Your Design Philosophy" (subsumes into Role)
- "Example Interactions" (takes up 20% of file size with illustrative content that is rarely needed)
- "Integration with Development Workflow" (workflow is in CLAUDE.md, not agents)
- Duplicate self-check sections (several agents have two checklist blocks)

### Size Budget

| Agent Category | Max Size | Rationale |
|---|---|---|
| Orchestration agents (team-lead, strategic-planner) | 8KB | High-level coordination, minimal domain detail |
| Design/planning agents (api-designer, spec-writer) | 15KB | Need process steps but not exhaustive examples |
| Implementation agents (express-api-developer, ui-developer, etc.) | 15KB | Patterns and rules, not encyclopedias |
| Specialist/audit agents (security-auditor, debugger-specialist) | 20KB | Legitimately complex checklists — use modularization |
| Framework experts (mastra-core-developer, mastra-framework-expert) | 15KB core + modules | Core must be <15KB; deep content in loadable modules |

**Hard limit: 20KB for any single agent file. Above this, extract to modules.**

### Confidence Protocol (required in all agents)

Every agent must include this section verbatim as a starting point, then adapt wording:

```markdown
## Confidence Protocol

Before acting, assess:
- **High (proceed):** Requirements are clear, patterns are established, path is obvious
- **Medium (state assumptions):** Mostly clear but requires assumptions — state them explicitly
- **Low (ask first):** Ambiguous, conflicting, or missing critical information — request clarification before writing any code or documents

Always state confidence level in the first response.
```

---

## Modularization Strategy

### Which Agents Need Splitting

Three agents are large enough to require a module pattern:

**1. security-auditor (41KB → core 15KB + 2 modules)**

Current structure mixes: OWASP checklists, CVE scanning instructions, FedRAMP/NIST control references, penetration testing guidance, and authentication review patterns. These are rarely needed simultaneously.

Proposed split:
- `security-auditor.md` (core, 15KB) — identity, confidence protocol, authentication/authorization review, input validation checklist, dependency scanning workflow
- `security-auditor-compliance.md` (module, ~10KB) — FedRAMP/NIST 800-53 controls, GDPR/HIPAA/PCI DSS, 7-year retention requirements, Section 508
- `security-auditor-pentest.md` (module, ~10KB) — penetration testing guidance, OWASP ZAP/Burp Suite patterns, threat modeling

**2. mastra-core-developer (35KB → core 15KB + 2 modules)**

Current content mixes: DAG workflow composition, agent lifecycle, tool integration, BullMQ patterns, LiteLLM multi-provider patterns, and MCP server/client code. The code examples alone account for ~18KB.

Proposed split:
- `mastra-core-developer.md` (core, 15KB) — identity, DAG patterns, agent lifecycle, tool schema patterns, when-to-use-which-pattern guidance
- `mastra-core-developer-workflows.md` (module, ~10KB) — `.then()`, `.parallel()`, `.branch()`, `.foreach()` examples, error handling, step retry patterns
- `mastra-core-developer-mcp.md` (module, ~8KB) — MCP server/client setup, tool registration, multi-LLM provider switching via LiteLLM

**3. technical-writer (34KB → core 15KB + 1 module)**

Current content mixes writing process with exhaustive style guides (voice, tone, grammar rules) that are rarely consulted mid-task.

Proposed split:
- `technical-writer.md` (core, 15KB) — identity, documentation types, process workflow, self-check
- `technical-writer-style.md` (module, ~12KB) — style guide, voice/tone rules, API doc conventions, changelog formats

### Module Loading Convention

When an agent needs to load a module, it follows this pattern (stated in the core agent's instructions):

```markdown
## Extended Reference

For compliance requirements, read: ~/.claude/agents/modules/security-auditor-compliance.md
For penetration testing guidance, read: ~/.claude/agents/modules/security-auditor-pentest.md

Load the relevant module ONLY when the task explicitly requires it.
```

Modules live in `~/.claude/agents/modules/` to keep the main agents directory clean.

---

## Model Assignments

### Rationale Framework

- **Opus:** Tasks requiring multi-step reasoning over ambiguous inputs, cross-system architectural decisions, complex debugging where root cause is non-obvious. The cost premium is justified only when the task genuinely requires broader reasoning.
- **Sonnet:** Tasks with clear structure and known output format. Code generation following established patterns, documentation writing, API contract generation, testing. Sonnet is faster and handles well-scoped implementation tasks reliably.
- **Haiku:** Tasks that are purely mechanical — reading and summarizing files, extracting data from known formats, running simple scripts. No agent currently warrants Haiku because all agents require some judgment.

### Model Assignment Table

| Agent | Assigned Model | Rationale |
|---|---|---|
| accessibility-specialist | claude-sonnet-4-6 | WCAG rules are well-defined; implementation is systematic, not creative |
| api-designer | claude-sonnet-4-6 | Structural design with known patterns; current assignment correct |
| database-schema-specialist | claude-sonnet-4-6 | Schema design follows normalization rules; migration writing is pattern-based |
| debugger-specialist | claude-opus-4-6 | Root cause analysis over ambiguous symptoms; non-obvious cross-system failures |
| devops-infrastructure | claude-sonnet-4-6 | CI/CD and container config follows known patterns; IaC is template-based |
| express-api-developer | claude-sonnet-4-6 | Pattern-following implementation with established rules in CLAUDE.md |
| frontend-developer | claude-sonnet-4-6 | State management and data fetching follow established React patterns |
| mastra-core-developer | claude-opus-4-6 | Complex workflow orchestration with DAG reasoning; multi-system debugging |
| mastra-framework-expert | claude-opus-4-6 | Cross-subsystem architectural decisions; routing across 6+ Mastra subsystems |
| nextjs-backend-developer | claude-sonnet-4-6 | Pattern-following Next.js API route implementation |
| nextjs-code-reviewer | claude-sonnet-4-6 | Code review against known rules; pattern matching, not open-ended reasoning |
| nextjs-qa-developer | claude-sonnet-4-6 | BDD test writing follows Gherkin → code translation; highly structured |
| refactoring-specialist | claude-sonnet-4-6 | Current assignment correct; refactoring follows analysis patterns |
| security-auditor | claude-opus-4-6 | Vulnerability analysis requires adversarial reasoning; non-obvious attack chains |
| spec-writer | claude-sonnet-4-6 | Structured document generation; current assignment correct |
| strategic-planner | claude-opus-4-6 | Architecture planning requires broad reasoning over system context |
| team-lead | claude-opus-4-6 | Coordination decisions require understanding parallel workstream tradeoffs |
| technical-writer | claude-sonnet-4-6 | Documentation writing is structured; current assignment correct |
| ui-developer | claude-sonnet-4-6 | TSX component writing follows established patterns; Opus is overkill |

**Net change:** Move 4 agents from `opus` → `sonnet` (accessibility-specialist, database-schema-specialist, ui-developer, nextjs-code-reviewer + nextjs-qa-developer + devops-infrastructure). Add `opus` to 2 agents with no model (strategic-planner, team-lead).

---

## Tool Restriction Instructions

Claude Code respects the `tools:` frontmatter field to restrict what tools an agent can invoke. Currently only 2/19 agents use this.

### Tool Restriction Profiles

**Profile A: Read-Only** — Design, planning, review, documentation agents
```yaml
tools: [Read, Grep, Glob]
```
These agents analyze and produce documents. They never write application code.

**Profile B: Write** — Implementation agents that produce code files
```yaml
tools: [Read, Grep, Glob, Write, Edit]
```
These agents write code but do not need to execute shell commands.

**Profile C: Full** — Agents that must run tests, linters, migrations, or scripts
```yaml
tools: [Read, Grep, Glob, Write, Edit, Bash, mcp__filesystem__write_file]
```
These agents need shell access to validate their own work.

### Agent Tool Assignment Table

| Agent | Profile | Tools | Rationale |
|---|---|---|---|
| accessibility-specialist | B | Read, Grep, Glob, Write, Edit | Writes test scripts and ARIA fixes; no shell needed |
| api-designer | A | Read, Grep, Glob | Design-only; never writes code |
| database-schema-specialist | C | Read, Grep, Glob, Write, Edit, Bash | Runs Prisma migrations to validate schema |
| debugger-specialist | C | Read, Grep, Glob, Write, Edit, Bash | Runs commands to reproduce bugs |
| devops-infrastructure | C | Read, Grep, Glob, Write, Edit, Bash | Executes docker/nx/terraform commands |
| express-api-developer | C | Read, Grep, Glob, Write, Edit, Bash | Runs tests after implementation |
| frontend-developer | B | Read, Grep, Glob, Write, Edit | Writes code; test execution handled by qa agent |
| mastra-core-developer | C | Read, Grep, Glob, Write, Edit, Bash | Runs worker processes and Mastra CLI |
| mastra-framework-expert | A | Read, Grep, Glob | Architectural guidance only; routes to specialists |
| nextjs-backend-developer | C | Read, Grep, Glob, Write, Edit, Bash | Runs Next.js build to verify |
| nextjs-code-reviewer | A | Read, Grep, Glob | Review only; never modifies code |
| nextjs-qa-developer | C | Read, Grep, Glob, Write, Edit, Bash | Runs test suite to verify coverage |
| refactoring-specialist | C | Read, Grep, Glob, Write, Edit, Bash | Needs to run tests after each refactoring step |
| security-auditor | C | Read, Grep, Glob, Bash | Runs npm audit, grep for vulnerabilities; writes findings |
| spec-writer | B | Read, Grep, Glob, Write | Creates spec docs; never writes application code |
| strategic-planner | A | Read, Grep, Glob | Planning only; no code generation |
| team-lead | A | Read, Grep, Glob | Coordination only; spawns sub-agents via Task tool |
| technical-writer | A | Read, Grep, Glob | Documentation only; current restriction correct |
| ui-developer | B | Read, Grep, Glob, Write, Edit | Writes TSX/CSS; test execution separate |

---

## Migration Plan

Per-agent specific action items. Agents are grouped by migration complexity.

### Group 1: Add Frontmatter Only (no content changes needed)
These agents have good content but no YAML frontmatter. Add frontmatter block only.

**express-api-developer.md** (6KB — good size, good content, no self-check)
- Add frontmatter: `name: express-api-developer`, `model: claude-sonnet-4-6`, `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Add Confidence Protocol section (8 lines)
- No other changes. File is already well-structured and appropriately sized.

**strategic-planner.md** (8KB — good size, no self-check)
- Add frontmatter: `name: strategic-planner`, `model: claude-opus-4-6`, `tools: [Read, Grep, Glob]`
- Add Confidence Protocol section
- Add Self-Verification Checklist section (currently absent)

**team-lead.md** (10KB — good size, no self-check)
- Add frontmatter: `name: team-lead`, `model: claude-opus-4-6`, `tools: [Read, Grep, Glob]`
- Add Confidence Protocol section
- No other content changes needed

### Group 2: Fix Name Mismatch + Add/Correct Frontmatter Fields

**frontend-developer.md** (8KB — has frontmatter but name is `front-end-developer`)
- Change `name: front-end-developer` to `name: frontend-developer`
- Change `model: sonnet` to `model: claude-sonnet-4-6` (use full model ID)
- Add `tools: [Read, Grep, Glob, Write, Edit]`

**nextjs-code-reviewer.md** (10KB — has frontmatter but name is `code-reviewer`)
- Change `name: code-reviewer` to `name: nextjs-code-reviewer`
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob]`
- Add Confidence Protocol section

**nextjs-qa-developer.md** (8KB — has frontmatter but name is `qa-engineer`)
- Change `name: qa-engineer` to `name: nextjs-qa-developer`
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit, Bash]`

### Group 3: Model Corrections + Tool Restrictions (no content changes)

**accessibility-specialist.md** (17KB)
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit]`
- Add Confidence Protocol section
- Content quality is good; no structural changes needed

**database-schema-specialist.md** (17KB)
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Add Confidence Protocol section

**devops-infrastructure.md** (29KB — bloated but borderline)
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Review content: remove "Example Interactions" section if present (~3–5KB savings)
- Target: reduce to under 22KB without losing critical content

**ui-developer.md** (5KB — already lean)
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit]`
- Add Confidence Protocol section
- Add Self-Verification Checklist section

**nextjs-backend-developer.md** (26KB — needs trimming)
- Change `model: opus` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Remove duplicate checklist blocks (currently has two)
- Target: reduce to under 18KB by condensing memory/doc protocol section

### Group 4: Content Restructuring (description condensation)

**api-designer.md** (27KB — over budget, needs trimming)
- `model` and `tools` already correct
- The description in frontmatter is 400+ words — condense to 3 sentences
- Remove "Example Interactions" section (~3KB)
- Remove duplicate Self-Verification Checklist (has two identical-purpose blocks)
- Target: reduce to 18KB

**refactoring-specialist.md** (22KB — borderline)
- Fix `model: sonnet` to `model: claude-sonnet-4-6` (full ID)
- Add `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Condense description from multi-paragraph essay to 3 sentences
- Target: reduce to 16KB by removing "Example Interactions"

**spec-writer.md** (8KB — good size but no self-check)
- Fix `model: sonnet` to `model: claude-sonnet-4-6`
- Add `tools: [Read, Grep, Glob, Write]`
- Add Confidence Protocol section
- Add Self-Verification Checklist section
- Condense description to 3 sentences

**technical-writer.md** (34KB — significantly over budget)
- Fix `model: sonnet` to `model: claude-sonnet-4-6`
- `tools` already correct: `["Read", "Grep", "Glob"]` — standardize to unquoted YAML list
- Condense description from multi-paragraph essay to 3 sentences
- Extract style guide content to `~/.claude/agents/modules/technical-writer-style.md`
- Remove "Example Interactions" section
- Target core file: 14KB; style module: 12KB

### Group 5: Full Modularization Required

**security-auditor.md** (41KB — most critical)
- Fix `model: opus` to `model: claude-opus-4-6`
- Add `tools: [Read, Grep, Glob, Bash]`
- Extract FedRAMP/NIST compliance section to `modules/security-auditor-compliance.md`
- Extract penetration testing guidance to `modules/security-auditor-pentest.md`
- Add module loading instructions to core file
- Target core file: 15KB

**mastra-core-developer.md** (35KB — no frontmatter, needs full work)
- Add frontmatter: `name: mastra-core-developer`, `model: claude-opus-4-6`, `tools: [Read, Grep, Glob, Write, Edit, Bash]`
- Extract workflow composition examples to `modules/mastra-core-developer-workflows.md`
- Extract MCP patterns to `modules/mastra-core-developer-mcp.md`
- Add Confidence Protocol section to core
- Target core file: 15KB

**mastra-framework-expert.md** (20KB — no frontmatter, borderline size)
- Add frontmatter: `name: mastra-framework-expert`, `model: claude-opus-4-6`, `tools: [Read, Grep, Glob]`
- Add Confidence Protocol section
- Review content for removal of encyclopedic reference material
- Target: reduce to 14KB without losing routing guidance

---

## Task List

### Phase 1: Infrastructure Setup
1. [ ] Create `~/.claude/agents/modules/` directory for extracted module files
2. [ ] Update `.gitignore` if not already ignoring `agents/modules/` (check if agents are committed)

### Phase 2: Group 1 — Add Frontmatter Only (low risk, no content change)
3. [ ] `express-api-developer.md`: Add frontmatter block + Confidence Protocol section
4. [ ] `strategic-planner.md`: Add frontmatter block + Confidence Protocol + Self-Verification Checklist
5. [ ] `team-lead.md`: Add frontmatter block + Confidence Protocol section

### Phase 3: Group 2 — Fix Name Mismatches
6. [ ] `frontend-developer.md`: Correct `name:` field to `frontend-developer`, update model to full ID, add tools
7. [ ] `nextjs-code-reviewer.md`: Correct `name:` to `nextjs-code-reviewer`, update model, add tools
8. [ ] `nextjs-qa-developer.md`: Correct `name:` to `nextjs-qa-developer`, update model, add tools

### Phase 4: Group 3 — Model/Tool Corrections
9. [ ] `accessibility-specialist.md`: Update model, add tools, add Confidence Protocol
10. [ ] `database-schema-specialist.md`: Update model, add tools, add Confidence Protocol
11. [ ] `devops-infrastructure.md`: Update model, add tools, remove Example Interactions section
12. [ ] `ui-developer.md`: Update model, add tools, add Confidence Protocol + Self-Verification Checklist
13. [ ] `nextjs-backend-developer.md`: Update model, add tools, remove duplicate checklist, trim to 18KB

### Phase 5: Group 4 — Content Restructuring
14. [ ] `api-designer.md`: Condense description, remove duplicate self-check, remove Example Interactions, target 18KB
15. [ ] `refactoring-specialist.md`: Condense description, add full model ID, add tools, remove Example Interactions
16. [ ] `spec-writer.md`: Condense description, add full model ID, add tools, add Confidence Protocol + Self-Verification Checklist
17. [ ] `technical-writer.md`: Condense description, standardize tools field, extract style guide to module, target 14KB core

### Phase 6: Group 5 — Full Modularization
18. [ ] Create `modules/technical-writer-style.md` from extracted technical-writer style guide content
19. [ ] Create `modules/security-auditor-compliance.md` from FedRAMP/NIST section of security-auditor
20. [ ] Create `modules/security-auditor-pentest.md` from penetration testing guidance section
21. [ ] `security-auditor.md`: Add full model ID, add tools, add module loading instructions, target 15KB core
22. [ ] Create `modules/mastra-core-developer-workflows.md` from workflow composition examples
23. [ ] Create `modules/mastra-core-developer-mcp.md` from MCP patterns section
24. [ ] `mastra-core-developer.md`: Add frontmatter, add Confidence Protocol, add module loading instructions, target 15KB core
25. [ ] `mastra-framework-expert.md`: Add frontmatter, add Confidence Protocol, trim to 14KB

### Phase 7: Validation
26. [ ] Verify all 19 agents have correct YAML frontmatter parseable by Claude Code
27. [ ] Verify all `name:` fields match their filenames exactly
28. [ ] Verify no agent exceeds 20KB (excluding modules)
29. [ ] Verify all agents have Confidence Protocol section
30. [ ] Verify all agents have Self-Verification Checklist section
31. [ ] Run a test invocation of each Group 5 agent to confirm module loading instructions are clear
