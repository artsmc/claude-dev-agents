# Technology Stack
Last Updated: 2026-03-09

## Core Technologies

### Python 3
**Purpose:** Primary language for all validation, quality enforcement, security analysis, and automation tools
**Version:** 3.6+ (uses only standard library features)
**Usage:**
- Security analysis (assess.py with 6 analyzers, ~10,500 SLOC)
- Quality gate enforcement (quality_gate.py)
- Task validation (task_validator.py)
- Agent context caching (cache_wrapper.py)
- Documentation analysis (validate_hub.py, detect_drift.py, extract_glossary.py)
- Knowledge management (validate_memorybank.py, detect_stale.py, extract_todos.py)
- SLOC tracking (sloc_tracker.py)

**Key Libraries (stdlib only):**
- `json` - Structured data output
- `pathlib` - File path manipulation
- `subprocess` - Execute shell commands
- `argparse` - CLI argument parsing
- `re` - Regular expressions for parsing
- `datetime` - Timestamp handling
- `hashlib` - SHA-256 hashing for cache invalidation
- `urllib` - OSV API integration for CVE database queries

---

### Markdown
**Purpose:** Primary format for skills, hooks, agents, and documentation
**Usage:**
- Skill definitions (all `/skills/*/` files)
- Hook definitions (all `/hooks/*/` files)
- Agent personas (all `/agents/` files)
- Documentation hub (cline-docs/)
- Planning documents (planning/)

**Features Used:**
- Frontmatter (YAML metadata)
- Code blocks with syntax highlighting
- Mermaid diagrams (architecture and sequence diagrams)
- Task lists and checklists
- Nested lists and tables

---

### Mermaid
**Purpose:** Visual diagrams for architecture and workflows
**Version:** Compatible with CommonMark renderers
**Usage:**
- System architecture diagrams (flowchart TD)
- Sequence diagrams (sequenceDiagram)
- Phase workflow visualization
- Module dependency graphs

**Diagram Types Used:**
- `flowchart TD` - Top-down architecture diagrams
- `sequenceDiagram` - Process flow diagrams

---

### Git
**Purpose:** Version control and commit workflow automation
**Usage:**
- Phase management commits (automated by hooks)
- Quality gate enforcement (block commits until checks pass)
- Checkpoint commits for long tasks (>30 min)
- Diff generation for change tracking

**Commands Used:**
- `git status` - Check working directory state
- `git add` - Stage files for commit
- `git commit` - Create commits with co-author attribution
- `git diff` - Analyze changes
- `git log` - Review commit history

---

### Bash/Shell
**Purpose:** Command execution and system integration
**Usage:**
- Run npm/yarn commands (lint, build, test)
- File system operations
- Process management
- Directory navigation

---

## Development Tools

### ESLint
**Purpose:** JavaScript/TypeScript linting (when applicable)
**Usage:** Invoked by quality_gate.py for lint checks
**Integration:** Detected in package.json, executed via npm/yarn/npx

### TypeScript Compiler (tsc)
**Purpose:** TypeScript build validation (when applicable)
**Usage:** Invoked by quality_gate.py for build checks
**Integration:** Detected in package.json, executed via npm/yarn

### npm/yarn/pnpm
**Purpose:** Package management and script execution (when applicable)
**Usage:** Execute lint, build, and test commands
**Detection:** quality_gate.py auto-detects which package manager is present

### pytest
**Purpose:** Python testing framework (when applicable)
**Usage:** Invoked by quality_gate.py for test checks in Python projects
**Integration:** Detected in project structure, executed via pytest command

---

## Security & Quality Tools

### Security Quality Assessment
**Purpose:** Zero-dependency OWASP Top 10 vulnerability scanning
**Version:** 1.0.0 (Production-ready 2026-02-08)
**Usage:** Automated security analysis for Python and JavaScript/TypeScript
**Integration:** Via `/security-assess` skill

**Components:**
- **assess.py** - Main CLI orchestrator (~1,200 lines)
- **6 Security Analyzers** (~7,000 lines):
  - **SecretsAnalyzer** - Hardcoded secrets, API keys, weak crypto (MD5/SHA1/DES), high-entropy strings
  - **InjectionAnalyzer** - SQL injection, command injection, code injection (eval/exec), XSS vulnerabilities
  - **AuthAnalyzer** - Weak JWT algorithms, insecure sessions, hardcoded passwords, missing authentication
  - **ConfigAnalyzer** - Debug mode enabled, insecure CORS, missing security headers, unsafe configurations
  - **SensitiveDataAnalyzer** - PII exposure, unencrypted sensitive data storage, data leakage
  - **DependencyAnalyzer** - Known CVEs in dependencies via OSV API integration
- **3 Language Parsers** (~700 lines):
  - Python parser (.py files)
  - JavaScript/TypeScript parser (.js, .ts, .jsx, .tsx)
  - Dependency parser (requirements.txt, poetry.lock, package-lock.json, yarn.lock)
- **Markdown Reporter** (~700 lines) - Executive summary, detailed findings, remediation guidance
- **Utility Libraries** (~1,200 lines):
  - OSV client with 24h caching
  - Suppression loader with audit trail
  - Entropy calculator for secret detection
  - Pattern matching for vulnerability signatures

**OWASP Top 10 (2021) Coverage:**
- A01:2021 - Broken Access Control ✅
- A02:2021 - Cryptographic Failures ✅
- A03:2021 - Injection ✅
- A04:2021 - Insecure Design ✅
- A05:2021 - Security Misconfiguration ✅
- A06:2021 - Vulnerable Components ✅
- A07:2021 - Identification/Auth Failures ✅
- A08-A10 - Planned for Phase 2 🔜

**OSV API Integration:**
- **Purpose:** Query CVE database for known dependency vulnerabilities
- **Endpoint:** https://api.osv.dev/v1/query
- **Caching:** 24h local cache for performance and offline support
- **Languages:** Python (requirements.txt, poetry.lock), JavaScript (package-lock.json, yarn.lock)
- **Rate Limiting:** Automatic retry with exponential backoff

**Suppression System:**
- **File:** `.security-suppress.json` in project root
- **Purpose:** Manage false positives with justification and audit trail
- **Features:**
  - Per-finding suppression with unique IDs
  - Justification required for each suppression
  - Expiration dates for periodic re-evaluation
  - Audit trail of who suppressed and when
  - Re-evaluation triggers on code changes

**Performance:** 11,300 LOC/sec (34x faster than 334 LOC/sec target)
**False Positive Rate:** 16.7% (beat 20% target)
**Total Size:** ~10,500 SLOC

---

## Team Coordination Tools

### Multi-Agent Orchestration
**Purpose:** Enable parallel task execution through team-based workflows
**Version:** Production-ready (2026-02-10)
**Usage:** Via `/start-phase-execute-team` and `/remote-control-builder` skills

**Tools:**
- **TeamCreate** - Spawn team with shared task list
  - Creates team configuration file
  - Initializes shared task list in PM-DB
  - Registers team members with names and roles
- **SendMessage** - Explicit agent-to-agent communication
  - Types: message (DM), broadcast (all), shutdown_request, plan_approval_response
  - Message delivery with summaries for UI
  - Automatic notification when messages arrive
- **TaskList** - Shared task queue coordination
  - View all pending/in-progress/completed tasks
  - Claim tasks by setting owner
  - Block on task dependencies (blockedBy)
  - Prefer tasks in ID order for context continuity
- **TaskUpdate** - Update task status and ownership
  - Mark tasks as in_progress when starting
  - Mark tasks as completed when done
  - Assign tasks to specific team members

**Workflow Pattern:**
1. Team lead creates team (TeamCreate)
2. Team lead creates tasks (TaskCreate)
3. Team lead spawns agents (Task tool with team_name)
4. Agents claim tasks (TaskUpdate with owner)
5. Agents execute and report (SendMessage)
6. Team lead aggregates and closes (SendMessage shutdown_request)

**Documentation:** 42KB across 3 files (TEAM-SKILLS-README.md, implementation guide, examples)

---

## Claude Code Integration

### Model Context Protocol (MCP)
**Purpose:** Next.js 16+ runtime diagnostics and tool invocation
**Usage:**
- Next.js dev server integration
- Runtime error detection
- Route inspection
- Cache management

### Claude Code CLI
**Purpose:** Primary interface for skill and agent invocation
**Version:** Compatible with claude.ai/code
**Features Used:**
- Slash command skills
- Hook system
- Agent personas
- Tool integration (Read, Write, Bash, etc.)

---

## Project Structure Technologies

### JSON
**Purpose:** Structured data interchange format
**Usage:**
- Tool output format (all .py scripts return JSON)
- Configuration files
- Validation results
- Metrics and reports

### YAML
**Purpose:** Frontmatter metadata in markdown files
**Usage:**
- Skill metadata (name, description, version)
- Hook trigger conditions
- Agent configuration

---

## Infrastructure

### File System
**Purpose:** Primary storage for skills, hooks, agents, and documentation
**Structure:**
```
/home/artsmc/.claude/
├── agents/           # Agent persona files
├── skills/           # Skill-based workflows
├── hooks/            # Automated workflow enforcement
├── cline-docs/       # Documentation hub
├── cache/            # Temporary cache storage
├── planning/         # Phase planning documents
├── plans/            # Generated plans
└── plugins/          # Extensible functionality
```

---

## Quality Enforcement Stack

### Lint → Build → Test Pipeline
**Purpose:** Three-stage quality gate enforcement
**Implementation:**
1. **Lint:** ESLint, Ruff (Python), or language-specific linters
2. **Build:** TypeScript compilation, Python syntax checks
3. **Test:** Jest, pytest, or framework-specific test runners

**Orchestration:** quality_gate.py coordinates all checks and returns pass/fail JSON

---

## Supported Project Types

### Next.js Projects
- MCP integration for runtime diagnostics
- Browser automation for page verification
- Upgrade tooling for Next.js 16+
- Cache Components migration support

### Python Projects
- FastAPI backend development
- pytest-based testing
- Python code review with Bandit/MyPy/Ruff
- Zero-dependency tooling

### TypeScript Projects
- ESLint integration
- TypeScript compiler checks
- Frontend and backend development
- React/Next.js support

---

## Plugin System

### Hookify
**Purpose:** Rule-based hook configuration and enforcement
**Location:** `plugins/marketplaces/claude-plugins-official/plugins/hookify/`
**Components:**
- `config_loader.py` - Load hookify.*.local.md files
- `rule_engine.py` - Evaluate blocking rules

### Security Guidance
**Purpose:** Security reminder hook for file operations
**Location:** `plugins/marketplaces/claude-plugins-official/plugins/security-guidance/`
**Features:**
- Architecture change detection
- Security-sensitive file warnings

---

## Documentation Standards

### CommonMark
**Purpose:** Markdown rendering specification
**Usage:** All markdown files follow CommonMark syntax
**Features:**
- GitHub-flavored extensions
- Mermaid diagram support
- Task list extensions

---

## Agent Infrastructure

### Model Routing
**Purpose:** Cost-optimized model selection per agent role
**Implementation:** YAML frontmatter `model:` field in every agent .md file
**Models Used:**
- `claude-opus-4-6` (6 agents) — Deep reasoning, architecture, security analysis
- `claude-sonnet-4-6` (13 agents) — Implementation, review, documentation
**Benefit:** 40-60% cost reduction by routing routine tasks to Sonnet

### Shadow Git Snapshots
**Purpose:** Automatic per-operation rollback via git branch checkpoints
**Implementation:** PreToolUse hook in settings.json
**Files:**
- `hooks/shadow-snapshot.sh` — Creates `shadow/{timestamp}` branch before Write/Edit
- `hooks/shadow-cleanup.sh` — Prunes branches older than 24h
**Usage:** `git checkout shadow/{timestamp} -- path/to/file` for instant rollback

### Working Memory
**Purpose:** Cross-agent context sharing within team sessions
**Implementation:** Shared markdown file at `working-memory/{team-name}.md`
**Lifecycle:** Created on TeamCreate, populated by agents, deleted on TeamDelete
**Sections:** Decisions, Discoveries, Blockers, Handoff Notes

### Agent Modules
**Purpose:** On-demand loading of deep-reference content for large agents
**Location:** `agents/modules/`
**Files:** 5 modules extracted from security-auditor, mastra-core-developer, technical-writer
**Benefit:** Core agents stay under 20KB; modules loaded only when task requires them

---

## Token Budget Management

### Context Window
**Size:** 1,000,000 tokens (Claude Opus 4.6 with 1M context)
**Usage Optimization:**
- start-phase: ~160k for 7-task phase
- document-hub: ~15k tokens
- memory-bank: ~12k tokens
- Agent definitions: 6-20KB each (max 20KB enforced)

**Strategy:**
- Model routing (Sonnet for routine tasks, Opus for deep reasoning)
- Modular agent definitions (core + on-demand modules)
- Structured JSON output from tools
- Incremental validation to avoid redundant reads

---

## Dependencies Philosophy

### Zero External Dependencies
**Rationale:** Eliminate installation friction and ensure portability
**Implementation:** All Python tools use only standard library
**Benefit:** Works anywhere Python 3.6+ is installed

**Allowed:**
- Python stdlib (json, pathlib, subprocess, argparse, re, datetime, etc.)

**Forbidden:**
- PyPI packages (no requirements.txt for tools)
- npm packages for core tools
- External binaries beyond git/npm/yarn

**Exception:** Project-specific dependencies (ESLint, TypeScript, pytest) are detected and used if available, but tools function without them.

---

## Version Control

### Repository Structure
- **Type:** Git repository
- **Location:** `/home/artsmc/.claude/`
- **Branch Strategy:** main branch for stable features
- **Commit Style:** Descriptive messages with co-author attribution

---

## Future Technology Considerations

### Potential Additions
- **Docker:** Containerization for consistent environments
- **GitHub Actions:** CI/CD integration for automated quality checks
- **SQL/NoSQL:** Database support for larger knowledge bases
- **GraphQL:** API layer for knowledge graph queries

### Technology Selection Criteria
1. **Zero dependencies first** - Prefer stdlib solutions
2. **Portability** - Must work across platforms (Linux, macOS, Windows)
3. **Simplicity** - Avoid over-engineering
4. **Integration** - Must integrate cleanly with existing tools
5. **Performance** - Must scale to large codebases

---

## Notes

- All Python tools are designed to work with zero external dependencies
- JavaScript/TypeScript tooling is detected and used when available
- The system adapts to project-specific technologies (npm vs yarn, ESLint vs Ruff)
- Mermaid diagrams are validated automatically by validate_hub.py
- Token budget is carefully managed to stay within Claude's 200k limit
