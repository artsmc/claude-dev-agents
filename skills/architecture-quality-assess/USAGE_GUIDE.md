# Architecture Quality Assessment - Usage Guide

**Version**: 1.0.0
**Last Updated**: 2026-02-07

This guide provides practical examples and detailed instructions for using the Architecture Quality Assessment skill in various scenarios.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Common Workflows](#common-workflows)
5. [CI/CD Integration](#cicd-integration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Analyze Current Project

```bash
cd /path/to/your/project
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py
```

This will:
- Detect your project type automatically
- Analyze all source files
- Generate `architecture-assessment.md` in the current directory

### View the Report

```bash
cat architecture-assessment.md
```

---

## Basic Usage

### 1. Analyze a Specific Project

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py /path/to/project
```

### 2. Generate JSON Output

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format json \
  --output assessment.json
```

### 3. Show Only Critical Issues

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --severity critical
```

### 4. Verbose Output

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --verbose
```

### 5. Generate All Report Formats

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format all
```

This creates:
- `architecture-assessment.md` - Human-readable report
- `architecture-assessment.json` - Machine-readable data
- `architecture-refactoring-tasks.md` - Actionable task list (if violations found)

---

## Advanced Features

### Disable Caching

By default, the tool caches parsing results to speed up re-runs. Disable with:

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --no-cache
```

### List Available Analyzers

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --list-analyzers
```

### Custom Output Location

```bash
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --output docs/architecture/assessment-$(date +%Y%m%d).md
```

---

## Common Workflows

### Workflow 1: Pre-Refactoring Assessment

**Goal**: Assess current state before starting refactoring.

```bash
# 1. Run full assessment
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format all

# 2. Review markdown report
cat architecture-assessment.md

# 3. Import tasks into PM-DB (if using)
# /pm-db import architecture-refactoring-tasks.md

# 4. Execute tasks systematically
# /start-phase execute architecture-refactoring-tasks.md

# 5. Re-run assessment after refactoring
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --output post-refactoring-assessment.md
```

### Workflow 2: CI/CD Quality Gate

**Goal**: Fail build if critical issues are detected.

```bash
#!/bin/bash
# quality-gate.sh

python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format json \
  --output assessment.json \
  --severity critical

# Check exit code (1 if critical issues found)
if [ $? -ne 0 ]; then
  echo "❌ Quality gate failed: Critical architecture violations detected"
  cat assessment.json
  exit 1
fi

echo "✅ Quality gate passed"
```

### Workflow 3: Weekly Architecture Review

**Goal**: Track architecture health over time.

```bash
#!/bin/bash
# weekly-assessment.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="docs/architecture/assessments"

mkdir -p "$REPORT_DIR"

python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format all \
  --output "$REPORT_DIR/assessment-$DATE.md"

echo "Assessment completed and saved to $REPORT_DIR/assessment-$DATE.md"

# Optional: Compare with previous week
# diff "$REPORT_DIR/assessment-$(date -d '7 days ago' +%Y-%m-%d).md" \
#      "$REPORT_DIR/assessment-$DATE.md"
```

### Workflow 4: Self-Analysis (Dog-Fooding)

**Goal**: Analyze the skill itself to validate functionality.

```bash
cd ~/.claude/skills/architecture-quality-assess

# Run self-analysis test
python3 tests/test_self_analysis.py --standalone

# Review results
cat tests/self-analysis-reports/skill-self-assessment.md
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/architecture-check.yml`:

```yaml
name: Architecture Quality Check

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  assess:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run architecture assessment
        run: |
          python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
            --format json \
            --output assessment.json \
            --severity high

      - name: Upload assessment report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: architecture-assessment
          path: assessment.json

      - name: Comment on PR (if violations found)
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const assessment = JSON.parse(fs.readFileSync('assessment.json', 'utf8'));

            const body = `## Architecture Quality Check Failed

            **Score**: ${assessment.summary.overall_score}/100
            **Critical**: ${assessment.summary.critical_count}
            **High**: ${assessment.summary.high_count}
            **Medium**: ${assessment.summary.medium_count}

            Please review the architecture violations before merging.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
architecture_check:
  stage: test
  script:
    - python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py --format json --severity critical
  artifacts:
    reports:
      junit: assessment.json
    paths:
      - architecture-assessment.md
    when: always
  allow_failure: false
```

---

## Troubleshooting

### Issue: "No project type detected"

**Cause**: Missing project manifest files (package.json, requirements.txt, etc.)

**Solution**:
- Ensure you're running from the project root
- Add appropriate manifest file for your project type
- Check that the directory contains source code files

### Issue: "Parser error on file X"

**Cause**: Syntax error in source file

**Solution**:
- File is automatically skipped
- Run with `--verbose` to see details
- Fix syntax errors in the source file

### Issue: "Analysis too slow"

**Cause**: Large project or disabled caching

**Solution**:
```bash
# Enable caching (default)
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py

# Exclude test files (if configured)
# Add to project config: .architecture-assess.json
```

### Issue: "Memory usage high"

**Cause**: Very large project

**Solution**:
- Run on smaller sub-projects separately
- Exclude build/dist directories
- Increase system memory limits if needed

### Issue: "No violations detected but I know there are issues"

**Cause**: Analyzers might need configuration

**Solution**:
- Check that source files are being parsed (see stats in output)
- Ensure project type is correctly detected
- Analyzers use heuristics - some patterns may not be detected
- Review SKILL.md for configuration options

---

## Best Practices

### 1. Run Regularly

Schedule weekly assessments to track architecture health:

```bash
# Add to crontab for weekly Sunday execution
0 9 * * 0 cd /path/to/project && python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py --output "reports/assessment-$(date +\%Y\%m\%d).md"
```

### 2. Use in Code Reviews

Before approving large PRs:

```bash
# Checkout PR branch
git checkout pr-branch-name

# Run assessment
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --severity high

# Review violations
cat architecture-assessment.md
```

### 3. Track Metrics Over Time

Save assessment JSON files with timestamps:

```bash
mkdir -p metrics
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py \
  --format json \
  --output "metrics/$(date +%Y%m%d).json"
```

Then analyze trends:

```bash
# Compare scores over time
jq '.summary.overall_score' metrics/*.json
```

### 4. Combine with Memory Bank

Use Memory Bank integration to detect drift:

```bash
# Ensure Memory Bank is initialized
# /memorybank init

# Run assessment (automatically checks Memory Bank)
python3 ~/.claude/skills/architecture-quality-assess/scripts/assess.py

# Review drift section in report
grep -A 10 "Drift" architecture-assessment.md
```

### 5. Create Custom Rules

Create `.architecture-assess.json` in project root:

```json
{
  "exclude_paths": [
    "node_modules/",
    "dist/",
    "*.test.ts"
  ],
  "rules": {
    "max_fan_out": 10,
    "max_file_loc": 300,
    "allow_sql_in_routes": false
  }
}
```

---

## Example Output Interpretation

### Good Score (90-100)

```
Overall Score: 95/100 (Excellent ✅)
Total Issues: 3
- Critical: 0
- High: 0
- Medium: 2
- Low: 1
```

**Action**: Address medium and low issues during refactoring cycles.

### Fair Score (60-75)

```
Overall Score: 72/100 (Fair ⚠️)
Total Issues: 15
- Critical: 1
- High: 5
- Medium: 7
- Low: 2
```

**Action**:
1. Fix critical issue immediately
2. Plan sprint to address high-priority issues
3. Track medium/low issues in backlog

### Poor Score (<60)

```
Overall Score: 45/100 (Needs Improvement ❌)
Total Issues: 35
- Critical: 8
- High: 12
- Medium: 10
- Low: 5
```

**Action**:
1. Stop feature development
2. Create refactoring plan with task list
3. Fix all critical issues before next release
4. Schedule architecture review meeting

---

## Additional Resources

- **SKILL.md**: Complete skill documentation
- **README.md**: Architecture and design overview
- **TR.md**: Technical requirements specification
- **FRS.md**: Functional requirements specification

---

## Support

For issues or questions:
1. Check this usage guide first
2. Review SKILL.md for detailed feature documentation
3. Run with `--verbose` flag to see detailed logs
4. Check Memory Bank for skill-specific context

---

**Generated by**: Architecture Quality Assessment Skill
**Version**: 1.0.0
**Date**: 2026-02-07
