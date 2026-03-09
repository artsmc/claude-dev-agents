# Spec Python Tools

Tier-aware validation and critique tools for feature specifications.

## Tools

### 1. validate_spec.py

**Purpose:** Structural validation of generated specifications, tier-aware.

**Usage:**
```bash
# Auto-detect tier from files present
python validate_spec.py /path/to/feature-folder

# Specify tier explicitly
python validate_spec.py /path/to/feature-folder --tier quick
python validate_spec.py /path/to/feature-folder --tier standard
python validate_spec.py /path/to/feature-folder --tier full
```

**Tier-Aware File Checks:**

| Tier | Required Files |
|------|---------------|
| Quick | task-list.md |
| Standard | FRD.md, TR.md, task-list.md |
| Full | FRD.md, FRS.md, GS.md, TR.md, task-list.md |

**Checks by Tier:**

| Check | Quick | Standard | Full |
|-------|-------|----------|------|
| File existence | task-list only | FRD + TR + task-list | All 5 |
| File content (size, headers) | task-list only | FRD + TR + task-list | All 5 |
| Gherkin syntax | - | - | GS.md |
| Task list quality | Yes | Yes | Yes |
| Gitignore | Yes | Yes | Yes |
| Cross-references | - | FRD↔TR | FRD↔FRS↔TR↔GS |

**Auto-Detection Logic:**
- All 5 files exist → `full`
- FRD + TR + task-list exist → `standard`
- Only task-list exists → `quick`
- Other combinations → infer closest tier, warn about unexpected files

**Output:**
```json
{
  "valid": true,
  "tier": "standard",
  "errors": [],
  "warnings": [],
  "completeness_score": 0.85,
  "checks_passed": 12,
  "total_checks": 14
}
```

**Exit Codes:**
- 0: Validation passed
- 1: Validation failed

---

### 2. critique_plan.py

**Purpose:** Quality analysis of specifications, tier-aware with scope-appropriateness checks.

**Usage:**
```bash
# Auto-detect tier
python critique_plan.py /path/to/feature-folder

# Specify tier
python critique_plan.py /path/to/feature-folder --tier standard

# Focus on specific areas
python critique_plan.py /path/to/feature-folder --tier full --focus requirements,tasks
```

**Critiques by Tier:**

| Critique Area | Quick | Standard | Full |
|--------------|-------|----------|------|
| Requirement quality (FRD) | - | Yes | Yes |
| Requirement quality (FRS) | - | - | Yes |
| Task breakdown | Yes | Yes | Yes |
| Technical design (TR) | - | Yes | Yes |
| Testability (GS) | - | - | Yes |
| Scope appropriateness | Yes | Yes | Yes |

**Scope Appropriateness Checks:**
- Quick tier with 10+ tasks → "May need standard-spec"
- Standard tier with 20+ tasks → "May need full-spec"
- Full tier with <5 tasks → "May be over-scoped"

**Output:**
```json
{
  "critique_score": 0.75,
  "tier": "standard",
  "critical_issues": [],
  "warnings": [],
  "recommendations": [],
  "score_breakdown": {
    "requirement_specificity": 0.8,
    "task_atomicity": 0.7,
    "technical_design": 0.75,
    "scope_appropriateness": 0.9
  }
}
```

**Exit Codes:**
- 0: Always (critique is informational)

---

## Dependencies

**None.** Both tools use Python standard library only:
- `json`, `sys`, `re`, `pathlib`

---

## Integration

### With /spec-review
Runs both tools with tier auto-detection.

### With feedback-loop hook
Auto-runs after spec-writer completes, detects tier from files present.

### Standalone
```bash
python validate_spec.py /path/to/feature --tier standard
python critique_plan.py /path/to/feature --tier standard
```

---

## Scoring

### Validation Completeness
- 0.9-1.0: All checks passed
- 0.7-0.9: Minor warnings
- 0.5-0.7: Several warnings
- <0.5: Errors present

### Critique Quality
- 0.8-1.0: Ready for development
- 0.6-0.8: Minor improvements needed
- 0.4-0.6: Several issues
- <0.4: Major revision needed
