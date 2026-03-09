# Key Modules & Responsibilities

**Last Updated: 2026-03-09**

## Project Overview

**Claude Code Development Environment** is a modular system for enhancing Claude Code with specialized workflows, automated quality enforcement, and structured development practices.

**Core Value Proposition:**
- Enable structured, multi-task development phases with automated quality gates
- Provide reusable skills for common workflows (documentation, knowledge management, specifications)
- Enforce quality through automated hooks (lint, build, test checks between tasks)
- Support specialized development through agent personas

## Module Breakdown

### 1. Skills System
**Location:** `/home/artsmc/.claude/skills/`
**Responsibility:** Provide reusable, composable workflows invoked via slash commands

#### start-phase (Flagship System)
**Location:** `skills/start-phase-plan/` and `skills/start-phase-execute/`
**Purpose:** Comprehensive phase management with quality enforcement

**Key Files:**
- `plan.md` - Strategic planning with human approval (Mode 1)
- `execute.md` - Five-part structured execution (Mode 2)
- `scripts/quality_gate.py` - Lint/build/test enforcement
- `scripts/task_validator.py` - Task completion validation
- `scripts/validate_phase.py` - Phase structure validation
- `scripts/sloc_tracker.py` - Source lines of code tracking

**Responsibilities:**
- Analyze task complexity and parallelism opportunities
- Force incremental builds and testing
- Run quality gates (lint + build + test) between every task
- Generate per-task code reviews
- Manage git workflow (commits only after quality passes)
- Track SLOC changes throughout phase

**Token Budget:** ~160k for 7-task phase (79.8% of 200k)

#### document-hub
**Location:** `skills/document-hub-{initialize,read,analyze,update}/`
**Purpose:** Documentation management and synchronization

**Key Files:**
- `initialize.md` - Bootstrap documentation structure
- `read.md` - Read and summarize documentation
- `analyze.md` - Detect documentation drift
- `update.md` - Sync documentation with codebase
- `scripts/validate_hub.py` - Structure validation
- `scripts/detect_drift.py` - Drift detection
- `scripts/extract_glossary.py` - Term extraction

**Responsibilities:**
- Create and maintain documentation hub structure
- Extract domain terminology from code
- Detect undocumented modules and technologies
- Validate documentation integrity
- Provide codebase-to-docs synchronization

#### memory-bank
**Location:** `skills/memory-bank-{initialize,read,sync,update}/`
**Purpose:** Knowledge storage and retrieval

**Key Files:**
- `initialize.md` - Bootstrap knowledge base
- `read.md` - Read and retrieve knowledge
- `sync.md` - Fast sync of active context and progress
- `update.md` - Comprehensive knowledge update
- `scripts/validate_memorybank.py` - Structure validation
- `scripts/detect_stale.py` - Stale knowledge detection
- `scripts/extract_todos.py` - TODO extraction
- `scripts/sync_active.py` - Active context sync

**Responsibilities:**
- Maintain six-file knowledge structure
- Track active context and progress
- Store architectural decisions and learnings
- Detect stale knowledge entries
- Extract and track TODOs

#### spec
**Location:** `skills/spec-{plan,review}/`
**Purpose:** Feature specification and documentation

**Key Files:**
- `plan.md` - Pre-planning and research
- `review.md` - Specification validation and critique
- `scripts/validate_spec.py` - Specification validation
- `scripts/critique_plan.py` - Plan critique

**Responsibilities:**
- Generate functional requirements documents (FRD)
- Create functional requirements specifications (FRS)
- Document technical requirements
- Validate specification completeness

#### pm-db
**Location:** `skills/pm-db/`
**Purpose:** Project management database for tracking projects, phases, and execution

**Key Files:**
- `SKILL.md` - PM-DB interaction guide
- `scripts/init_db.py` - Database initialization
- `scripts/import_phases.py` - Import phase definitions

**Responsibilities:**
- Track projects and their phases
- Store phase plans (approved execution blueprints)
- Record phase runs and task runs
- Store quality gate results
- Calculate phase metrics (SLOC changes, duration, etc.)
- Provide execution history and audit trail

**Database Schema (v2):**
- `projects` - Top-level project records
- `phases` - Phase definitions within projects
- `phase_plans` - Approved plans for phases
- `phase_runs` - Actual execution instances
- `tasks` - Task definitions within plans
- `task_runs` - Individual task execution records
- `quality_gates` - Lint/build/test results
- `phase_metrics` - Performance and code metrics
- `code_reviews` - Generated code review records

#### security-quality-assess
**Location:** `skills/security-quality-assess/`
**Purpose:** Automated security vulnerability scanning for Python and JavaScript/TypeScript

**Key Files:**
- `SKILL.md` - Security assessment invocation guide (228 lines)
- `README.md` - Comprehensive documentation (903 lines)
- `scripts/assess.py` - Main CLI orchestrator (~1,200 lines)
- `lib/analyzers/` - 6 security analyzers (~7,000 lines)
  - `secrets_analyzer.py` - Hardcoded secrets, weak crypto
  - `injection_analyzer.py` - SQL/command/code injection, XSS
  - `auth_analyzer.py` - Authentication and session vulnerabilities
  - `config_analyzer.py` - Security misconfigurations
  - `sensitive_data_analyzer.py` - PII exposure, data leakage
  - `dependency_analyzer.py` - Known CVEs via OSV API
- `lib/parsers/` - Language and dependency parsers (~700 lines)
- `lib/reporters/` - Markdown report generator (~700 lines)
- `lib/utils/` - OSV client, suppression loader, entropy calculations (~1,200 lines)
- `tests/fixtures/` - Test fixtures with 40 expected findings
- `examples/` - Example configuration and usage

**Responsibilities:**
- OWASP Top 10 detection (A01-A07, 85% coverage)
- Multi-language support: Python (.py), JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- False positive management via `.security-suppress.json`
- CVE database integration with 24h caching (OSV API)
- File discovery with `.gitignore` respect and test file exclusion
- Markdown report generation with executive summary and remediation guidance
- Performance: 11,300 LOC/sec (34x faster than target)
- Zero external dependencies (Python stdlib only)

**Token Budget:** ~5k for 12K LOC scan

**Status:** Production-ready v1.0.0 (2026-02-08)

#### start-phase-execute-team
**Location:** `skills/start-phase-execute-team/`
**Purpose:** Parallel task execution with multi-agent coordination

**Key Files:**
- `SKILL.md` - Team execution workflow guide
- Integration with PM-DB for shared task list

**Responsibilities:**
- Spawn team of specialized agents via TeamCreate
- Distribute tasks across team members with TaskList
- Coordinate parallel execution with message passing
- Handle idle state management (normal between turns)
- Aggregate results from team members
- Handle blockers and dependencies
- Graceful shutdown with approval workflow
- Complete audit trail via PM-DB and SendMessage logs

**Token Budget:** Variable based on team size and task complexity

**Status:** Production-ready (2026-02-10)

#### remote-control-builder
**Location:** `skills/remote-control-builder/`
**Purpose:** Build remote control systems using multi-agent workflows

**Key Files:**
- `SKILL.md` - Remote control builder workflow

**Responsibilities:**
- Multi-agent team orchestration for complex systems
- Coordinated development across multiple components
- Specialized agent assignment for different subsystems
- Integration with team coordination tools

**Status:** Production-ready (2026-02-10)

---

### 2. Hooks System
**Location:** `/home/artsmc/.claude/hooks/`
**Responsibility:** Automated workflow enforcement triggered by specific events

#### start-phase Hooks
**Location:** `hooks/start-phase/`
**Purpose:** Enforce quality gates and automate phase lifecycle

**Key Files:**
- `phase-start.md` - Pre-flight validation before phase begins
- `task-complete.md` - Bridge between task execution and quality gate
- `quality-gate.md` - Quality enforcement between every task (Part 3.5)
- `phase-complete.md` - Phase closeout and summary generation (Part 5)

**Responsibilities:**
- Validate phase structure before execution
- Trigger quality gates after each task completion
- Block progression if lint/build/test fails
- Generate comprehensive phase summaries
- Update documentation and knowledge base
- Create git commits only after validation passes

#### Shadow Git Snapshots
**Location:** `hooks/shadow-snapshot.sh`, `hooks/shadow-cleanup.sh`
**Purpose:** Automatic git checkpoints before file mutations

- PreToolUse hook registered in settings.json
- Creates shadow/{timestamp} branch before Write/Edit
- 24h auto-cleanup of old branches

---

### 3. Agents System
**Location:** `/home/artsmc/.claude/agents/`
**Responsibility:** Specialized development personas for specific technologies and roles

**Total Agents:** 19 (all with standardized YAML frontmatter, model routing, and tool restrictions)

#### Code Review Agents
**Files:**
- `nextjs-code-reviewer.md` — Code review (model: sonnet, tools: read-only)

**Responsibilities:**
- Comprehensive code review with framework-specific context
- Security vulnerability detection
- Best practice enforcement
- Style and convention validation
- Confidence level assessment

#### Development Agents
**Files:**
- `frontend-developer.md` — React state management (model: sonnet)
- `ui-developer.md` — Visual implementation (model: sonnet)
- `express-api-developer.md` — Express 5.x REST APIs (model: sonnet) [NEW]
- `nextjs-backend-developer.md` — Next.js API routes (model: sonnet)
- `database-schema-specialist.md` — Database design (model: sonnet)
- `refactoring-specialist.md` — Code modernization (model: sonnet)
- `debugger-specialist.md` — Root cause analysis (model: opus)
- `security-auditor.md` — Security scanning (model: opus, modularized: core + 2 modules)
- `devops-infrastructure.md` — CI/CD and deployment (model: sonnet)
- `accessibility-specialist.md` — WCAG compliance (model: sonnet)
- `mastra-core-developer.md` — Mastra framework (model: opus, modularized: core + 2 modules)
- `mastra-framework-expert.md` — Mastra architecture (model: opus)

**Responsibilities:**
- Technology-specific implementation
- Framework best practices
- API design and development
- State management patterns
- Security scanning with modular compliance and pentest modules
- Mastra workflow composition and MCP integration

#### QA Agents
**Files:**
- `nextjs-qa-developer.md` — Testing strategies (model: sonnet)

**Responsibilities:**
- Test suite generation and coverage analysis
- Integration testing strategies
- Confidence level assessment

#### Specification Agents
**Files:**
- `spec-writer.md` — Feature specs (model: sonnet)
- `api-designer.md` — API contract design (model: sonnet, tools: read-only)
- `technical-writer.md` — Documentation (model: sonnet, modularized: core + 1 module)

**Responsibilities:**
- FRD/FRS/TR document generation
- Requirements analysis and specification writing
- API contract design and OpenAPI specification
- User-facing documentation with style guide module

#### Orchestration Agents
**Files:**
- `strategic-planner.md` — Strategic planning and wave analysis (model: opus, tools: read-only) [NEW]
- `team-lead.md` — Multi-agent team coordination (model: opus, tools: read-only) [NEW]

**Responsibilities:**
- Strategic planning with task decomposition and wave analysis
- Multi-agent team creation, coordination, and lifecycle management
- Read-only tools to prevent accidental mutations during planning

---

### Agent Modules
**Location:** `/home/artsmc/.claude/agents/modules/`
**Purpose:** Extracted deep-reference content loaded on-demand

**Files:**
- `security-auditor-compliance.md` — FedRAMP/NIST 800-53 compliance guidance
- `security-auditor-pentest.md` — Penetration testing patterns
- `mastra-core-developer-workflows.md` — Workflow composition examples
- `mastra-core-developer-mcp.md` — MCP integration patterns
- `technical-writer-style.md` — Style guide and documentation conventions

**Responsibilities:**
- Provide deep-reference material without bloating core agent files
- Loaded on-demand when specific domain expertise is needed
- Keep core agent files under 20KB size limit

---

### 4. Python Tools
**Location:** `skills/*/scripts/`
**Responsibility:** Zero-dependency validation and quality enforcement utilities

#### Quality Gate Tools (start-phase)
**Files:**
- `quality_gate.py` - Run lint/build/test checks with JSON output
- `task_validator.py` - Validate task completion (files, commits, checklists)
- `validate_phase.py` - Validate phase structure and planning docs
- `sloc_tracker.py` - Track source lines of code changes

**Responsibilities:**
- Execute lint, build, and test checks
- Validate file existence and content
- Check git commit presence
- Measure code growth/reduction
- Return structured JSON for automation

#### Documentation Tools (document-hub)
**Files:**
- `validate_hub.py` - Validate documentation structure
- `detect_drift.py` - Find undocumented modules and technologies
- `extract_glossary.py` - Extract domain-specific terms from code

**Responsibilities:**
- Validate documentation file structure
- Check Mermaid diagram syntax
- Detect missing documentation
- Extract terminology with context
- Rank terms by relevance

#### Knowledge Tools (memory-bank)
**Files:**
- `validate_memorybank.py` - Validate knowledge base structure
- `detect_stale.py` - Detect outdated knowledge entries
- `extract_todos.py` - Extract TODO items from code
- `sync_active.py` - Sync active context with codebase

**Responsibilities:**
- Validate six-file structure
- Check for stale knowledge (>30 days)
- Extract inline TODOs
- Update active context
- Maintain progress tracking

#### Specification Tools (spec)
**Files:**
- `validate_spec.py` - Validate specification structure
- `critique_plan.py` - Critique feature plans

**Responsibilities:**
- Validate FRD/FRS completeness
- Check specification consistency
- Provide planning feedback

#### Security Tools (security-quality-assess)
**Files:**
- `assess.py` - Main CLI and orchestration (~1,200 lines)
- `lib/analyzers/*.py` - 6 security analyzers (~7,000 lines total)
  - `secrets_analyzer.py` (~1,100 lines)
  - `injection_analyzer.py` (~1,200 lines)
  - `auth_analyzer.py` (~1,750 lines)
  - `config_analyzer.py` (~1,200 lines)
  - `sensitive_data_analyzer.py` (~1,200 lines)
  - `dependency_analyzer.py` (~600 lines)
- `lib/parsers/*.py` - Language and dependency parsers (~700 lines)
  - `python_parser.py` - Python AST parsing
  - `javascript_parser.py` - JavaScript/TypeScript parsing
  - `dependency_parser.py` - Lockfile parsing (pip, poetry, npm, yarn)
- `lib/reporters/*.py` - Report generators (~700 lines)
  - `markdown_reporter.py` - Markdown report with executive summary
- `lib/utils/*.py` - Utility libraries (~1,200 lines)
  - `osv_client.py` - OSV API integration with 24h caching
  - `suppression_loader.py` - Load and validate `.security-suppress.json`
  - `entropy.py` - Calculate Shannon entropy for secret detection
  - `patterns.py` - Vulnerability signature patterns (1,060 lines)

**Responsibilities:**
- Execute 6 security analyzers across codebase
- Parse Python, JavaScript, TypeScript source files
- Query OSV API for known CVEs in dependencies
- Generate comprehensive markdown reports with findings
- Manage suppression system with audit trail
- Calculate entropy for high-risk string detection
- Match vulnerability patterns (SQL injection, XSS, etc.)
- Return structured JSON for automation
- Respect `.gitignore` and exclude test files
- Handle encoding errors gracefully

**Total Size:** ~10,500 SLOC
**Performance:** 11,300 LOC/sec
**False Positive Rate:** 16.7%

#### Agent Caching Tools (start-phase integration)
**Files:**
- `cache_wrapper.py` - Agent context caching wrapper (~230 lines)

**Responsibilities:**
- Initialize agent invocations in PM-DB with purpose and phase linkage
- Track file reads with cache hit/miss status
- Calculate token savings from cache hits
- Log file reads to agent_file_reads table
- Display cache statistics (hit rate, tokens saved)
- Complete invocations with final metrics
- Support sub-agent invocations (nested agents)
- Commands: init, read, stats, complete

**Integration:**
- start-phase-plan: Track documentation and Memory Bank reads
- start-phase-execute: Track per-task file reads with task_run_id linkage

**Performance:** <5ms cache lookups, 40-66% token savings measured

---

## Cross-Module Dependencies

### Skills → Tools
Skills invoke Python tools for validation and quality checks. Tools return structured JSON for automation.

### Hooks → Tools
Hooks use tools to enforce quality gates and validate completion. Tools provide pass/fail decisions.

### Hooks → Skills
Phase hooks may update documentation (document-hub) or knowledge (memory-bank) after phase completion.

### Skills → Agents
start-phase execute invokes specialized agents for task execution based on technology stack.

---

## Development Workflow Integration

```
User invokes skill → Skill loads instructions → Agent executes
                                                      ↓
                                              Uses tools (Read, Write, Bash)
                                                      ↓
                                              Invokes helper scripts
                                                      ↓
                                              Returns structured results
                                                      ↓
                                              Hook triggers (if applicable)
                                                      ↓
                                              Quality gate enforces standards
                                                      ↓
                                              Pass → Continue | Fail → Block
```

---

## Maintenance Guidelines

### Adding New Skills
1. Create skill directory: `skills/{system-name}-{action}/`
2. Add skill file: `{action}.md`
3. Add helper scripts: `scripts/*.py`
4. Update main README.md
5. Test skill invocation

### Adding New Agents
1. Create agent file: `agents/{role}-{technology}.md`
2. All agents must have YAML frontmatter (name, model, tools)
3. Max 20KB per agent file; extract modules to `agents/modules/` for larger content
4. Must include Confidence Protocol section
5. Test with start-phase execute

### Adding New Hooks
1. Create hook file: `hooks/{system}/event-name.md`
2. Define trigger conditions
3. Implement validation logic
4. Test with actual workflow

### Adding New Tools
1. Create Python script: `skills/{system}/scripts/tool_name.py`
2. Use only Python stdlib (zero dependencies)
3. Return structured JSON
4. Add `--help` flag
5. Document in `scripts/README.md`

---

## Quality Standards

- **Zero dependencies:** All tools use Python stdlib only
- **Structured output:** Tools return JSON for automation
- **Comprehensive validation:** Every system has validation scripts
- **Documentation first:** Every module has README.md
- **Token efficiency:** Skills designed for <200k token budget
- **Modular design:** Low coupling, high cohesion
- **Test coverage:** Critical paths validated
