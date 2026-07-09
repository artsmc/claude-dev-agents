---
name: document-hub-analyze
description: Deep analysis of codebase vs documentation alignment (cline-docs/). Detects drift, identifies undocumented code, extracts missing glossary terms, and provides actionable recommendations without making changes. Use this skill when the user asks "are the docs up to date", "check documentation quality", "what's missing from the docs", or wants a read-only audit before deciding what to update. For actually making changes, use document-hub-update instead.
---

# Document Hub: Analyze

Analyze documentation quality and detect drift from the actual codebase. This is a read-only diagnostic: report problems and recommendations, make no changes. Suggest `/document-hub update` if drift is detected.

**Helper Scripts** — canonical copies live in `/home/artsmc/.claude/skills/document-hub-initialize/scripts/` (see its `README.md` for full docs):
- `detect_drift.py <project>` - module + technology drift (JSON: drift scores + specific gaps)
- `extract_glossary.py <project>` - ranked undocumented domain terms with contexts
- `validate_hub.py <project>` - structure validation (JSON: structural issues)

## Analysis Workflow

Run all six phases, then present findings without making changes.

### Phase 1: Validation Check

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/validate_hub.py /path/to/project
```

If validation fails: report structural errors, recommend fixing before analyzing content, and exit early if the hub doesn't exist.

### Phase 2: Module Drift

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/detect_drift.py /path/to/project
```

Returns:

```json
{
  "drift_score": 0.23,
  "module_drift": {
    "undocumented": ["analytics", "webhooks"],
    "documented_but_missing": ["legacy"]
  }
}
```

- `undocumented` → code exists (src/) but not in keyPairResponsibility.md
- `documented_but_missing` → docs reference non-existent code

### Phase 3: Technology Drift

Same `detect_drift.py` output:

```json
{
  "technology_drift": {
    "undocumented": ["Redis", "BullMQ"],
    "documented_but_missing": ["MongoDB"]
  }
}
```

Check `package.json`/`requirements.txt` vs techStack.md; identify when tech was added (git log) and whether it is actually in use.

### Phase 4: Glossary Gaps

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/extract_glossary.py /path/to/project
```

Returns ranked terms from the codebase. Read the existing `cline-docs/glossary.md`, identify terms in code but not in the glossary, rank by the script's importance score, and recommend the top 10-20 additions.

### Phase 5: Health Scoring

`Health Score = 100 - (drift_score * 100)`

| Score | Drift | Rating | Action |
|---|---|---|---|
| 90-100 | < 0.10 | Excellent - minor gaps only | continue monitoring |
| 75-89 | 0.10-0.25 | Good - easy to fix | update as needed |
| 60-74 | 0.25-0.40 | Needs Attention - significant gaps | schedule update next sprint |
| < 60 | > 0.40 | Poor - major documentation debt | run `/document-hub update` now |

Regardless of score, immediate action is needed for drift > 0.35, multiple undocumented core modules, or broken cross-references.

### Phase 6: Recommendations

Prioritize by impact:

- **HIGH**: undocumented modules with many files; missing critical technologies (databases, frameworks); broken cross-references
- **MEDIUM**: documented-but-missing code; complex diagrams needing split; missing glossary terms for core concepts
- **LOW**: minor tech stack updates; formatting inconsistencies; additional glossary terms

## Report Format

The full report template (section structure with sample output) and a complete Python example that runs all three scripts and assembles the report live in `references/report-format.md` — read it before presenting findings.

## Use Cases

- **Pre-update health check** - run before `/document-hub update` to understand scope and prioritize changes
- **Periodic audit** (monthly/quarterly) - track health score trend, address high-priority items
- **Onboarding validation** - when taking over a project, gauge documentation completeness and identify knowledge gaps

## Best Practices & Pitfalls

- ✅ Run before updating; use findings to guide updates; track health score trends over time
- ✅ Prioritize high-impact recommendations - don't try to fix everything at once
- ❌ Don't make changes during analysis - this is read-only
- ❌ Don't ignore high-priority items - they indicate real gaps
- ❌ Don't run too frequently - analysis is for planning, not continuous monitoring
