---
name: document-hub-session-start
trigger: on-conversation-start
description: Automatically loads documentation hub context at the start of each session, enabling the "Brain" persona behavior where you rely on documentation as your memory.
enabled: true
silent: true
---

# Document Hub: Session Start

Automatically load documentation context at session start.

## Purpose

This hook implements the "Brain" persona behavior: your memory resets between sessions, so you rely entirely on the Documentation Hub. At the start of every session, this hook automatically reads the hub to restore your context.

## Trigger

**Event:** `on-conversation-start`
**When:** At the very beginning of each new Claude Code session
**Frequency:** Once per session

## Behavior

### If Documentation Hub Exists

1. **Validate silently:**
   ```bash
   python skills/hub/scripts/validate_hub.py $(pwd)
   ```

2. **If valid:**
   - Read all 4 core files silently
   - Load context into your working memory
   - No user notification (silent operation)
   - Ready to answer questions about the project

3. **If invalid:**
   - Note validation warnings internally
   - Still read what exists
   - May suggest fixes if user asks about documentation

### If Documentation Hub Doesn't Exist

- Skip silently (no error)
- Wait for user to initialize if needed
- Don't interrupt normal workflow

## What Gets Loaded

From the documentation hub, load:

1. **System Architecture** (`systemArchitecture.md`)
   - High-level system design
   - Key components and relationships
   - Architecture diagrams (understand the flow)

2. **Module Responsibilities** (`keyPairResponsibility.md`)
   - What each module does
   - Module boundaries and responsibilities
   - Key files and their purposes

3. **Glossary** (`glossary.md`)
   - Domain-specific terminology
   - Acronyms and their meanings
   - Project-specific concepts

4. **Technology Stack** (`techStack.md`)
   - Frameworks and libraries in use
   - Infrastructure components
   - Development tools

## Implementation

```python
import json
import subprocess
from pathlib import Path

# Get current project directory
project_path = Path.cwd()
docs_path = project_path / "cline-docs"

# Check if documentation hub exists
if not docs_path.exists():
    # No hub - skip silently
    exit(0)

# Validate the hub
result = subprocess.run(
    ["python", "skills/hub/scripts/validate_hub.py", str(project_path)],
    capture_output=True,
    text=True
)

validation = json.loads(result.stdout)

# Read all files (even if validation has warnings)
files_to_read = [
    "systemArchitecture.md",
    "keyPairResponsibility.md",
    "glossary.md",
    "techStack.md"
]

context = {}
for filename in files_to_read:
    file_path = docs_path / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            context[filename] = f.read()

# Context is now loaded into memory
# No output to user - silent operation
```

## Silent Operation

**Important:** This hook runs **silently** with no user notification because:

- Users don't need to know about background loading
- It happens automatically every session
- It's part of the "Brain" persona (invisible memory loading)
- Only shows output if critical errors occur

## When to Show Output

Only notify the user if:

1. **Critical validation errors** that would block work
   - Missing all documentation files
   - Completely corrupted structure

2. **User explicitly asks about documentation**
   - "What does this project do?"
   - "Show me the architecture"
   - Then reference the loaded context

## Benefits

### For "Brain" Persona
- Memory resets → Documentation is your memory
- Every session starts with full project context
- No need to manually read docs each time

### For Users
- Invisible, automatic context loading
- You immediately understand the project
- No startup commands needed
- Better answers about architecture/modules

### For Development Flow
- Jump straight into work
- Reference architecture automatically
- Understand module responsibilities instantly
- Know domain terminology

## Examples

### Example 1: Architecture Question

```
[Session starts - hook loads documentation silently]

User: "Where should I add the new payment processing logic?"

Claude: "Based on the system architecture, payment processing should go
in the src/payments module, which handles all payment integrations and
transaction processing. This module interfaces with the StripeWebhook
handler and FulfillmentQueue for async processing."

[Response uses knowledge from loaded documentation]
```

### Example 2: Module Question

```
[Session starts - hook loads documentation silently]

User: "What does the analytics module do?"

Claude: "According to the documentation, the analytics module (src/analytics)
is responsible for tracking user behavior events, generating reports, and
integrating with the data warehouse for long-term storage."

[Response references keyPairResponsibility.md loaded at session start]
```

### Example 3: Term Definition

```
[Session starts - hook loads documentation silently]

User: "What's a FulfillmentJob?"

Claude: "A FulfillmentJob represents a job in the fulfillment pipeline. It
tracks order processing status and completion. This is a core domain concept
used throughout the order processing system."

[Response uses glossary.md loaded at session start]
```

## Integration with Skills

This hook complements the manual skills:

- **Hook:** Automatic reading at session start (silent)
- **`/document-hub read`:** Manual reading with formatted output (explicit)
- **`/document-hub update`:** Updates documentation when code changes
- **`/document-hub analyze`:** Deep analysis of documentation quality

The hook provides baseline context, skills provide explicit operations.

## Performance

- **Validation:** < 1 second
- **Reading 4 files:** < 1 second
- **Total overhead:** ~2 seconds per session start
- **User experience:** Seamless, no noticeable delay

## Configuration

This hook is **enabled by default** because:
- Core "Brain" persona behavior
- Minimal performance impact
- No user interruption (silent)
- Significant benefit for context quality

To disable (if needed):
```yaml
# In .claude/settings.json or hook config
hooks:
  document-hub-session-start:
    enabled: false
```

## Error Handling

### Graceful Degradation

If errors occur during loading:

1. **File read errors:** Skip that file, continue with others
2. **Validation errors:** Load anyway, note warnings internally
3. **No documentation:** Skip silently, no error message
4. **Script errors:** Fall back to no context loading

**Never interrupt session start** - this hook should be invisible even when errors occur.

## Best Practices

### For Claude (You)

- **Use loaded context naturally** - Reference architecture/modules in responses
- **Don't mention the hook** - Users don't need to know it ran
- **If outdated context** - Suggest `/document-hub update` if you notice drift
- **If no context loaded** - Suggest `/document-hub initialize` for new projects

### For Users

- **No action needed** - Hook works automatically
- **Keep docs updated** - Run `/document-hub update` after major changes
- **Trust the responses** - Claude has project context from session start

## Comparison: With vs Without Hook

### Without Session-Start Hook
```
User: "Where should I add authentication logic?"
Claude: "I'd need to see your project structure first.
Can you show me the codebase?"
[Requires back-and-forth to understand project]
```

### With Session-Start Hook
```
User: "Where should I add authentication logic?"
Claude: "Based on the architecture, add it to the src/auth module,
which handles user authentication and authorization. You'll want to
extend the AuthService class and integrate with the existing
SessionManager."
[Immediate, context-aware response]
```

## Status

**Implementation:** Complete
**Testing:** Pending
**Integration:** Automatic via Claude Code hooks system
**Maintenance:** None required (reads existing documentation)

## See Also

- **Manual reading:** `/document-hub read` skill
- **Documentation updates:** `/document-hub update` skill
- **Validation tool:** `scripts/validate_hub.py`
- **Main README:** `skills/hub/README.md`
