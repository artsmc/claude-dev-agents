# Claude Dev Agents — Claude Code Development Environment

**Version:** 0.4.0
**Last Updated:** 2026-07-09
**Architecture:** Modular Skills, Agents, Hooks & Tools with PM-DB Tracking and Reasoning-Skill Cueing

A multi-agent development framework built on the Claude Code CLI. It lives in `~/.claude/` and turns Claude Code into a coordinated team of specialized AI agents — driven by `/skill-name` commands, backed by a SQLite project-tracking database, and guarded by quality gates, session-start context restoration, and a metacognitive reasoning layer that nudges the model to plan, debug, verify, and self-correct.

---

## 🏗️ Architecture Overview

This repository implements a **modular, skill-based architecture** with five cooperating layers:

- ✅ **Agents** — 19 specialized development personas (plus 5 loadable modules) with standardized YAML frontmatter (`name` / `model` / `tools`)
- ✅ **Skills** — 43 composable `/slash-command` workflows (43 `SKILL.md` files — `start-phase/` and eval workspace dirs have none)
- ✅ **Hooks** — 30 hook files across 8 subsystems, from quality gates to audible Stop/Notification feedback and a PreToolUse shadow-snapshot
- ✅ **Tools** — Zero-dependency Python utilities (PM-DB layer, quality enforcement, backup/restore) — Python stdlib only
- ✅ **PM-DB** — A 17-table SQLite project database (`projects.db`) tracking specs, phases, tasks, and execution runs, with both a Python and a generated Prisma access layer

**Design pillars:**

- ✅ **Specialized personas** — each agent is a focused expert (API design, debugging, security audit, refactoring, testing, docs) rather than a generalist
- ✅ **Cost-efficient model routing** — Opus for deep reasoning (architecture, security, debugging, orchestration); Sonnet for implementation, review, and documentation
- ✅ **Tool-restriction profiles** — Read-only (advisory/review), Write-no-shell (UI/frontend), and Full (implementation) profiles scope what each agent can touch
- ✅ **Modularized agents** — large agents split into a small core plus on-demand loadable modules (security-auditor, mastra-core-developer, technical-writer)
- ✅ **Metacognitive reasoning layer** — 8 procedural-judgment skills that encode *how* to plan, debug, verify, delegate, and respond to steering, surfaced via their always-in-context frontmatter descriptions
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
│   ├── refactoring-specialist.md    # Code modernization
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
├── archive/                         # Retired & merged skill content (all preserved)
│   ├── skills/                      # 5 archived SKILL.md files
│   │   ├── remote-control-builder/  # Retired one-off builder (was a live skill)
│   │   ├── memory-bank-sync/        # Merged → memory-bank-update --quick
│   │   ├── feature-continue/        # Merged → feature-new --continue
│   │   ├── start-phase-execute-team/# Merged → start-phase-execute --team
│   │   └── documentation-start/     # Folded → memory-bank-initialize + document-hub-initialize
│   └── command-stubs/               # 11 stale eval-generated stubs (removed from skill routing)
│
├── skills/                          # 43 SKILL.md files; start-phase/ + eval workspace dirs have none
│   ├── research-gated-build-plan/   # 🧠 Reasoning skill
│   ├── diagnose-from-raw-symptom/   # 🧠 Reasoning skill
│   ├── prove-it-live-before-done/   # 🧠 Reasoning skill
│   ├── fleet-dispatch-and-watch/    # 🧠 Reasoning skill
│   ├── steer-and-correct-the-agent/ # 🧠 Reasoning skill
│   ├── enumerated-menu-pick-and-sweep/  # 🧠 Reasoning skill
│   ├── reference-as-executable-spec/    # 🧠 Reasoning skill
│   ├── scope-question-and-delegate/     # 🧠 Reasoning skill
│   │
│   ├── feature-new/                 # 🎯 End-to-end feature orchestration (--continue resumes)
│   ├── spec-plan/  spec-review/     # 📋 Spec authoring + critique
│   ├── start-phase/                 # 🚀 cache_wrapper.py helper (no SKILL.md)
│   ├── start-phase-plan/            # 🚀 Mode 1: strategic planning ⭐ FLAGSHIP
│   │   └── scripts/                 #   quality_gate.py, task_validator.py,
│   │                                #   validate_phase.py, sloc_tracker.py
│   ├── start-phase-execute/         # 🚀 Mode 2: execution (--team for multi-agent) ⭐
│   ├── pm-db/                       # 🗄️ Project-tracking DB skill
│   │   └── scripts/                 #   init_db, migrate, import_specs,
│   │                                #   import_phases, generate_report,
│   │                                #   export_to_memory_bank
│   ├── memory-bank-*/               # 🧠 3 Memory Bank skills (initialize, read, update)
│   │                                #   update --quick for fast 2-file sync
│   ├── document-hub-*/              # 📚 4 Document Hub skills (cline-docs)
│   ├── architecture-quality-assess/ # 🔍 Code quality assessment
│   ├── security-quality-assess/     # 🔍 OWASP / secrets / CVE scan
│   ├── code-duplication/            # 🔍 Exact/structural duplicate finder
│   ├── mastra-*/                    # ⚙️ 11 Mastra framework skills
│   ├── gitlab-maintainer/           # 🔌 GitLab CI + MR maintenance
│   ├── miro-diagram/  miro-infographic/  # 🔌 Miro visual creation
│   ├── jira-reader/  jira-writer/   # 🔌 Jira integration (MCP, VPN-only)
│   ├── skill-creator/               # 🛠️ Author/measure/optimize skills
│   ├── new-product/                 # 🛠️ Deep product research + design
│   └── headroom-context-compression/# 🛠️ MCP-backed context compression
│
├── hooks/                           # 30 hook files across 8 subsystems
│   ├── reasoning-skills/            # Description-based cue (dispatch.py NOT in settings.json)
│   │   ├── dispatch.py              #   exists; wires as UserPromptSubmit if added to settings.json
│   │   └── signatures.json          #   editable trigger table (8 skills)
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
│   ├── shadow-snapshot.sh           # PreToolUse shadow-git checkpoint (registered in settings.json)
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

### Code Quality & Refactoring
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

43 composable workflows (43 `SKILL.md` files — `start-phase/` and eval workspace dirs have none). Every skill is a `/slash-command`. Skills are grouped by system below; **every skill is listed**.

---

### 🧠 Reasoning & Metacognitive Skills (8 skills)

**Mark's working grammar.** Procedural-judgment skills that encode *how* to plan, debug, verify, delegate, and respond to steering — invoked by terse signals rather than a build command. They surface via their always-in-context frontmatter descriptions; `hooks/reasoning-skills/dispatch.py` exists for optional wiring as a UserPromptSubmit nudge hook (see Hooks).

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

### 🎯 Feature Workflow Orchestration (1 skill)

End-to-end feature delivery that chains planning, review, tracking, and execution with human checkpoints.

```bash
/feature-new "feature description"                                   # Full new-feature workflow
/feature-new --continue ./job-queue/feat/task-list.md                # Resume interrupted work (formerly /feature-continue)
```

- `/feature-new` — Complete new-feature workflow orchestrating spec → plan → execute into one flow with **two human approval checkpoints** and PM-DB tracking. Pass `--continue` to resume from an existing `task-list.md`, with PM-DB detecting the last completed task (formerly `/feature-continue`).

**Features:**
- ✅ One-command feature development with full automation
- ✅ Two human approval checkpoints (spec, then plan)
- ✅ PM-DB tracking integration (separate Phase Run ID per feature)
- ✅ Session resilience — `--continue` resumes from last completed task

**Location:** `/home/mark/.claude/skills/feature-new/`

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

### 🚀 Start-Phase Execution (2 skills) ⭐ FLAGSHIP

Structured task-list execution with quality gates, parallel waves, and PM-DB tracking — solo or multi-agent.

```bash
/start-phase-plan ./job-queue/feat/task-list.md            # Mode 1: strategic planning + human approval
/start-phase-execute ./job-queue/feat/task-list.md          # Mode 2: structured execution with quality gates
/start-phase-execute --team ./job-queue/feat/task-list.md   # Multi-agent parallel execution (formerly /start-phase-execute-team)
```

- `/start-phase-plan` — **Mode 1:** strategic planning of a task list (parallelism, complexity, agent delegation) with **human approval before execution**.
- `/start-phase-execute` — **Mode 2:** structured task execution with quality gates, parallel waves, and PM-DB tracking. Pass `--team` for multi-agent parallel execution (formerly `/start-phase-execute-team`).

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

### 🧠 Memory Bank (3 skills)

Six-file persistent project memory for cross-session continuity (`projectbrief`, `productContext`, `techContext`, `systemPatterns`, `activeContext`, `progress`).

```bash
/memory-bank-initialize    # Bootstrap the 6 core files; cues Document Hub init if neither Brain exists
/memory-bank-read          # Validate + read all 6 files, summarize with staleness warnings
/memory-bank-update        # Comprehensive review/update of all 6 files
/memory-bank-update --quick  # Fast 2-file sync (activeContext + progress only) — formerly /memory-bank-sync
```

- `/memory-bank-initialize` — Bootstrap a new project's Memory Bank. Also cues Document Hub initialization when neither Brain exists (formerly, `/documentation-start` bootstrapped both).
- `/memory-bank-read` — Quick overview of Memory Bank state with staleness warnings.
- `/memory-bank-update` — Comprehensive review and update of all 6 files after significant work. Pass `--quick` for a fast `activeContext.md` + `progress.md` sync (formerly `/memory-bank-sync`).

> Note: `/memory-bank-sync` and `/documentation-start` are archived — content preserved in `archive/skills/`.

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

### 🔌 Integrations — GitLab, Miro & Jira (5 skills)

Skills that drive external platforms.

```bash
/gitlab-maintainer     # Check/diagnose/fix failing CI pipelines; handle MR review via glab
/miro-diagram          # Flowcharts, UML class/sequence, ERDs directly on Miro boards
/miro-infographic      # Multi-element infographics, dashboards, one-pagers on Miro
/jira-reader           # Read Jira issues, search via JQL, summarize sprint/backlog state (MCP, VPN-only)
/jira-writer           # Create/update/transition Jira issues; project-scope only, no PII (MCP, VPN-only)
```

- `/gitlab-maintainer` — Maintainer-level GitLab Enterprise work: diagnose & autonomously fix failing CI (build/test/lint), push the fix, wait for green; handle MR code review (respond, approve, request changes) via `glab`.
- `/miro-diagram` — Professional diagrams (flowcharts, UML class/sequence, ERDs) directly on Miro boards via the Miro MCP.
- `/miro-infographic` — Multi-element infographics, dashboards, and one-pagers (diagrams + text + tables + metrics) composed into cohesive Miro layouts.
- `/jira-reader` — Read Jira issues and epics, search via JQL, summarize sprint/backlog state. Requires VPN. Project-scope access only (no PII). Governed by the jira-reader/jira-writer access split.
- `/jira-writer` — Create, update, and transition Jira issues. Requires VPN. Project-scope only; no PII fields. Governed by the jira-reader/jira-writer access split.

---

### 🛠️ Skill Tooling & Meta-Build (3 skills)

Tooling for authoring/measuring skills and context management.

```bash
/skill-creator                 # Create, modify, eval, and optimize skills (triggering accuracy + variance)
/new-product                   # Deep research & architecture design for a new product
/headroom-context-compression  # MCP-backed context compression for large sessions
```

- `/skill-creator` — Create, modify, and improve skills; run evals, benchmark performance with variance analysis, and optimize descriptions for triggering accuracy.
- `/new-product` — Deep research and architecture design for a new product from docs or a description.
- `/headroom-context-compression` — MCP-backed context compression that trims context window weight for large sessions; requires the `headroom-context-compression` MCP server (see `skills/headroom-context-compression/INSTALL.md`).

> Note: `/remote-control-builder` (formerly here) is archived — see `archive/skills/remote-control-builder/` for the multi-agent system builder skill and its integration guide.

---

## 🪝 Hooks

Automated behaviors triggered by events — **30 hook files across 8 subsystems**. Three are registered Claude Code event hooks in `settings.json`: **Stop** and **Notification** for audio feedback, and **PreToolUse** for the shadow-snapshot. All other hooks are markdown-defined workflow hooks or explicit-call utility scripts invoked by skills.

### Sound & Shadow-Git Hooks ⭐ (the registered event hooks)

The three hooks registered in `settings.json`:

- **Stop** → `paplay sounds/done.wav` — audible completion signal after every Claude response
- **Notification** → `paplay sounds/loop.wav` — audible notification for agent activity
- **PreToolUse** → `shadow-snapshot.sh` — shadow-git checkpoint before Write/Edit tools

> ⚠️ `shadow-snapshot.sh` and `shadow-cleanup.sh` hardcode `/home/artsmc/.claude` — re-point the `REPO`/`cd` path to this machine before relying on rollback. `health-check.sh` treats `sounds/done.wav` as a foundation check.

### Reasoning-Skills Description Cue

The 8 reasoning skills surface via their always-in-context **frontmatter descriptions** — no event hook registration required for basic operation.

- **`dispatch.py`** — A UserPromptSubmit-style dispatcher that reads the prompt JSON from stdin, lowercases it, and matches against `signatures.json` (an editable trigger table of phrases + case-insensitive regexes per skill). On a match it injects `additionalContext` nudging the model to invoke the matching reasoning skill. **Not currently registered in `settings.json`** — wire it there as a UserPromptSubmit hook to enable explicit nudging.
- **`signatures.json`** covers all **8 reasoning skills**: `research-gated-build-plan`, `diagnose-from-raw-symptom`, `prove-it-live-before-done`, `fleet-dispatch-and-watch`, `steer-and-correct-the-agent`, `enumerated-menu-pick-and-sweep`, `reference-as-executable-spec`, `scope-question-and-delegate`.
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

---

## ⚡ Token Efficiency (2026-07)

2026-07 overhaul results from the skill-efficiency project (A/B benchmarks, isolated config, Sonnet 5).

### Always-in-Context Description Overhead

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total description chars | 18,895 | 16,169 | −14% |
| Approx. tokens per request | ~4,723 | ~4,042 | −681 tokens |

Four under-triggering skills were deliberately **expanded** (including `architecture-quality-assess`, which had no frontmatter at all and is now eval-validated). Net savings persist even after expansion.

### On-Trigger SKILL.md Body Size

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total SKILL.md body chars | 356,536 | 207,343 | −41% |
| Approx. tokens (on trigger) | ~89k | ~52k | −37k tokens |

Inline templates, cookbooks, and examples moved to per-skill `references/` files — never deleted, just not loaded unless the skill fires.

### Benchmark Results

| Skill | Token change | Quality before | Quality after |
|-------|-------------|----------------|---------------|
| `mastra-dev` | −45% | 8.5/10 | 9.5/10 |
| `document-hub-initialize` | −15% | 10/10 | 10/10 |

Two description trims were auto-rolled back after measurably hurting trigger accuracy (`prove-it-live-before-done`, `enumerated-menu-pick-and-sweep`). Per-skill eval sets now live in each skill's `evals/trigger-eval.json`.

### Effort Playbook

The 30-day transcript analysis + controlled A/B showed the **effort dial barely moves cost or quality on bounded tasks** (medium: 9.50/10 vs xhigh: 9.78/10 quality at +11% tokens). Real cost multipliers come from workflow/agent fan-out (3.4× tokens per turn) and context weight.

Rules:
- ✅ Keep `effortLevel: medium` persisted in `settings.json` as the default
- ⚠️ `/effort max` and `ultracode` **auto-expire** (session-scoped only); `low/medium/high/xhigh` **PERSIST** — beware escalating without intending to keep it
- ✅ Fan out agents on demand, not by default (fan-out sessions cost 3.4× more per turn than flat sessions at identical effort)
- ✅ Keep orchestrator sessions short; give subagents minimal scoped snapshots (goal/inputs/constraints/acceptance)

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
| **reasoning-skills** | ✅ v1.0 | 8 | 0 (descriptions, not wired) | `dispatch.py` + `signatures.json` | `hooks/reasoning-skills/` |
| **feature-orchestration** | ✅ v1.1 | 1 | 0 | 0 | Complete |
| **start-phase** | ✅ v2.0 | 2 | 4 | 4 | `skills/start-phase-plan/scripts/README.md` |
| **pm-db** | ✅ v2.0 | 1 | 12 | `project_database.py` + 6 scripts + Prisma | Complete |
| **memory-bank** | ✅ v1.1 | 3 | 1 (session-start) | `validate_memorybank.py` | Complete |
| **document-hub** | ✅ v1.0 | 4 | 1 (+3 planned) | hub scripts | Complete |
| **spec** | ✅ v1.0 | 2 | 1 (feedback-loop) | `validate_spec.py`, `critique_plan.py` | Complete |
| **code-quality** | ✅ v1.0 | 3 | 0 | analyzers | Complete |
| **mastra** | ✅ v1.0 | 11 | 0 | 0 | Per-skill guides |
| **integrations** | ✅ v1.0 | 5 | 0 | 0 | Per-skill guides |
| **meta-build** | ✅ v1.0 | 3 | 0 | skill-creator evals | Complete |

### Total Implementation

- ✅ **43 skills** (43 `SKILL.md` files — `start-phase/` and eval workspace dirs have none)
- ✅ **19 agent personas** + **5 loadable modules** (6 Opus / 13 Sonnet routing)
- ✅ **30 hook files** across 8 subsystems (3 registered in `settings.json`: Stop/Notification/PreToolUse + 4 quality-gate + 12 pm-db + Brain/spec)
- ✅ **17-table SQLite PM-DB** (`projects.db`, WAL mode) with Python + generated-Prisma access layers
- ✅ **~71KB** `ProjectDatabase` layer + zero-dependency quality tools
- ✅ **Zero external dependencies** (Python stdlib only)
- ✅ **Archive** — 5 retired/merged skills + 11 stale command stubs in `archive/` (all content preserved)

### Skill Naming Convention

Skills follow the pattern `/{system}-{action}` (a few take space-separated arguments or flags):
- `/feature-new` (orchestration; `--continue` resumes interrupted work)
- `/spec-plan`, `/spec-review` (spec)
- `/start-phase-plan`, `/start-phase-execute` (execution; `--team` for multi-agent)
- `/pm-db init`, `/pm-db import`, `/pm-db dashboard` (database)
- `/memory-bank-*`, `/document-hub-*` (Brain; `memory-bank-update --quick` for fast sync)
- `/mastra-*` (framework), `/miro-*`, `/gitlab-maintainer`, `/jira-reader`, `/jira-writer` (integrations)
- Reasoning skills carry descriptive verb-phrase slugs (`/diagnose-from-raw-symptom`, `/prove-it-live-before-done`, …)

---

## 📥 Installation

This repository **is** your `~/.claude/` directory — installing it means putting
its contents (agents, skills, hooks, tools) where Claude Code looks for them.

### Prerequisites

- ✅ **Claude Code CLI** installed (it creates and owns `~/.claude/`)
- ✅ **git** and **Python 3.8+** — every tool here is pure stdlib, no `pip install` needed
- ✅ *(optional)* **pipx** — only for skills backed by an MCP server (e.g.
  `headroom-context-compression`, which has its own `INSTALL.md`)

### Install into an existing `~/.claude/` (recommended)

Claude Code has usually already created `~/.claude/` with your auth and settings.
Those files are **git-ignored** (machine-local), so adopting the repo in place
leaves them untouched — only the tracked files (agents, skills, hooks, etc.)
are written:

```bash
cd ~/.claude
git init
git remote add origin git@github.com:artsmc/claude-dev-agents.git
git fetch origin
git checkout -f main      # writes tracked files; your ignored local files stay put
```

### Clean install on a brand-new machine

```bash
# Preserve anything Claude Code already put there (auth, settings)
mv ~/.claude ~/.claude.local.bak 2>/dev/null || true
git clone git@github.com:artsmc/claude-dev-agents.git ~/.claude

# Restore machine-local, git-ignored files the repo does NOT carry
cd ~/.claude
for f in settings.json settings.local.json config.json .credentials.json projects; do
  [ -e ~/.claude.local.bak/"$f" ] && cp -r ~/.claude.local.bak/"$f" ./
done
```

### What the repo does and doesn't carry

| Tracked (travels with the repo) | Machine-local (git-ignored, per machine) |
|---|---|
| `agents/ skills/ hooks/ bin/ scripts/ lib/ docs/ sounds/` | `settings.json`, `settings.local.json`, `config.json` |
| `README.md`, `.gitignore`, `prisma.config.ts` | `.credentials.json`, `projects/` (PM-DB + session data) |
| | `~/CLAUDE.md` and `~/.claude.json` — **outside** this repo |

> ⚠️ `~/CLAUDE.md` (workspace instructions) and `~/.claude.json` (MCP server
> registrations) live in your home dir, **not** in `~/.claude/`, so they are not
> part of this repo and must be set up separately on each machine. MCP-backed
> skills also carry their own `INSTALL.md` (see
> `skills/headroom-context-compression/INSTALL.md`).

### Verify the install

```bash
bash ~/.claude/scripts/health-check.sh     # foundation validator
```

Then run the one-time project setup below.

---

## 🚀 Quick Start

### Beginner (Orchestrated Workflow)

**The Easy Way (Recommended) — complete feature development in one command:**

```bash
# One-time setup
/memory-bank-initialize       # Initialize Memory Bank (cues Document Hub if neither Brain exists)
/pm-db init                   # Bootstrap projects.db

# Develop features
/feature-new "add user login"
/feature-new "integrate payments"

# Resume if interrupted
/feature-new --continue ./job-queue/feature-login/task-list.md
```

**That's it!** The orchestration skill handles spec → review → plan → tracking → execution automatically, pausing at two human checkpoints.

---

### Advanced (Manual Control)

**For experienced users who want fine-grained control over every step:**

```bash
# 1. Initialize
/memory-bank-initialize
/document-hub-initialize
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
/memory-bank-initialize
```

This creates:
- Memory Bank (6 files tracking project knowledge)
- Cues Document Hub initialization (`/document-hub-initialize`) if neither Brain exists yet
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
/feature-new --continue ./job-queue/feature-login/task-list.md
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
/memory-bank-update --quick  # Quick update (activeContext + progress only)
/document-hub-update         # Full documentation sync
```

**When to use each:**
- `/memory-bank-update --quick` — after each task or small change (fast, 2 files)
- `/memory-bank-update` — after completing a phase (comprehensive, 6 files)
- `/document-hub-update` — after architectural changes

---

### Complete Beginner Workflow

```bash
# === ONE-TIME SETUP ===
/memory-bank-initialize               # Memory Bank (+ cues Document Hub)
/pm-db init                           # Project database

# === FOR EACH FEATURE ===
/feature-new "add user login with OAuth"
# [Review spec at checkpoint 1] → approve
# [Review plan at checkpoint 2] → approve
# [System executes automatically with quality gates]

# === IF INTERRUPTED ===
/feature-new --continue ./job-queue/feature-auth/task-list.md

# === AFTER FEATURE COMPLETE ===
/memory-bank-update --quick           # Update knowledge base (fast)
/pm-db dashboard                      # View metrics
```

**That's it!** Three orchestration skills handle everything:
1. `/memory-bank-initialize` — setup (once)
2. `/feature-new` — build features (many times)
3. `/pm-db dashboard` — track progress (any time)

---

### Common Beginner Questions

**Q: Do I have to remember to invoke the reasoning skills?**
- For the most part, no. Reasoning skills surface via their always-in-context frontmatter descriptions — the model's internal routing picks them up naturally (e.g. a pasted stack trace naturally cues `/diagnose-from-raw-symptom`).
- `hooks/reasoning-skills/dispatch.py` **exists** and can optionally be wired as a UserPromptSubmit hook in `settings.json` for explicit prompt-level nudging; it caps at 3 cues per prompt and fails open.
- Edit `hooks/reasoning-skills/signatures.json` to tune or extend the trigger phrases.

**Q: Can I cancel during execution?**
- Yes — Ctrl+C to stop. Progress is saved in PM-DB.
- Use `/feature-new --continue` to resume from the last completed task.

**Q: What if quality gates fail?**
- The quality-gate hook hard-blocks on lint/build failures, a missing code review, or a missing task-update doc.
- No git commit is created until every gate passes.

**Q: How do I see what changed?**
- Git history: `git log --oneline`
- PM-DB: `/pm-db dashboard`
- Phase summary written by `phase-complete.md` at phase closeout

**Q: How is my work recovered if an edit goes wrong?**
- `shadow-snapshot.sh` is a PreToolUse hook (registered in `settings.json`) that branches `shadow/<epoch>_<ts>` before Write/Edit. ⚠️ It hardcodes `/home/artsmc/.claude` — re-point it before relying on rollback.
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
- ✅ **Initialize first:** `/memory-bank-initialize` for new projects (cues Document Hub)
- ✅ **Keep docs current:** `/document-hub-update` after changes
- ✅ **Audit drift:** `/document-hub-analyze` before deciding what to update

### Knowledge Management
- ✅ **Read before coding:** `/memory-bank-read` for context (the session-start hook does this for you)
- ✅ **Sync after tasks:** `/memory-bank-update --quick` (2 files, fast)
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
/start-phase-execute --team ./job-queue/feature-notifications/task-list.md

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
/start-phase-execute --team ./job-queue/feature-payment/task-list.md
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
/memory-bank-update --quick

# Deep update after phases (all 6 files)
/memory-bank-update

# Stale detection (read shows staleness warnings)
/memory-bank-read

# Documentation health audit before changing anything
/document-hub-analyze        # read-only drift report
/document-hub-update         # then apply

# Re-bootstrap both Brains for a fresh/severely-stale project
/memory-bank-initialize
/document-hub-initialize
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

- ✅ **2 execution skills** — `/start-phase-plan` (Mode 1), `/start-phase-execute` (Mode 2 + `--team` for multi-agent)
- ✅ **4 comprehensive lifecycle hooks** — phase-start, task-complete, quality-gate, phase-complete
- ✅ **4 zero-dependency Python tools** — `quality_gate.py`, `task_validator.py`, `validate_phase.py`, `sloc_tracker.py`
- ✅ **Quality gates between every task** — lint + build hard-block, mandatory AI review, mandatory task-update doc
- ✅ **Git workflow** — commits only after quality passes
- ✅ **SLOC tracking** — baseline, updates, final markdown report
- ✅ **PM-DB integration** — every task/review/gate written to `projects.db` via the pm-db hook suite
- ✅ **Parallel execution** — multi-agent team support via `--team` flag and `team-lead` coordination

**Recommended phase size:** 5–7 tasks. **Recommended for:** any multi-task development phase requiring quality enforcement and structured workflow.

---

## 📊 Statistics

### Inventory at a Glance

| Metric | Count | Basis |
|--------|-------|-------|
| Skills | **43** | `SKILL.md` count; `start-phase/` + eval workspace dirs have none |
| Agent personas | **19** | `agents/*.md` (excludes `modules/`) |
| Loadable modules | **5** | `agents/modules/*.md` |
| Hook files | **30** | Across 8 subsystems |
| Registered event hooks | **3** | Stop/Notification (sounds) + PreToolUse (shadow-snapshot), in `settings.json` |
| Reasoning skills | **8** | Trigger via frontmatter descriptions; `dispatch.py` optional |
| Archived skills | **5** | `archive/skills/` (all content preserved in targets' `references/`) |
| Archived command stubs | **11** | `archive/command-stubs/` (stale eval-generated stubs) |
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

### Reasoning-Skills Cue (dispatch.py)

| Property | Value |
|----------|-------|
| Trigger method | Always-in-context frontmatter descriptions (primary); `dispatch.py` optional |
| Registered in `settings.json` | ❌ No — wire manually as UserPromptSubmit to enable prompt nudging |
| Timeout (if wired) | 10s |
| Max cues per prompt (`MAX_SKILLS`) | 3 |
| Failure mode | ✅ Fails OPEN (exit 0, never blocks/alters the prompt) |
| Skills covered in `signatures.json` | 8 |

---

## 🐛 Troubleshooting

### Common Issues

**Q: Skills not showing up in the slash-command list**
- Ensure each skill directory contains a `SKILL.md` (`start-phase/` intentionally has none — it is a tools/scripts helper)
- Check file permissions (should be readable)
- Restart Claude Code if needed

**Q: Reasoning skills never trigger automatically**
- Reasoning skills trigger via their always-in-context frontmatter descriptions — no registration needed for basic operation
- For explicit prompt-level nudging, wire `dispatch.py` as a UserPromptSubmit hook in `settings.json`
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
- `shadow-snapshot.sh` hardcodes `/home/artsmc/.claude` — re-point the `REPO`/`cd` path to this machine before relying on it
- It is registered in `settings.json` as a PreToolUse hook on this machine

**Q: I used `/feature-continue` or `/memory-bank-sync` and they're not found**
- These skills were merged and archived. Use `/feature-new --continue` and `/memory-bank-update --quick` respectively. Original SKILL.md files are preserved in `archive/skills/`.

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
- [Reasoning-Skills Cue](hooks/reasoning-skills/) — `dispatch.py` + `signatures.json`

---

**Version:** 0.4.0
**Architecture:** Modular Skills, Agents, Hooks & Tools with PM-DB Tracking and Reasoning-Skill Cueing
**Status:** ✅ Production Ready
**Last Updated:** 2026-07-09
**Inventory:** 43 skills · 19 agents (+5 modules) · 30 hook files · 17-table PM-DB · zero dependencies

**Version History:**
- 0.4.0 (2026-07-09): Skill-efficiency overhaul — 5 skills archived (4 merged, 1 retired), 3 new (jira-reader, jira-writer, headroom-context-compression); −41% on-trigger SKILL.md chars; −14% always-in-context overhead; fix stale reasoning-skills "wired hook" claim
- 0.3.0 (2026-06-09): Reasoning-skills cue hook, refactoring-specialist, installation section
