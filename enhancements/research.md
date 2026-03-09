# Research: Claude Dev Agents Through the Lens of OpenDev

**Date:** 2026-03-09
**Paper:** "Building AI Coding Agents for the Terminal" (Bui, 2026 — arxiv:2603.05344v1)
**Subject:** What the paper teaches us about our own framework's real problems

---

## Method

This is not a feature wishlist derived from a paper. This is an honest audit of the Claude Dev Agents framework (`~/.claude/`) using the OpenDev paper's hard-won lessons as a diagnostic lens. Every finding is grounded in observed framework behavior, not theoretical gaps.

---

## Part 1: What the Paper Actually Learned (That Matters to Us)

The paper describes building a terminal AI agent from scratch. We built ours on top of Claude Code. The relevant lessons are ones that apply to the **layer we control** — agent definitions, skills, hooks, memory, coordination — not the layer Claude Code owns.

### Lesson 1: Context is the primary constraint, not features

> "The finite token window fundamentally shapes all other design choices."

The paper's single most important insight. Everything — prompt design, tool selection, safety layers, memory — serves the context budget. Adding features that consume context without proportional value is net-negative.

**What this means for us:** Our security-auditor.md is ~75KB. Loading it consumes ~40-50K tokens before the agent does ANY work. This is a framework-level failure. We're burning our most precious resource (context) on agent definitions that are too large to use.

### Lesson 2: Schema filtering beats runtime instruction

> "The LLM never sees tool definitions it cannot use, eliminating the possibility of write attempts during planning."

OpenDev's biggest safety win: don't tell the agent about tools it shouldn't use. Don't add "please don't use Bash" to the prompt — remove Bash from the schema entirely. Compile-time enforcement over runtime hope.

**What this means for us:** We can't modify Claude Code's tool schemas. But we CAN control what we put in agent .md files. Today, our agents are monolithic — they contain everything the agent might need. The paper says: give agents ONLY what they need for THIS task.

### Lesson 3: One parameterized class, not a class hierarchy

> "Early designs created separate classes... This created a diamond problem."

OpenDev rejected specialized agent classes in favor of a single agent with construction-time parameters. The variation comes from config, not code.

**What this means for us:** Our 19 agent .md files have no consistent structure. Some have YAML frontmatter, some don't. Some are 5KB, some are 75KB. Some have self-checking patterns, 11 don't. We have a "diamond problem" in markdown — agents that should share patterns (all reviewers need read-only guidance, all developers need write patterns) duplicate or omit them inconsistently.

### Lesson 4: Eager building prevents state bugs

> "Deferring system prompt construction until the first LLM call introduced first-call latency and race conditions."

OpenDev builds the full prompt before the agent starts. No lazy loading, no runtime assembly.

**What this means for us:** Our skills-to-hooks-to-agents cascade is the opposite of eager building. When `/feature-new` runs, it lazily invokes 6 sub-skills, each of which might trigger hooks that might or might not fire. If a hook fails silently, the entire orchestration is broken and nobody knows. The paper says: assemble everything upfront, fail fast.

### Lesson 5: Dual memory works, but working memory is the gap

> "Episodic memory: long-term storage. Working memory: current-turn reasoning artifacts."

OpenDev uses both. The key is working memory — short-lived context that dies when the task completes but persists across agent handoffs within a session.

**What this means for us:** Our Memory Bank is all episodic (6 static files about the project). When Agent A hands off to Agent B in a team, Agent B starts from zero. The decisions Agent A made, the files it explored, the dead ends it found — all gone. This is real daily friction.

### Lesson 6: Modular prompt composition, not monolithic blobs

> "System prompt assembled from ~40 independent priority-ordered templates. Conditional sections load only when contextually relevant."

OpenDev composes prompts from small pieces. Each piece loads only when relevant (e.g., git guidance only loads when git operations are detected).

**What this means for us:** Our agent .md files are monolithic blobs. `security-auditor.md` contains 30+ vulnerability examples, full OWASP coverage, and code samples for EVERY vulnerability type — all loaded every time, even if the task only involves checking one endpoint. Modular composition would mean loading OWASP-injection guidance only when SQL queries are detected.

---

## Part 2: Our Framework's Actual Problems (Observed, Not Theoretical)

### CRITICAL: Agent Definitions Are Broken

| Problem | Evidence | Impact |
|---------|----------|--------|
| Inconsistent format | Some have YAML frontmatter, some don't | Can't programmatically parse or validate agents |
| Size catastrophe | security-auditor.md ~75KB, refactoring-specialist large | Burns 40-50K tokens before any work starts |
| Self-check pattern incomplete | Only 6/19 agents have confidence levels | Inconsistent quality assurance across agents |
| No model field | settings.json hardcodes `opus[1m]` globally | Every agent, even Explore-style tasks, runs on most expensive model |
| Monolithic content | Everything loaded every time | Paying context cost for irrelevant guidance |

### CRITICAL: Orchestration Cascade Is Fragile

The documented workflow is:
```
/feature-new → 6 sub-skills → hooks → quality gates → PM-DB tracking
```

Reality:
- Hooks may not fire (no error handling documented, no validation they trigger)
- PM-DB appears uninitialized (sqlite3 query returns no tables)
- If any layer fails silently, user doesn't know until output is wrong
- No feedback loop: skills don't verify hooks fired, hooks don't verify PM-DB updated

### HIGH: Memory Bank Is Stale

- `activeContext.md` references work from 2026-02-10
- `productContext.md` says Memory Bank files don't exist (template artifact)
- `progress.md` mixes completed work with planning notes
- No timestamp validation or staleness warnings
- Agent reads stale context → makes wrong decisions

### HIGH: Agent Context Caching Is Invisible

- Documented as "production-ready" with "40-66% token savings"
- PM-DB has 8 cache tables in schema
- PM-DB file appears to have no data
- No visible integration in any active workflow
- Zero evidence it's actually running

### MEDIUM: Model Is Hardcoded

- `settings.json`: `"model": "opus[1m]"` — no per-agent override
- Claude Code's Task tool supports `model` parameter
- But no agent .md files specify a model preference
- Result: exploration tasks that Haiku could handle run on Opus

---

## Part 3: What We Should Actually Do

Applying the paper's lessons to our real problems. Ordered by: fixes real pain, respects Claude Code constraints, proportional effort.

### 1. Fix Agent Definitions (Standardize + Modularize)

**Paper lesson:** Single parameterized class, modular prompt composition, context as primary constraint.

**The problem:** 19 agents, no consistent structure, some too large to use.

**The fix:**

**a) Define a standard agent format:**
```markdown
---
name: agent-name
model: sonnet | opus | haiku
tools: full | read-only | no-shell
category: development | review | documentation | planning
max_context_budget: 10000  # estimated tokens this agent def consumes
---

# Agent Name

## Role
One paragraph.

## Core Rules
Numbered list, max 10 rules.

## Patterns
Only patterns relevant to THIS agent's specialty.

## Self-Check
Confidence levels, verification steps.
```

**b) Split bloated agents into modular pieces:**
```
agents/
  security-auditor.md          # Core agent (< 15KB)
  security-auditor/
    owasp-injection.md         # Loaded only when SQL/NoSQL detected
    owasp-auth.md              # Loaded only when auth code detected
    owasp-xss.md               # Loaded only when frontend code detected
    ...
```

**c) Add model field to every agent:**
- Planning/Security/Architecture → `model: opus`
- Development/Review/Spec → `model: sonnet`
- Exploration/Search → `model: haiku`

**Why this matters:** Fixes the #1 pain point (agents too large), enables model routing (saves 40-60% cost), creates consistency (agents become predictable), and respects context as primary constraint.

**Effort:** 2-3 days. No code — just markdown restructuring.

---

### 2. Add Working Memory for Team Coordination

**Paper lesson:** Dual-memory architecture, working memory for current-turn reasoning.

**The problem:** Agent B starts from zero when Agent A hands off in a team.

**The fix:**

```
~/.claude/working-memory/
  {team-name}.md    # Created when team starts, deleted when team ends
```

Format:
```markdown
# Working Memory: {team-name}
## Decisions
- [agent-name @ timestamp] Decision and rationale

## Discoveries
- [agent-name @ timestamp] What was found

## Blockers
- [agent-name @ timestamp] What's stuck and why

## Handoff Notes
- [agent-name @ timestamp] What the next agent needs to know
```

**Integration:** Team lead instructions updated to:
1. Create working memory file when team starts
2. Tell each agent: "Read ~/.claude/working-memory/{team}.md before starting. Append your decisions and discoveries when done."
3. Delete file when team completes

**Why this matters:** Directly fixes daily friction. Zero infrastructure needed — just a file convention and updated team-lead instructions.

**Effort:** Half a day. Update team-lead.md + create template.

---

### 3. Add Shadow Git Snapshots (Pre-Tool Hook)

**Paper lesson:** Defense-in-depth, lifecycle hooks for custom policies.

**The problem:** When an agent writes bad code, recovery is manual git operations.

**The fix:** A pre-tool hook script that creates a lightweight git checkpoint before Write/Edit operations.

```bash
# ~/.claude/hooks/pre-write-snapshot.sh
#!/bin/bash
# Creates a shadow git ref before file modifications
stash_ref=$(git stash create "shadow: pre-op snapshot" 2>/dev/null)
if [ -n "$stash_ref" ]; then
    git branch "shadow/$(date +%s)" "$stash_ref" 2>/dev/null
fi
```

Wire into Claude Code's PreToolUse hook for Write and Edit tools.

Add a cleanup cron:
```bash
# Delete shadow branches older than 24 hours
git for-each-ref --format='%(refname)' refs/heads/shadow/ | while read ref; do
    git branch -D "${ref#refs/heads/}" 2>/dev/null
done
```

**Why this matters:** Instant rollback. Safety net before we make any other framework changes. The paper's core insight: defense-in-depth, no single point of failure.

**Effort:** Half a day. One bash script + hook config.

---

### 4. Fix the Orchestration Foundation

**Paper lesson:** Eager building, fail-fast, deterministic operations outside the agent loop.

**The problem:** Skills → Hooks → PM-DB cascade fails silently.

**The fix:** Not new features — fix what's broken.

**a) Validate PM-DB:**
```bash
# Does pm.db have tables? If not, initialize it.
sqlite3 ~/.claude/pm.db "SELECT name FROM sqlite_master WHERE type='table'"
```
If empty, run the initialization. If corrupted, rebuild.

**b) Validate hooks fire:**
Create a test hook that writes a timestamp to a file when triggered. Run a skill. Check the file. If hooks don't fire, we know the entire orchestration cascade is broken and we fix THAT instead of building on top of it.

**c) Add health check:**
A simple script that validates:
- All 6 Memory Bank files exist and are non-empty
- PM-DB has initialized tables
- Hooks are registered in settings.json
- Agent .md files parse correctly

Run this BEFORE any workflow starts (eager validation).

**Why this matters:** Every other improvement is worthless if the foundation is broken. The paper says: deterministic operations happen outside the agent loop. Validate infrastructure before invoking agents.

**Effort:** 1 day. Python health-check script + PM-DB initialization.

---

### 5. Refresh Memory Bank

**Paper lesson:** Context must be current to be useful. Stale context is worse than no context.

**The problem:** Memory Bank files are stale, some contain template artifacts.

**The fix:**
- Update `activeContext.md` with CURRENT state (what's actually in progress now)
- Fix `productContext.md` template artifact
- Clear completed items from `progress.md`
- Add a "last-updated" timestamp to each file
- Add staleness check to health script (warn if >7 days old)

**Effort:** 1-2 hours. Manual review + updates.

---

## Part 4: What We Should NOT Do

### Skip: Custom Context Compaction
Claude Code already compresses context as it approaches limits. Building custom compaction on top is redundant. If Claude Code's compaction is bad, file a feature request — don't build a fragile layer on top.

### Skip: Self-Critique Phase
Our quality gates (lint/build after each task) catch errors post-action. Pre-action critique adds latency to every operation for uncertain benefit. No observed incidents of errors that pre-critique would have caught but quality gates missed.

### Skip: System Reminder Anti-Fade
Subagents get fresh context each spawn — fade is not their problem. The team lead could benefit, but the fix is simpler than an event-driven reminder system: just make the team-lead.md instructions concise enough that they survive long sessions.

### Skip: Complex Tool Restriction Infrastructure
We can't modify Claude Code's tool schemas for custom agents. Instructions-based restrictions ("DO NOT use Bash") are the only feasible approach. Add a `## Tool Restrictions` section to agent .md files and move on.

---

## Part 5: Execution Order

```
Week 1:
  Day 1:  Fix foundation (PM-DB init, hook validation, health check)
  Day 1:  Shadow git snapshots (safety net before other changes)
  Day 2:  Refresh Memory Bank (current context)
  Day 2:  Working memory template + team-lead update

Week 2:
  Day 3-5: Standardize agent format (define template, restructure all 19)
  Day 3-5: Add model field to all agents
  Day 3-5: Split bloated agents into modular pieces
```

**Total: ~5 days of actual work.**

No PM-DB migrations, no custom compaction algorithms, no FedRAMP audit trails, no compound model patterns. Just fix what's broken, add what's missing, and respect the context budget.

---

## Part 6: Success Criteria

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Largest agent definition | ~75KB | < 15KB core | `wc -c agents/*.md` |
| Agent format consistency | ~30% consistent | 100% | All have frontmatter, core rules, self-check |
| Model cost per team run | Unknown (all Opus) | -40% | Add model field, measure before/after |
| Cross-agent context retention | 0% | Qualitative improvement | Working memory file populated after team runs |
| Rollback time after agent error | Manual (5-30 min) | Instant (< 5 sec) | Shadow git branch exists |
| Health check pass rate | Unknown | 100% | Run health script on fresh session |
| Memory Bank staleness | Weeks old | < 7 days | Timestamp in each file |

---

## Appendix: Paper Concepts We Absorbed vs. Dismissed

| Paper Concept | Absorbed? | Rationale |
|---------------|-----------|-----------|
| Context as primary constraint | **YES** | Drives agent size limits and modular composition |
| Dual memory (episodic + working) | **YES** | Working memory fills real gap |
| Defense-in-depth (shadow snapshots) | **YES** | Rollback is real pain |
| Modular prompt composition | **YES** | Fixes bloated agent problem |
| Single parameterized class | **YES** | Standardized agent format |
| Eager building / fail-fast | **YES** | Health check, hook validation |
| Multi-model routing | **YES** | Simple config, big cost savings |
| Schema-level tool filtering | **NO** | Can't modify Claude Code tool schemas |
| Custom context compaction | **NO** | Claude Code already handles this |
| Self-critique phase | **NO** | Quality gates exist, no evidence of gap |
| Event-driven reminders | **NO** | Subagents have fresh context; team lead fix is simpler |
| Approval persistence | **NO** | Claude Code handles this natively |
| Fuzzy edit matching | **NO** | Claude Code handles this natively |
| Provider-level prompt caching | **NO** | Claude Code handles this natively |

---

*This research document replaces the previous over-engineered 7-spec roadmap. The paper is a lens, not a blueprint.*
