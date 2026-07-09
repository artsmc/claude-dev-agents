---
name: document-hub-update
description: Comprehensive review and update of the documentation hub (cline-docs/). Analyzes recent code changes, detects drift, validates structure, and proposes specific updates to keep documentation synchronized with the codebase. Use this skill whenever the user says "update the docs", "sync documentation with code", "docs are outdated", or after significant code changes. For read-only analysis without changes, use document-hub-analyze instead.
---

# Document Hub: Update

Intelligently update documentation based on code changes and drift detection.

**Helper Scripts** — canonical copies live in `/home/artsmc/.claude/skills/document-hub-initialize/scripts/` (see its `README.md` or `--help` for usage and output format):
- `analyze_changes.py` - Analyzes git history since last doc update
- `detect_drift.py` - Finds undocumented modules and technologies
- `validate_hub.py` - Validates documentation structure
- `extract_glossary.py` - Extracts new domain terms

## Decision Tree: Update Strategy

```
User requests update → Is this a git repository?
    ├─ Yes → Analyze changes since last doc update
    │         ├─ No changes → Check drift anyway (dependencies might have changed)
    │         └─ Changes detected → Categorize and scope update
    │
    └─ No git → Full drift analysis
        ├─ Low drift (<0.15) → Minor updates only
        ├─ Medium drift (0.15-0.35) → Focused updates
        └─ High drift (>0.35) → Comprehensive review needed
```

## Update Workflow

### Phase 1: Pre-Update Analysis

**Step 1: Validate Current State**

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/validate_hub.py /path/to/project
```

If validation fails, fix structural errors, broken cross-references, and invalid Mermaid diagrams before content updates.

**Step 2: Analyze Recent Changes**

Use git history to scope the update (returns JSON categorizing changes; auto-detects since last doc update, or pass a commit/date as second arg):

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/analyze_changes.py /path/to/project
```

**Step 3: Detect Drift**

Even with no recent changes, check for drift — undocumented modules, missing technologies, documented-but-removed code:

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/detect_drift.py /path/to/project
```

### Phase 2: Propose Updates

Based on analysis, propose specific updates to the user with priorities (high/medium/low).

### Phase 3: Execute Updates

Update each file systematically based on change analysis.

### Phase 4: Post-Update Validation

After making updates, always re-run `validate_hub.py` on the project.

## Best Practices

- **Present proposals** - Show user what will change before editing
- **Update incrementally** - One file at a time, validate between
