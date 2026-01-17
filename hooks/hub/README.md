# Document Hub Hooks

Automatic behaviors that maintain the "Brain" persona and proactive documentation management.

## Implemented Hooks

### ✅ document-hub-session-start.md

**Trigger:** Start of every Claude Code session
**Status:** ✅ Implemented
**Enabled:** Yes (by default)
**Silent:** Yes (no user notification)

**What It Does:**
- Automatically reads the documentation hub at session start
- Loads system architecture, module responsibilities, glossary, and tech stack
- Validates documentation structure
- Provides instant project context
- Implements "Brain" persona (documentation as memory)

**Benefits:**
- No manual `/document-hub read` needed
- Immediate context-aware responses
- Seamless onboarding experience
- Understanding of architecture from first message

**Performance:** ~2 seconds overhead per session start

**See:** `document-hub-session-start.md` for complete documentation

---

## Future Hooks (Not Implemented)

### ⏳ document-hub-task-complete.md

**Trigger:** After completing significant tasks
**Status:** ⏳ Planned (Phase 2)
**Purpose:** Suggest `/document-hub update` when architecture changes detected

**Why Not Implemented Yet:**
- Risk of notification fatigue
- Needs careful tuning to avoid false positives
- Users can manually run `/document-hub update` when needed

**Potential Implementation:**
- Check if task involved architecture files
- Detect new modules added
- Suggest update only for high-impact changes
- Allow user to disable per-project

---

### ⏳ document-hub-file-watch.md

**Trigger:** When files in `cline-docs/` are modified
**Status:** ⏳ Planned (Phase 2)
**Purpose:** Validate documentation on save

**Why Not Implemented Yet:**
- Most edits are via skills (which validate already)
- Manual edits are rare
- Can be added if users request it

**Potential Implementation:**
- Run `validate_hub.py` on save
- Show validation errors immediately
- Prevent broken cross-references
- Catch Mermaid syntax errors

---

### ⏳ document-hub-module-tracker.md

**Trigger:** When new directories are created in `src/`
**Status:** ⏳ Planned (Phase 3)
**Purpose:** Extract glossary terms from new modules

**Why Not Implemented Yet:**
- Low priority
- Can be done manually via `/document-hub update`
- Needs sophisticated file system watching

**Potential Implementation:**
- Detect new `src/` subdirectories
- Run `extract_glossary.py` on new code
- Suggest adding terms to glossary
- Background operation

---

## Hook Philosophy

### What We Implemented

**Only the session-start hook** because:
- ✅ Core "Brain" persona behavior
- ✅ No notification fatigue (silent)
- ✅ High value, low overhead
- ✅ Works for 100% of users

### What We Didn't Implement

**Task-complete and file-watch hooks** because:
- ⚠️ Risk of notification fatigue
- ⚠️ Users can invoke skills manually
- ⚠️ Needs per-project tuning
- ⚠️ Better to start minimal, add later if needed

### When to Add More Hooks

Consider implementing additional hooks if:
- Users consistently forget to update docs
- Documentation drift becomes common
- Users explicitly request automatic behavior
- We can avoid notification fatigue

---

## Configuration

### Enable/Disable Session-Start Hook

The session-start hook is enabled by default. To disable:

```yaml
# In .claude/settings.json or hook configuration
hooks:
  document-hub-session-start:
    enabled: false
```

### Per-Project Configuration

You can disable hooks per-project:

```yaml
# In project/.claude/settings.local.json
hooks:
  document-hub-session-start:
    enabled: false
```

This is useful for:
- Projects without documentation hubs
- Projects where you don't want automatic loading
- Testing/debugging scenarios

---

## How Hooks Work with Skills

Hooks and skills work together:

| Component | Type | Trigger | User Visible |
|-----------|------|---------|--------------|
| **session-start hook** | Automatic | Every session | No (silent) |
| `/document-hub read` | Manual skill | User invokes | Yes (formatted output) |
| `/document-hub update` | Manual skill | User invokes | Yes (shows changes) |
| `/document-hub analyze` | Manual skill | User invokes | Yes (detailed report) |

**Hook provides baseline context, skills provide explicit operations.**

---

## Testing Hooks

### Test Session-Start Hook

1. **Create a test project with documentation:**
   ```bash
   cd /tmp/test-project
   mkdir -p cline-docs
   # Create basic documentation files
   ```

2. **Start a new Claude Code session:**
   ```bash
   claude-code
   ```

3. **Verify context is loaded:**
   - Ask: "What does this project do?"
   - Claude should reference documentation
   - No explicit read command needed

4. **Check performance:**
   - Session start should feel instant
   - No noticeable delay from hook

### Test Hook Graceful Degradation

1. **Test with no documentation:**
   ```bash
   cd /tmp/empty-project
   claude-code
   # Hook should skip silently
   ```

2. **Test with invalid documentation:**
   ```bash
   cd /tmp/broken-docs
   echo "invalid" > cline-docs/systemArchitecture.md
   claude-code
   # Hook should load what it can, no crash
   ```

---

## Troubleshooting

### Hook Not Running

**Check:**
1. Hook file exists: `hooks/hub/document-hub-session-start.md`
2. Hook is enabled in settings
3. Claude Code recognizes the hook trigger

**Debug:**
- Check Claude Code logs
- Verify frontmatter has correct trigger
- Test manually with `/document-hub read`

### Performance Issues

**If session start feels slow:**
1. Check documentation hub size
2. Verify validation script completes quickly
3. Consider disabling hook for large projects

**Typical performance:**
- Small projects (< 10 files): < 1 second
- Medium projects (< 100 files): 1-2 seconds
- Large projects (> 1000 files): 2-3 seconds

### Context Not Loaded

**If Claude doesn't seem to have context:**
1. Verify documentation hub exists
2. Check files aren't empty
3. Run `/document-hub read` manually to verify content
4. Check hook is enabled

---

## Future Enhancements

Potential improvements to session-start hook:

### Smart Caching
- Cache documentation content
- Only reload if files changed
- Speed up repeat session starts

### Lazy Loading
- Load only on first documentation question
- Reduce startup overhead
- Better for projects with large docs

### Selective Loading
- Load only systemArchitecture.md by default
- Load other files on-demand
- Faster for quick sessions

### Context Summarization
- Generate brief summary of documentation
- Load summary instead of full content
- Reduce context window usage

---

## Statistics

### Current Implementation

- **Hooks Implemented:** 1/4 planned
- **Coverage:** Session-start only
- **Status:** Production-ready
- **User Impact:** High value, zero friction

### Planned Additions

- **Phase 2:** Task-complete hook (optional, user-configurable)
- **Phase 3:** File-watch hook (if requested)
- **Phase 4:** Module-tracker hook (advanced feature)

---

## See Also

- **Skills documentation:** `../skills/hub/README.md`
- **Tool documentation:** `../skills/hub/scripts/README.md`
- **Migration guide:** `../commands/_deprecated/MIGRATION.md`
- **Planning documents:** `../planning/`

---

## Status: Phase 2 Partial Implementation ✅

**What's Done:**
- ✅ Session-start hook (core "Brain" behavior)
- ✅ Silent, automatic context loading
- ✅ Minimal user disruption
- ✅ Production-ready

**What's Deferred:**
- ⏳ Task-complete hook (notification risk)
- ⏳ File-watch hook (low priority)
- ⏳ Module-tracker hook (advanced feature)

**Rationale:** Start minimal, add more automation only if users request it. The session-start hook provides 80% of the value with 20% of the complexity.
