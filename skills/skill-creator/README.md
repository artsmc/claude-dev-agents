# /skill-creator

> Create new skills, modify and improve existing skills, and measure skill performance. Use for creating a skill from scratch, editing or optimizing an existing skill, running evals, benchmarking with variance analysis, or optimizing a skill's description for better triggering accuracy.

Upstream-maintained skill (Anthropic, MIT-style license in `LICENSE.txt`). Do not hand-edit SKILL.md casually — changes may be overwritten by upstream updates.

## What it does

Runs the full skill-development loop: interview the user about intent, draft the SKILL.md, generate realistic test prompts, run with-skill vs baseline subagents in parallel, grade outputs against assertions, aggregate into a quantitative benchmark, and present everything in a browser-based review UI. Feedback from the human review drives the next iteration. A separate automated loop optimizes the frontmatter description for triggering accuracy.

## When it triggers

- "I want to make a skill for X" / "turn this workflow into a skill"
- "improve the miro-diagram skill, it keeps missing the layout step"
- "run the evals for spec-plan and show me the results"
- "is the new version of this skill actually better?" (blind A/B comparison)
- "the skill isn't triggering when I ask about Y — fix the description"

## Usage

Invoke as `/skill-creator` or just describe the skill work. The core loop: draft → spawn test runs (with-skill + baseline in the same turn) → draft assertions while runs execute → grade → `python -m scripts.aggregate_benchmark` → launch `eval-viewer/generate_review.py` → read `feedback.json` → improve → repeat. Results live in a `<skill-name>-workspace/` sibling directory, one `iteration-N/` per pass.

Description optimization is its own sub-loop: generate ~20 should/should-not-trigger queries, review them via the `assets/eval_review.html` UI, then run `python -m scripts.run_loop` in the background — it splits train/test, evaluates trigger rates (3 runs per query), and iterates up to 5 description rewrites, picking the best by held-out test score.

## Context cost

Description always in context (~350 chars); SKILL.md body loads on trigger (~29k chars); on demand: `references/schemas.md` (~12k), `references/environments.md` (~5k, Claude.ai/Cowork adaptations), `agents/*.md` (read only when spawning that subagent).

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Full workflow: create → test → benchmark → iterate → optimize description |
| `references/schemas.md` | Exact JSON schemas for evals.json, eval_metadata.json, grading.json, benchmark.json |
| `references/environments.md` | Platform adaptations for Claude.ai and Cowork (no subagents, headless viewer, packaging) |
| `agents/grader.md` | Subagent instructions: evaluate assertions against run outputs |
| `agents/comparator.md` | Subagent instructions: blind A/B comparison of two skill versions |
| `agents/analyzer.md` | Subagent instructions: analyze benchmark patterns and why a winner won |
| `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/improve_description.py` | Description-optimization loop (trigger-rate eval + rewrite iterations) |
| `scripts/aggregate_benchmark.py`, `scripts/generate_report.py` | Roll per-run grading/timing into benchmark.json/md and HTML reports |
| `scripts/quick_validate.py`, `scripts/package_skill.py`, `scripts/utils.py` | Frontmatter validation, `.skill` packaging, shared helpers |
| `eval-viewer/generate_review.py`, `eval-viewer/viewer.html` | Browser review UI (Outputs + Benchmark tabs, feedback capture; `--static` for headless) |
| `assets/eval_review.html` | Template UI for reviewing/editing trigger-eval query sets |

## Related skills

- This is the only skill-authoring skill in the repo — its own description-optimization loop was used during the 2026-07 refactor of the other skills' descriptions.
- Do NOT confuse with `/verify` or `/code-review` — those check code changes; skill-creator's evals test skill behavior.
