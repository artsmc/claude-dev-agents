# Memory Bank Refactoring Plan

## Executive Summary

Transform the monolithic `commands/memory-bank.md` into a modular system leveraging skills, hooks, and Python tools, following the same pattern used for document-hub.

**Current State:** Monolithic command file (87 lines, ~5.5 KB)

**Target State:** Modular system with:
- 4 user-invocable skills
- 4 Python tools (zero dependencies)
- 1-2 hooks (session-start + optional task-complete)
- Clear separation of concerns

---

## Analysis of Current Structure

### Current Components

1. **Persona Definition** - "Brain" character with memory-reset behavior
2. **Memory Bank Structure** - 6 core markdown files in hierarchy
3. **Commands** - `/memorybank initialize` and `/memorybank update`
4. **Standard Operating Procedure** - Read-Plan-Execute-Document loop
5. **File Hierarchy** - Dependency flow from projectbrief → activeContext → progress

### Key Differences from Document Hub

| Aspect | Document Hub | Memory Bank |
|--------|--------------|-------------|
| **Files** | 4 core files | 6 core files |
| **Focus** | Architecture & modules | Progress & context |
| **Updates** | After architecture changes | After ANY task completion |
| **Dynamic files** | None | activeContext.md, progress.md |
| **Hierarchy** | Flat | Hierarchical dependencies |
| **Diagrams** | Heavy (Mermaid) | Light (optional) |

### Identified Patterns

- **Frequent updates** → activeContext.md and progress.md change often
- **Hierarchical reading** → Must read in dependency order
- **Manual update proposals** → Should be automated
- **Progress tracking** → Unique to memory-bank, needs specialized tools
- **Context management** → Active work vs historical context

---

## Proposed Architecture

### 1. Skills (User-Invocable Commands)

#### Skill: `/memorybank initialize`
**Location:** `skills/memory-bank/initialize.md`

**Purpose:** Bootstrap a new project's memory bank

**Behavior:**
- Creates `/memory-bank` directory (or configurable name)
- Creates 6 core files:
  - `projectbrief.md`
  - `productContext.md`
  - `techContext.md`
  - `systemPatterns.md`
  - `activeContext.md`
  - `progress.md`
- Prompts user for initial project information
- Uses templates for each file type
- Validates result

**Tool Calls:**
- `validate_memorybank.py` - Pre/post validation
- None needed for detection (simpler than document-hub)

**Implementation Notes:**
- Simpler than document-hub initialize (no codebase scanning)
- More user input required upfront
- Focus on capturing project goals and context

---

#### Skill: `/memorybank update`
**Location:** `skills/memory-bank/update.md`

**Purpose:** Comprehensive review and update of all memory bank files

**Behavior:**
- Announces: "Initiating full Memory Bank review and update"
- Reads all 6 files in dependency order
- Analyzes recent conversation context
- Proposes specific updates to each file
- Focuses heavily on activeContext.md and progress.md
- Waits for user confirmation
- Applies updates
- Validates result

**Tool Calls:**
- `validate_memorybank.py` - Pre/post validation
- `detect_stale.py` - Find outdated information
- `extract_todos.py` - Extract action items from conversation

**Implementation Notes:**
- More frequent than document-hub update
- Should be quick to run (users do this often)
- Focus on activeContext.md and progress.md

---

#### Skill: `/memorybank read`
**Location:** `skills/memory-bank/read.md`

**Purpose:** Quick overview of current memory bank state

**Behavior:**
- Validates memory bank structure
- Reads all 6 files in order
- Presents structured summary:
  - Project brief
  - Product goals
  - Tech stack
  - System patterns
  - Current focus (activeContext)
  - Progress status
- Identifies any gaps or inconsistencies

**Tool Calls:**
- `validate_memorybank.py` - Structure validation
- `detect_stale.py` - Check for outdated info

**Implementation Notes:**
- Similar to document-hub read
- Must respect file hierarchy when presenting
- Show "freshness" of activeContext and progress

---

#### Skill: `/memorybank sync`
**Location:** `skills/memory-bank/sync.md`

**Purpose:** Quick sync of activeContext.md and progress.md after task completion

**Behavior:**
- Lightweight version of update
- Only updates activeContext.md and progress.md
- Doesn't touch foundational files (projectbrief, productContext, etc.)
- Faster than full update
- Use after completing individual tasks

**Tool Calls:**
- `sync_active.py` - Specialized sync tool
- `extract_todos.py` - Get next steps from conversation

**Implementation Notes:**
- NEW skill (didn't exist in original)
- Addresses frequent update need
- Much faster than full update
- Users can run after every task

---

### 2. Python Tools (Specialized Scripts)

#### Tool: `validate_memorybank.py`
**Location:** `skills/memory-bank/scripts/validate_memorybank.py`

**Purpose:** Validate memory bank structure and detect issues

**Functionality:**
- Check all 6 required files exist
- Validate file hierarchy consistency
- Check for empty files
- Detect contradictions between files
- Validate markdown formatting
- Check for broken links

**Output:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "file": "activeContext.md",
      "message": "Not updated in 7 days - may be stale"
    }
  ],
  "last_updated": {
    "activeContext.md": "2024-01-10",
    "progress.md": "2024-01-10"
  }
}
```

**Used By:** All skills

---

#### Tool: `detect_stale.py`
**Location:** `skills/memory-bank/scripts/detect_stale.py`

**Purpose:** Detect outdated or contradictory information

**Functionality:**
- Check file modification timestamps
- Compare technical context with actual dependencies
- Detect contradictions between files
- Find completed items still in progress.md
- Identify abandoned activeContext items

**Output:**
```json
{
  "stale_files": [
    {
      "file": "activeContext.md",
      "last_modified": "2024-01-01",
      "days_old": 16,
      "recommendation": "Update current focus and recent changes"
    }
  ],
  "contradictions": [
    {
      "file1": "techContext.md",
      "file2": "systemPatterns.md",
      "issue": "techContext mentions PostgreSQL, systemPatterns shows MongoDB"
    }
  ],
  "completed_in_progress": [
    "Build authentication system (marked done in conversation but still in progress.md)"
  ]
}
```

**Used By:** update, read, sync

---

#### Tool: `extract_todos.py`
**Location:** `skills/memory-bank/scripts/extract_todos.py`

**Purpose:** Extract action items and next steps from conversation or files

**Functionality:**
- Parse conversation history for "next steps"
- Extract TODO comments from recent code
- Identify uncompleted tasks from progress.md
- Prioritize by urgency/importance
- Format for activeContext.md

**Output:**
```json
{
  "next_steps": [
    {
      "task": "Implement user authentication API",
      "priority": "high",
      "context": "Mentioned in conversation as next feature",
      "source": "conversation"
    },
    {
      "task": "Add error handling to payment flow",
      "priority": "medium",
      "context": "TODO comment in src/payments/handler.ts",
      "source": "code"
    }
  ],
  "completed": [
    "Set up database schema",
    "Create initial API routes"
  ]
}
```

**Used By:** update, sync

---

#### Tool: `sync_active.py`
**Location:** `skills/memory-bank/scripts/sync_active.py`

**Purpose:** Fast synchronization of activeContext.md and progress.md

**Functionality:**
- Quick update of active work status
- Move completed items from activeContext to progress
- Add new focus areas
- Update "what's working" in progress.md
- Doesn't require full memory bank review

**Input:**
```json
{
  "completed": ["Task that was finished"],
  "new_focus": "What you're working on now",
  "learnings": ["New patterns discovered"],
  "blockers": ["Any issues encountered"]
}
```

**Output:**
```json
{
  "updated": {
    "activeContext.md": true,
    "progress.md": true
  },
  "changes": {
    "moved_to_progress": ["Completed task"],
    "added_to_active": ["New focus area"],
    "updated_learnings": 1
  }
}
```

**Used By:** sync skill

---

### 3. Hooks (Event-Driven Automation)

#### Hook: `memory-bank-session-start.md`
**Location:** `hooks/memory-bank/session-start.md`

**Trigger:** Start of every Claude Code session

**Behavior:**
- Automatically reads entire memory bank
- Reads files in dependency order (projectbrief → ... → progress)
- Validates structure
- Loads context into working memory
- Silently operates (no user notification)
- Implements "Brain" persona behavior

**Configuration:**
```json
{
  "hookType": "on-conversation-start",
  "name": "memory-bank-session-start",
  "enabled": true,
  "silent": true
}
```

**Implementation Notes:**
- Similar to document-hub session-start
- Must read files in correct order (hierarchy)
- Check for staleness warnings

---

#### Hook: `memory-bank-task-complete.md` (OPTIONAL)
**Location:** `hooks/memory-bank/task-complete.md`

**Trigger:** After user completes a task via TodoWrite

**Behavior:**
- Detects task completion
- Suggests: "Task completed. Run `/memorybank sync` to update progress?"
- User can accept/decline
- If accepted, runs sync skill automatically

**Configuration:**
```json
{
  "hookType": "on-task-complete",
  "name": "memory-bank-task-complete",
  "enabled": false,  // Disabled by default
  "severity": "low"   // Low-priority suggestion
}
```

**Implementation Notes:**
- More useful than document-hub task-complete
- Memory bank updates after EVERY task
- Still risk notification fatigue
- Make opt-in (disabled by default)

---

## File Structure (Post-Migration)

```
.claude/
├── skills/
│   └── memory-bank/
│       ├── initialize.md
│       ├── update.md
│       ├── read.md
│       ├── sync.md               [NEW skill]
│       └── scripts/
│           ├── validate_memorybank.py
│           ├── detect_stale.py
│           ├── extract_todos.py
│           ├── sync_active.py
│           ├── requirements.txt
│           └── README.md
├── hooks/
│   └── memory-bank/
│       ├── session-start.md
│       └── task-complete.md      [Optional, disabled by default]
└── commands/
    └── _deprecated/
        └── memory-bank.md        [Archived]
```

---

## Migration Strategy

### Phase 1: Python Tools (Week 1)

**Day 1-2: Setup**
- Create `skills/memory-bank/scripts/` directory
- Set up structure
- Create requirements.txt (empty)

**Day 3-4: Validation & Staleness**
- Implement `validate_memorybank.py`
- Implement `detect_stale.py`
- Test both tools

**Day 5-7: Action & Sync**
- Implement `extract_todos.py`
- Implement `sync_active.py`
- Write comprehensive README

### Phase 2: Skills (Week 2)

**Day 1-2: Core Skills**
- Create `initialize.md`
- Create `read.md`

**Day 3-5: Update Skills**
- Create `update.md` (most complex)
- Create `sync.md` (new skill)

**Day 6-7: Testing**
- Test all skills
- Verify tool integration
- Refine based on testing

### Phase 3: Hooks (Week 3)

**Day 1-3: Session Start**
- Implement `session-start.md` hook
- Test automatic loading
- Verify hierarchy reading

**Day 4-5: Task Complete (Optional)**
- Implement `task-complete.md` hook
- Make disabled by default
- Test opt-in behavior

**Day 6-7: Documentation**
- Write hooks README
- Document configuration
- Create migration guide

---

## Benefits of Refactoring

### Modularity
- Each skill has focused purpose
- Tools are reusable
- Easy to add new skills

### Automation
- Session-start loads context automatically
- Tools detect stale information
- Sync skill enables frequent updates

### Speed
- Sync skill faster than full update
- Tools provide structured output
- No manual review needed

### Quality
- Validation catches errors
- Staleness detection prevents drift
- TODO extraction captures action items

---

## Key Differences from Document Hub

### More Frequent Updates

Memory bank updates after EVERY task, so we need:
- ✅ Fast sync skill (new)
- ✅ Lightweight tools
- ✅ Optional task-complete hook

### Hierarchical Files

Must read in correct order:
- projectbrief → productContext/techContext/systemPatterns
- All above → activeContext
- activeContext → progress

### Dynamic Files

activeContext.md and progress.md change constantly:
- Need staleness detection
- Need fast sync
- Need TODO extraction

### Less Technical

Memory bank is more about context/progress than architecture:
- Fewer diagrams to validate
- More prose to analyze
- Different tool needs

---

## Implementation Priorities

### Must Have (Phase 1)
1. `validate_memorybank.py` - Essential validation
2. `detect_stale.py` - Detect outdated info
3. All 4 skills - Core functionality
4. Session-start hook - "Brain" behavior

### Nice to Have (Phase 2)
5. `extract_todos.py` - Better TODO tracking
6. `sync_active.py` - Fast updates

### Optional (Phase 3)
7. Task-complete hook - Useful but risky
8. Advanced staleness detection
9. Cross-file consistency checks

---

## Success Criteria

### Functionality
- ✅ All 4 skills working
- ✅ All tools returning valid JSON
- ✅ Session-start hook loading context
- ✅ Validation catching errors

### Performance
- ✅ Validate in < 1 second
- ✅ Sync skill in < 2 seconds
- ✅ Full update in < 5 seconds
- ✅ Session-start in < 3 seconds

### Quality
- ✅ Zero dependencies
- ✅ Comprehensive documentation
- ✅ Following Anthropic pattern
- ✅ Backward compatible

---

## Next Steps

1. **Review this plan** - Get feedback on approach
2. **Start Phase 1** - Implement Python tools
3. **Test tools** - Verify on sample memory bank
4. **Implement skills** - Following tool implementation
5. **Add hooks** - After skills proven
6. **Document everything** - READMEs and guides

---

## Estimated Effort

**Total:** ~2-3 weeks for complete implementation

- **Phase 1 (Tools):** 5-7 days
- **Phase 2 (Skills):** 5-7 days
- **Phase 3 (Hooks):** 3-5 days

**Token budget:** ~30-40k tokens (based on document-hub experience)

---

## Conclusion

The memory-bank refactoring follows the same successful pattern as document-hub, with adaptations for:
- More frequent updates (sync skill)
- Hierarchical file structure (correct reading order)
- Dynamic files (staleness detection)
- Progress tracking (TODO extraction)

The result will be a more maintainable, automated, and efficient system for managing project memory.
