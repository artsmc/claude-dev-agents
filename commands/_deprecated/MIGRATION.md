# Document Hub Migration Guide

The monolithic `commands/document-hub.md` has been replaced with a modular system.

## What Changed

### Old Structure (Deprecated)
```
commands/
└── document-hub.md  ← Single command file with all logic
```

### New Structure (Current)
```
skills/hub/
├── document-hub-initialize.md   ← Skill for initialization
├── document-hub-update.md       ← Skill for updates
├── document-hub-read.md         ← Skill for reading
├── document-hub-analyze.md      ← Skill for analysis
└── scripts/
    ├── validate_hub.py          ← Validation tool
    ├── detect_drift.py          ← Drift detection
    ├── analyze_changes.py       ← Git analysis
    └── extract_glossary.py      ← Term extraction

hooks/hub/
├── document-hub-session-start.md    ← Auto-read on session start
├── document-hub-task-complete.md    ← Suggest updates after tasks
└── document-hub-file-watch.md       ← Validate architecture changes
```

## How to Use Now

### Command Invocations (Same as Before)

```bash
# Initialize documentation
/document-hub initialize

# Update documentation
/document-hub update

# Read documentation
/document-hub read

# Analyze documentation
/document-hub analyze
```

**Nothing changes for users!** The invocations are the same, but they now use the modular skills instead of the monolithic command.

## What You Gain

### 1. Intelligent Automation
- Python tools analyze your codebase
- Git-aware change detection
- Automatic drift detection
- Smart glossary extraction

### 2. Modular Architecture
- Each skill has focused purpose
- Tools are reusable
- Easy to extend

### 3. Better Validation
- Structure validation
- Mermaid syntax checking
- Cross-reference validation
- Complexity detection

### 4. Automatic Behavior (via Hooks)
- Auto-read documentation at session start
- Suggestions after task completion
- File-watch validation

## Migration Timeline

- ✅ **Phase 1 Complete** - Skills + Python tools implemented
- ⏳ **Phase 2 Next** - Hooks for automatic behavior
- ⏳ **Phase 3 Future** - Custom agents for complex operations

## "Brain" Persona

The original "Brain" persona concept (memory resets, relies on documentation) is now implemented via:

- **Skills** - Explicit documentation operations
- **Hooks** - Automatic session-start reading
- **Tools** - Intelligent analysis and validation

The behavior is the same, but the implementation is cleaner and more powerful.

## Backward Compatibility

If you have scripts or workflows that referenced the old command file, they will continue to work because:

1. Claude Code will use skills with matching names
2. The invocation format hasn't changed
3. The documentation hub structure is identical

## Need Help?

- **Skill documentation:** `skills/hub/README.md`
- **Tool documentation:** `skills/hub/scripts/README.md`
- **Planning docs:** `.claude/planning/`
