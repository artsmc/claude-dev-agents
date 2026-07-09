# Operations: Setup, Performance, Configuration

Setup/tuning detail moved verbatim from SKILL.md. Read for installation of optional dependencies, slow-analysis tuning, or the full `.architecture-assess.json` schema.

**Version**: 1.0.0 · **Status**: Active · **Category**: Code Analysis & Quality · **License**: MIT · **Maintainer**: Claude Code Team

---

## Installation

This skill is installed by default in the Claude CLI skills directory:

```bash
~/.claude/skills/architecture-quality-assess/
```

### Requirements

**Core Dependencies** (No installation required):
- Python 3.8+
- Standard library: `ast`, `pathlib`, `json`, `re`, `dataclasses`

**Optional Dependencies** (Recommended):
- `networkx` - Enhanced graph algorithms for circular dependency detection
- `tree-sitter` - Advanced multi-language parsing (fallback available)

**Install optional dependencies:**
```bash
pip install networkx tree-sitter
```

---

---

## Performance

### Analysis Speed

**Small Project** (<100 files):
- Analysis time: <10 seconds
- Memory usage: ~50 MB

**Medium Project** (100-1000 files):
- Analysis time: 30-120 seconds
- Memory usage: ~200 MB

**Large Project** (1000-5000 files):
- Analysis time: 2-10 minutes
- Memory usage: ~500 MB

### Optimization Strategies

**Caching:**
- File parsing results cached (80% speedup on re-runs)
- AST analysis cached per file hash
- Dependency graph cached

**Incremental Analysis:**
- Git integration detects changed files
- Only re-analyzes modified modules
- 70%+ faster than full analysis

**Parallel Processing:**
- Multiple files parsed concurrently
- CPU-bound analysis distributed
- Scales with available cores

---

---

## Configuration

### Configuration File

**Location**: `.architecture-assess.json` (project root)

**Example:**
```json
{
  "exclude_paths": [
    "node_modules/",
    "dist/",
    "build/",
    ".next/",
    "__pycache__/",
    "*.test.ts",
    "*.spec.js"
  ],
  "severity_thresholds": {
    "critical": 0,
    "high": 5,
    "medium": 20
  },
  "rules": {
    "max_fan_out": 15,
    "max_file_loc": 500,
    "max_method_count": 10,
    "allow_sql_in_routes": false,
    "require_repository_pattern": true
  },
  "output": {
    "format": "markdown",
    "path": "docs/architecture-assessment.md",
    "generate_task_list": true
  },
  "integrations": {
    "memory_bank": {
      "enabled": true,
      "check_drift": true
    },
    "ci_cd": {
      "fail_on_critical": true,
      "comment_on_pr": true
    }
  }
}
```

---

---

## Extra Troubleshooting (not in README.md)

**"Parser error on file X"**
- **Cause**: Syntax error in source file
- **Fix**: File skipped automatically, check --verbose for details

## Extra FAQ (not in README.md)

**Q: How does it compare to SonarQube?**
A: Complements SonarQube. SonarQube focuses on bugs/security, this focuses on architecture patterns.

---

## Changelog

### Version 1.0.0 (2026-02-07)
- Initial release
- Multi-language project detection
- SOLID principles analysis
- Layer separation validation
- Coupling metrics calculation
- Circular dependency detection
- Markdown and JSON report output
- Task list generation
- Memory Bank integration

---
