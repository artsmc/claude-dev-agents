---
name: document-hub-read
description: Read and summarize the current state of the documentation hub (cline-docs/). Provides a quick overview of system architecture, module responsibilities, technology stack, and glossary terms. Use this skill whenever the user asks about the project's documentation, wants to understand the architecture, asks "what does this project do", "show me the docs", or needs a quick onboarding summary. Also use before starting work to understand project context.
---

# Document Hub: Read

View and summarize the current documentation hub state.

**Helper Scripts Available** (canonical copies live in document-hub-initialize):
- `/home/artsmc/.claude/skills/document-hub-initialize/scripts/validate_hub.py` - Validates documentation structure

**Use this skill to** quickly understand a project's documentation without reading all files individually.

## What This Skill Does

Reads all documentation hub files and presents a structured summary:

1. Validates the hub structure
2. Extracts key information from each file
3. Presents an organized overview
4. Identifies any gaps or issues

## Decision Tree: When to Use This Skill

```
User wants to understand docs → Does hub exist?
    ├─ No → Suggest /document-hub initialize
    │
    └─ Yes → Read and summarize:
        1. Validate structure first
        2. Read all four core files
        3. Extract key sections
        4. Present formatted summary
        5. Identify any warnings/gaps
```

## Read Workflow

### Step 1: Validate Before Reading

Always validate first to catch structural issues:

```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/validate_hub.py /path/to/project
```

If validation returns warnings or errors, include them in the summary.

### Step 2: Read Core Files

Read all four core files:
- `systemArchitecture.md`
- `keyPairResponsibility.md`
- `glossary.md`
- `techStack.md`

### Step 3: Extract Key Information

From each file, extract:

**systemArchitecture.md:**
- High-level system description
- Number of Mermaid diagrams
- Key architectural components

**keyPairResponsibility.md:**
- Project purpose
- Number of documented modules
- Module names and responsibilities

**glossary.md:**
- Total number of terms
- Sample key terms (top 5-10)

**techStack.md:**
- Core technologies listed
- Infrastructure components
- Development tools

### Step 4: Present Summary

Format the summary in a clear, scannable structure. Read `references/output-format.md` for the full summary template and a complete example read operation (Python) before presenting output.

## Use Cases

### Quick Onboarding

When joining a project:
```
Developer: "What does this project do?"
→ Run /document-hub read
→ Get instant architecture + module overview
```

### Pre-Task Context

Before starting work:
```
Developer: "I need to understand the auth system"
→ Run /document-hub read
→ See auth module responsibility
→ Check glossary for domain terms
```

### Documentation Health Check

Periodic maintenance:
```
→ Run /document-hub read
→ Check for validation warnings
→ If drift detected, run /document-hub analyze
```

## Best Practices

- **Always validate first** - Catch structural issues
- **Present concisely** - Users want overview, not full content
- **Highlight warnings** - Draw attention to validation issues
- **Suggest actions** - If issues found, suggest next steps

## Common Pitfalls

❌ **Don't** just dump file contents - summarize them
❌ **Don't** skip validation - it catches important issues
❌ **Don't** hide warnings - users need to know about problems

✅ **Do** provide structured, scannable output
✅ **Do** include health status upfront
✅ **Do** suggest follow-up actions if needed

## What Comes Next

After reading:
- If gaps found → Suggest `/document-hub analyze` for detailed drift report
- If outdated → Suggest `/document-hub update` to refresh
- If invalid → Show specific errors and suggest fixes

## Helper Script Reference

**validate_hub.py** - Check documentation structure
```bash
python /home/artsmc/.claude/skills/document-hub-initialize/scripts/validate_hub.py /path/to/project
# Returns: {"valid": bool, "errors": [], "warnings": []}
```

See `/home/artsmc/.claude/skills/document-hub-initialize/scripts/README.md` for complete documentation.
