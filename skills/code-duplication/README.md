# Code Duplication Analysis Skill

Deep analysis of codebase for code duplication. Detects exact, structural, and pattern-level duplicates, generates comprehensive reports with refactoring suggestions and metrics.

## Features

- **🔴 Exact Duplicate Detection** - Hash-based detection of identical code blocks
- **🟡 Structural Duplicate Detection** - AST-based detection of functionally identical code with different names
- **🔵 Pattern Duplicate Detection** - Regex-based detection of common anti-patterns (12 patterns)
- **📊 Comprehensive Metrics** - LOC analysis, duplication percentage, trend analysis
- **🗺️ Heatmap Visualization** - Visual representation of duplication across codebase
- **💡 Refactoring Suggestions** - Actionable recommendations with implementation steps
- **📄 Multiple Output Formats** - Markdown reports and CSV exports

## Quick Start

```bash
# Analyze current directory
/code-duplication .

# Analyze specific directory
/code-duplication /path/to/project

# Analyze with Python only
/code-duplication /path/to/project --language python

# Multiple languages
/code-duplication /path/to/project --language python javascript typescript
```

## Usage

### Detection Modes

```bash
# Run all detection engines (default)
/code-duplication /path/to/project

# Only exact duplicates (faster)
/code-duplication /path/to/project --exact-only

# Only structural duplicates
/code-duplication /path/to/project --structural-only

# Only pattern duplicates
/code-duplication /path/to/project --pattern-only
```

### Output Options

```bash
# Custom output path
/code-duplication /path/to/project --output report.md

# Export to CSV for data analysis
/code-duplication /path/to/project --csv duplicates.csv

# Limit duplicates in report
/code-duplication /path/to/project --max-duplicates 20

# Quiet mode (no progress indicators)
/code-duplication /path/to/project --quiet
```

### Filtering

```bash
# Exclude patterns
/code-duplication /path/to/project --exclude "**/test_*.py" "**/__pycache__/**"

# Configure thresholds
/code-duplication /path/to/project --min-lines 10 --min-chars 100
```

## How It Works

### 1. Exact Duplicate Detection

Hash-based comparison after code normalization (Python tokenize, JavaScript regex).

### 2. Structural Duplicate Detection

AST-based comparison - finds code with identical logic but different variable names.

### 3. Pattern Duplicate Detection

Regex matching for 12 common anti-patterns (try-catch-logging, null-check, env-var-access, etc.).

## Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Code Duplication Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Path: /home/user/project

✅ Scanning files (127 found) - 0.1s
✅ Reading files (127 found) - 0.3s
✅ Detecting exact duplicates (15 found) - 2.4s
✅ Detecting structural duplicates (8 found) - 3.1s
✅ Detecting pattern duplicates (23 found) - 1.2s
✅ Calculating metrics - 0.1s
✅ Generating report - 0.2s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Analysis Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files analyzed: 127
Total LOC: 15,432
Duplicate LOC: 1,234
Duplication: 8.00%

Duplicate blocks found: 46
  - Exact: 15
  - Structural: 8
  - Pattern: 23

📄 Report: /home/user/project/duplication-report.md

✅ Good - Low duplication, minor cleanup opportunities
```

## Report Structure

The generated markdown report includes:

- **📊 Executive Summary** - Metrics, assessment, top offenders, heatmap
- **📋 Duplicate Blocks** - Detailed listings with code samples and refactoring suggestions
- **💡 Recommendations** - Priority actions grouped by difficulty (easy/medium/hard)

## Dependencies

- **Python 3.7+** (required)
- **Zero external dependencies** - Uses only Python stdlib

## Development Status

✅ **Complete** - All features implemented and tested

## Technical Details

See full documentation in README.md for:
- Architecture overview
- Data models
- Pattern catalog
- Performance benchmarks
- Development guide
