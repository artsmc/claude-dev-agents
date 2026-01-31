# Claude Code Development Environment

**Version:** 2.0
**Last Updated:** 2026-01-17
**Architecture:** Modular Skills, Hooks & Tools

Custom agents, skills, hooks, and tools for Claude Code (claude.ai/code).

---

## 🏗️ Architecture Overview

This repository implements a **modular, skill-based architecture** with:
- ✅ **Agents** - Specialized development personas
- ✅ **Skills** - Reusable, composable workflows
- ✅ **Hooks** - Automated workflow enforcement
- ✅ **Tools** - Zero-dependency Python utilities

---

## 📁 Directory Structure

```
.claude/
├── agents/                    # Specialized development agents
│   ├── code-reviewer.md
│   ├── frontend-developer.md
│   ├── nextjs-backend-developer.md
│   ├── nextjs-qa-engineer.md
│   ├── python-fastapi-expert.md
│   ├── python-reviewer.md
│   ├── python-tester.md
│   └── ui-developer.md
│
├── skills/                    # Modular skill-based workflows
│   ├── hub/                   # Document Hub system
│   │   ├── document-hub-analyze.md
│   │   ├── document-hub-initialize.md
│   │   ├── document-hub-read.md
│   │   ├── document-hub-update.md
│   │   ├── scripts/          # Hub validation tools
│   │   └── README.md
│   │
│   ├── memory-bank/           # Knowledge storage system
│   │   ├── initialize.md
│   │   ├── read.md
│   │   ├── sync.md
│   │   ├── update.md
│   │   ├── scripts/          # Memory bank tools
│   │   └── README.md
│   │
│   ├── spec/                  # Specification system
│   │   ├── plan.md
│   │   ├── review.md
│   │   ├── scripts/          # Spec validation tools
│   │   └── README.md
│   │
│   └── start-phase/           # Phase management system ⭐
│       ├── plan.md           # Mode 1: Strategic planning
│       ├── execute.md        # Mode 2: Structured execution
│       ├── README.md         # Complete system guide (68KB)
│       └── scripts/          # Quality enforcement tools
│           ├── quality_gate.py
│           ├── task_validator.py
│           ├── validate_phase.py
│           ├── sloc_tracker.py
│           ├── requirements.txt
│           └── README.md
│
└── hooks/                     # Automated workflow enforcement
    └── start-phase/           # Phase workflow automation ⭐
        ├── phase-start.md    # Pre-flight validation
        ├── task-complete.md  # Task completion bridge
        ├── quality-gate.md   # Quality enforcement (Part 3.5)
        ├── phase-complete.md # Phase closeout (Part 5)
        └── README.md
```

---

## 🎯 Agents

Specialized development personas for different aspects of development.

### Code Review & Quality
- **code-reviewer.md** - Comprehensive code review with security analysis
- **python-reviewer.md** - Python-specific code review (PEP 8, MyPy, Bandit, Ruff)

### Development
- **frontend-developer.md** - Frontend application logic and state management
- **ui-developer.md** - Visual implementation and styling
- **nextjs-backend-developer.md** - Next.js backend API development
- **python-fastapi-expert.md** - FastAPI backend development

### Testing & QA
- **nextjs-qa-engineer.md** - Quality assurance for Next.js applications
- **python-tester.md** - Pytest-based testing with fixtures

**Location:** `/home/artsmc/.claude/agents/`

---

## 🔧 Skills

Modular, reusable workflows for common development tasks.

### 🎯 Workflow Orchestration (3 skills) ⭐ NEW

End-to-end feature development automation.

```bash
/documentation-start                      # Initialize Memory Bank + Document Hub
/feature-new "feature description"        # Complete workflow: spec → plan → execute
/feature-continue ./path/to/tasks.md      # Resume interrupted work with PM-DB tracking
```

**Features:**
- One-command feature development
- Automatic documentation initialization
- PM-DB tracking integration
- Session resilience (resume after interruptions)
- Two human approval checkpoints
- Complete workflow automation

**Location:** `/home/artsmc/.claude/skills/documentation-start/`, `/home/artsmc/.claude/skills/feature-new/`, `/home/artsmc/.claude/skills/feature-continue/`

---

### 📚 Document Hub (4 skills)

Documentation management system for codebases.

```bash
/document-hub-initialize    # Initialize documentation structure
/document-hub-read          # Read and summarize documentation
/document-hub-analyze       # Analyze documentation coverage
/document-hub-update        # Update documentation
```

**Features:**
- Automated documentation generation
- Codebase synchronization
- Documentation validation
- Template management

**Location:** `/home/artsmc/.claude/skills/hub/`
**Documentation:** `/home/artsmc/.claude/skills/hub/README.md`

---

### 🧠 Memory Bank (4 skills)

Knowledge storage and retrieval system with automatic context management.

```bash
/memory-bank-initialize     # Initialize knowledge base
/memory-bank-read           # Read and retrieve knowledge
/memory-bank-sync           # Sync knowledge with codebase
/memory-bank-update         # Update knowledge entries
```

**Features:**
- Context-aware knowledge storage
- Semantic search capabilities
- Automatic categorization
- Knowledge graph maintenance

**Location:** `/home/artsmc/.claude/skills/memory-bank/`
**Documentation:** `/home/artsmc/.claude/skills/memory-bank/README.md`

---

### 📋 Spec (2 skills)

Feature specification and documentation system.

```bash
/spec-plan                  # Plan feature specifications
/spec-review                # Review specifications
```

**Features:**
- Structured feature planning
- FRD (Functional Requirements Document) generation
- FRS (Functional Requirements Specification)
- Technical requirements documentation

**Location:** `/home/artsmc/.claude/skills/spec/`
**Documentation:** `/home/artsmc/.claude/skills/spec/README.md`

---

### 🚀 Start-Phase (2 skills) ⭐ FLAGSHIP

Comprehensive phase management system with quality gates, hooks, and tools.

```bash
/start-phase plan /path/to/tasks.md              # Mode 1: Strategic planning
/start-phase execute /path/to/tasks.md [extra]   # Mode 2: Structured execution
```

**Features:**
- **Mode 1 (Plan):** Strategic planning with human approval
  - Analyzes task complexity
  - Identifies parallelism opportunities
  - Forces incremental builds
  - Requires human approval before execution

- **Mode 2 (Execute):** Five-part structured execution
  - Part 1: Finalize plan + create directories
  - Part 2: Generate detailed planning docs
  - Part 3: Execute tasks with agent personas
  - Part 3.5: Quality gates (automatic via hooks)
  - Part 4: Task updates + commits (automatic via hooks)
  - Part 5: Phase closeout + summary (automatic via hooks)

**Quality Enforcement:**
- ✅ Lint checks (hard block) between every task
- ✅ Build checks (hard block) between every task
- ✅ Per-task AI code reviews
- ✅ Automated task updates and documentation
- ✅ Git commits only after quality gates pass
- ✅ Checkpoint commits for long tasks (>30 min)

**Python Tools (Zero Dependencies):**
- `quality_gate.py` - Run lint/build/test checks
- `task_validator.py` - Validate task completion
- `validate_phase.py` - Validate phase structure
- `sloc_tracker.py` - Track Source Lines of Code changes

**Comprehensive Hooks:**
- `phase-start.md` - Pre-flight validation
- `task-complete.md` - Bridge to quality gate
- `quality-gate.md` - Quality enforcement (Part 3.5)
- `phase-complete.md` - Phase closeout (Part 5)

**Token Budget:** ~160k tokens for 7-task phase (79.8% of 200k)
**Recommended:** 5-7 tasks per phase
**Maximum:** 10 tasks (with optimizations)

**Location:** `/home/artsmc/.claude/skills/start-phase/`
**Documentation:** `/home/artsmc/.claude/skills/start-phase/README.md` (68KB comprehensive guide)

---

## 🪝 Hooks

Automated workflow enforcement triggered by specific events.

### Start-Phase Hooks ⭐

The start-phase system includes 4 comprehensive hooks for automated quality enforcement:

- **phase-start.md** - Pre-flight validation before phase starts
- **task-complete.md** - Bridge between task execution and quality gate
- **quality-gate.md** - Quality enforcement between every task (Part 3.5)
- **phase-complete.md** - Comprehensive phase closeout (Part 5)

**Location:** `/home/artsmc/.claude/hooks/start-phase/`
**Documentation:** `/home/artsmc/.claude/hooks/start-phase/README.md`

---

## 🛠️ Tools

Zero-dependency Python utilities for quality enforcement.

### Start-Phase Tools

**quality_gate.py** - Quality enforcement
```bash
python quality_gate.py /path/to/project [--test]
```
- Runs lint (npm/yarn/npx eslint)
- Runs build (npm/yarn/tsc)
- Optional test checks
- Returns JSON with pass/fail

**task_validator.py** - Task completion validation
```bash
python task_validator.py /path/to/project task-name
```
- Validates task update file exists
- Validates code review file exists
- Checks checklist completion
- Verifies git commit exists

**validate_phase.py** - Phase structure validation
```bash
python validate_phase.py /path/to/project
```
- Validates directory structure
- Checks planning files exist
- Validates Mermaid graphs
- Samples task updates and reviews

**sloc_tracker.py** - SLOC tracking
```bash
python sloc_tracker.py /path/to/project --baseline file1.ts file2.ts
python sloc_tracker.py /path/to/project --update
python sloc_tracker.py /path/to/project --final
```
- Creates baseline measurements
- Tracks current SLOC
- Generates final report with markdown table

**Dependencies:** Zero (Python stdlib only)
**Location:** `/home/artsmc/.claude/skills/start-phase/scripts/`

---

## 📦 System Overview

### Production-Ready Systems

| System | Status | Skills | Hooks | Tools | Documentation |
|--------|--------|--------|-------|-------|---------------|
| **orchestration** | ✅ v1.0 | 3 | 0 | 0 | Complete |
| **start-phase** | ✅ v2.0 | 2 | 4 | 4 | 68KB comprehensive |
| **hub** (document-hub) | ✅ v1.0 | 4 | 0 | 4 | Complete |
| **memory-bank** | ✅ v1.0 | 4 | 0 | 4 | Complete |
| **spec** | ✅ v1.0 | 2 | 0 | 2 | Complete |
| **pm-db** | ✅ v2.0 | 1 | 6 | 1 | Complete |

### Total Implementation

- **16 skills** across 6 systems
- **10 hooks** for automated workflow (start-phase + pm-db)
- **15 Python tools** (890+ lines of code)
- **8 specialized agents** for development
- **~300 KB** of production code
- **Zero external dependencies** (Python stdlib only)

### Skill Naming Convention

Skills follow the pattern `/{system-name}-{action}`:
- `/documentation-start`, `/feature-new`, `/feature-continue` (orchestration)
- `/document-hub-initialize`, `/document-hub-read`, etc.
- `/memory-bank-initialize`, `/memory-bank-read`, etc.
- `/spec-plan`, `/spec-review`
- `/start-phase plan`, `/start-phase execute` (space-separated for arguments)
- `/pm-db init`, `/pm-db import`, `/pm-db dashboard`, etc.

---

## 🚀 Quick Start

### Beginner (Orchestrated Workflow)

**Complete feature development in one command:**

```bash
# One-time setup
/documentation-start
/pm-db init

# Develop features
/feature-new "add user login"
/feature-new "integrate payments"
/feature-new "build admin panel"

# Resume if interrupted
/feature-continue ./job-queue/feature-name/tasks.md
```

**That's it!** The orchestration skills handle everything automatically.

---

### Advanced (Manual Control)

**Fine-grained control over each step:**

```bash
# 1. Initialize
/document-hub-initialize
/memory-bank-initialize

# 2. Plan feature
/spec-plan "advanced feature"
/spec-review

# 3. Execute
/start-phase plan ./job-queue/feature-name/tasks.md
/pm-db import
/start-phase execute ./job-queue/feature-name/tasks.md

# 4. Update docs
/memory-bank-update
/document-hub-update
```

See "Beginner Quickstart" and "Advanced Workflows" sections below for more patterns.

---

## 🎓 Beginner Quickstart

New to this system? Start here!

### First-Time Setup (5 minutes)

**Step 1: Initialize Documentation**

```bash
/documentation-start
```

This creates:
- Memory Bank (6 files tracking project knowledge)
- Document Hub (4 files documenting codebase)

**Step 2: Initialize PM-DB**

```bash
/pm-db init
```

This creates the project database at `~/.claude/projects.db`.

**Done!** Your project is now ready for feature development.

---

### Develop Your First Feature

**The Easy Way (Recommended):**

```bash
/feature-new "add user login page"
```

This runs the complete workflow automatically:
1. ✅ Checks documentation is initialized
2. ✅ Creates feature specification
3. ⏸️ Waits for your approval
4. ✅ Creates strategic execution plan
5. ⏸️ Waits for your approval
6. ✅ Imports to PM-DB
7. ✅ Executes with quality gates

**Two human approval checkpoints ensure quality before execution.**

---

### Resume Interrupted Work

If your session drops or you need to pause:

```bash
/feature-continue ./job-queue/feature-login/tasks.md
```

This:
- ✅ Detects where you left off
- ✅ Resumes from last incomplete task
- ✅ Maintains PM-DB tracking
- ✅ Preserves git history

---

### View Progress

```bash
/pm-db dashboard
```

Shows:
- All features in progress
- Completed tasks
- Phase metrics
- Success rates

---

### Update Documentation

After completing features:

```bash
/memory-bank-sync        # Quick update (2 files)
/document-hub-update     # Full documentation sync
```

---

### Complete Beginner Workflow

```bash
# One-time setup
/documentation-start
/pm-db init

# For each feature
/feature-new "feature description"

# If interrupted
/feature-continue ./job-queue/feature-name/tasks.md

# After feature complete
/memory-bank-sync
/pm-db dashboard
```

**That's it!** Three orchestration skills handle everything.

---

## 📖 Documentation

Each system has comprehensive documentation:

- **start-phase:** `/home/artsmc/.claude/skills/start-phase/README.md` (68KB)
- **hub:** `/home/artsmc/.claude/skills/hub/README.md`
- **memory-bank:** `/home/artsmc/.claude/skills/memory-bank/README.md`
- **spec:** `/home/artsmc/.claude/skills/spec/README.md`

### Tool Documentation

- **start-phase tools:** `/home/artsmc/.claude/skills/start-phase/scripts/README.md`
- **start-phase hooks:** `/home/artsmc/.claude/hooks/start-phase/README.md`

---

## 🎓 Best Practices

### Phase Management
- ✅ **Optimal phase size:** 5-7 tasks
- ✅ **Maximum recommended:** 10 tasks
- ✅ **Beyond 10 tasks:** Split into multiple phases
- ✅ **Always use Mode 1 first:** Get strategic plan approved
- ✅ **Trust quality gates:** They prevent shipping broken code

### Documentation
- ✅ **Initialize first:** Use `/document-hub-initialize` for new projects
- ✅ **Keep docs current:** Use `/document-hub-update` after changes
- ✅ **Analyze regularly:** Use `/document-hub-analyze` to check coverage

### Knowledge Management
- ✅ **Initialize knowledge base:** Use `/memory-bank-initialize` once
- ✅ **Sync with codebase:** Use `/memory-bank-sync` regularly
- ✅ **Read before coding:** Use `/memory-bank-read` for context

### Specifications
- ✅ **Plan before implementing:** Use `/spec-plan` first
- ✅ **Review specifications:** Use `/spec-review` for validation

---

## 🎯 Advanced Workflows

For experienced users who want fine-grained control.

### Custom Feature Workflow

Skip orchestration and use individual skills:

```bash
# 1. Plan specification
/spec-plan "advanced feature with custom requirements"

# 2. Review and iterate
/spec-review
# [Make changes to specs manually if needed]
/spec-review  # Validate again

# 3. Strategic planning
/start-phase plan ./job-queue/feature-advanced/tasks.md
# [Review plan, request changes if needed]

# 4. Import to PM-DB
/pm-db import --project advanced

# 5. Execute phase
/start-phase execute ./job-queue/feature-advanced/tasks.md

# 6. Update documentation
/memory-bank-update       # Full update (all 6 files)
/document-hub-analyze     # Deep analysis
/document-hub-update      # Apply recommendations
```

---

### Parallel Feature Development

Work on multiple features simultaneously:

```bash
# Feature A: Auth
/feature-new "add user authentication"
# [Let run in background]

# Feature B: Payments (different folder)
/feature-new "integrate stripe payments"

# Feature C: Admin (resume later)
/spec-plan "build admin dashboard"
# [Stop here, resume tomorrow]
/spec-review
/start-phase plan ./job-queue/feature-admin/tasks.md
```

**PM-DB tracks all features independently.**

---

### Documentation-First Approach

For large refactors or architecture changes:

```bash
# 1. Analyze current state
/document-hub-analyze
# Review health score and recommendations

# 2. Update documentation first
# [Edit systemArchitecture.md manually]
# [Edit keyPairResponsibility.md manually]
/document-hub-update      # Validate changes

# 3. Plan implementation
/spec-plan "refactor auth to match new architecture"

# 4. Execute with new patterns
/feature-new "refactor auth layer"
```

---

### Quality-First Iteration

For complex features requiring multiple passes:

```bash
# Pass 1: MVP
/spec-plan "user profiles - MVP only"
/spec-review
# [User approves MVP scope]
/feature-new "user profiles MVP"

# Pass 2: Enhancements
/spec-plan "user profiles - add avatar upload"
/spec-review
/feature-new "user profiles enhancements"

# Pass 3: Polish
/spec-plan "user profiles - add editing"
/spec-review
/feature-new "user profiles polish"
```

**Each pass tracked separately in PM-DB.**

---

### Resume Strategies

Different resume scenarios:

**A) Clean Resume (recommended):**
```bash
/feature-continue ./path/to/tasks.md
# Automatically detects last completed task
```

**B) Force Re-run Specific Task:**
```bash
# Delete task-run record from PM-DB
sqlite3 ~/.claude/projects.db "DELETE FROM task_runs WHERE task_key='4';"

# Resume (will re-run task 4)
/feature-continue ./path/to/tasks.md
```

**C) Skip Failed Task:**
```bash
# Mark task as complete (exit_code=0) even if failed
sqlite3 ~/.claude/projects.db "UPDATE task_runs SET exit_code=0, completed_at=datetime('now') WHERE task_key='4';"

# Resume (will skip task 4)
/feature-continue ./path/to/tasks.md
```

**D) Manual Execution:**
```bash
# Skip orchestration entirely
/start-phase execute ./path/to/tasks.md --resume-from=4
```

---

### PM-DB Advanced Queries

Get insights from the database:

```bash
# View all active phase runs
sqlite3 ~/.claude/projects.db "SELECT * FROM phase_runs WHERE exit_code IS NULL;"

# Calculate average task duration
sqlite3 ~/.claude/projects.db "
  SELECT
    AVG(CAST((julianday(completed_at) - julianday(started_at)) * 1440 AS INTEGER)) as avg_minutes
  FROM task_runs
  WHERE completed_at IS NOT NULL;
"

# Find features with failed tasks
sqlite3 ~/.claude/projects.db "
  SELECT DISTINCT p.name, ph.name
  FROM projects p
  JOIN phases ph ON p.id = ph.project_id
  JOIN phase_runs pr ON ph.id = pr.phase_id
  JOIN task_runs tr ON pr.id = tr.phase_run_id
  WHERE tr.exit_code != 0;
"

# Export complete history
sqlite3 ~/.claude/projects.db "
  .mode csv
  .output history.csv
  SELECT * FROM phase_runs;
  .output stdout
"
```

---

### Memory Bank Strategies

**Quick sync after tasks:**
```bash
/memory-bank-sync   # Updates activeContext.md + progress.md only
```

**Deep update after phases:**
```bash
/memory-bank-update # Updates all 6 files + runs analysis
```

**Stale detection:**
```bash
/memory-bank-read   # Shows staleness warnings
# If activeContext.md > 7 days old → triggers alert
```

**Manual refresh:**
```bash
/documentation-start --force
# Rebuilds both Memory Bank and Document Hub
```

---

### Document Hub Strategies

**Health monitoring:**
```bash
/document-hub-analyze
# Returns health score (0-100)
# Lists drift detection findings
# Prioritizes recommendations
```

**Selective updates:**
```bash
# Only update specific files
/document-hub-update --files systemArchitecture.md,glossary.md
```

**Extract glossary terms:**
```bash
# Use helper script directly
python ~/.claude/skills/document-hub-initialize/scripts/extract_glossary.py .
```

---

### Integration with CI/CD

**Pre-commit hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Update Memory Bank before commit
claude /memory-bank-sync

# Validate documentation
claude /document-hub-analyze

# If health score < 70, warn
```

**Post-deployment:**
```bash
#!/bin/bash
# After deployment

# Update documentation
claude /document-hub-update

# Export PM-DB metrics
claude /pm-db dashboard --format json > metrics.json
```

---

## 🏆 Flagship System: start-phase

The **start-phase** system is the most comprehensive and production-ready system:

- ✅ **234KB of code** (skills + hooks + tools)
- ✅ **~72k tokens total** (complete system)
- ✅ **4 comprehensive hooks** (automated workflow)
- ✅ **4 Python tools** (zero dependencies)
- ✅ **Quality gates** between every task
- ✅ **Per-task code reviews** (AI-powered)
- ✅ **Git workflow** (commits only after quality passes)
- ✅ **SLOC tracking** (baseline, updates, final)
- ✅ **Path preservation** (never lose folder locations)
- ✅ **Parallel execution** (multi-agent support)

**Token budget:** Efficiently manages ~160k tokens for 7-task phases (79.8% of 200k budget)

**Recommended for:** Any multi-task development phase requiring quality enforcement and structured workflow.

---

## 📊 Statistics

### Token Efficiency

| System | Token Cost | Use Case |
|--------|-----------|----------|
| document-hub | ~15k | Documentation management |
| memory-bank | ~12k | Knowledge storage |
| spec | ~8k | Feature specifications |
| start-phase | ~160k (7 tasks) | Phase management with quality gates |

---

## 🐛 Troubleshooting

### Common Issues

**Q: Skills not showing up in slash command list**
- Ensure files are in correct directories (`skills/`, `hooks/`, `agents/`)
- Check file permissions (should be readable)
- Restart Claude Code if needed
- Skills appear with their full names (e.g., `/document-hub-initialize`)

**Q: Quality gates failing**
- Check that lint/build commands exist in package.json
- Ensure ESLint and TypeScript are installed
- See `/home/artsmc/.claude/skills/start-phase/README.md` troubleshooting section

**Q: Hooks not triggering**
- Verify hook files are in `/home/artsmc/.claude/hooks/`
- Check hook trigger conditions match your workflow
- Ensure hook frontmatter is correctly formatted
- Currently only start-phase has hooks implemented

### Getting Help

1. **Read the documentation** - Each system has comprehensive README
2. **Check planning docs** - `/home/artsmc/.claude/planning/` (local only)
3. **Review examples** - READMEs include extensive examples

---

## 📝 License

Private repository for personal use.

---

## 🔗 Quick Links

- [start-phase Complete Guide](skills/start-phase/README.md) - 68KB comprehensive documentation
- [start-phase Tools Guide](skills/start-phase/scripts/README.md) - Python tools documentation
- [start-phase Hooks Guide](hooks/start-phase/README.md) - Hook system documentation
- [Document Hub Guide](skills/hub/README.md) - Documentation management
- [Memory Bank Guide](skills/memory-bank/README.md) - Knowledge storage
- [Spec Guide](skills/spec/README.md) - Specification system

---

**Version:** 2.0
**Architecture:** Modular Skills, Hooks & Tools
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-17
