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
│   ├── document-hub/          # Documentation management system
│   │   ├── init.md           # Initialize documentation hub
│   │   ├── sync.md           # Sync documentation
│   │   ├── query.md          # Query documentation
│   │   ├── update.md         # Update documentation
│   │   ├── analyze.md        # Analyze documentation
│   │   ├── validate.md       # Validate documentation
│   │   ├── export.md         # Export documentation
│   │   ├── template.md       # Apply documentation templates
│   │   └── README.md         # Complete system guide
│   │
│   ├── memory-bank/           # Knowledge storage system
│   │   ├── remember.md       # Store knowledge
│   │   ├── recall.md         # Retrieve knowledge
│   │   ├── update.md         # Update knowledge
│   │   ├── search.md         # Search knowledge
│   │   ├── forget.md         # Remove knowledge
│   │   ├── summarize.md      # Summarize knowledge
│   │   ├── export.md         # Export knowledge
│   │   ├── rebuild.md        # Rebuild knowledge index
│   │   └── README.md         # Complete system guide
│   │
│   ├── spec/                  # Specification system
│   │   ├── plan.md           # Plan feature specifications
│   │   ├── write.md          # Write specifications
│   │   └── README.md         # Complete system guide
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
├── hooks/                     # Automated workflow enforcement
│   ├── document-hub/
│   │   ├── sync-on-save.md
│   │   ├── validate-on-commit.md
│   │   └── README.md
│   │
│   ├── memory-bank/
│   │   ├── auto-remember.md
│   │   ├── periodic-sync.md
│   │   └── README.md
│   │
│   └── start-phase/           # Phase workflow automation ⭐
│       ├── phase-start.md    # Pre-flight validation
│       ├── task-complete.md  # Task completion bridge
│       ├── quality-gate.md   # Quality enforcement (Part 3.5)
│       ├── phase-complete.md # Phase closeout (Part 5)
│       └── README.md
│
├── commands/                  # Legacy commands (deprecated)
│   ├── document-hub.md       # → Use /document-hub skills
│   ├── memory-bank.md        # → Use /memory-bank skills
│   ├── spec.md               # → Use /spec skills
│   └── start-phase.md        # → Use /start-phase skills
│
└── README.md                  # This file
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

### 📚 Document Hub (8 skills)

Comprehensive documentation management system.

```bash
/document-hub init          # Initialize documentation structure
/document-hub sync          # Sync documentation with codebase
/document-hub query         # Query documentation
/document-hub update        # Update documentation
/document-hub analyze       # Analyze documentation coverage
/document-hub validate      # Validate documentation integrity
/document-hub export        # Export documentation
/document-hub template      # Apply documentation templates
```

**Features:**
- Automated documentation generation
- Codebase synchronization
- Documentation validation
- Template management

**Documentation:** `/home/artsmc/.claude/skills/document-hub/README.md`

---

### 🧠 Memory Bank (8 skills)

Knowledge storage and retrieval system with automatic context management.

```bash
/memory-bank remember       # Store knowledge (facts, patterns, decisions)
/memory-bank recall         # Retrieve relevant knowledge
/memory-bank update         # Update existing knowledge
/memory-bank search         # Search knowledge base
/memory-bank forget         # Remove outdated knowledge
/memory-bank summarize      # Summarize knowledge
/memory-bank export         # Export knowledge base
/memory-bank rebuild        # Rebuild knowledge index
```

**Features:**
- Context-aware knowledge storage
- Semantic search
- Automatic categorization
- Knowledge graph maintenance

**Documentation:** `/home/artsmc/.claude/skills/memory-bank/README.md`

---

### 📋 Spec (2 skills)

Feature specification and documentation system.

```bash
/spec plan [feature]        # Plan feature specifications (with optional arg)
/spec write                 # Write detailed specifications
```

**Features:**
- Structured feature planning
- FRD (Functional Requirements Document) generation
- FRS (Functional Requirements Specification)
- GS (Game Script) for implementation steps
- TR (Technical Requirements) documentation

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

**Documentation:** `/home/artsmc/.claude/skills/start-phase/README.md` (68KB comprehensive guide)

---

## 🪝 Hooks

Automated workflow enforcement triggered by specific events.

### Document Hub Hooks
- **sync-on-save.md** - Auto-sync documentation on file save
- **validate-on-commit.md** - Validate documentation before git commit

### Memory Bank Hooks
- **auto-remember.md** - Automatically capture important information
- **periodic-sync.md** - Periodic knowledge base synchronization

### Start-Phase Hooks ⭐
- **phase-start.md** - Pre-flight validation before phase starts
- **task-complete.md** - Bridge between task execution and quality gate
- **quality-gate.md** - Quality enforcement between every task (Part 3.5)
- **phase-complete.md** - Comprehensive phase closeout (Part 5)

**Location:** `/home/artsmc/.claude/hooks/`

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
| **start-phase** | ✅ v2.0 | 2 | 4 | 4 | 68KB |
| **document-hub** | ✅ v1.0 | 8 | 2 | 0 | Complete |
| **memory-bank** | ✅ v1.0 | 8 | 2 | 0 | Complete |
| **spec** | ✅ v1.0 | 2 | 0 | 0 | Complete |

### Total System Size

```
Skills:        ~135 KB (28 skill files)
Hooks:         ~85 KB (8 hook systems)
Tools:         ~50 KB (4 Python tools)
Documentation: ~125 KB (comprehensive guides)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:         ~395 KB (production-ready)
```

---

## 🚀 Quick Start

### For New Projects

**1. Initialize documentation:**
```bash
/document-hub init
```

**2. Plan your first phase:**
```bash
# Create task list
cat > ./my-feature/tasks.md <<EOF
# My Feature
1. Task 1
2. Task 2
3. Task 3
EOF

# Strategic planning
/start-phase plan ./my-feature/tasks.md

# Execute with quality gates
/start-phase execute ./my-feature/tasks.md
```

**3. Store important knowledge:**
```bash
/memory-bank remember "API uses JWT tokens with 24h expiration"
```

### For Existing Projects

**1. Analyze current documentation:**
```bash
/document-hub analyze
```

**2. Recall project context:**
```bash
/memory-bank recall "authentication patterns"
```

**3. Plan next feature:**
```bash
/spec plan "add user profile page"
```

---

## 📖 Documentation

Each system has comprehensive documentation:

- **start-phase:** `/home/artsmc/.claude/skills/start-phase/README.md` (68KB)
- **document-hub:** `/home/artsmc/.claude/skills/document-hub/README.md`
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
- ✅ **Keep docs in sync:** Use `/document-hub sync` regularly
- ✅ **Validate before commits:** Hooks do this automatically
- ✅ **Use templates:** Consistent documentation structure

### Knowledge Management
- ✅ **Remember key decisions:** Use `/memory-bank remember`
- ✅ **Context before coding:** Use `/memory-bank recall`
- ✅ **Clean up outdated knowledge:** Use `/memory-bank forget`

### Specifications
- ✅ **Plan before implementing:** Use `/spec plan` first
- ✅ **Detailed requirements:** Use `/spec write` for FRD/FRS
- ✅ **Include in documentation:** Export to documentation hub

---

## 🔄 Migration from Legacy Commands

Legacy command files in `/commands/` have been **deprecated** and replaced with modular skills.

| Old Command | New Skills | Migration |
|-------------|------------|-----------|
| `/document-hub` | `/document-hub {init,sync,query,etc.}` | Use specific skill |
| `/memory-bank` | `/memory-bank {remember,recall,etc.}` | Use specific skill |
| `/spec` | `/spec {plan,write}` | Use specific skill |
| `/start-phase` | `/start-phase {plan,execute}` | Use Mode 1 then Mode 2 |

**Note:** Legacy command files contain migration guides and deprecation notices.

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

### Total Implementation

- **28 skills** across 4 systems
- **8 hooks** for automated workflow
- **4 Python tools** (890 lines of code)
- **8 specialized agents** for development
- **~395 KB** of production code
- **Zero external dependencies** (Python stdlib only)

### Token Efficiency

| System | Token Cost | Use Case |
|--------|-----------|----------|
| document-hub | ~30k | Documentation management |
| memory-bank | ~25k | Knowledge storage |
| spec | ~45k | Feature specifications |
| start-phase | ~160k (7 tasks) | Phase management with quality gates |

---

## 🐛 Troubleshooting

### Common Issues

**Q: Skills not showing up**
- Ensure files are in correct directories (`skills/`, `hooks/`, `agents/`)
- Check file permissions (should be readable)
- Restart Claude Code if needed

**Q: Quality gates failing**
- Check that lint/build commands exist in package.json
- Ensure ESLint and TypeScript are installed
- See `/home/artsmc/.claude/skills/start-phase/README.md` troubleshooting section

**Q: Hooks not triggering**
- Verify hook files are in `/home/artsmc/.claude/hooks/`
- Check hook trigger conditions match your workflow
- Ensure hook frontmatter is correctly formatted

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
- [document-hub Guide](skills/document-hub/README.md) - Documentation management
- [memory-bank Guide](skills/memory-bank/README.md) - Knowledge storage
- [spec Guide](skills/spec/README.md) - Specification system

---

**Version:** 2.0
**Architecture:** Modular Skills, Hooks & Tools
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-17
