---
name: document-hub-initialize
description: Bootstrap a new project's documentation hub by creating the four core documentation files (systemArchitecture.md, keyPairResponsibility.md, glossary.md, techStack.md) with initial content based on codebase analysis.
---

# Document Hub: Initialize

Bootstrap a new project with a complete documentation hub structure.

**Helper Scripts Available**:
- `scripts/validate_hub.py` - Validates documentation structure
- `scripts/extract_glossary.py` - Extracts domain-specific terms from code
- `scripts/detect_drift.py` - Detects existing modules and technologies

**Always run scripts with `--help` or check scripts/README.md first** to understand their usage and output format.

## What This Skill Does

Creates the Documentation Hub file structure in a project's `cline-docs/` directory:

```
project-root/
└── cline-docs/
    ├── systemArchitecture.md      # High-level architecture diagrams
    ├── keyPairResponsibility.md   # Module responsibilities
    ├── glossary.md                # Domain-specific terms
    └── techStack.md               # Technologies used
```

## Decision Tree: When to Use This Skill

```
User wants to set up documentation → Does cline-docs/ exist?
    ├─ Yes → Run validation first
    │         ├─ Valid → Use /document-hub read instead
    │         └─ Invalid → Ask user: overwrite or skip?
    │
    └─ No → Initialize new hub:
        1. Create directory structure
        2. Detect technologies (detect_drift.py)
        3. Extract glossary terms (extract_glossary.py)
        4. Generate initial content
        5. Validate result (validate_hub.py)
```

## Initialization Workflow

### Step 1: Check Existing State

First, check if a documentation hub already exists:

```bash
# Check if cline-docs exists
ls project-root/cline-docs/

# If exists, validate it first
python scripts/validate_hub.py /path/to/project
```

If validation returns `"valid": false` with missing files, proceed with initialization.

### Step 2: Gather Project Information

Use helper scripts to analyze the project:

**Detect existing technologies and modules:**
```bash
python scripts/detect_drift.py /path/to/project
```

This returns JSON with:
- Actual modules found in `src/`
- Technologies detected from `package.json`/`requirements.txt`
- Configuration files present

**Extract domain-specific terms:**
```bash
python scripts/extract_glossary.py /path/to/project
```

This returns ranked terms with context from code comments.

### Step 3: Create Documentation Files

Create the four core files with initial content based on the gathered information.

**Templates:** starter templates for all four files live in `references/templates/` (`systemArchitecture.md`, `keyPairResponsibility.md`, `glossary.md`, `techStack.md`). Read the relevant template file when creating each doc file.

### Step 4: Populate with Detected Information

Use the JSON output from helper scripts to populate initial content:

1. **From detect_drift.py output:**
   - Add detected technologies to `techStack.md`
   - Add detected modules to `keyPairResponsibility.md`

2. **From extract_glossary.py output:**
   - Add top 20-30 terms to `glossary.md` alphabetically
   - Include contexts as definitions

### Step 5: Prompt User for Additional Context

After creating initial files, ask the user:

```
Documentation hub initialized with detected information.

Please provide additional context:
1. What is the primary purpose of this project?
2. Are there any key architectural decisions to document?
3. Any specific modules or workflows that need detailed explanation?

I can update the documentation with your input.
```

### Step 6: Validate Result

After initialization, always validate:

```bash
python scripts/validate_hub.py /path/to/project
```

Check that:
- `"valid": true`
- All required files exist
- No Mermaid syntax errors

## Example: Complete Initialization

A full end-to-end Python example of the 6-step workflow is in `references/example-initialization.md` — read it if you want a concrete script-driven walkthrough.

## Best Practices

- **Run detection scripts first** - Don't guess what's in the project
- **Use templates** - Ensure consistent structure across projects
- **Validate after creation** - Always run `validate_hub.py` at the end
- **Prompt for context** - Auto-detected info needs human input for completeness
- **Keep diagrams simple** - Initial architecture diagrams should be high-level

## Common Pitfalls

❌ **Don't** create documentation without analyzing the codebase first
❌ **Don't** overwrite existing valid documentation without user confirmation
❌ **Don't** create empty files - populate with at least template structure

✅ **Do** use helper scripts to gather information
✅ **Do** validate before and after
✅ **Do** ask user for additional context

## Bootstrapping both systems at once (formerly /documentation-start)

To initialize BOTH Brain systems in one pass: run this skill (skip if `cline-docs/` already has all 4 files), then run `/memory-bank-initialize` (skip if `memory-bank/` already has its 6 files). Re-run either to force re-initialization if a system is present but incomplete.

## What Comes Next

After initialization:
1. User reviews generated documentation
2. User provides additional context via prompts
3. Documentation is refined
4. Future updates use `/document-hub update` skill

## Helper Script Reference

Usage and JSON output shapes for validate_hub.py, detect_drift.py, and extract_glossary.py are in `references/script-reference.md` — read it before invoking a script; `scripts/README.md` has complete documentation.
