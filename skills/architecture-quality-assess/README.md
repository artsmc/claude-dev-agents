# Architecture Quality Assessment - User Guide

**Quick Start Guide for the Architecture Quality Assessment Skill**

---

## What Does This Skill Do?

This skill analyzes your codebase architecture to find quality issues like:

- 🔍 Layer mixing (SQL in API routes, business logic in wrong places)
- 🔗 Tight coupling between modules
- 🔄 Circular dependencies that make testing hard
- 📐 SOLID principles violations
- 🏗️ Missing or misused design patterns
- 📊 Code organization problems

It generates a detailed report with specific recommendations and can create a task list for fixing issues.

---

## Quick Start

### 1. Run Analysis

```bash
# Analyze current project
cd /path/to/your/project
/architecture-quality-assess

# Analyze specific project
/architecture-quality-assess /path/to/project
```

### 2. View Report

The skill generates `architecture-assessment.md` in your project root:

```bash
cat architecture-assessment.md
```

### 3. Review Findings

The report includes:
- Overall architecture score (0-100)
- Critical/High/Medium/Low priority issues
- Specific file paths and line numbers
- Actionable recommendations

### 4. Generate Refactoring Tasks (Optional)

```bash
/architecture-quality-assess --generate-tasks

# Creates: architecture-refactoring-tasks.md
```

### 5. Execute Fixes (Optional)

```bash
/start-phase execute architecture-refactoring-tasks.md
```

---

## Output Example

```markdown
# Architecture Quality Assessment Report

## Executive Summary
**Overall Score**: 76/100 (Good)
**Critical Issues**: 2
**High Priority**: 8

## Critical Issues

### 1. SQL in API Route (CRITICAL)
**File**: src/app/api/users/route.ts:12
**Issue**: Direct database query in route handler
**Why it matters**: Violates layer separation, makes testing impossible
**Fix**: Create UserService.getUserList() method

### 2. Circular Dependency (CRITICAL)
**Files**: src/lib/user-service.ts ↔️ src/lib/auth-service.ts
**Why it matters**: Prevents proper dependency injection and testing
**Fix**: Extract shared interface to break cycle

## Recommendations

1. **Immediate (Next Sprint)**:
   - Fix 2 critical issues above
   - Reduce coupling in auth-service.ts (FAN-OUT: 18)

2. **Short-term (Next Month)**:
   - Implement Repository Pattern for all data access
   - Split large modules (3 files > 500 LOC)

3. **Long-term (Next Quarter)**:
   - Add dependency injection container
   - Standardize error handling patterns
```

---

## Use Cases

### Use Case 1: Pre-Refactoring Assessment

**Scenario**: You want to refactor auth system but don't know where to start

**Steps**:
1. Run assessment: `/architecture-quality-assess`
2. Review coupling metrics for auth modules
3. Identify circular dependencies
4. Generate task list: `--generate-tasks`
5. Execute refactoring: `/start-phase execute`

**Result**: Data-driven refactoring plan with priorities

---

### Use Case 2: New Developer Onboarding

**Scenario**: New developer needs to understand codebase quality

**Steps**:
1. Run assessment to generate architecture report
2. Review "Design Patterns" section to see what patterns are used
3. Check "Code Organization" for structure conventions
4. Use report as reference during code review

**Result**: New developer understands architecture patterns and quality baseline

---

### Use Case 3: CI/CD Quality Gate

**Scenario**: Prevent architecture degradation in pull requests

**Steps**:
1. Add to GitHub Actions:
   ```yaml
   - run: /architecture-quality-assess --format json --severity critical
   ```
2. Fail builds if critical issues found
3. Post report as PR comment

**Result**: Automated architecture quality enforcement

---

### Use Case 4: Detect Drift from Documentation

**Scenario**: You documented Clean Architecture but want to verify compliance

**Steps**:
1. Ensure Memory Bank has systemPatterns.md with architecture patterns
2. Run: `/architecture-quality-assess`
3. Review "Drift Detection" section
4. See which files deviate from documented patterns

**Result**: Identify gaps between documentation and implementation

---

### Use Case 5: Technical Debt Measurement

**Scenario**: Need to quantify technical debt for stakeholders

**Steps**:
1. Run assessment monthly
2. Track overall score over time
3. Track violation counts by severity
4. Present trend to management

**Result**: Data-driven technical debt conversations

---

## Understanding the Report

### Overall Score (0-100)

- **90-100**: Excellent - Minimal technical debt
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Moderate refactoring recommended
- **Below 60**: Poor - Significant issues require attention

### Severity Levels

**CRITICAL** - Fix immediately
- Blocks development or causes production issues
- Examples: Circular dependencies, SQL injection risks

**HIGH** - Fix within 1 sprint
- Impacts maintainability significantly
- Examples: Tight coupling, large god objects

**MEDIUM** - Plan for next quarter
- Improvements that reduce future maintenance cost
- Examples: Missing design patterns, code organization

**LOW** - Nice-to-have
- Small optimizations and cleanup
- Examples: Naming inconsistencies, small files

### Key Metrics Explained

**FAN-OUT** - Number of modules this module depends on
- Target: < 10 (good), 10-15 (acceptable), >15 (refactor)
- High FAN-OUT = Hard to test, fragile to changes

**FAN-IN** - Number of modules depending on this module
- High FAN-IN = Central/shared module, changes impact many files
- Low FAN-IN = Potentially unused or isolated module

**Instability** - FAN-OUT / (FAN-IN + FAN-OUT)
- 0.0 = Stable (many dependents, few dependencies)
- 1.0 = Unstable (many dependencies, few dependents)
- Goal: Critical modules should be stable (low instability)

---

## Command Reference

### Basic Commands

```bash
# Default analysis (current directory, markdown output)
/architecture-quality-assess

# Specify project path
/architecture-quality-assess /path/to/project

# Generate JSON output
/architecture-quality-assess --format json

# Save report to specific location
/architecture-quality-assess --output docs/architecture.md

# Only show high/critical issues
/architecture-quality-assess --severity high

# Verbose progress output
/architecture-quality-assess --verbose
```

### Advanced Commands

```bash
# Incremental analysis (only changed files)
/architecture-quality-assess --incremental

# Disable caching (force full re-analysis)
/architecture-quality-assess --no-cache

# Generate refactoring task list
/architecture-quality-assess --generate-tasks

# Custom config file
/architecture-quality-assess --config .my-arch-config.json
```

---

## Configuration

### Basic Configuration File

Create `.architecture-assess.json` in your project root:

```json
{
  "exclude_paths": [
    "node_modules/",
    "dist/",
    "build/",
    ".next/",
    "*.test.ts"
  ],
  "severity_thresholds": {
    "critical": 0,
    "high": 5,
    "medium": 20
  },
  "rules": {
    "max_fan_out": 15,
    "max_file_loc": 500,
    "allow_sql_in_routes": false
  }
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `exclude_paths` | Paths to skip during analysis | `["node_modules/"]` |
| `severity_thresholds` | Max violations before build fails | Critical: 0 |
| `max_fan_out` | Maximum coupling allowed | 15 |
| `max_file_loc` | Maximum lines per file | 500 |
| `allow_sql_in_routes` | Allow database queries in routes | false |

---

## Integration with Other Skills

### With Memory Bank

Memory Bank stores your documented architecture patterns. This skill compares your code against those patterns.

**Workflow**:
```bash
# 1. Document your architecture
/memorybank update
# (Ensure systemPatterns.md describes your architecture)

# 2. Run analysis
/architecture-quality-assess

# 3. Review "Drift Detection" section
# See which code violates documented patterns
```

**Benefits**:
- Detect when code deviates from documented architecture
- Find undocumented new patterns
- Identify obsolete patterns still in code

---

### With PM-DB

PM-DB tracks your development progress. Use it to track refactoring work.

**Workflow**:
```bash
# 1. Generate assessment and task list
/architecture-quality-assess --generate-tasks

# 2. Import tasks to PM-DB
/pm-db import architecture-refactoring-tasks.md

# 3. Execute with tracking
/start-phase execute architecture-refactoring-tasks.md

# 4. Monitor progress
/pm-db dashboard
```

**Benefits**:
- Track refactoring progress over time
- Measure time spent on technical debt
- Generate reports for stakeholders

---

### With Document Hub

Document Hub maintains technical documentation. Use architecture assessment to validate it.

**Workflow**:
```bash
# 1. Check documentation alignment
/document-hub-analyze

# 2. Check architecture quality
/architecture-quality-assess

# 3. Compare findings
# - Document Hub: What's documented vs what exists
# - Architecture Assess: Code quality and pattern compliance
```

**Benefits**:
- Comprehensive quality view (docs + code)
- Identify gaps in both documentation and implementation
- Prioritize both doc updates and code refactoring

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Architecture Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  architecture-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install Claude CLI
        run: |
          curl -sS https://claude.ai/cli/install.sh | bash
          claude auth ${{ secrets.CLAUDE_API_KEY }}

      - name: Run Architecture Assessment
        id: assessment
        run: |
          claude /architecture-quality-assess \
            --format json \
            --severity critical \
            --output assessment.json

      - name: Check for Critical Issues
        run: |
          CRITICAL=$(jq '.summary.critical_count' assessment.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ $CRITICAL critical architecture violations detected"
            jq -r '.violations[] | select(.severity=="critical") | "- \(.title) (\(.file):\(.line))"' assessment.json
            exit 1
          fi
          echo "✅ No critical architecture violations"

      - name: Upload Assessment Report
        uses: actions/upload-artifact@v3
        with:
          name: architecture-assessment
          path: assessment.json

      - name: Comment on PR
        uses: actions/github-script@v6
        if: always()
        with:
          script: |
            const fs = require('fs');
            const assessment = JSON.parse(fs.readFileSync('assessment.json', 'utf8'));

            const body = `## Architecture Quality Assessment

            **Overall Score**: ${assessment.summary.overall_score}/100

            **Issues Found**:
            - Critical: ${assessment.summary.critical_count}
            - High: ${assessment.summary.high_count}
            - Medium: ${assessment.summary.medium_count}

            ${assessment.summary.critical_count > 0 ? '❌ Critical issues must be fixed before merge' : '✅ No critical issues'}

            [View Full Report](../actions/runs/${context.runId})
            `;

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body
            });
```

---

## Troubleshooting

### Issue: "No project type detected"

**Cause**: Missing manifest files (package.json, requirements.txt, etc.)

**Fix**:
```bash
# For JavaScript projects
ls package.json  # Should exist

# For Python projects
ls requirements.txt  # Or pyproject.toml
```

---

### Issue: "Analysis is slow"

**Causes**:
1. Large project (>5000 files)
2. No caching enabled
3. Analyzing test files and node_modules

**Fix**:
```bash
# Enable caching (default)
/architecture-quality-assess --cache

# Exclude unnecessary files
# Create .architecture-assess.json:
{
  "exclude_paths": [
    "node_modules/",
    "*.test.ts",
    "*.spec.js",
    "dist/",
    "build/"
  ]
}

# Use incremental mode for repeated runs
/architecture-quality-assess --incremental
```

---

### Issue: "Too many false positives"

**Cause**: Default rules too strict for your project

**Fix**:
```json
// .architecture-assess.json
{
  "rules": {
    "max_fan_out": 20,           // Increase from default 15
    "max_file_loc": 800,          // Increase from default 500
    "allow_sql_in_routes": true   // Allow if microservice pattern
  }
}
```

---

### Issue: "Memory Bank integration fails"

**Cause**: Memory Bank not initialized

**Fix**:
```bash
# Initialize Memory Bank first
/memorybank init

# Then run assessment
/architecture-quality-assess
```

---

## Best Practices

### When to Run

✅ **Do run**:
- Before starting major refactoring
- Monthly for technical debt tracking
- As CI/CD quality gate on main branch
- After onboarding new team members

❌ **Don't run**:
- On every single commit (use incremental mode)
- On generated code or build artifacts
- Without excluding test files first

### Interpreting Results

**Start with Critical Issues**:
1. Read all critical violations first
2. Fix those before anything else
3. Critical issues often indicate systemic problems

**Group Related Issues**:
- Same module with multiple violations? Likely needs redesign
- Same pattern (e.g., SQL in routes)? Create team guideline

**Track Trends**:
- Run monthly and track score over time
- Improving score = technical debt decreasing
- Degrading score = need architecture discussion

### Team Adoption

**Phase 1: Awareness**
- Run assessment, share report with team
- Discuss findings in retrospective
- No enforcement yet

**Phase 2: Guidelines**
- Document architecture patterns in Memory Bank
- Add assessment to PR review checklist
- Fix critical issues as they appear

**Phase 3: Enforcement**
- Add to CI/CD pipeline
- Block merges on critical violations
- Track metrics in sprint planning

---

## Examples

### Example 1: Clean Next.js Project

```markdown
# Architecture Quality Assessment Report

**Overall Score**: 94/100 (Excellent)
**Critical Issues**: 0 ✅
**High Priority**: 1

## Summary
Your architecture follows best practices well!

**Strengths**:
- ✅ Clean layer separation (routes → services → repositories)
- ✅ SOLID principles compliance (89/100)
- ✅ Repository pattern used consistently
- ✅ No circular dependencies

**Minor Improvements**:
- 1 high-priority issue: auth-service has FAN-OUT of 16 (target: <15)

## Recommended Action
Consider splitting auth-service into smaller modules.
```

---

### Example 2: Legacy Codebase

```markdown
# Architecture Quality Assessment Report

**Overall Score**: 47/100 (Poor)
**Critical Issues**: 8 ❌
**High Priority**: 23

## Summary
Significant refactoring needed.

**Critical Issues**:
1. 4 circular dependencies blocking testing
2. 3 god objects (>1000 LOC each)
3. SQL in 12 API routes

**Recommended Approach**:
1. **Week 1**: Break circular dependencies
2. **Week 2**: Extract SQL to service layer
3. **Month 2**: Refactor god objects

**Estimated Effort**: 3-4 weeks

See generated task list: architecture-refactoring-tasks.md
```

---

## FAQ

**Q: Will this modify my code?**
A: No, analysis only. It generates reports and task lists but never edits code.

**Q: How long does analysis take?**
A: Small project: 10s, Medium: 30-120s, Large: 2-10 minutes

**Q: Can I run on CI/CD?**
A: Yes, use `--format json --severity critical` for automated checks

**Q: Does it support TypeScript?**
A: Yes, JavaScript, TypeScript, JSX, TSX fully supported

**Q: What about Python?**
A: Yes, Python 3.x fully supported

**Q: Can I customize rules?**
A: Yes, create `.architecture-assess.json` in project root

**Q: How accurate is SOLID analysis?**
A: ~85% accurate, manual review recommended for complex cases

**Q: Does it work with monorepos?**
A: Yes, run per sub-project or target specific paths

---

## Support

**Documentation**: See SKILL.md for complete technical reference

**Issues**: Report via `/help` in Claude CLI

**Custom Configuration**: See Configuration section above

---

**Last Updated**: 2026-02-07
