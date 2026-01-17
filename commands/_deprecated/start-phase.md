---
name: start-phase
description: DEPRECATED - Use /start-phase plan or /start-phase execute skills instead
---

# ⚠️ DEPRECATED: start-phase command

**This command has been refactored into a modular skill-based system.**

---

## 🔄 Migration Guide

### Old Usage (DEPRECATED)
```bash
/start-phase <phase_name> <task_list_file> [additional_planning_context]
```

### New Usage (RECOMMENDED)

**Step 1: Strategic Planning (Mode 1)**
```bash
/start-phase plan /path/to/task-list.md
```
- Analyzes task list
- Proposes refinements
- Requires human approval
- No execution

**Step 2: Structured Execution (Mode 2)**
```bash
/start-phase execute /path/to/task-list.md [extra_instructions]
```
- Five-part execution (Part 1-5)
- Quality gates between tasks
- Automated documentation
- Git commits after quality passes

---

## ✨ New System Features

The modular system provides:
- ✅ **Quality gates** between every task (lint + build must pass)
- ✅ **Per-task code reviews** (AI-powered)
- ✅ **Automated git commits** (only after quality gates)
- ✅ **Checkpoint commits** (for long tasks >30 min)
- ✅ **Comprehensive hooks** (4 automated workflows)
- ✅ **Python tools** (quality enforcement, validation, SLOC tracking)
- ✅ **Path preservation** (never lose folder locations)
- ✅ **Parallel execution** (multi-agent support)

---

## 📚 Documentation

**Complete system guide:**
```bash
Read /home/artsmc/.claude/skills/start-phase/README.md
```

**Key files:**
- Skills: `/home/artsmc/.claude/skills/start-phase/{plan,execute}.md`
- Hooks: `/home/artsmc/.claude/hooks/start-phase/*.md`
- Tools: `/home/artsmc/.claude/skills/start-phase/scripts/*.py`

---

## 🚀 Quick Start

```bash
# 1. Create task list
cat > ./my-feature/tasks.md <<EOF
# My Feature
1. Task 1
2. Task 2
3. Task 3
EOF

# 2. Strategic planning (Mode 1)
/start-phase plan ./my-feature/tasks.md

# 3. Execute with quality gates (Mode 2)
/start-phase execute ./my-feature/tasks.md
```

---

## Why Refactored?

**Old system (monolithic):**
- Single command file (6,072 bytes)
- No quality gates between tasks
- Manual git commits
- No automated documentation
- No per-task code reviews

**New system (modular):**
- 2 skills + 4 hooks + 4 tools (234,016 bytes)
- Quality gates enforced automatically
- Git commits after quality passes
- Comprehensive automated documentation
- Token-optimized for 5-7 task phases
- Per-task code reviews

---

## Key Differences

| Feature | Old Command | New Skills |
|---------|-------------|------------|
| Mode separation | ❌ Mixed | ✅ Plan vs Execute |
| Quality gates | ❌ Manual | ✅ Automated (Part 3.5) |
| Code reviews | ✅ End only | ✅ Per task |
| Git commits | ✅ Manual | ✅ After quality gates |
| Checkpoint commits | ❌ No | ✅ Yes (>30 min) |
| Path management | ⚠️ Basic | ✅ Never lost |
| Documentation | ⚠️ Basic | ✅ Comprehensive |
| Hooks | ❌ None | ✅ 4 hooks |
| Python tools | ❌ None | ✅ 4 tools |
| SLOC tracking | ❌ Manual | ✅ Automated |

---

## Migration Actions

1. Replace `/start-phase` with `/start-phase plan` for planning
2. Replace `/start-phase` with `/start-phase execute` for execution
3. Update any documentation referencing old command
4. Review new README for updated workflows
5. Note: Phase name is now inferred from task list location

---

**Refactored:** 2026-01-17
**Version:** 2.0
**Status:** ✅ New system production-ready
**See:** `/home/artsmc/.claude/skills/start-phase/README.md`
