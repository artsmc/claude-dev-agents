---
name: memorybank-initialize
description: Bootstrap a new project's Memory Bank by creating the six core files with templates and gathering initial project information from the user. Also the entry point to initialize/set up project documentation in a new or freshly cloned repo — including bootstrapping BOTH Brain systems (Memory Bank + Document Hub) at once.
---

# Memory Bank: Initialize

Bootstrap a new project with complete Memory Bank structure.

**Helper Scripts Available:**
- `scripts/validate_memorybank.py` - Validates structure

## What It Does

Creates Memory Bank structure in `memory-bank/` directory:

```
project-root/
└── memory-bank/
    ├── projectbrief.md         # Foundation (goals, scope)
    ├── productContext.md       # User experience & vision
    ├── techContext.md          # Technologies & setup
    ├── systemPatterns.md       # Architecture & patterns
    ├── activeContext.md        # Current work focus
    └── progress.md             # Status & learnings
```

## Workflow

1. **Check if exists:** Validate memory-bank doesn't already exist
2. **Create directory:** Make `memory-bank/` folder
3. **Create 6 files:** Use templates for each file
4. **Gather info:** Prompt user for initial project details
5. **Validate:** Run `validate_memorybank.py`

## File Templates

Starter templates for all six files live in `references/templates/` (`projectbrief.md`, `productContext.md`, `techContext.md`, `systemPatterns.md`, `activeContext.md`, `progress.md`). Read the relevant template file when creating each Memory Bank file.

## Bootstrapping both systems at once (formerly /documentation-start)

To initialize BOTH Brain systems in one pass: run this skill first (skip if `memory-bank/` already has all 6 files), then run `/document-hub-initialize` (skip if `cline-docs/` already has its 4 files). Re-run either to force re-initialization if a system is present but incomplete.

## Tool Usage

```bash
# After creating files, validate
python3 scripts/validate_memorybank.py /path/to/project
```

See `scripts/README.md` for complete documentation.
