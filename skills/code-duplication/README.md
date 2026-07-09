# /code-duplication

> Deep analysis of codebase for code duplication. Detects exact, structural, and pattern-level duplicates, generates comprehensive reports with refactoring suggestions and metrics.

## What it does

Scans a codebase with three detection engines — exact (hash-based), structural (AST-based), and pattern (regex anti-patterns) — then writes a markdown report (`duplication-report.md`) with duplication percentage, top offenders, a file heatmap, and concrete refactoring suggestions. Analysis-only; never edits code. Pure Python stdlib, no dependencies.

## When it triggers

- "How much duplication is in this codebase?"
- "Find copy-pasted code in src/"
- "What refactoring would reduce our LOC the most?"
- "Run a duplication report before the refactor"
- `/code-duplication` invoked directly

## Context cost

Description always in context (~0.2k chars); SKILL.md body loads on trigger (~4k chars); no `references/` dir — this README and `scripts/` never load into model context.

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

## Configuration

CLI flags cover most needs (`--min-lines`, `--min-chars`, `--exclude`, `--language`). A `.duplication-config.json` in the project root (or any parent directory) is discovered automatically by `scripts/config_loader.py` — there is no `--config` CLI flag.

## Dependencies

- **Python 3.7+** (required)
- **Zero external dependencies** - Uses only Python stdlib

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill instructions (loads on trigger) |
| `skill.sh` | Entry point wrapper around `scripts/cli.py` |
| `scripts/cli.py` | CLI with full argument parsing |
| `scripts/exact_detector.py`, `structural_detector.py`, `pattern_detector.py` | The three detection engines |
| `scripts/file_discovery.py`, `gitignore_parser.py`, `git_integration.py` | File scanning, .gitignore handling, incremental (changed-files) mode |
| `scripts/metrics_calculator.py`, `heatmap_renderer.py`, `suggestion_engine.py`, `report_generator.py` | Metrics, heatmap, refactoring suggestions, markdown/CSV output |
| `scripts/models.py`, `config_loader.py`, `utils.py` | Data models, `.duplication-config.json` loader, helpers |
| `scripts/duplication-report.md` | Sample report output |

## Related skills

- **architecture-quality-assess** — structural/architecture scoring (layers, SOLID, coupling); use it when the question is architecture health rather than duplicated code
- **security-quality-assess** — OWASP vulnerability scanning of the same codebases
- **start-phase-execute** — execute the refactoring work the report suggests
