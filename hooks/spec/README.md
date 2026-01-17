# Spec Hooks

Automated feedback loop for feature specification generation.

## Hook: feedback-loop.md

**Trigger:** `on-task-complete` (when spec-writer agent finishes)

**Purpose:** Automatically validates and critiques generated specifications, implementing human-in-loop workflow.

### Workflow

```
1. Spec-writer agent completes
2. Hook detects completion
3. Runs validate_spec.py automatically
4. Runs critique_plan.py automatically
5. Presents results to user
6. Collects feedback (approve/iterate)
7. If iterate → re-run agent with feedback → repeat
8. If approve → done
```

### Configuration

**Enabled by default:**
```yaml
enabled: true
silent: false
filter:
  subagent_type: spec-writer
```

**Disable if needed:**
```yaml
enabled: false
```

Then manually run `/spec review` after agent completes.

### Performance

- **Validation:** < 2 seconds
- **Critique:** < 3 seconds
- **Total overhead:** ~5 seconds
- **User impact:** Immediate, actionable feedback

### Benefits

1. **Automatic Quality Gate**
   - No manual checklists
   - Consistent standards
   - Early error detection

2. **Human-in-Loop**
   - User approval required
   - Easy iteration
   - Feedback-driven refinement

3. **Time Savings**
   - Validation in seconds
   - No manual document review
   - Automated critique

### Example Output

#### When Everything Passes

```
✅ Spec Validation Complete
✅ Quality Critique Complete

Generated Specifications:
📁 /job-queue/feature-auth/docs/
  ├── FRD.md - Business requirements ✅
  ├── FRS.md - Functional specs ✅
  ├── GS.md - Gherkin scenarios ✅
  ├── TR.md - Technical requirements ✅
  └── task-list.md - Development tasks ✅

Completeness: 95%
Quality Score: 88%

Ready to proceed with development?
```

#### When Issues Found

```
✅ Spec Structure Valid
⚠️ Quality Issues Detected

Validation: PASSED ✅
Quality: 65%

Critical Issues:
• FRS.md - Requirement FR-003 is vague
  → Suggestion: Specify exact validation rules

Warnings:
• task-list.md - 5/12 tasks are too broad
  → Suggestion: Break down "Implement auth" tasks

What would you like to do?
1. Iterate on these issues
2. Proceed anyway
3. Focus on specific areas
```

### Integration

Works seamlessly with:
- **`/spec plan`** - Launches spec-writer agent
- **Spec-writer agent** - Generates specifications
- **Hook** - Automatically validates when agent completes
- **`/spec review`** - Manual trigger if hook disabled

### Error Handling

Graceful degradation:
- **Feature folder not found:** Ask user for path
- **Tool script errors:** Show error, offer manual validation
- **Validation fails:** Present errors, offer fixes
- **Hook disabled:** Skip silently

Never blocks development workflow.

---

See `../skills/spec/README.md` for complete spec system documentation.
See `feedback-loop.md` for detailed hook implementation.
