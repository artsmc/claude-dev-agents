# Claude Dev Agents — Claude Code Development Environment

**Version:** 0.3.0
**Last Updated:** 2026-05-30
**Architecture:** Modular Skills, Agents, Hooks & Tools with PM-DB Tracking and Reasoning-Skill Cueing

A multi-agent development framework built on the Claude Code CLI. It lives in `~/.claude/` and turns Claude Code into a coordinated team of specialized AI agents — driven by `/skill-name` commands, backed by a SQLite project-tracking database, and guarded by quality gates, session-start context restoration, and a metacognitive reasoning layer that nudges the model to plan, debug, verify, and self-correct.

---

## 🏗️ Architecture Overview

This repository implements a **modular, skill-based architecture** with five cooperating layers:

- ✅ **Agents** — 19 specialized development personas (plus 5 loadable modules) with standardized YAML frontmatter (`name` / `model` / `tools`)
- ✅ **Skills** — 45 composable `/slash-command` workflows across 46 skill directories
- ✅ **Hooks** — 30 hook files across 8 subsystems, from quality gates to the one genuinely-wired event hook
- ✅ **Tools** — Zero-dependency Python utilities (PM-DB layer, quality enforcement, backup/restore) — Python stdlib only
- ✅ **PM-DB** — A 17-table SQLite project database (`projects.db`) tracking specs, phases, tasks, and execution runs, with both a Python and a generated Prisma access layer

**Design pillars:**

- ✅ **Specialized personas** — each agent is a focused expert (API design, debugging, security audit, refactoring, testing, docs) rather than a generalist
- ✅ **Cost-efficient model routing** — Opus for deep reasoning (architecture, security, debugging, orchestration); Sonnet for implementation, review, and documentation
- ✅ **Tool-restriction profiles** — Read-only (advisory/review), Write-no-shell (UI/frontend), and Full (implementation) profiles scope what each agent can touch
- ✅ **Modularized agents** — large agents split into a small core plus on-demand loadable modules (security-auditor, mastra-core-developer, technical-writer)
- ✅ **Metacognitive reasoning layer** — 8 procedural-judgment skills that encode *how* to plan, debug, verify, delegate, and respond to steering, surfaced automatically by a UserPromptSubmit cue hook
- ✅ **Safety net** — shadow-git snapshot scripts, session-start context restoration, audible completion hooks, and a `health-check.sh` foundation validator
- ✅ **Zero external dependencies** — every utility is pure Python stdlib

---

## 📁 Directory Structure

```
.claude/
├── agents/                          # 19 agent personas + 5 loadable modules
│   ├── api-designer.md              # Contract-first API design (read-only)
│   ├── database-schema-specialist.md# Schema, migrations, query tuning
│   ├── debugger-specialist.md       # Root-cause analysis (Opus)
│   ├── devops-infrastructure.md     # CI/CD, containers, IaC
│   ├── express-api-developer.md     # Express 5 + Prisma + JWT
│   ├── frontend-developer.md        # State & data logic (no Bash)
│   ├── refactoring-specialist.md    # Code modernization (NEW)
│   ├── security-auditor.md          # OWASP audit-only (Opus)
│   ├── ui-developer.md              # Visual TSX implementation
│   ├── [10 more personas...]
│   └── modules/                     # Loadable extension modules (no frontmatter)
│       ├── mastra-core-developer-mcp.md
│       ├── mastra-core-developer-workflows.md
│       ├── security-auditor-compliance.md
│       ├── security-auditor-pentest.md
│       └── technical-writer-style.md
│
├── skills/                          # 46 skill dirs (45 with SKILL.md)
│   ├── research-gated-build-plan/   # 🧠 Reasoning skill ⭐ NEW
│   ├── diagnose-from-raw-symptom/   # 🧠 Reasoning skill ⭐ NEW
│   ├── prove-it-live-before-done/   # 🧠 Reasoning skill ⭐ NEW
│   ├── fleet-dispatch-and-watch/    # 🧠 Reasoning skill ⭐ NEW
│   ├── steer-and-correct-the-agent/ # 🧠 Reasoning skill ⭐ NEW
│   ├── enumerated-menu-pick-and-sweep/  # 🧠 Reasoning skill ⭐ NEW
│   ├── reference-as-executable-spec/    # 🧠 Reasoning skill ⭐ NEW
│   ├── scope-question-and-delegate/     # 🧠 Reasoning skill ⭐ NEW
│   │
│   ├── feature-new/                 # 🎯 End-to-end feature orchestration
│   ├── feature-continue/            # 🎯 Resume interrupted work
│   ├── spec-plan/  spec-review/     # 📋 Spec authoring + critique
│   ├── start-phase/                 # 🚀 cache_wrapper.py helper
│   ├── start-phase-plan/            # 🚀 Mode 1: strategic planning ⭐ FLAGSHIP
│   │   └── scripts/                 #   quality_gate.py, task_validator.py,
│   │                                #   validate_phase.py, sloc_tracker.py
│   ├── start-phase-execute/         # 🚀 Mode 2: structured execution ⭐
│   ├── start-phase-execute-team/    # 🚀 Multi-agent parallel execution ⭐
│   ├── pm-db/                       # 🗄️ Project-tracking DB skill
│   │   └── scripts/                 #   init_db, migrate, import_specs,
│   │                                #   import_phases, generate_report,
│   │                                #   export_to_memory_bank
│   ├── memory-bank-*/               # 🧠 4 Memory Bank skills (6-file memory)
│   ├── document-hub-*/              # 📚 4 Document Hub skills (cline-docs)
│   ├── documentation-start/         # 📚 One-shot Brain bootstrap
│   ├── architecture-quality-assess/ # 🔍 Code quality assessment
│   ├── security-quality-assess/     # 🔍 OWASP / secrets / CVE scan
│   ├── code-duplication/            # 🔍 Exact/structural duplicate finder
│   ├── mastra-*/                    # ⚙️ 11 Mastra framework skills
│   ├── gitlab-maintainer/           # 🔌 GitLab CI + MR maintenance
│   ├── miro-diagram/  miro-infographic/  # 🔌 Miro visual creation
│   ├── skill-creator/               # 🛠️ Author/measure/optimize skills
│   ├── new-product/                 # 🛠️ Deep product research + design
│   └── remote-control-builder/      # 🛠️ Multi-agent system builder
│
├── hooks/                           # 30 hook files across 8 subsystems
│   ├── reasoning-skills/            # ⭐ THE wired event hook (UserPromptSubmit)
│   │   ├── dispatch.py              #   matches prompt → injects skill cue
│   │   └── signatures.json          #   editable trigger table (7 skills)
│   ├── start-phase/                 # ⭐ Quality-gate lifecycle (4 hooks)
│   │   ├── phase-start.md  task-complete.md
│   │   ├── quality-gate.md  phase-complete.md  README.md
│   ├── pm-db/                       # 12 explicit-call tracking scripts
│   │   ├── on-task-start.py  on-task-complete.py
│   │   ├── on-quality-gate.py  on-code-review.py
│   │   ├── on-memory-bank-sync.py  [+7 more]  test_v2_hooks.sh
│   ├── hub/                         # Document Hub session-start (+ planned)
│   ├── memory-bank/                 # session-start.md (context restore)
│   ├── spec/                        # feedback-loop.md (spec-writer loop)
│   ├── shadow-snapshot.sh           # PreToolUse shadow-git checkpoint
│   └── shadow-cleanup.sh            # shadow/* branch pruner
│
├── lib/
│   ├── project_database.py          # ~71KB zero-dep SQLite layer (PM-DB v2)
│   └── generated/prisma/            # Generated TS client (16 models)
│
├── scripts/                         # backup_db.py  restore_db.py  health-check.sh
├── bin/                             # bash-quiet  run-quiet  pm-db-import
├── docs/                            # pm-db-v2-migration, agent-confidence-levels,
│                                    #   TEAM-SKILLS docs, docs/designs/
├── projects.db                      # 🗄️ The PM-DB datastore (WAL, 17 tables)
├── prisma.config.ts  .env           # Prisma config + DATABASE_URL
└── settings.json                    # Hooks, agent-teams flag, permissions, plugins
```

---

## 🎯 Agents

Specialized development personas, one expert per concern. Every agent ships standardized YAML frontmatter (`name`, `model`, `tools`) and a tool-restriction profile. Agents are model-routed for cost: **6 Opus** personas for deep reasoning, **13 Sonnet** personas for implementation/review/docs.

### Code Quality & Refactoring ⭐ NEW
- **refactoring-specialist** — Technical-debt reduction, code modernization, legacy decomposition; preserves behavior via incremental changes and rollback strategies *(Sonnet · Full tools)*
- **debugger-specialist** — Complex issue diagnosis, root-cause analysis, production incident investigation *(Opus · Full tools)*

### Code Review & Quality
- **nextjs-code-reviewer** — Reviews Next.js/TypeScript for security, performance, maintainability, and production reliability before merge *(Sonnet · read-only review)*
- **security-auditor** — OWASP compliance audits across auth, RBAC, input validation, dependency and API security; **audit-only** (no Write/Edit). Loadable modules: `compliance`, `pentest` *(Opus)*

### Development
- **frontend-developer** — Frontend app logic & data: Zustand state, TanStack Query, routing, business logic *(Sonnet · no Bash)*
- **ui-developer** — Visual implementation: TSX, CSS/SCSS/Tailwind, responsive layouts, basic interactions *(Sonnet · no Bash)*
- **express-api-developer** — Express 5 REST endpoints with TypeScript, Prisma, JWT, RFC 7807 errors, Zod validation *(Sonnet · Full tools)*
- **nextjs-backend-developer** — Backend code inside Next.js: API routes, service & DB integrations *(Sonnet · Full tools)*
- **database-schema-specialist** — Database design, schema migrations, query optimization, data modeling *(Sonnet · Full tools)*
- **devops-infrastructure** — CI/CD pipelines, containerization, deployment automation, infrastructure as code *(Sonnet · Full tools)*
- **mastra-core-developer** — Mastra implementation: DAG workflows, agent lifecycle, tools, BullMQ, persistence. Loadable modules: `mcp`, `workflows` *(Opus · Full tools)*
- **mastra-framework-expert** — First point of contact for Mastra tasks: architecture guidance & skill routing across subsystems *(Opus · read-only advisory)*

### API Design
- **api-designer** — Contract-first, **design-only**: OpenAPI specs, three-tier (route → service → external) architecture, TypeScript DTOs before implementation *(Sonnet · read-only — no Write/Edit/Bash)*

### Testing & QA
- **nextjs-qa-developer** — Reads Gherkin features to write unit/integration/E2E tests for Next.js, targeting 90%+ coverage *(Sonnet · Full tools)*
- **accessibility-specialist** — WCAG 2.1 AA/AAA, ARIA, semantic HTML, focus management; axe / WAVE / Lighthouse / Pa11y; NVDA / JAWS / VoiceOver *(Sonnet · Write/Edit, no Bash)*

### Planning & Orchestration
- **strategic-planner** — Architectural plans, implementation strategies, phased breakdowns for complex features *(Opus · read-only planning)*
- **team-lead** — Coordinates multi-agent teams for parallel workstreams; orchestrates planning → spec → implementation *(Opus · orchestration)*
- **spec-writer** — Produces FRD, FRS, GS (Gherkin), TR documents plus an actionable task list before development *(Sonnet · Write, no Edit/Bash)*

### Documentation
- **technical-writer** — User-facing docs: API references, READMEs, tutorials, changelogs. Never writes implementation code. Loadable module: `style` *(Sonnet · read-only, docs only)*

**Total:** 19 specialized agent personas + 5 loadable modules
**Model routing:** 6 Opus (debugger-specialist, mastra-core-developer, mastra-framework-expert, security-auditor, strategic-planner, team-lead) · 13 Sonnet
**Self-checking:** Agents use confidence levels (🟢🟡🔴) with explicit STOP/escalation criteria
**Location:** `/home/mark/.claude/agents/`
**Reference:** `/home/mark/.claude/docs/agent-confidence-levels.md` — confidence-level guide

---

## 🔧 Skills

45 composable workflows (across 46 directories — `start-phase/` is a scripts-only helper without a `SKILL.md`). Every skill is a `/slash-command`. Skills are grouped by system below; **every skill is listed**.

---

### 🧠 Reasoning & Metacognitive Skills (8 skills) ⭐ NEW

**Mark's working grammar.** Procedural-judgment skills that encode *how* to plan, debug, verify, delegate, and respond to steering — invoked by terse signals rather than a build command. Because they undertrigger on their own, they are surfaced automatically by the `reasoning-skills` UserPromptSubmit cue hook (see Hooks).

- `/research-gated-build-plan` — Front-loaded planning discipline: inventory what exists, scope the gap against a concrete target, persist the approach as an artifact, and bake quality bars + phase gates *before* any code is written; decides **whether and how** to enter the execution skills.
- `/diagnose-from-raw-symptom` — Front-to-back debugging from a pasted raw artifact (stack trace, HTTP 500/403, console/Prisma error, screenshot): extract the trigger, probe whether the plumbing even exists, localize good-vs-broken, drive to a durable root cause *before* any fix.
- `/prove-it-live-before-done` — Treat every *done / fixed / passing* claim as **unproven** until the real artifact is exercised end-to-end: drive the live URL/UI/API, confirm the deployed revision, verify the side-effect fired, then name the residual defect with expected-vs-actual.
- `/fleet-dispatch-and-watch` — The dispatch → snapshot → poll → escalate → checkpoint loop for fanning mechanical work across a machine fleet and monitoring long-running/background/remote agents with trustworthy liveness proxies and hard escalation thresholds.
- `/steer-and-correct-the-agent` — Mid-flight interpreter of terse steering grammar (greenlights, autonomy grants, hard overrides, re-anchoring, method constraints) — encodes when bounded autonomy is granted vs when a human checkpoint is required.
- `/enumerated-menu-pick-and-sweep` — Structure consequential choices as a numbered/lettered menu so a bare one-token reply counts as a full selection; correctly resolve terse picks, riders, ranged scope-cuts, and multi-item sweeps.
- `/reference-as-executable-spec` — When a concrete reference is named ("build it like editor.js", "same as X") instead of behavior, go observe the real thing, extract its behavior, and treat **that** as the acceptance bar.
- `/scope-question-and-delegate` — Triage-then-delegate for ambiguity and the ~200k context cliff: stop only on *real* ambiguity or context cost (not a hard gate), ask only the **decisive** questions, budget the window, and hand each worker a minimal scoped snapshot (goal/inputs/constraints/acceptance) via Workflow/teams/fleet so the orchestrator plans and synthesizes without accumulating execution detail.

**Location:** `/home/mark/.claude/skills/<slug>/`
**Cue table:** `/home/mark/.claude/hooks/reasoning-skills/signatures.json`

---

### 🎯 Feature Workflow Orchestration (2 skills)

End-to-end feature delivery that chains planning, review, tracking, and execution with human checkpoints.

```bash
/feature-new "feature description"        # spec-plan → spec-review → start-phase-plan → pm-db → start-phase-execute
/feature-continue ./job-queue/feat/task-list.md   # Resume interrupted work from task-list.md
```

- `/feature-new` — Complete new-feature workflow orchestrating spec → plan → execute into one flow with **two human approval checkpoints** and PM-DB tracking.
- `/feature-continue` — Resume interrupted feature work from an existing `task-list.md`, with PM-DB detecting the last completed task.

**Features:**
- ✅ One-command feature development with full automation
- ✅ Two human approval checkpoints (spec, then plan)
- ✅ PM-DB tracking integration (separate Phase Run ID per feature)
- ✅ Session resilience (resume after interruptions)

**Location:** `/home/mark/.claude/skills/feature-new/`, `/home/mark/.claude/skills/feature-continue/`

---

### 📋 Spec — Planning & Review (2 skills)

Pre-build specification authoring and critique that feeds the execution pipeline.

```bash
/spec-plan "feature description"   # Pre-planning & research, scope-aware tiered output
/spec-review                       # Validate, critique, and iterate on the generated spec
```

- `/spec-plan` — Pre-planning and research for feature specifications with scope-aware tiered output.
- `/spec-review` — Validate, critique, and iterate on generated specifications, collecting user feedback.

**Location:** `/home/mark/.claude/skills/spec-plan/`, `/home/mark/.claude/skills/spec-review/`

---

### 🚀 Start-Phase Execution (3 skills) ⭐ FLAGSHIP

Structured task-list execution with quality gates, parallel waves, and PM-DB tracking — solo or multi-agent.

```bash
/start-phase-plan ./job-queue/feat/task-list.md           # Mode 1: strategic planning + human approval
/start-phase-execute ./job-queue/feat/task-list.md         # Mode 2: structured execution with quality gates
/start-phase-execute-team ./job-queue/feat/task-list.md    # Parallel execution across multi-agent teams
```

- `/start-phase-plan` — **Mode 1:** strategic planning of a task list (parallelism, complexity, agent delegation) with **human approval before execution**.
- `/start-phase-execute` — **Mode 2:** structured task execution with quality gates, parallel waves, and PM-DB tracking.
- `/start-phase-execute-team` — Parallel task execution across multi-agent teams with quality gates.

**Quality Enforcement (automatic via hooks):**
- ✅ Lint check (hard block) between every task
- ✅ Build check (hard block) between every task
- ✅ Per-task AI code review (missing review hard-blocks)
- ✅ Mandatory task-update doc per task
- ✅ Git commit **only after** all gates pass

**Python tools (zero dependencies):** `quality_gate.py`, `task_validator.py`, `validate_phase.py`, `sloc_tracker.py`
**Location:** `/home/mark/.claude/skills/start-phase-execute/`
**Tools & helper dir:** `/home/mark/.claude/skills/start-phase-plan/scripts/`

---

### 🗄️ Project Management Database (1 skill)

Central tracking store for specs, phases, tasks, and execution runs powering the feature/start-phase workflows.

```bash
/pm-db init        # Bootstrap schema into ~/.claude/projects.db
/pm-db import      # Ingest /spec-plan output into projects/phases/tasks
/pm-db dashboard   # Status dashboard / progress report
```

- `/pm-db` — Project-management database for tracking specs, phases, tasks, and execution runs; provides status dashboards and spec import.

**Backed by:** `lib/project_database.py` (~71KB, zero-dep SQLite layer, PM-DB v2) and CLI scripts in `skills/pm-db/scripts/` (`init_db`, `migrate`, `import_specs`, `import_phases`, `generate_report`, `export_to_memory_bank`).
**Datastore:** `/home/mark/.claude/projects.db` (WAL mode, foreign keys ON, **17 tables**)

---

### 🧠 Memory Bank (4 skills)

Six-file persistent project memory for cross-session continuity (`projectbrief`, `productContext`, `techContext`, `systemPatterns`, `activeContext`, `progress`).

```bash
/memory-bank-initialize    # Bootstrap the 6 core files with templates
/memory-bank-read          # Validate + read all 6 files, summarize with staleness warnings
/memory-bank-sync          # Fast sync: activeContext.md + progress.md only
/memory-bank-update        # Comprehensive review/update of all 6 files
```

- `/memory-bank-initialize` — Bootstrap a new project's Memory Bank.
- `/memory-bank-read` — Quick overview of Memory Bank state with staleness warnings.
- `/memory-bank-sync` — Fast lightweight sync of `activeContext.md` + `progress.md` for post-task saves.
- `/memory-bank-update` — Comprehensive review and update of all 6 files after significant work.

**Auto-restore:** `hooks/memory-bank/session-start.md` validates and reads the bank at session start (~3s, silent if absent).
**Location:** `/home/mark/.claude/skills/memory-bank-*/`

---

### 📚 Document Hub (4 skills)

The `cline-docs` documentation lifecycle (four core files: `systemArchitecture.md`, `keyPairResponsibility.md`, `glossary.md`, `techStack.md`).

```bash
/document-hub-initialize    # Bootstrap the 4 core docs from codebase analysis
/document-hub-read          # Read & summarize current doc state for onboarding
/document-hub-analyze       # Read-only audit of code-vs-docs drift
/document-hub-update        # Sync docs to recent code changes with drift detection
```

- `/document-hub-initialize` — Bootstrap a project's documentation hub from codebase analysis.
- `/document-hub-read` — Read and summarize current hub state for quick onboarding.
- `/document-hub-analyze` — **Read-only** audit of codebase-vs-docs alignment (drift, undocumented code, missing glossary terms).
- `/document-hub-update` — Comprehensive review and update, syncing docs to recent code changes.

**Auto-load:** `hooks/hub/document-hub-session-start.md` silently reads & validates the hub at session start (~2s).
**Location:** `/home/mark/.claude/skills/document-hub-*/`

---

### 📚 Documentation Bootstrap (1 skill)

```bash
/documentation-start    # Initialize BOTH Memory Bank and Document Hub
```

- `/documentation-start` — One-shot initializer that stands up both the Memory Bank and the Document Hub for a project, if not already set up.

---

### 🔍 Code Quality Assessment (3 skills)

Automated static analysis of a codebase for architecture, security, and duplication issues.

```bash
/architecture-quality-assess   # Architecture analysis: anti-patterns & improvement opportunities
/security-quality-assess        # OWASP Top 10, secrets, injection, known CVEs
/code-duplication               # Exact / structural / pattern-level duplicate detection
```

- `/architecture-quality-assess` — Architecture analysis identifying quality issues and anti-patterns; provides shared `BaseParser` / `BaseAnalyzer` patterns reused by the security skill.
- `/security-quality-assess` — Security scanning of Python/JS/TS for OWASP Top 10, hardcoded secrets, injection risks, and known CVEs with remediation guidance.
- `/code-duplication` — Deep duplication analysis detecting exact, structural, and pattern-level duplicates with refactoring suggestions and metrics.

---

### ⚙️ Mastra Framework (11 skills)

Comprehensive development toolkit for the Mastra agent/workflow framework, split by subsystem.

```bash
/mastra-dev          # Top-level toolkit / router
/mastra-planning     # Classify task complexity, design team compositions, route to specialist skills
/mastra-agents       # Agents: tools, memory, networks, processors, guardrails, voice, structured output
/mastra-workflows    # DAG composition, control flow, suspend/resume, HITL, time travel, state, streaming
/mastra-memory       # Storage backends, message history, working/semantic memory, threads
/mastra-rag          # Document processing, chunking, embedding, vector DBs, retrieval, GraphRAG
/mastra-streaming    # Agent/workflow/tool streams, SSE events, AI SDK for React/Next.js
/mastra-mcp-tools    # MCPClient (consume) / MCPServer (expose), tool creation, publishing
/mastra-deploy       # Server adapters, auth, middleware, MastraClient SDK, cloud deployment
/mastra-evals        # Built-in/custom scorers, datasets, experiments, CI integration
/mastra-workspace    # Filesystem providers, sandbox execution, skills system, search/indexing
```

All 11 listed above are present as `skills/mastra-*` directories.

---

### 🔌 Integrations — GitLab & Miro (3 skills)

Skills that drive external platforms.

```bash
/gitlab-maintainer     # Check/diagnose/fix failing CI pipelines; handle MR review via glab
/miro-diagram          # Flowcharts, UML class/sequence, ERDs directly on Miro boards
/miro-infographic      # Multi-element infographics, dashboards, one-pagers on Miro
```

- `/gitlab-maintainer` — Maintainer-level GitLab Enterprise work: diagnose & autonomously fix failing CI (build/test/lint), push the fix, wait for green; handle MR code review (respond, approve, request changes) via `glab`.
- `/miro-diagram` — Professional diagrams (flowcharts, UML class/sequence, ERDs) directly on Miro boards via the Miro MCP.
- `/miro-infographic` — Multi-element infographics, dashboards, and one-pagers (diagrams + text + tables + metrics) composed into cohesive Miro layouts.

---

### 🛠️ Skill Tooling & Meta-Build (3 skills)

Tooling for authoring/measuring skills and building larger bespoke systems.

```bash
/skill-creator             # Create, modify, eval, and optimize skills (triggering accuracy + variance)
/new-product               # Deep research & architecture design for a new product
/remote-control-builder    # Build a Claude Code remote-control system via a multi-agent team
```

- `/skill-creator` — Create, modify, and improve skills; run evals, benchmark performance with variance analysis, and optimize descriptions for triggering accuracy.
- `/new-product` — Deep research and architecture design for a new product from docs or a description.
- `/remote-control-builder` — Build a remote-control system for Claude Code using a multi-agent team.

---

## 🪝 Hooks

Automated behaviors triggered by events — **30 hook files across 8 subsystems**. Only one is a genuinely-wired Claude Code event hook (registered in `settings.json`); the rest are markdown-defined workflow hooks and explicit-call utility scripts invoked by skills.

### Reasoning-Skills Cue Hook ⭐ (the wired event hook)

The single registered Claude Code event hook — a **UserPromptSubmit** dispatcher with a 10s timeout.

- **`dispatch.py`** reads the prompt JSON from stdin, lowercases it, and matches against `signatures.json` (an editable trigger table of phrases + case-insensitive regexes per skill). On a match it injects `additionalContext` nudging the model to invoke the matching reasoning skill — because those skills undertrigger.
- **`signatures.json`** currently covers **7 skills**: `research-gated-build-plan`, `diagnose-from-raw-symptom`, `prove-it-live-before-done`, `fleet-dispatch-and-watch`, `steer-and-correct-the-agent`, `enumerated-menu-pick-and-sweep`, `reference-as-executable-spec`.
- ✅ Caps at 3 cues (`MAX_SKILLS`) to avoid nagging
- ✅ Strictly **non-blocking** and **fails OPEN** — any error → exit 0, never alters or blocks the prompt

**Location:** `/home/mark/.claude/hooks/reasoning-skills/`

### Start-Phase Hooks ⭐

Four markdown-defined workflow hooks implementing the `/start-phase` execution lifecycle with mandatory quality enforcement:

- **`phase-start.md`** — Pre-flight validation (task list exists, git clean, deps/quality tools available; blocks on failure in Mode 2)
- **`task-complete.md`** — Bridges each finished task into the quality gate
- **`quality-gate.md`** — Mandatory between-task gate: lint + build (+ optional test), AI code review, completion validation, task-update doc, then git commit **only after all pass** (hard-blocks on lint/build/missing-review/missing-update)
- **`phase-complete.md`** — Closeout: phase-summary, next-phase candidates, SLOC analysis, planning archive, handoff docs

**Location:** `/home/mark/.claude/hooks/start-phase/`

### PM-DB Hook Suite (explicit-call utilities)

12 Python scripts that write execution/tracking records into `projects.db`. **Not** registered Claude Code event hooks and **not** in `settings.json` — skills invoke them directly via stdin/stdout JSON, **failing open** (on error: stderr + exit 0).

`on-job-start`, `on-task-start`, `on-task-complete`, `on-agent-assign`, `on-tool-use`, `on-code-review`, `on-quality-gate`, `on-phase-run-start`, `on-phase-run-complete`, `on-task-run-start`, `on-task-run-complete`, `on-memory-bank-sync` (bridges PM-DB → Memory Bank with per-project 5-min debouncing). Plus `test_v2_hooks.sh`.

**Location:** `/home/mark/.claude/hooks/pm-db/`

### Brain Session-Start Hooks

- **`hooks/memory-bank/session-start.md`** — On conversation start, validates via `validate_memorybank.py` and reads the 6 Memory Bank files in hierarchical order (~3s, skips silently if absent).
- **`hooks/hub/document-hub-session-start.md`** — Silently reads & validates the Document Hub at session start (~2s). (Three further hub hooks — `document-hub-task-complete.md`, `document-hub-file-watch.md`, and a module-tracker — are **planned-only** stubs deferred to avoid notification fatigue.)

### Spec Feedback-Loop Hook

- **`hooks/spec/feedback-loop.md`** — On `spec-writer` completion, auto-runs `validate_spec.py` + `critique_plan.py` (~5s), presents a completeness + quality score, then collects approve-vs-iterate feedback (iterate re-runs the agent). Degrades gracefully; never blocks.

### Shadow-Git Snapshot Hooks

- **`shadow-snapshot.sh`** — Designed as a PreToolUse hook: for Write/Edit tools, creates a zero-cost `shadow/<epoch>_<timestamp>` branch at current HEAD for instant rollback, then GC's shadow branches older than 24h.
- **`shadow-cleanup.sh`** — Standalone pruner that deletes `shadow/*` branches older than 86400s.

> ⚠️ Both shadow scripts currently hardcode `/home/artsmc/.claude` and are **not** registered in `settings.json` — re-point them to this machine before relying on them.

### Notification (sound) Hooks

Registered in `settings.json`: on **Stop** and **TaskCompleted**, `sounds/done.wav` plays via `ffplay` for audible completion feedback. `health-check.sh` treats `sounds/done.wav` as a foundation check.

---

## 🛠️ Tools & Scripts

Zero-dependency Python utilities (stdlib only) plus shell helpers.

### Start-Phase Tools (`skills/start-phase-plan/scripts/`)

**`quality_gate.py`** — Quality enforcement
```bash
python quality_gate.py /path/to/project [--test]
```
Runs lint and build (+ optional tests), returns JSON pass/fail.

**`task_validator.py`** — Task completion validation
```bash
python task_validator.py /path/to/project task-name
```
Validates task-update + code-review files exist, checklist complete, git commit present.

**`validate_phase.py`** — Phase structure validation. **`sloc_tracker.py`** — baseline / update / final SLOC reports.

### PM-DB Tools

- **`lib/project_database.py`** — ~71KB zero-dependency `ProjectDatabase` SQLite layer (PM-DB v2: planning split from execution; parameterized queries; context-managed transactions).
- **`skills/pm-db/scripts/`** — `init_db.py`, `migrate.py`, `import_specs.py`, `import_phases.py`, `generate_report.py`, `export_to_memory_bank.py`.
- **`lib/generated/prisma/`** — generated TypeScript Prisma client (16 model files) for typed read access to the same `projects.db`.

### Database Maintenance (`scripts/`)

```bash
python scripts/backup_db.py                # Timestamped copy → ~/.claude/backups/
python scripts/restore_db.py <backup>      # Restore w/ auto-backup + integrity + schema checks
bash   scripts/health-check.sh             # Validate the whole foundation (non-zero on any failure)
```

`health-check.sh` asserts: `projects.db` exists/non-empty; required tables present; **no phantom `pm.db`**; Python can import `ProjectDatabase`; `sounds/done.wav` exists; all `pm-db/on-*.py` are executable; `memory-bank/` has ≥4 `.md` files.

### Quiet-Wrapper Bin Utilities (`bin/`)

- **`bash-quiet`** — filters the `setlocale: LC_ALL` warning from a wrapped command's stderr
- **`run-quiet`** — Python wrapper that passes stdout through and strips the same warning, preserving exit code
- **`pm-db-import`** — locale-safe entrypoint that execs `import_phases.py`

**Dependencies:** Zero (Python stdlib only).

---

## 📦 System Overview

### Production-Ready Systems

| System | Status | Skills | Hooks | Tools | Documentation |
|--------|--------|--------|-------|-------|---------------|
| **reasoning-skills** | ✅ v1.0 | 8 | 1 (UserPromptSubmit) | `dispatch.py` + `signatures.json` | `hooks/reasoning-skills/` |
| **feature-orchestration** | ✅ v1.0 | 2 | 0 | 0 | Complete |
| **start-phase** | ✅ v2.0 | 3 | 4 | 4 | `skills/start-phase-plan/scripts/README.md` |
| **pm-db** | ✅ v2.0 | 1 | 12 | `project_database.py` + 6 scripts + Prisma | Complete |
| **memory-bank** | ✅ v1.0 | 4 | 1 (session-start) | `validate_memorybank.py` | Complete |
| **document-hub** | ✅ v1.0 | 4 | 1 (+3 planned) | hub scripts | Complete |
| **spec** | ✅ v1.0 | 2 | 1 (feedback-loop) | `validate_spec.py`, `critique_plan.py` | Complete |
| **code-quality** | ✅ v1.0 | 3 | 0 | analyzers | Complete |
| **mastra** | ✅ v1.0 | 11 | 0 | 0 | Per-skill guides |
| **integrations** | ✅ v1.0 | 3 | 0 | 0 | Per-skill guides |
| **meta-build** | ✅ v1.0 | 3 | 0 | skill-creator evals | Complete |

### Total Implementation

- ✅ **45 skills** across 46 skill directories (`start-phase/` is a scripts-only helper without `SKILL.md`)
- ✅ **19 agent personas** + **5 loadable modules** (6 Opus / 13 Sonnet routing)
- ✅ **30 hook files** across 8 subsystems (1 wired event hook + 4 quality-gate + 12 pm-db + Brain/spec/shadow)
- ✅ **17-table SQLite PM-DB** (`projects.db`, WAL mode) with Python + generated-Prisma access layers
- ✅ **~71KB** `ProjectDatabase` layer + zero-dependency quality tools
- ✅ **Zero external dependencies** (Python stdlib only)

### Skill Naming Convention

Skills follow the pattern `/{system}-{action}` (a few take space-separated arguments):
- `/feature-new`, `/feature-continue` (orchestration)
- `/spec-plan`, `/spec-review` (spec)
- `/start-phase-plan`, `/start-phase-execute`, `/start-phase-execute-team` (execution)
- `/pm-db init`, `/pm-db import`, `/pm-db dashboard` (database)
- `/memory-bank-*`, `/document-hub-*`, `/documentation-start` (Brain)
- `/mastra-*` (framework), `/miro-*`, `/gitlab-maintainer` (integrations)
- Reasoning skills carry descriptive verb-phrase slugs (`/diagnose-from-raw-symptom`, `/prove-it-live-before-done`, …)

---

## 🚀 Quick Start

### Beginner (Orchestrated Workflow)

**The Easy Way (Recommended) — complete feature development in one command:**

```bash
# One-time setup
/documentation-start          # Initialize Memory Bank + Document Hub
/pm-db init                   # Bootstrap projects.db

# Develop features
/feature-new "add user login"
/feature-new "integrate payments"

# Resume if interrupted
/feature-continue ./job-queue/feature-login/task-list.md
```

**That's it!** The orchestration skill handles spec → review → plan → tracking → execution automatically, pausing at two human checkpoints.

---

### Advanced (Manual Control)

**For experienced users who want fine-grained control over every step:**

```bash
# 1. Initialize
/documentation-start
/pm-db init

# 2. Plan feature
/spec-plan "advanced feature"
/spec-review

# 3. Plan & execute the phase
/start-phase-plan ./job-queue/feature-name/task-list.md
/pm-db import
/start-phase-execute ./job-queue/feature-name/task-list.md

# 4. Update docs
/memory-bank-update
/document-hub-update
```

See **Beginner Quickstart** and **Advanced Workflows** below for more patterns.

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
- Document Hub (4 `cline-docs` files documenting the codebase)
- Auto-initializes only if missing

**Step 2: Initialize PM-DB**

```bash
/pm-db init
```

This creates:
- The project database at `~/.claude/projects.db` (WAL mode, 17 tables)
- Phase-run and task-execution tracking

**Step 3: Verify the foundation**

```bash
bash ~/.claude/scripts/health-check.sh
```

**Done!** Your project is now ready for feature development.

**What you'll see:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 .claude Foundation Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ projects.db exists and is non-empty
✅ Required tables present (projects, phases, tasks, phase_runs)
✅ No phantom pm.db
✅ ProjectDatabase imports cleanly
✅ sounds/done.wav present (Stop hook)
✅ pm-db/on-*.py hooks executable
✅ memory-bank/ present (≥4 .md files)

Foundation: HEALTHY
```

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
4. ✅ Creates a strategic execution plan with tasks
5. ⏸️ **Waits for your approval** (checkpoint 2)
6. ✅ Imports to PM-DB for tracking
7. ✅ Executes with quality gates between every task
8. ✅ AI code review after each task
9. ✅ Git commit only after quality passes

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

👤 CHECKPOINT 1: Review specifications
Options: approve / revise / cancel
> approve

Step 3/6: Creating strategic plan...
✅ 8 tasks identified
✅ 2 parallel waves detected

👤 CHECKPOINT 2: Approve execution plan?
Options: approve / revise / cancel
> approve

Step 4/6: Importing to PM-DB...
✅ Phase Run created

Step 5/6: Executing tasks with quality gates...
[Progress bar shows 0/8 tasks complete]

Task 1: Setup auth API endpoint
  Agent: nextjs-backend-developer
  ✅ Code written
  ✅ Quality gate passed (lint: 0 errors, build: success)
  ✅ Code review passed
  ✅ Git commit created

Step 6/6: Phase complete!
✅ 8/8 tasks completed
✅ All quality gates passed
✅ 8 git commits created
```

---

### Resume Interrupted Work

If your session drops or you need to pause:

```bash
/feature-continue ./job-queue/feature-login/task-list.md
```

**What happens:**
- ✅ Reads PM-DB to find the last completed task
- ✅ Shows progress ("Task 5/8 complete")
- ✅ Resumes from the next task
- ✅ Maintains quality gates for remaining tasks

**Example output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Resume Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: User Authentication MVP
Progress: [██████████░░░░░░░░░░] 5/8 tasks (62%)

Completed:
✅ Task 1: Setup auth API
✅ Task 2: Create login UI
✅ Task 3: Connect API to UI
✅ Task 4: Add JWT tokens
✅ Task 5: Create user schema

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

**Shows** active phase runs, completed phases, task counts, and per-phase status pulled straight from `projects.db`.

---

### Update Documentation

After completing features:

```bash
/memory-bank-sync        # Quick update (activeContext + progress only)
/document-hub-update     # Full documentation sync
```

**When to use each:**
- `/memory-bank-sync` — after each task or small change (fast, 2 files)
- `/memory-bank-update` — after completing a phase (comprehensive, 6 files)
- `/document-hub-update` — after architectural changes

---

### Complete Beginner Workflow

```bash
# === ONE-TIME SETUP ===
/documentation-start                  # Memory Bank + Document Hub
/pm-db init                           # Project database

# === FOR EACH FEATURE ===
/feature-new "add user login with OAuth"
# [Review spec at checkpoint 1] → approve
# [Review plan at checkpoint 2] → approve
# [System executes automatically with quality gates]

# === IF INTERRUPTED ===
/feature-continue ./job-queue/feature-auth/task-list.md

# === AFTER FEATURE COMPLETE ===
/memory-bank-sync                     # Update knowledge base
/pm-db dashboard                      # View metrics
```

**That's it!** Four orchestration skills handle everything:
1. `/documentation-start` — setup (once)
2. `/feature-new` — build features (many times)
3. `/feature-continue` — resume work (when needed)
4. `/pm-db dashboard` — track progress (any time)

---

### Common Beginner Questions

**Q: Do I have to remember to invoke the reasoning skills?**
- No. The `reasoning-skills` UserPromptSubmit hook watches your prompt and silently cues the matching skill (e.g. a pasted stack trace cues `/diagnose-from-raw-symptom`).
- It caps at 3 cues and fails open — it never blocks or rewrites your prompt.
- Edit `hooks/reasoning-skills/signatures.json` to tune the triggers.

**Q: Can I cancel during execution?**
- Yes — Ctrl+C to stop. Progress is saved in PM-DB.
- Use `/feature-continue` to resume from the last completed task.

**Q: What if quality gates fail?**
- The quality-gate hook hard-blocks on lint/build failures, a missing code review, or a missing task-update doc.
- No git commit is created until every gate passes.

**Q: How do I see what changed?**
- Git history: `git log --oneline`
- PM-DB: `/pm-db dashboard`
- Phase summary written by `phase-complete.md` at phase closeout

**Q: How is my work recovered if an edit goes wrong?**
- `shadow-snapshot.sh` is designed as a PreToolUse hook that branches `shadow/<epoch>_<ts>` before Write/Edit. ⚠️ It is not wired by default and hardcodes a stale home path — re-point and register it first.
- The Memory Bank + Document Hub session-start hooks restore project context automatically each session.

---

## 📖 Documentation

Each system ships its own documentation:

- **start-phase tools:** `/home/mark/.claude/skills/start-phase-plan/scripts/README.md`
- **start-phase hooks:** `/home/mark/.claude/hooks/start-phase/README.md`
- **pm-db hooks:** `/home/mark/.claude/hooks/pm-db/README.md`
- **PM-DB v2 migration:** `/home/mark/.claude/docs/pm-db-v2-migration-summary.md`
- **Agent confidence levels:** `/home/mark/.claude/docs/agent-confidence-levels.md`
- **Multi-agent teams:** `/home/mark/.claude/docs/TEAM-SKILLS-README.md`, `team-skills-implementation-guide.md`, `teams-in-action-example.md`

---

## 🎓 Best Practices

### Phase Management
- ✅ **Optimal phase size:** 5–7 tasks
- ✅ **Beyond ~10 tasks:** split into multiple phases
- ✅ **Always plan first:** run `/start-phase-plan` and get approval before `/start-phase-execute`
- ✅ **Trust the quality gates:** they prevent shipping broken code

### Reasoning & Verification
- ✅ **Plan before code:** let `/research-gated-build-plan` inventory what exists and scope the gap first
- ✅ **Debug from the artifact:** paste the raw error; `/diagnose-from-raw-symptom` finds root cause before any fix
- ✅ **Never trust "done":** `/prove-it-live-before-done` exercises the real URL/UI/API and names the residual defect
- ✅ **Offer menus, not open questions:** `/enumerated-menu-pick-and-sweep` makes a one-token reply a full selection

### Documentation
- ✅ **Initialize first:** `/documentation-start` for new projects
- ✅ **Keep docs current:** `/document-hub-update` after changes
- ✅ **Audit drift:** `/document-hub-analyze` before deciding what to update

### Knowledge Management
- ✅ **Read before coding:** `/memory-bank-read` for context (the session-start hook does this for you)
- ✅ **Sync after tasks:** `/memory-bank-sync` (2 files, fast)
- ✅ **Full refresh after milestones:** `/memory-bank-update` (all 6 files)

### Specifications
- ✅ **Plan before implementing:** `/spec-plan` first
- ✅ **Critique before building:** `/spec-review` validates structure, completeness, feasibility

### Foundation Hygiene
- ✅ **Run `health-check.sh`** before trusting the foundation
- ✅ **Back up before risky migrations:** `python scripts/backup_db.py`
- ✅ **Re-point shadow hooks** off the stale `/home/artsmc/` path before relying on rollback

---

## 🎯 Advanced Workflows

For experienced users who want fine-grained control over every step.

### Custom Feature Workflow

Skip orchestration and drive each skill yourself:

```bash
# === PHASE 1: SPECIFICATION ===
/spec-plan "real-time notification system with WebSocket support"
# Creates: FRD, FRS, GS, TR documents under job-queue/<feature>/docs/

/spec-review
# spec/feedback-loop.md auto-runs validate_spec.py + critique_plan.py,
# shows a completeness + quality score, collects approve-vs-iterate feedback

# === PHASE 2: STRATEGIC PLANNING ===
/start-phase-plan ./job-queue/feature-notifications/task-list.md
# - Analyzes task complexity
# - Identifies parallel waves
# - Proposes incremental build strategy
# - Waits for your approval
#
# Options: approve / revise / reject / question
# > approve

# === PHASE 3: PM-DB IMPORT ===
/pm-db import
# Ingests the approved plan into projects/phases/tasks via import_phases.py
# (locale-safe entrypoint: ~/.claude/bin/pm-db-import)

# === PHASE 4: EXECUTION ===
/start-phase-execute ./job-queue/feature-notifications/task-list.md
# Part 1: planning/ directory structure
# Part 2: delegation plan, parallel strategy, system changes
# Part 3: per-task execution (adopt agent persona → write code →
#         quality gate → AI code review → git commit → PM-DB record)
# Part 4/5: task updates + phase closeout (automatic via hooks)

# Multi-agent variant for parallel waves:
/start-phase-execute-team ./job-queue/feature-notifications/task-list.md

# === PHASE 5: DOCUMENTATION ===
/memory-bank-update       # All 6 files
/document-hub-analyze     # Drift detection + recommendations
/document-hub-update      # Apply recommendations
```

**Why use this instead of `/feature-new`?**
- ✅ Pause between phases (plan today, execute days later)
- ✅ Manual PM-DB import control
- ✅ Custom extra instructions per phase
- ✅ Iterate on specs independently before committing to a plan

---

### Parallel Feature Development

Work on multiple features at once with proper isolation:

```bash
# === STRATEGY 1: Concurrent Features (Different Files) ===
/feature-new "add user authentication API"      # backend files
/feature-new "build reusable component library" # frontend files
/feature-new "add analytics tables"             # schema/migrations
# ✅ Safe in parallel — no file conflicts
# ✅ PM-DB tracks each with its own Phase Run ID

# === STRATEGY 2: Sequential Dependencies ===
/spec-plan "design notification API contract"
/spec-review
# Phase 2A (backend) and 2B (frontend) can run in parallel off the contract,
# then Phase 3 integrates end-to-end.

# === STRATEGY 3: Multi-Agent Team Execution ===
/start-phase-execute-team ./job-queue/feature-payment/task-list.md
# team-lead coordinates specialists across parallel waves with quality gates
```

**PM-DB tracks all features independently with separate Phase Run IDs.**

---

### PM-DB Advanced Queries

The store is `~/.claude/projects.db` (17 tables). Query it directly:

```bash
# Active phase runs
sqlite3 ~/.claude/projects.db "SELECT id, phase_id, status FROM phase_runs WHERE status='in-progress';"

# Per-phase task progress
sqlite3 ~/.claude/projects.db <<'EOF'
SELECT
  p.name  AS project,
  ph.name AS phase,
  pr.status,
  COUNT(tr.id) AS total_tasks,
  SUM(CASE WHEN tr.status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks
FROM projects p
JOIN phases ph     ON p.id = ph.project_id
JOIN phase_runs pr ON ph.id = pr.phase_id
LEFT JOIN task_runs tr ON pr.id = tr.phase_run_id
GROUP BY p.name, ph.name, pr.status;
EOF

# Inspect the schema (17 tables)
sqlite3 ~/.claude/projects.db ".tables"
# projects phases phase_plans plan_documents tasks task_dependencies
# task_runs task_updates phase_runs quality_gates code_reviews
# agent_assignments execution_logs run_artifacts phase_metrics
# schema_version sqlite_sequence
```

> Prefer the Python `ProjectDatabase` layer (`lib/project_database.py`) or the generated Prisma client (`lib/generated/prisma/`) for typed, parameterized access in scripts.

---

### Brain Strategies (Memory Bank + Document Hub)

```bash
# Quick sync after tasks (2 files)
/memory-bank-sync

# Deep update after phases (all 6 files)
/memory-bank-update

# Stale detection (read shows staleness warnings)
/memory-bank-read

# Documentation health audit before changing anything
/document-hub-analyze        # read-only drift report
/document-hub-update         # then apply

# Re-bootstrap both Brains for a fresh/severely-stale project
/documentation-start
```

> The Memory Bank and Document Hub session-start hooks restore both Brains automatically each session — these commands are the manual operations on top.

---

### Integration with CI/CD

```bash
#!/bin/bash
# .git/hooks/pre-commit — validate the foundation before committing
bash ~/.claude/scripts/health-check.sh || exit 1

#!/bin/bash
# nightly — back up the PM-DB datastore
python ~/.claude/scripts/backup_db.py   # → ~/.claude/backups/

# GitLab CI maintenance (self-hosted), driven by the skill:
# /gitlab-maintainer  → diagnose & fix failing pipeline, push, wait for green
```

---

## 🏆 Flagship System: start-phase

The **start-phase** system is the most comprehensive and production-ready system in the repo:

- ✅ **3 execution skills** — `/start-phase-plan` (Mode 1), `/start-phase-execute` (Mode 2), `/start-phase-execute-team` (multi-agent)
- ✅ **4 comprehensive lifecycle hooks** — phase-start, task-complete, quality-gate, phase-complete
- ✅ **4 zero-dependency Python tools** — `quality_gate.py`, `task_validator.py`, `validate_phase.py`, `sloc_tracker.py`
- ✅ **Quality gates between every task** — lint + build hard-block, mandatory AI review, mandatory task-update doc
- ✅ **Git workflow** — commits only after quality passes
- ✅ **SLOC tracking** — baseline, updates, final markdown report
- ✅ **PM-DB integration** — every task/review/gate written to `projects.db` via the pm-db hook suite
- ✅ **Parallel execution** — multi-agent team support via `team-lead` coordination

**Recommended phase size:** 5–7 tasks. **Recommended for:** any multi-task development phase requiring quality enforcement and structured workflow.

---

## 📊 Statistics

### Inventory at a Glance

| Metric | Count | Basis |
|--------|-------|-------|
| Skills | **45** (46 dirs) | Dirs with `SKILL.md`; `start-phase/` is scripts-only |
| Agent personas | **19** | `agents/*.md` (excludes `modules/`) |
| Loadable modules | **5** | `agents/modules/*.md` |
| Hook files | **30** | Across 8 subsystems |
| Wired event hooks | **1** | `reasoning-skills` UserPromptSubmit (in `settings.json`) |
| Reasoning skills cued | **8** | `signatures.json` trigger table |
| PM-DB tables | **17** | `projects.db` (WAL, FK ON) |
| External dependencies | **0** | Python stdlib only |

### Model Routing (cost efficiency)

| Tier | Count | Agents | Used for |
|------|-------|--------|----------|
| **Opus** | 6 | debugger-specialist, mastra-core-developer, mastra-framework-expert, security-auditor, strategic-planner, team-lead | Deep reasoning, architecture, security, orchestration |
| **Sonnet** | 13 | the remaining personas | Implementation, review, testing, documentation |

### Tool-Restriction Profiles

| Profile | Example agents | Capability |
|---------|----------------|------------|
| **Read-only / advisory** | api-designer, security-auditor, strategic-planner, mastra-framework-expert, nextjs-code-reviewer, technical-writer | Read/Grep/Glob — no mutation |
| **Write, no shell** | frontend-developer, ui-developer, accessibility-specialist, spec-writer | Write/Edit, no Bash |
| **Full** | express-api-developer, nextjs-backend-developer, database-schema-specialist, devops-infrastructure, debugger-specialist, refactoring-specialist, nextjs-qa-developer, mastra-core-developer | Read/Grep/Glob/Write/Edit/Bash |

### Reasoning-Skills Cue Hook

| Property | Value |
|----------|-------|
| Event | UserPromptSubmit |
| Timeout | 10s |
| Max cues per prompt (`MAX_SKILLS`) | 3 |
| Failure mode | ✅ Fails OPEN (exit 0, never blocks/alters the prompt) |
| Skills covered | 8 (editable in `signatures.json`) |

---

## 🐛 Troubleshooting

### Common Issues

**Q: Skills not showing up in the slash-command list**
- Ensure each skill directory contains a `SKILL.md` (`start-phase/` intentionally has none — it is a tools/scripts helper)
- Check file permissions (should be readable)
- Restart Claude Code if needed

**Q: Reasoning skills never trigger automatically**
- Confirm the `reasoning-skills` UserPromptSubmit hook is registered in `settings.json`
- Inspect / extend the trigger phrases in `hooks/reasoning-skills/signatures.json` (8 skills covered)
- Remember it caps at 3 cues per prompt and fails open — it will never block you

**Q: Quality gates failing**
- Ensure lint/build commands exist in the project's `package.json`
- The `quality-gate.md` hook hard-blocks on lint/build errors, a missing code review, or a missing task-update doc
- See `/home/mark/.claude/hooks/start-phase/README.md`

**Q: `health-check.sh` reports failures**
- It exits non-zero if `projects.db` is missing/empty, required tables are absent, a phantom `pm.db` exists, `ProjectDatabase` won't import, `sounds/done.wav` is missing, a `pm-db/on-*.py` hook isn't executable, or `memory-bank/` lacks ≥4 `.md` files
- Fix the specific failing assertion it prints

**Q: Shadow-git rollback isn't working**
- `shadow-snapshot.sh` / `shadow-cleanup.sh` hardcode `/home/artsmc/.claude` and are **not** registered in `settings.json`
- Re-point the `REPO`/`cd` path to this machine and wire `shadow-snapshot.sh` as a PreToolUse hook before relying on it

### Getting Help

1. **Read the per-system READMEs** — start-phase, pm-db, hub, memory-bank, spec each ship one
2. **Check `docs/`** — migration summary, agent-confidence-levels, team-skills guides
3. **Run `health-check.sh`** — it pinpoints foundation problems fast

---

## 📝 License

Private repository for personal use.

---

## 🔗 Quick Links

- [Start-Phase Tools Guide](skills/start-phase-plan/scripts/README.md) — zero-dependency quality tools
- [Start-Phase Hooks Guide](hooks/start-phase/README.md) — quality-gate lifecycle
- [PM-DB Hooks Guide](hooks/pm-db/README.md) — 12 explicit-call tracking scripts
- [PM-DB v2 Migration](docs/pm-db-v2-migration-summary.md) — planning↔execution split rationale
- [Agent Confidence Levels](docs/agent-confidence-levels.md) — 🟢🟡🔴 self-checking guide
- [Multi-Agent Teams](docs/TEAM-SKILLS-README.md) — team-skills implementation + examples
- [Reasoning-Skills Cue Hook](hooks/reasoning-skills/) — `dispatch.py` + `signatures.json`

---

**Version:** 0.3.0
**Architecture:** Modular Skills, Agents, Hooks & Tools with PM-DB Tracking and Reasoning-Skill Cueing
**Status:** ✅ Production Ready
**Last Updated:** 2026-05-30
**Inventory:** 44 skills · 19 agents (+5 modules) · 30 hook files · 17-table PM-DB · zero dependencies
