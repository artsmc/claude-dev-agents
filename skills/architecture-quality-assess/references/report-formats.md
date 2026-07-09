# Report and Task-List Formats

Full output schemas, moved verbatim from SKILL.md. Read when parsing the JSON report (e.g., in CI) or consuming the generated task list.

## Report Output

### Markdown Report Structure

```markdown
# Architecture Quality Assessment Report

**Generated**: 2026-02-07 15:45:32
**Project**: my-nextjs-app
**Path**: /home/user/projects/my-nextjs-app

---

## Executive Summary

**Overall Score**: 76/100 (Good)
**Critical Issues**: 2
**High Priority**: 8
**Medium Priority**: 15
**Low Priority**: 23

---

## 1. Project Overview
[Project type, framework, version]

## 2. Layer Separation Analysis
[Violations, recommendations]

## 3. SOLID Principles
[Per-principle scores, violations]

## 4. Design Patterns
[Patterns found, anti-patterns]

## 5. Dependency Management
[Coupling metrics, circular dependencies]

## 6. Code Organization
[File structure, naming, module sizes]

## 7. Drift Detection
[Comparison with documented architecture]

## 8. Recommended Actions
[Prioritized refactoring task list]

---

## Appendix: Detailed Violations
[Full list with file paths, line numbers]
```

### JSON Report Structure

```json
{
  "metadata": {
    "generated_at": "2026-02-07T15:45:32Z",
    "project_name": "my-nextjs-app",
    "project_path": "/home/user/projects/my-nextjs-app",
    "analysis_duration_seconds": 42.3
  },
  "summary": {
    "overall_score": 76,
    "critical_count": 2,
    "high_count": 8,
    "medium_count": 15,
    "low_count": 23
  },
  "project_detection": {
    "type": "nextjs",
    "framework_version": "14.0.3",
    "architecture_pattern": "three-tier"
  },
  "violations": [
    {
      "id": "LSV-001",
      "category": "layer_separation",
      "severity": "critical",
      "title": "SQL in API Route",
      "file": "src/app/api/users/route.ts",
      "line": 12,
      "description": "Direct SQL query in route handler",
      "recommendation": "Move database access to service layer",
      "code_snippet": "const users = await db.query('SELECT * FROM users');"
    }
  ],
  "metrics": {
    "solid_compliance": {
      "overall": 72,
      "srp": 65,
      "ocp": 80,
      "lsp": 90,
      "isp": 75,
      "dip": 50
    },
    "coupling": {
      "highest_fan_out": {
        "module": "src/lib/auth-service.ts",
        "fan_out": 18
      },
      "circular_dependencies_count": 2
    }
  },
  "recommended_actions": [
    {
      "priority": "P0",
      "category": "layer_separation",
      "title": "Move SQL to Service Layer",
      "files": ["src/app/api/users/route.ts"],
      "estimated_effort": "1 hour"
    }
  ]
}
```

---

## Task List Generation

Automatically generates refactoring task list compatible with `/start-phase-execute`:

**Output File**: `architecture-refactoring-tasks.md`

**Structure:**
```markdown
# Architecture Refactoring Tasks

## Phase 1: Critical Fixes (Priority P0)

### Task 1: Move SQL to Service Layer
**File**: src/app/api/users/route.ts
**Issue**: Direct database access in route handler
**Action**: Create UserService with getUserList() method
**Verification**: Route handler only calls service method
**Estimated Time**: 1 hour

### Task 2: Break Circular Dependency
**Files**: src/lib/user-service.ts ↔️ src/lib/auth-service.ts
**Issue**: Circular dependency prevents clean testing
**Action**: Extract shared interface to src/types/auth-types.ts
**Verification**: No circular imports remain
**Estimated Time**: 2 hours

## Phase 2: High Priority Refactoring (Priority P1)

[...]

## Phase 3: Medium Priority Improvements (Priority P2)

[...]
```

**Integration:**
```bash
# Generate assessment and task list
/architecture-quality-assess

# Execute refactoring tasks
/start-phase execute architecture-refactoring-tasks.md
```

---
