---
name: code-duplication
description: Deep analysis of codebase for code duplication. Detects exact, structural, and pattern-level duplicates, generates comprehensive reports with refactoring suggestions and metrics.
---

# Code Duplication Analysis Skill

Comprehensive code duplication detection and analysis for all programming languages.

**Use this skill to** identify technical debt from code duplication, quantify duplication metrics, and receive actionable refactoring suggestions.

## Usage

```bash
# Analyze entire codebase
/code-duplication

# Analyze specific directory
/code-duplication src/components

# Analyze with custom configuration
/code-duplication --config .duplication-config.json

# Generate JSON output
/code-duplication --format json --output duplication-report.json
```

## What This Skill Does

Performs comprehensive duplicate detection to answer:
- What code blocks are duplicated across the codebase?
- What is the overall duplication percentage?
- Which files have the most duplication?
- How much LOC could be saved through refactoring?
- What specific refactoring techniques should be applied?

## Detection Types

### 1. Exact Duplicates
Identical code blocks (copy-pasted code)
- Threshold: 5-10 lines minimum
- Ignores whitespace and comments
- Groups all instances together

### 2. Structural Duplicates
Similar logic with minor variations
- Uses AST-based comparison for Python/JavaScript
- Detects code with different variable names but same structure
- Similarity scoring with configurable threshold

### 3. Pattern Duplicates
Repeated coding patterns that could be abstracted
- Common anti-patterns (repeated try-catch, validation logic, etc.)
- Opportunities for extract function/class refactoring
- Pattern catalog extensible

## Report Output

### Markdown Report (Default)

```markdown
# Code Duplication Analysis Report

## Executive Summary
- Total LOC analyzed: 12,450
- Duplicate LOC: 1,834 (14.7%)
- Duplicate blocks found: 47
- Estimated LOC reduction: 1,200-1,500

## Top Offenders
1. src/services/user_service.py - 23% duplication (340 LOC)
2. src/api/handlers.py - 18% duplication (245 LOC)
...

## Detailed Findings
### Duplicate Block #1 (Exact)
**Instances**: 4 files
**LOC per instance**: 23 lines
**Potential savings**: 69 lines

**Locations**:
- src/services/user_service.py:145-167
- src/services/order_service.py:89-111
...

**Refactoring Suggestion**:
Extract common authentication logic into shared function:
...
```

### JSON Report (--format json)

```json
{
  "summary": {
    "total_files": 156,
    "total_loc": 12450,
    "duplicate_loc": 1834,
    "duplication_percentage": 14.7,
    "duplicate_blocks": 47
  },
  "duplicates": [...],
  "top_offenders": [...],
  "heatmap": {...}
}
```

## Configuration

Create `.duplication-config.json` in your project root:

```json
{
  "min_lines": 5,
  "exclude_patterns": ["**/test_*.py", "**/migrations/*.py"],
  "similarity_threshold": 0.85,
  "ignore_comments": true,
  "ignore_whitespace": true,
  "languages": ["python", "javascript", "typescript"]
}
```

## Quality Metrics

This skill provides:
- **Duplication Percentage**: % of codebase that is duplicated
- **Top Offenders**: Files ranked by duplication amount
- **File Heatmap**: Visual representation of duplication distribution
- **Cleanup Potential**: Estimated LOC reduction from refactoring

## Technical Details

- **Zero external dependencies**: Pure Python 3.8+ stdlib
- **Multi-language support**: Python, JavaScript, TypeScript, and more
- **Performance**: < 30 seconds for 10,000 LOC
- **Memory efficient**: Streaming file processing
- **Git integration**: Supports incremental mode (analyze only changed files)

## Implementation Status

🚧 **Currently in development** - Wave 1 (Foundation) complete

### Completed (Wave 1):
- ✅ Data models
- ✅ Configuration loader
- ✅ Utility functions

### Planned (Wave 2-6):
- ⏳ Detection engines
- ⏳ Metrics calculation
- ⏳ Report generation
- ⏳ CLI interface

---

**Estimated completion**: Waves 2-6 (~62 hours remaining)
**Next session**: Execute Wave 2 (Detection Engines)
