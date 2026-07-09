---
name: architecture-quality-assess
description: Assess and score codebase architecture health — layer separation, SOLID compliance, module coupling (FAN-IN/FAN-OUT), circular dependencies, drift from documented patterns. Use whenever the user asks to assess/review/grade architecture quality, wants an architecture score, or asks how healthy the codebase's architecture is. Analysis-only report + refactoring tasks; for docs-vs-code drift use document-hub-analyze.
---

# Architecture Quality Assessment

Static-analysis pipeline that scores a codebase's architecture (0-100) and reports violations with file:line detail and fix recommendations. Analysis-only — never edits code. Supports Python and JS/TS projects (Next.js, React, Vue, Express, NestJS, FastAPI, Django, Flask).

## Workflow

1. **Run the assessment**:
   ```bash
   bash ~/.claude/skills/architecture-quality-assess/skill.sh [PROJECT_PATH] [OPTIONS]
   ```
   The project root must contain a manifest (package.json, requirements.txt, or pyproject.toml) or project detection fails.

2. **CLI options** (verified against `scripts/assess.py --help` — trust this table over older docs):

   | Option | Meaning | Default |
   |---|---|---|
   | `project_path` | Directory to analyze | `.` |
   | `--format {markdown,json,tasks,all}` | Report format(s) | `markdown` |
   | `--output`, `-o` | Output file path | `<project>/architecture-assessment.{md,json}` |
   | `--severity {critical,high,medium,low}` | Minimum severity reported | `low` |
   | `--verbose`, `-v` | Detailed progress | off |
   | `--no-cache` | Force full re-parse | caching on |
   | `--list-analyzers` | List analyzers and exit | — |

   Caution: README.md mentions `--incremental`, `--cache`, `--generate-tasks`, and `--config`; those flags do NOT exist in assess.py. Use `--format tasks` for the task list.

3. **Read the report** (`architecture-assessment.md` in the project root): overall score, then violations by severity (critical → low), each with file, line, and recommendation. Exit code is 1 when critical violations exist — usable directly as a CI gate (`--format json --severity critical`).

4. **Optional follow-ups**:
   - `--format tasks` (or `all`) writes `architecture-refactoring-tasks.md`, consumable by `/start-phase-execute` and `/pm-db import`.
   - Drift detection runs automatically when `memory-bank/systemPatterns.md` / `systemArchitecture.md` exist in the project.

## What it analyzes

Seven analyzers: project/framework detection, layer separation (Clean Architecture), SOLID (all 5 principles), design patterns and anti-patterns, coupling metrics + circular dependencies, code organization, and memory-bank drift.

## Docs and references (read on demand)

- `README.md` (this dir) — user guide: use cases, score/severity/metric interpretation, `.architecture-assess.json` config basics, skill integrations (memory-bank, pm-db, document-hub), GitHub Actions CI example, troubleshooting, best practices, FAQ.
- `USAGE_GUIDE.md` (this dir) — command walkthroughs and workflow scripts: pre-refactor assessment, CI quality gate, weekly review, self-analysis.
- `references/analysis-details.md` — per-analyzer violation heuristics (SOLID rules, pattern/anti-pattern catalog, coupling thresholds, drift detection) with example output. Read when explaining why something was flagged.
- `references/report-formats.md` — full markdown/JSON report schemas and generated task-list format. Read when parsing JSON output or wiring CI checks.
- `references/operations.md` — optional deps (networkx, tree-sitter), full config-file schema, performance/caching notes, extra troubleshooting/FAQ, changelog. Read for setup or slow analysis.
