---
name: memory-bank-session-start
trigger: on-conversation-start
description: Automatically loads Memory Bank context at session start, implementing "Brain" persona where documentation serves as your memory between sessions.
enabled: true
silent: true
---

# Memory Bank: Session Start

Automatically load Memory Bank context at session start.

## Purpose

Implements "Brain" persona: memory resets between sessions, so you rely on the Memory Bank. At session start, automatically read the entire Memory Bank to restore context.

## Trigger

**Event:** `on-conversation-start`
**When:** Start of each new Claude Code session
**Frequency:** Once per session

## Behavior

### If Memory Bank Exists

1. **Validate silently:**
   ```bash
   python skills/memory-bank/scripts/validate_memorybank.py $(pwd)
   ```

2. **Read files in hierarchical order:**
   - projectbrief.md → Foundation
   - productContext.md, techContext.md, systemPatterns.md → Context
   - activeContext.md → Current work
   - progress.md → Status

3. **Load context silently:**
   - No user notification
   - Context ready for immediate use

4. **If validation warnings:**
   - Note internally
   - Don't interrupt session start

### If Memory Bank Doesn't Exist

- Skip silently
- No error message
- Wait for user to initialize if needed

## What Gets Loaded

1. **Project Brief** - Goals, objectives, scope
2. **Product Context** - User problems, features, vision
3. **Technical Context** - Stack, dependencies, constraints
4. **System Patterns** - Architecture, decisions, patterns
5. **Active Context** - Current focus, blockers, next steps
6. **Progress** - What's working, what's left, status

## Silent Operation

Runs **silently** with no output because:
- Background memory loading
- Part of "Brain" persona (invisible)
- Only show output for critical errors

## Implementation

```python
import json
import subprocess
from pathlib import Path

project_path = Path.cwd()
memory_path = project_path / "memory-bank"

if not memory_path.exists():
    exit(0)  # Skip silently

# Validate
result = subprocess.run(
    ["python", "skills/memory-bank/scripts/validate_memorybank.py", str(project_path)],
    capture_output=True, text=True
)
validation = json.loads(result.stdout)

# Read all files in order
files_to_read = [
    "projectbrief.md",
    "productContext.md",
    "techContext.md",
    "systemPatterns.md",
    "activeContext.md",
    "progress.md"
]

for filename in files_to_read:
    file_path = memory_path / filename
    if file_path.exists():
        with open(file_path, 'r') as f:
            # Context loaded into memory
            pass
```

## Benefits

- **"Brain" persona:** Documentation as memory
- **Immediate context:** Understand project from first message
- **No manual commands:** Automatic loading
- **Seamless:** Invisible to user

## Performance

- **Validation:** < 1 second
- **Reading 6 files:** < 2 seconds
- **Total:** ~3 seconds overhead
- **User experience:** Seamless

## Example

```
[Session starts - hook loads memory bank silently]

User: "What should I work on next?"

Claude: "Based on activeContext.md, you're currently implementing
the payment processing API. Next steps are to add error handling
and integrate with the webhook system. The main blocker is waiting
for Stripe API credentials."

[Response uses loaded context automatically]
```

## Integration with Skills

- **Hook:** Automatic reading (silent)
- **`/memorybank read`:** Manual reading with output
- **`/memorybank update`:** Update after changes
- **`/memorybank sync`:** Quick updates after tasks

## Configuration

Enabled by default. To disable:
```yaml
hooks:
  memory-bank-session-start:
    enabled: false
```

## Error Handling

Graceful degradation:
- File read errors → Skip that file, continue
- Validation errors → Load anyway, note warnings
- No memory bank → Skip silently
- Script errors → Fall back to no context

**Never interrupt session start.**

See `skills/memory-bank/README.md` for complete documentation.
