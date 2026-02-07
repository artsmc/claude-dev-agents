# Code Duplication Analysis Skill

Automated detection and analysis of code duplication across your entire codebase.

## Overview

The Code Duplication Analysis Skill helps you:
- 🔍 **Detect** exact, structural, and pattern-level code duplicates
- 📊 **Quantify** technical debt with duplication metrics
- 💡 **Refactor** with actionable, specific refactoring suggestions
- 📈 **Track** duplication trends over time

## Quick Start

```bash
# Analyze entire project
/code-duplication

# Analyze specific directory
/code-duplication src/

# Custom output location
/code-duplication --output reports/duplication.md
```

## Features

### Multi-Type Detection

**Exact Duplicates**
- Finds copy-pasted code blocks
- Configurable minimum line threshold (default: 5-10 lines)
- Ignores comments and whitespace

**Structural Duplicates**
- AST-based analysis for Python and JavaScript
- Detects similar code with different variable names
- Adjustable similarity threshold

**Pattern Duplicates**
- Identifies repeated coding patterns
- Suggests opportunities for abstraction
- Extensible pattern catalog

### Comprehensive Reports

**Metrics**:
- Duplication percentage
- Total duplicate blocks
- LOC savings potential
- Per-file breakdown

**Visualizations**:
- Top offender files ranked by duplication
- File-level heatmap
- Trend analysis (with historical data)

**Actionable Suggestions**:
- Extract function
- Extract class
- Use helper utilities
- Apply DRY principle
- And more...

## Configuration

Create `.duplication-config.json`:

```json
{
  "min_lines": 7,
  "exclude_patterns": [
    "**/node_modules/**",
    "**/test_*.py",
    "**/__generated__/**"
  ],
  "similarity_threshold": 0.85,
  "languages": ["python", "javascript", "typescript", "go"]
}
```

## Command-Line Options

```bash
/code-duplication [path] [options]

Options:
  --config PATH          Path to configuration file
  --format FORMAT        Output format: markdown (default) or json
  --output PATH          Output file path (default: ./duplication-report.md)
  --min-lines N          Minimum lines for duplication (default: 7)
  --exclude PATTERN      Exclude pattern (can be repeated)
  --incremental          Analyze only git-modified files
  --verbose              Show detailed progress
```

## Example Output

```markdown
# Code Duplication Analysis Report

## Executive Summary
📊 Analysis Date: 2026-02-07
📁 Files Analyzed: 156 files
📏 Total LOC: 12,450
🔄 Duplicate LOC: 1,834 (14.7%)
🎯 Cleanup Potential: 1,200-1,500 LOC reduction

## Top 5 Files with Duplication

1. **src/services/user_service.py** - 340 LOC duplicated (23%)
   - 6 duplicate blocks found
   - Primary issue: Repeated authentication logic
   - Suggested: Extract to auth_utils.py

2. **src/api/handlers.py** - 245 LOC duplicated (18%)
   ...
```

## Performance

- **Small projects** (<5k LOC): < 5 seconds
- **Medium projects** (5-20k LOC): < 30 seconds
- **Large projects** (20-50k LOC): < 2 minutes
- **Very large projects** (>50k LOC): Use --incremental mode

## Development Status

🚧 **Wave 1 Complete** - Foundation established

Current capabilities:
- ✅ Data models defined
- ✅ Configuration system
- ✅ Utility functions

Coming in future waves:
- ⏳ Detection algorithms (Wave 2)
- ⏳ Metrics and analysis (Wave 3)
- ⏳ Report generation (Wave 3)
- ⏳ CLI interface (Wave 4)
- ⏳ Testing and documentation (Wave 5)

## Technical Specifications

- **Language**: Python 3.8+
- **Dependencies**: None (pure stdlib)
- **Platform**: Linux, macOS, Windows (WSL2)
- **License**: Part of Claude Code CLI

## Integration

Works seamlessly with:
- **PM-DB**: Track duplication cleanup tasks
- **Memory Bank**: Store baseline metrics
- **Git**: Incremental analysis mode
- **CI/CD**: Automated quality gates

## Roadmap

### Wave 2: Detection Engines (~12 hours)
- File discovery with .gitignore support
- Exact duplicate detector
- AST-based structural detector
- Pattern matching detector

### Wave 3: Analysis & Reporting (~10 hours)
- Metrics calculator
- Refactoring suggestion engine
- Markdown and JSON report generators

### Wave 4-6: Integration & Quality (~20 hours)
- CLI interface
- Error handling
- Testing suite
- Documentation

---

**Total remaining effort**: ~62 hours (Waves 2-6)
**Next milestone**: Wave 2 execution
