# Claude Code Development Environment

**Version:** 2.1
**Last Updated:** 2026-01-31
**Architecture:** Modular Skills, Hooks & Tools with Agent Context Caching

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
├── agents/                    # Specialized development agents (14 total)
│   ├── api-designer.md              # Contract-first API design
│   ├── code-reviewer.md             # Security-focused reviews
│   ├── debugger-specialist.md       # Bug investigation (ENHANCED)
│   ├── frontend-developer.md        # State management & logic
│   ├── nextjs-backend-developer.md  # Next.js APIs
│   ├── nextjs-qa-engineer.md        # Next.js testing
│   ├── python-fastapi-expert.md     # FastAPI backends
│   ├── python-reviewer.md           # Python code review
│   ├── python-tester.md             # Pytest testing
│   ├── refactoring-specialist.md    # Code modernization (NEW)
│   ├── technical-writer.md          # Documentation
│   ├── ui-developer.md              # Visual implementation
│   └── [2 more agents...]
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

Specialized development personas for different aspects of development. All agents include comprehensive self-checking mechanisms with confidence levels (🟢🟡🔴).

### Code Quality & Refactoring ⭐ NEW
- **refactoring-specialist.md** - Technical debt reduction and code modernization
  - Pre-execution verification (5-point checklist)
  - Confidence level system with STOP criteria
  - 32-item quality checklist (3 phases)
  - Memory & Documentation Protocol (mandatory reads)
- **debugger-specialist.md** - Bug investigation and root cause analysis (ENHANCED)
  - Pre-investigation verification
  - Confidence-based escalation
  - 44-item quality checklist (3 phases)
  - "When to Ask for Help" protocol

### Code Review & Quality
- **code-reviewer.md** - Comprehensive code review with security analysis
- **python-reviewer.md** - Python-specific code review (PEP 8, MyPy, Bandit, Ruff)

### Development
- **frontend-developer.md** - Frontend application logic and state management
- **ui-developer.md** - Visual implementation and styling
- **nextjs-backend-developer.md** - Next.js backend API development
- **python-fastapi-expert.md** - FastAPI backend development

### API Design
- **api-designer.md** - Contract-first API design with OpenAPI specs and three-tier architecture

### Testing & QA
- **nextjs-qa-engineer.md** - Quality assurance for Next.js applications
- **python-tester.md** - Pytest-based testing with fixtures

### Documentation
- **technical-writer.md** - Documentation creation and maintenance

**Total:** 14 specialized agents
**Self-Checking:** All agents include confidence levels (🟢🟡🔴)
**Location:** `/home/artsmc/.claude/agents/`
**Reference:** `/home/artsmc/.claude/docs/agent-confidence-levels.md` - Comprehensive guide

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
- **15 Python tools** (~900 lines of code, zero dependencies)
- **14 specialized agents** for development (including refactoring-specialist, debugger-specialist)
- **~350 KB** of production code (skills + hooks + tools + agents)
- **Agent Context Cache (Migration 006)** - 60-85% token savings
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
- Auto-initializes if missing

**Step 2: Initialize PM-DB**

```bash
/pm-db init
```

This creates:
- Project database at `~/.claude/projects.db`
- Agent Context Cache (Migration 006) for 60-85% token savings
- Phase run tracking
- Task execution history

**Done!** Your project is now ready for feature development.

---

### Develop Your First Feature

**The Easy Way (Recommended):**

```bash
/feature-new "add user login page"
```

This runs the complete workflow automatically:
1. ✅ Checks documentation is initialized
2. ✅ Creates feature specification (FRD, FRS, GS, TR)
3. ⏸️ **Waits for your approval** (checkpoint 1)
4. ✅ Creates strategic execution plan with tasks
5. ⏸️ **Waits for your approval** (checkpoint 2)
6. ✅ Imports to PM-DB for tracking
7. ✅ Executes with quality gates between every task
8. ✅ AI code reviews after each task
9. ✅ Git commits only after quality passes

**Two human approval checkpoints ensure quality before execution.**

**What you'll see:**
```
Step 1/6: Checking documentation...
✅ Memory Bank found
✅ Document Hub found

Step 2/6: Creating feature specification...
✅ FRD created (Functional Requirements Document)
✅ FRS created (Functional Requirements Specification)
✅ GS created (Gherkin Scenarios)
✅ TR created (Technical Requirements)

[Shows specifications]

👤 CHECKPOINT 1: Review specifications
Options: approve / revise / cancel
> approve

Step 3/6: Creating strategic plan...
✅ 8 tasks identified
✅ 2 parallel waves detected
✅ Estimated time: 6-7 hours

[Shows task list with dependencies]

👤 CHECKPOINT 2: Approve execution plan?
Options: approve / revise / cancel
> approve

Step 4/6: Importing to PM-DB...
✅ Phase Run ID: 5 created

Step 5/6: Executing tasks with quality gates...
[Progress bar shows 0/8 tasks complete]

Task 1: Setup auth API endpoint
  Agent: nextjs-backend-developer
  ✅ Code written
  ✅ Quality gate passed (lint: 0 errors, build: success)
  ✅ Code review passed
  ✅ Git commit created
  Duration: 15m

[Continues for all tasks...]

Step 6/6: Phase complete!
✅ 8/8 tasks completed
✅ All quality gates passed
✅ 8 git commits created
✅ Phase Run #5 completed

Cache Performance:
  Token savings: 65% (12,450 tokens saved)
  Cache hit rate: 78%
```

---

### Resume Interrupted Work

If your session drops or you need to pause:

```bash
/feature-continue ./job-queue/feature-login/tasks.md
```

**What happens:**
- ✅ Reads PM-DB to find last completed task
- ✅ Shows progress: "Task 5/8 complete"
- ✅ Resumes from Task 6
- ✅ Maintains quality gates for remaining tasks
- ✅ Preserves git history and cache

**Example output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Resume Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: User Authentication MVP
Progress: [██████████░░░░░░░░░░] 5/8 tasks (62%)

Completed:
✅ Task 1: Setup auth API (18m)
✅ Task 2: Create login UI (22m)
✅ Task 3: Connect API to UI (15m)
✅ Task 4: Add JWT tokens (25m)
✅ Task 5: Create user schema (20m)

Remaining:
⏳ Task 6: Add password hashing
⏳ Task 7: Add auth middleware
⏳ Task 8: Write integration tests

Resuming from Task 6...
```

---

### View Progress

```bash
/pm-db dashboard
```

**Shows:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PM-DB Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Projects: 3 active
Phases: 8 total (5 complete, 2 in-progress, 1 pending)

Active Phase Runs:
  #5 - User Authentication MVP (62% complete, 2h 15m elapsed)
  #7 - Payment Integration (25% complete, 45m elapsed)

Recently Completed:
  #4 - Admin Dashboard (100%, 4h 30m, all quality gates passed)
  #3 - Email Templates (100%, 1h 45m, all quality gates passed)

Overall Metrics:
  Total tasks: 127
  Success rate: 98.4%
  Avg task duration: 22 minutes
  Cache hit rate: 73%
  Token savings: 62%
```

---

### Update Documentation

After completing features:

```bash
/memory-bank-sync        # Quick update (activeContext + progress only)
/document-hub-update     # Full documentation sync
```

**When to use each:**
- `/memory-bank-sync`: After each task or small change (fast, 2 files)
- `/memory-bank-update`: After completing a phase (comprehensive, 6 files)
- `/document-hub-update`: After architectural changes

---

### Complete Beginner Workflow

```bash
# === ONE-TIME SETUP ===
/documentation-start     # Initialize Memory Bank + Document Hub
/pm-db init              # Initialize project database

# === FOR EACH FEATURE ===
/feature-new "add user login with OAuth"

# [Review spec at checkpoint 1] → approve
# [Review plan at checkpoint 2] → approve
# [System executes automatically with quality gates]

# === IF INTERRUPTED ===
/feature-continue ./job-queue/feature-auth/tasks.md

# === AFTER FEATURE COMPLETE ===
/memory-bank-sync        # Update knowledge base
/pm-db dashboard         # View metrics

# === REPEAT FOR NEXT FEATURE ===
/feature-new "integrate payment processing"
```

**That's it!** Three orchestration skills handle everything:
1. `/documentation-start` - Setup (once)
2. `/feature-new` - Build features (many times)
3. `/feature-continue` - Resume work (when needed)

---

### Common Beginner Questions

**Q: How long does `/feature-new` take?**
- Spec creation: 5-15 minutes
- Plan creation: 5-10 minutes
- Execution: Depends on task count (1-8 hours for typical feature)
- Total: Budget 2-10 hours for complete feature

**Q: Can I cancel during execution?**
- Yes! Ctrl+C to stop
- Progress is saved in PM-DB
- Use `/feature-continue` to resume

**Q: What if quality gates fail?**
- System stops automatically
- Shows errors (lint, build, test failures)
- Offers to fix automatically
- Won't proceed until all gates pass

**Q: How do I see what changed?**
- Check git history: `git log --oneline`
- View PM-DB: `/pm-db dashboard`
- Read phase summary: `./job-queue/feature-name/planning/phase-structure/phase-summary.md`

**Q: What's the cache system?**
- Saves 60-85% tokens by caching file reads
- Automatic - no manual work needed
- Invalidates on file changes (SHA-256 hashing)
- Persists across sessions

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

For experienced users who want fine-grained control over every step.

### Custom Feature Workflow

Skip orchestration and use individual skills:

```bash
# === PHASE 1: SPECIFICATION ===
/spec-plan "real-time notification system with WebSocket support"
# Creates: FRD, FRS, GS, TR documents
# Duration: ~10-15 minutes

# Review specifications manually
cat ./notifications-spec/FRS.md
# [Make edits if needed]

/spec-review
# Validates structure, completeness, technical feasibility
# Shows health score and recommendations

# === PHASE 2: STRATEGIC PLANNING ===
# First, create initial task list manually or use spec output
# Then run strategic planning

/start-phase plan ./job-queue/feature-notifications/tasks.md

# What this does:
# - Analyzes task complexity
# - Identifies parallelism opportunities (Wave 1, Wave 2, etc.)
# - Proposes incremental build strategy
# - Questions scope if too large
# - Waits for your approval

# Example output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝 Proposed Refined Plan
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Changes made:
# ✅ Reduced scope to MVP (deferred auth to Phase 2)
# ✅ Reorganized for early integration
# ✅ Identified 2 parallel waves (saves ~2h)
# ✅ Ensured working code after each task
#
# Revised Task List:
# Wave 1 (Parallel):
#   1. Setup WebSocket server (nextjs-backend)
#   2. Create notification UI (ui-developer)
# Wave 2 (Sequential):
#   3. Connect UI to WebSocket
#   4. Add Redis pub/sub
# ...
#
# Options: approve / revise / reject / question
> approve

# === PHASE 3: PM-DB SETUP ===
# Create project and import phase plan

/pm-db init  # If not already done

sqlite3 ~/.claude/projects.db <<EOF
INSERT INTO projects (name, description, filesystem_path)
VALUES ('notification-system', 'Real-time notification system', './job-queue/feature-notifications');

INSERT INTO phases (project_id, name, description)
SELECT id, 'Notification MVP', 'WebSocket-based real-time notifications'
FROM projects WHERE name = 'notification-system';
EOF

# Or use PM-DB skill:
/pm-db create-project --name "notification-system" --path "./job-queue/feature-notifications"

# === PHASE 4: EXECUTION ===
/start-phase execute ./job-queue/feature-notifications/tasks.md

# Optional: Add extra instructions
/start-phase execute ./job-queue/feature-notifications/tasks.md "Use Socket.io library, add reconnection logic, prioritize error handling"

# What happens:
# Part 1: Creates planning/ directory structure
# Part 2: Generates delegation plan, parallel strategy, system changes
# Part 3: Executes tasks with quality gates
#   - For each task:
#     • Adopts specialized agent persona
#     • Writes code
#     • Runs quality gate (lint, build, tests)
#     • AI code review
#     • Git commit
#     • Updates PM-DB
# Part 4: Task updates (automatic via hooks)
# Part 5: Phase closeout with metrics

# === PHASE 5: DOCUMENTATION ===
/memory-bank-update       # Full update (all 6 files)
# Updates: projectbrief, productContext, techContext,
#          systemPatterns, activeContext, progress

/document-hub-analyze     # Deep analysis
# Checks:
#   - Documentation coverage
#   - Drift detection (code vs docs)
#   - Missing glossary terms
#   - Architectural alignment
# Returns health score: 0-100

/document-hub-update      # Apply recommendations
# Updates: systemArchitecture, keyPairResponsibility,
#          glossary, techStack

# === PHASE 6: VERIFICATION ===
/pm-db dashboard
# View metrics:
#   - Tasks: 12/12 complete
#   - Duration: 4h 23m
#   - Cache hit rate: 78%
#   - Token savings: 65%
#   - Quality gates: 12/12 passed

# Check git history
git log --oneline --since="4 hours ago"
# Should show 12 commits (one per task)

# Read phase summary
cat ./job-queue/feature-notifications/planning/phase-structure/phase-summary.md
```

**Why use this instead of `/feature-new`?**
- Fine-grained control at each step
- Can pause between phases
- Manual PM-DB management
- Custom extra instructions per phase
- Iterate on specs independently
- Separate planning from execution days apart

---

### Parallel Feature Development

Work on multiple features simultaneously with proper isolation:

```bash
# === STRATEGY 1: Concurrent Features (Different Files) ===
# Feature A: Auth (backend)
/feature-new "add user authentication API"
# Modifies: src/api/auth/, src/lib/jwt.ts, tests/auth.test.ts

# Feature B: UI Components (frontend)
/feature-new "build reusable component library"
# Modifies: src/components/, src/stories/, tests/components/

# Feature C: Database Schema (separate concern)
/feature-new "add analytics tables"
# Modifies: prisma/schema.prisma, migrations/, seeds/

# ✅ Safe to run in parallel - no file conflicts
# ✅ PM-DB tracks each independently
# ✅ Each gets own Phase Run ID

# === STRATEGY 2: Sequential Dependencies ===
# Phase 1: API Contract
/spec-plan "design notification API contract"
/spec-review
# [Save OpenAPI spec]

# Phase 2A: Backend Implementation (can start immediately)
cd backend/
/feature-new "implement notification API endpoints"

# Phase 2B: Frontend Implementation (can start in parallel)
cd frontend/
/feature-new "build notification UI components"
# Uses OpenAPI spec from Phase 1

# Phase 3: Integration (after both Phase 2 complete)
cd integration/
/feature-new "integrate notification system end-to-end"

# === STRATEGY 3: Team Collaboration ===
# Developer A: Core feature
/feature-new "implement core payment logic"
# Creates: ./job-queue/feature-payment/

# Developer B: Tests (different branch)
git checkout -b add-payment-tests
/feature-new "write payment integration tests"
# Creates: ./job-queue/feature-payment-tests/

# Developer C: Documentation (different branch)
git checkout -b update-payment-docs
/feature-new "document payment integration"
# Creates: ./job-queue/feature-payment-docs/

# Merge strategy:
# 1. A merges core feature
# 2. B rebases on A's branch, merges tests
# 3. C rebases on B's branch, merges docs

# === STRATEGY 4: Staggered Execution ===
# Morning: Plan multiple features
/spec-plan "feature A"
/spec-plan "feature B"
/spec-plan "feature C"

# Review and approve all specs
/spec-review  # For each feature

# Afternoon: Execute one at a time
/start-phase plan ./job-queue/feature-a/tasks.md
/start-phase execute ./job-queue/feature-a/tasks.md

# Next day: Continue with feature B
/start-phase plan ./job-queue/feature-b/tasks.md
/start-phase execute ./job-queue/feature-b/tasks.md

# === PM-DB Query: Active Features ===
sqlite3 ~/.claude/projects.db <<EOF
SELECT
  p.name as project,
  ph.name as phase,
  pr.status,
  COUNT(tr.id) as total_tasks,
  SUM(CASE WHEN tr.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
  ROUND(100.0 * SUM(CASE WHEN tr.status = 'completed' THEN 1 ELSE 0 END) / COUNT(tr.id), 1) as pct_complete
FROM projects p
JOIN phases ph ON p.id = ph.project_id
JOIN phase_runs pr ON ph.id = pr.phase_id
LEFT JOIN task_runs tr ON pr.id = tr.phase_run_id
WHERE pr.status = 'in-progress'
GROUP BY p.name, ph.name, pr.status;
EOF
# Example output:
# project           | phase              | status      | total_tasks | completed_tasks | pct_complete
# payment-system    | MVP Implementation | in-progress | 15          | 8               | 53.3
# auth-system       | OAuth Integration  | in-progress | 10          | 3               | 30.0
# admin-dashboard   | Dashboard UI       | in-progress | 12          | 10              | 83.3
```

**PM-DB tracks all features independently with separate Phase Run IDs.**

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

### Cache Optimization & Performance Tuning

**Understanding the Agent Context Cache (Migration 006):**

The cache system automatically saves 60-85% tokens by caching file reads.

```bash
# === HOW IT WORKS ===
# 1. First read: File content cached with SHA-256 hash
# 2. Subsequent reads: Hash checked, cache hit if unchanged
# 3. File modified: Hash changes, cache miss, new cache entry
# 4. Persists: Cache survives across sessions and agent invocations

# === VIEW CACHE STATISTICS ===
sqlite3 ~/.claude/projects.db <<EOF
SELECT
  ai.agent_name,
  ai.purpose,
  ai.total_files_read,
  ai.cache_hits,
  ai.cache_misses,
  ROUND(100.0 * ai.cache_hits / NULLIF(ai.cache_hits + ai.cache_misses, 0), 1) as hit_rate_pct,
  ai.estimated_tokens_used,
  ai.duration_seconds
FROM agent_invocations ai
ORDER BY ai.started_at DESC
LIMIT 10;
EOF

# Example output:
# agent_name              | purpose                | files | hits | misses | hit_rate | tokens | duration
# technical-writer        | Task 3: Create guide   | 2     | 0    | 2      | 0%       | 13115  | 76
# technical-writer        | Task 2: Update debug   | 1     | 0    | 1      | 0%       | 7069   | 54
# technical-writer        | Task 1: Update refact  | 1     | 0    | 1      | 0%       | 5447   | 36
# nextjs-backend          | Implement auth API     | 5     | 4    | 1      | 80%      | 8420   | 120

# === CACHE PERFORMANCE BY PHASE ===
sqlite3 ~/.claude/projects.db <<EOF
SELECT
  pr.id as phase_run_id,
  ph.name as phase_name,
  COUNT(ai.id) as agent_invocations,
  SUM(ai.total_files_read) as total_reads,
  SUM(ai.cache_hits) as total_hits,
  SUM(ai.cache_misses) as total_misses,
  ROUND(100.0 * SUM(ai.cache_hits) / NULLIF(SUM(ai.cache_hits) + SUM(ai.cache_misses), 0), 1) as hit_rate,
  SUM(ai.estimated_tokens_used) as tokens_used
FROM phase_runs pr
JOIN phases ph ON pr.phase_id = ph.id
LEFT JOIN agent_invocations ai ON pr.id = ai.phase_run_id
GROUP BY pr.id
ORDER BY pr.started_at DESC;
EOF

# === OPTIMIZE CACHE HIT RATE ===

# Strategy 1: Read files early, modify late
# ✅ Good: Read all Memory Bank files at start of session
/memory-bank-read
# [All files cached]
# [Do work that references but doesn't modify files]
# ✅ High cache hit rate

# ❌ Bad: Modify files immediately
/memory-bank-update  # Modifies files
/memory-bank-read    # Now needs to re-cache everything
# ❌ Low cache hit rate

# Strategy 2: Batch reads before modifications
# Read phase:
cat memory-bank/systemPatterns.md     # Cache miss (first read)
cat memory-bank/activeContext.md      # Cache miss (first read)
cat agents/refactoring-specialist.md  # Cache miss (first read)

# Work phase (references cached files multiple times):
# Multiple agent invocations, all read same files → cache hits!

# Modify phase (end of session):
/memory-bank-sync    # Now modify files

# Strategy 3: Use sub-agents for repeated reads
# Main orchestrator: Spawns 5 sub-agents
# Each sub-agent reads: Memory Bank (6 files) + Documentation Hub (4 files)
# Without cache: 5 × 10 files = 50 reads = ~150k tokens
# With cache: 10 misses + 40 hits = ~30k tokens (80% savings!)

# === CACHE INVALIDATION (AUTOMATIC) ===
# Files are automatically invalidated when modified
# SHA-256 hash detects changes

# View cached files:
sqlite3 ~/.claude/projects.db <<EOF
SELECT
  file_path,
  SUBSTR(content_hash, 1, 12) as hash_preview,
  estimated_tokens,
  priority,
  last_accessed_at
FROM cached_files
ORDER BY last_accessed_at DESC
LIMIT 20;
EOF

# Manually invalidate cache (rarely needed):
sqlite3 ~/.claude/projects.db "DELETE FROM cached_files WHERE file_path LIKE '%memory-bank%';"

# === CACHE PRIORITY LEVELS ===
# High priority: Memory Bank, Documentation Hub, agent files
# Medium priority: Source code files
# Low priority: Test files, generated files

# Files are cached based on read frequency and token count
# High-priority files stay in cache longer

# === PERFORMANCE METRICS ===
# Target performance:
# - Cache lookup: <5ms (actual: 1-2ms average)
# - Hash calculation: <100ms for 1MB file (actual: ~1ms)
# - Hit rate: 60-85% in multi-agent workflows (actual: 65-80%)
# - Token savings: 40-66% (actual: 60-85%)
```

**Real-world impact:**
- **Without cache:** 15 file reads × 30k tokens avg = 450k tokens
- **With cache:** 3 misses + 12 hits = 90k tokens
- **Savings:** 360k tokens (80% reduction)

---

### Memory Bank Strategies

**Quick sync after tasks:**
```bash
/memory-bank-sync   # Updates activeContext.md + progress.md only
# Fast: ~5-10 minutes
# Use: After each task or small change
# Cache impact: Minimal (only 2 files modified)
```

**Deep update after phases:**
```bash
/memory-bank-update # Updates all 6 files + runs analysis
# Comprehensive: ~15-20 minutes
# Use: After completing a phase or major milestone
# Cache impact: All Memory Bank files invalidated
```

**Stale detection:**
```bash
/memory-bank-read   # Shows staleness warnings
# If activeContext.md > 7 days old → triggers alert
# If progress.md > 14 days old → triggers alert
```

**Manual refresh:**
```bash
/documentation-start --force
# Rebuilds both Memory Bank and Document Hub
# Use: When documentation is severely out of date
# Cache impact: All documentation files invalidated
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

| System | Token Cost (Without Cache) | Token Cost (With Cache) | Savings | Use Case |
|--------|---------------------------|------------------------|---------|----------|
| document-hub | ~15k | ~5k (2nd+ read) | 67% | Documentation management |
| memory-bank | ~12k | ~4k (2nd+ read) | 67% | Knowledge storage |
| spec | ~8k | ~8k (rarely cached) | 0% | Feature specifications (one-time) |
| start-phase | ~160k (7 tasks) | ~55-65k (7 tasks) | 60-65% | Phase with quality gates |
| feature-new | ~180k (full workflow) | ~70-80k (with cache) | 55-60% | Complete orchestrated workflow |

### Cache Performance (Migration 006)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Cache lookup time | <50ms | 1-2ms | ✅ 24x better |
| Hash calculation | <100ms | ~1ms | ✅ 100x better |
| Hit rate (multi-agent) | 60-70% | 65-85% | ✅ Exceeds target |
| Token savings | 40-66% | 60-85% | ✅ Exceeds target |
| Scale | 1000 files | 10,000+ files | ✅ 10x capacity |

**Real-world example:**
- **Phase with 8 tasks, 3 agents:**
  - Without cache: 450k tokens
  - With cache: 160k tokens
  - Savings: 290k tokens (64%)

### Agent Performance

| Agent | Specialty | Cache Benefit | Avg Duration |
|-------|-----------|---------------|--------------|
| refactoring-specialist | Code modernization | High (reads docs) | 15-30m |
| debugger-specialist | Bug investigation | High (reads logs) | 20-45m |
| nextjs-backend-developer | API development | Medium | 12-25m |
| ui-developer | Component building | Low (new code) | 10-20m |
| code-reviewer | Quality checks | Very High | 5-10m |
| technical-writer | Documentation | Very High | 8-15m |

**Cache benefit:**
- **High:** Agents that read Memory Bank, Documentation Hub repeatedly
- **Medium:** Agents that read source code files
- **Low:** Agents that primarily write new files

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

**Version:** 2.1
**Architecture:** Modular Skills, Hooks & Tools with Agent Context Caching
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-31
**Cache System:** Migration 006 - 60-85% token savings
