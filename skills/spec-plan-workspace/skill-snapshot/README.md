# Spec Plan v2

Scope-aware feature specification system. Generates **right-sized** documentation based on feature complexity.

## Quick Start

```bash
# Auto-detect scope (recommended)
/spec-plan build a user authentication feature

# Force a tier
/spec-plan add logout button --tier quick
/spec-plan add OAuth2 support --tier standard
/spec-plan build SSO with MFA --tier full --team

# Interactive mode
/spec-plan
```

---

## The Tiered System

### Core Principle

> Match spec depth to requirement depth.

Not every feature needs 5 documents. The system triages scope and generates only what's needed.

### Tiers

| Tier | Output | Time | Tokens | Use When |
|------|--------|------|--------|----------|
| **Quick** | task-list.md | 1-3 min | ~15K | Single concern, known pattern, <5 tasks |
| **Standard** | FRD + TR + task-list | 3-7 min | ~35K | Moderate scope, API/schema changes, 5-15 tasks |
| **Full** | FRD + FRS + GS + TR + task-list | 8-15 min | ~80K | Multi-app, security, new architecture, 15+ tasks |
| **Full + Team** | Same (parallel) | 5-10 min | ~120K | Same as full, time-sensitive |

### Auto-Detection Examples

```
"add logout button"                    → Quick
"add field to user form"               → Quick
"build notification system"            → Standard
"add file upload with S3 storage"      → Standard
"implement SSO with MFA"               → Full
"build real-time workflow monitoring"   → Full
```

---

## Workflow

```
1. /spec-plan [description]
2. Lightweight clarification (2-3 questions)
3. Triage → classify as quick/standard/full
4. Scope confirmation → user approves before generation
5. Budgeted research → capped context per section
6. Launch spec-writer with structured brief
7. [Agent generates tier-appropriate deliverables]
8. Hook auto-validates and critiques
9. User approves or iterates
```

### What's New in v2

| v1 | v2 |
|----|-----|
| Always generates 5 files | Generates 1, 3, or 5 files based on tier |
| Unbounded research phase | Budget-capped research per section |
| Narrative prompt blob to agent | Structured JSON brief to agent |
| No scope confirmation | User confirms scope before generation |
| Same cost for simple and complex | 15K tokens (quick) to 80K (full) |

---

## Skills (2)

### 1. `/spec-plan [description]` — Plan & Generate

**Phases:**
1. **Feature description** — from argument or interactive
2. **Clarify** — 2-3 lightweight questions (problem, affected apps, constraints)
3. **Triage** — auto-classify tier based on signals
4. **Confirm** — show user what will be generated, get buy-in
5. **Research** — budget-constrained context gathering
6. **Launch** — spec-writer agent with structured brief

**Token usage:** ~1,200 tokens (skill itself)

### 2. `/spec-review` — Validate & Critique

**Tier-aware validation:**
- Quick: validates task-list only
- Standard: validates FRD + TR + task-list
- Full: validates all 5 files

**Tools:** `validate_spec.py`, `critique_plan.py` (both tier-aware)

**Token usage:** ~600 tokens

---

## Generated Structure

### Quick Tier
```
/job-queue/feature-{name}/docs/
└── task-list.md          # Tasks with inline requirements
```

### Standard Tier
```
/job-queue/feature-{name}/docs/
├── FRD.md                # Feature requirements
├── TR.md                 # Technical requirements
└── task-list.md          # Implementation tasks
```

### Full Tier
```
/job-queue/feature-{name}/docs/
├── FRD.md                # Feature requirements
├── FRS.md                # Functional specification
├── GS.md                 # Gherkin scenarios
├── TR.md                 # Technical requirements
└── task-list.md          # Implementation tasks
```

---

## Python Tools (2)

### validate_spec.py

Structural validation, tier-aware.

```bash
# Auto-detect tier from files present
python validate_spec.py /path/to/feature-folder

# Specify tier explicitly
python validate_spec.py /path/to/feature-folder --tier standard
```

Output includes `tier` field:
```json
{
  "valid": true,
  "tier": "standard",
  "errors": [],
  "warnings": [],
  "completeness_score": 0.85
}
```

### critique_plan.py

Quality analysis, tier-aware. Includes scope-appropriateness check.

```bash
python critique_plan.py /path/to/feature-folder --tier standard
```

Output includes scope warnings:
```json
{
  "critique_score": 0.75,
  "tier": "standard",
  "critical_issues": [],
  "warnings": [
    {
      "file": "task-list.md",
      "issue": "20 tasks detected — this may need a full-spec",
      "suggestion": "Consider re-running with --tier full"
    }
  ]
}
```

---

## Hook (1)

### feedback-loop

**Trigger:** After spec-writer agent completes
**Behavior:** Runs validate + critique automatically, presents results
**Tier-aware:** Only checks files expected for the detected tier

---

## Design Decisions

**Why triage before research?**
Research is expensive. A quick-spec needs a grep, not a documentation deep-dive.

**Why confirm scope?**
Prevents generating 5 documents for a feature that only needs a task list.

**Why budget context?**
Unbounded context gathering leads to bloat. Caps force prioritization.

**Why default to lower tier?**
Over-production wastes tokens. Under-production is easily fixed by re-running.

---

## File Structure

```
.claude/skills/spec-plan/
├── SKILL.md                # Core skill definition (v2)
├── README.md               # This file
├── TEAM-ENHANCEMENT.md     # Team mode (full tier only)
└── scripts/
    ├── validate_spec.py    # Tier-aware structural validation
    ├── critique_plan.py    # Tier-aware quality critique
    ├── requirements.txt    # Empty — no dependencies
    └── README.md           # Tool documentation
```

---

## Version History

- **v2.0** — Tiered output, triage gate, scope confirmation, structured briefs, context budgets
- **v1.0** — Always generates 5 files, unbounded research, narrative prompts

---

**Status:** v2.0 implemented
**Dependencies:** None (Python stdlib only)
