---
name: start-phase-phase-complete
trigger: on-phase-complete
description: Phase closeout, summary, and next steps after all tasks complete
enabled: true
silent: false
filter:
  context: start-phase-execute
---

# Start-Phase: Phase Complete Hook

Handles phase closeout, generates summary, and prepares for next phase.

## Purpose

Implements **Part 5 (Phase Closeout)** of Mode 2:
- Generate phase summary
- Collect quality metrics
- Identify next phase candidates
- Final SLOC analysis
- Archive phase data
- Prepare handoff documentation

## Trigger

**Event:** `on-phase-complete` or manual `/phase-complete`
**Filter:** Only during `/start-phase execute` context
**When:** After ALL tasks complete successfully

## Behavior

### Step 1: Detect Phase Completion

When all tasks complete:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 All Tasks Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: {phase_name}
Total tasks: 8
All completed: ✅

Beginning phase closeout process...
```

---

### Step 2: Collect Phase Metrics

Gather comprehensive metrics:

#### Task Completion Metrics

```
📊 Task Metrics

Total tasks: 8
Completed: 8 ✅
Failed: 0
Skipped: 0

Success rate: 100%

Task breakdown by agent:
• nextjs-backend-developer: 3 tasks
• ui-developer: 2 tasks
• qa-engineer: 2 tasks
• code-reviewer: 1 task (final review)
```

---

#### Quality Gate Metrics

```
🚦 Quality Gate Metrics

Total quality gates: 8
Passed first try: 6 ✅
Required fixes: 2 ⚠️

Quality gate stats:
• Average time per gate: 1m 42s
• Total gate time: 13m 36s
• Lint failures: 2 (fixed)
• Build failures: 1 (fixed)
• Test failures: 0

Fix time:
• Average fix time: 8m 15s
• Total fix time: 16m 30s
```

---

#### Git Metrics

```
📦 Git Metrics

Commits created: 11
• Task commits: 8
• Checkpoint commits: 3
• Fix commits: 0

Total changes:
• Files changed: 24
• Insertions: +1,247
• Deletions: -142
• Net change: +1,105 lines
```

---

#### Code Review Metrics

```
📋 Code Review Metrics

Reviews performed: 8
Issues found: 12
• Blocking: 0
• Non-blocking: 12

Issue breakdown:
• Code quality: 7
• Convention: 3
• Security: 1
• Performance: 1

Average review time: 45s per task
```

---

#### Time Metrics

```
⏱️ Time Metrics

Phase duration: 3h 24m
• Planning time: 12m (Mode 1 + Mode 2 Part 1-2)
• Execution time: 2h 47m (Part 3)
• Quality gates: 14m (Part 3.5)
• Review time: 11m (Part 4)

Average task time: 21m per task
Longest task: 45m (Task 4: Integration)
Shortest task: 8m (Task 7: Update docs)
```

---

### Step 3: Generate Phase Summary

Create `planning/phase-structure/phase-summary.md`:

```markdown
# Phase Summary: {phase_name}

**Date Completed:** {timestamp}
**Duration:** 3h 24m
**Status:** ✅ COMPLETE

## Objective

{Original phase objective from task list}

## What Was Delivered

### Features Implemented

1. **User Authentication API**
   - JWT-based authentication
   - Login/logout endpoints
   - Password hashing with bcrypt
   - Rate limiting (5 attempts / 15 min)

2. **UI Components**
   - LoginForm component
   - AuthGuard wrapper
   - User profile display

3. **Testing**
   - Unit tests for auth logic
   - Integration tests for API
   - E2E tests for login flow

### Files Created/Modified

**New files:** 15
- src/api/auth.ts
- src/components/LoginForm.tsx
- tests/auth.test.ts
- [... full list]

**Modified files:** 9
- src/app/layout.tsx
- src/types/user.ts
- [... full list]

### Documentation Updated

- README.md - Added auth setup instructions
- API.md - Documented auth endpoints
- TESTING.md - Added test coverage info

## What Was Deferred

1. **Password Reset Flow**
   - Reason: Not in MVP scope
   - Moved to: Phase 2 (user-mgmt)

2. **OAuth Integration**
   - Reason: Complexity too high for Phase 1
   - Moved to: Phase 3 (external-auth)

3. **2FA Support**
   - Reason: Low priority for prototype
   - Moved to: Backlog

## Notable Decisions

### Technical Decisions

1. **JWT Storage**
   - Decision: httpOnly cookies (not localStorage)
   - Rationale: XSS protection
   - Trade-off: Slightly more complex mobile app integration

2. **Password Hashing**
   - Decision: bcrypt with 12 rounds
   - Rationale: Industry standard, good security/performance balance
   - Alternative considered: argon2 (too new, less ecosystem support)

3. **Session Duration**
   - Decision: 7 days with refresh
   - Rationale: Balance security vs UX
   - Alternative: 24h (too short, annoying for users)

### Process Decisions

1. **Parallel Execution**
   - Backend and frontend developed in parallel
   - Saved ~1h vs sequential approach
   - Required clear API contract upfront

2. **Quality Gates**
   - Enforced lint/build between tasks
   - Caught 3 issues that would've blocked integration
   - Time investment: 14m, time saved: ~1h

## Known Risks

### Technical Risks

1. **JWT Secret Management**
   - Risk: Currently in .env (dev only)
   - Mitigation needed: Move to secure vault for production
   - Priority: HIGH
   - Timeline: Before production deploy

2. **Rate Limiting**
   - Risk: In-memory (lost on restart)
   - Mitigation: Move to Redis for production
   - Priority: MEDIUM
   - Timeline: Phase 2

### Process Risks

None identified.

## Quality Metrics

### Code Quality

- **Lint errors:** 0
- **Build errors:** 0
- **Test coverage:** 87% (target: 80%)
- **Type safety:** 100% (no 'any' types)

### Code Review

- **Issues found:** 12
- **Blocking issues:** 0
- **All issues:** Resolved ✅

### SLOC Analysis

| Category | Baseline | Final | Delta |
|----------|----------|-------|-------|
| Source code | 0 | 1,247 | +1,247 |
| Tests | 0 | 543 | +543 |
| Docs | 0 | 89 | +89 |
| **Total** | **0** | **1,879** | **+1,879** |

**Quality ratio:** 0.44 (test/source lines)
**Target:** 0.5 (good)
**Assessment:** Good test coverage

## Team Performance

### Productivity

- **Tasks completed:** 8/8 (100%)
- **Average task time:** 21m
- **Quality gate pass rate:** 75% first try
- **Rework time:** 8% of total time

### Collaboration

- **Parallel tasks executed:** 3 waves
- **Dependencies respected:** 100%
- **Blockers encountered:** 0
- **Integration issues:** 1 (resolved quickly)

## Lessons Learned

### What Went Well ✅

1. **Parallel execution saved time** - Backend + frontend concurrently
2. **Quality gates caught issues early** - Before integration
3. **Clear API contract upfront** - Enabled parallel work
4. **Checkpoint commits** - Made long tasks safer

### What Could Improve ⚠️

1. **Better task estimation** - Task 4 took 2x expected time
2. **Earlier integration testing** - Found 1 issue late
3. **More detailed acceptance criteria** - Some tasks needed clarification

### Recommendations for Next Phase

1. **Task estimation:** Add 30% buffer for integration tasks
2. **Integration testing:** Test earlier, don't wait for all tasks
3. **API contracts:** Continue writing contracts before split work
4. **Quality gates:** Keep enforcing, they save time overall

## Next Steps

See `next-phase-candidates.md` for detailed backlog.

## Appendix

### Task List

| Task | Status | Duration | Agent |
|------|--------|----------|-------|
| 1. Setup auth API | ✅ | 28m | backend |
| 2. Create UI components | ✅ | 34m | ui |
| 3. Write tests | ✅ | 19m | qa |
| 4. Integration | ✅ | 45m | backend |
| 5. Error handling | ✅ | 15m | backend |
| 6. Add rate limiting | ✅ | 12m | backend |
| 7. Update docs | ✅ | 8m | backend |
| 8. Final review | ✅ | 11m | reviewer |

### Files Changed

[Complete list of all files created/modified]

### Commit History

[List of all commits with links]
```

---

### Step 4: Generate Next Phase Candidates

Create `planning/phase-structure/next-phase-candidates.md`:

```markdown
# Next Phase Candidates

Identified during Phase: {phase_name}
Date: {timestamp}

## Backlog Items Discovered

### High Priority

1. **Password Reset Flow**
   - Description: Users can request password reset via email
   - Reason deferred: Not in MVP scope
   - Effort estimate: 8 tasks, ~3h
   - Dependencies: Email service integration
   - Suggested phase: Phase 2 (user-mgmt)

2. **Move JWT Secret to Vault**
   - Description: Migrate from .env to secure secret management
   - Reason: Production security requirement
   - Effort estimate: 2 tasks, ~45m
   - Dependencies: Vault service setup
   - Suggested phase: Phase 2 (pre-production)

### Medium Priority

3. **Rate Limiting with Redis**
   - Description: Replace in-memory rate limiter with Redis
   - Reason: Persistence across restarts
   - Effort estimate: 3 tasks, ~1.5h
   - Dependencies: Redis setup
   - Suggested phase: Phase 3 (scaling)

4. **Session Management UI**
   - Description: Let users see/revoke active sessions
   - Reason: Nice-to-have security feature
   - Effort estimate: 5 tasks, ~2h
   - Dependencies: None
   - Suggested phase: Phase 3 (user-features)

### Low Priority

5. **OAuth Integration (Google, GitHub)**
   - Description: Social login options
   - Reason: Complex, not essential for prototype
   - Effort estimate: 12 tasks, ~5h
   - Dependencies: OAuth app setup with providers
   - Suggested phase: Phase 4 (external-auth)

6. **2FA Support**
   - Description: Two-factor authentication
   - Reason: Low priority for prototype
   - Effort estimate: 8 tasks, ~3h
   - Dependencies: TOTP library
   - Suggested phase: Phase 5 (advanced-security)

## Technical Debt Notes

### Code Quality

1. **AuthService complexity**
   - Location: src/api/auth.ts
   - Issue: Main auth function is 78 lines (too long)
   - Suggestion: Break into smaller functions
   - Impact: Medium (maintainability)

2. **Duplicate error handling**
   - Location: Multiple files
   - Issue: Error formatting repeated 4 times
   - Suggestion: Extract to utility function
   - Impact: Low (DRY violation)

### Performance

None identified.

### Security

1. **CORS configuration**
   - Location: src/api/middleware.ts
   - Issue: Currently allows all origins (dev only)
   - Suggestion: Restrict to specific domains before production
   - Impact: HIGH (security)
   - Timeline: Before production deploy

## Improvements Needed

### Testing

1. **E2E test coverage**
   - Current: 2 scenarios
   - Target: 8 scenarios
   - Missing: Password validation, rate limiting, error cases

2. **Load testing**
   - Not performed yet
   - Needed before production
   - Target: 1000 concurrent users

### Documentation

1. **API documentation**
   - Current: Basic endpoint list
   - Needed: Request/response examples, error codes
   - Effort: ~30m

2. **Deployment guide**
   - Missing: Environment setup, secrets management
   - Effort: ~1h

### Infrastructure

1. **Monitoring setup**
   - No monitoring yet
   - Needed: Logging, error tracking, metrics
   - Suggested: Next phase

2. **CI/CD pipeline**
   - Currently manual
   - Needed: Automated tests, deployment
   - Suggested: Phase 2

## Follow-up Tasks

### Immediate (Before Next Phase)

- [ ] Archive phase planning files
- [ ] Update Memory Bank with phase results
- [ ] Create Phase 2 task list from high-priority items

### Short-term (Within 1 week)

- [ ] Address CORS security issue
- [ ] Refactor long AuthService function
- [ ] Add missing E2E test scenarios

### Long-term (Backlog)

- [ ] OAuth integration
- [ ] 2FA support
- [ ] Advanced session management

## Suggested Next Phase

**Phase 2: User Management & Security**

**Objective:** Production-ready auth system

**Scope:**
- Password reset flow
- JWT secret migration
- CORS configuration
- Additional E2E tests
- Deployment documentation

**Estimated effort:** 15 tasks, ~5-6h
**Priority:** HIGH (security requirements)
```

---

### Step 5: Final SLOC Analysis

Run final SLOC tracking:

```bash
python skills/start-phase/scripts/sloc_tracker.py --final
```

Update `planning/phase-structure/system-changes.md`:

```markdown
## Final SLOC Analysis

### Per-File Changes

| File | Baseline | Final | Delta | Change % |
|------|----------|-------|-------|----------|
| src/api/auth.ts | 0 (new) | 287 | +287 | +100% |
| src/types/user.ts | 45 | 89 | +44 | +98% |
| src/lib/db.ts | 156 | 223 | +67 | +43% |
| tests/auth.test.ts | 0 (new) | 543 | +543 | +100% |
| [... rest of files ...] |  |  |  |  |

### Summary

- **Total files changed:** 24
- **New files:** 15
- **Modified files:** 9
- **Deleted files:** 0

- **Total SLOC added:** +1,879
- **Total SLOC removed:** -142
- **Net SLOC change:** +1,737

### Code Distribution

- **Source code:** 1,247 lines (66%)
- **Tests:** 543 lines (29%)
- **Documentation:** 89 lines (5%)

### Quality Ratios

- **Test coverage ratio:** 0.44 (good)
- **Doc ratio:** 0.07 (acceptable)
- **Churn rate:** 0.08 (low, stable)
```

---

### Step 6: Final Code Review Summary

Consolidate all per-task reviews:

```
📋 Final Code Review Summary

Individual task reviews: 8
Total issues found: 12
• Resolved during phase: 12 ✅
• Deferred to next phase: 0

Issue severity:
• Critical: 0
• High: 1 (CORS - addressed)
• Medium: 5 (code quality)
• Low: 6 (minor improvements)

Overall code quality: ✅ GOOD

All blocking issues resolved.
Ready for integration testing.
```

---

### Step 7: Archive Phase Data

Create archive:

```
📦 Archiving Phase Data

Creating archive: planning-archive-{phase_name}-{timestamp}/
```

**Archive structure:**
```
planning-archive-prototype-build-20260117/
├── task-updates/ (8 files)
├── code-reviews/ (8 files)
├── agent-delegation/ (2 files)
├── phase-structure/ (3 files)
└── phase-archive-metadata.json
```

**Metadata:**
```json
{
  "phase_name": "prototype-build",
  "completed_date": "2026-01-17T14:30:00Z",
  "duration_minutes": 204,
  "tasks_completed": 8,
  "quality_gates_passed": 8,
  "git_commits": 11,
  "sloc_added": 1879,
  "status": "complete"
}
```

---

### Step 8: Update Memory Bank

Prompt to update Memory Bank:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Update Memory Bank
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase complete. Update Memory Bank with phase results?

This will update:
• activeContext.md (clear current work)
• progress.md (add phase completion)
• systemPatterns.md (document new patterns)

Run: /memorybank sync

Would you like me to do this now? (y/n)
```

---

### Step 9: Generate Handoff Documentation

Create handoff document:

```markdown
# Phase Handoff: {phase_name}

**For:** Next developer / Next phase
**Date:** {timestamp}
**Status:** ✅ Complete and verified

## Quick Start

To continue from this phase:

1. **Pull latest code:**
   ```bash
   git pull origin main
   git checkout -b phase-2-user-mgmt
   ```

2. **Review phase summary:**
   - Read: planning/phase-structure/phase-summary.md
   - Understand what was built and decisions made

3. **Check next phase candidates:**
   - Read: planning/phase-structure/next-phase-candidates.md
   - High-priority items ready for Phase 2

## What You're Inheriting

### Working Features

- ✅ User authentication (JWT-based)
- ✅ Login/logout endpoints
- ✅ Rate limiting
- ✅ UI components (LoginForm, AuthGuard)
- ✅ Comprehensive tests (87% coverage)

### Code Quality

- ✅ Lint: Clean (0 errors)
- ✅ Build: Clean (0 errors)
- ✅ Tests: Passing (100%)
- ✅ Type safety: 100%

### Known Issues

1. **CORS configuration** (HIGH priority)
   - Currently allows all origins
   - Must restrict before production
   - See: src/api/middleware.ts:15

2. **JWT secret in .env** (HIGH priority)
   - Works for dev
   - Must migrate to vault for production

## Where to Start

### Immediate Next Steps

1. **Address security concerns** (CORS + JWT secret)
2. **Start Phase 2 planning**
3. **Review technical debt** (next-phase-candidates.md)

### Suggested Phase 2 Focus

- Password reset flow
- Production security hardening
- Additional E2E tests
- Deployment documentation

## Getting Help

### Documentation

- API docs: docs/API.md
- Testing guide: docs/TESTING.md
- Architecture: memory-bank/systemPatterns.md

### Code Structure

```
src/
├── api/
│   └── auth.ts         # Authentication endpoints
├── lib/
│   ├── db.ts          # Database connection
│   └── jwt.ts         # JWT utilities
├── types/
│   └── user.ts        # Type definitions
└── components/
    └── LoginForm.tsx  # UI components
```

### Key Files to Understand

1. **src/api/auth.ts** - Core auth logic
2. **src/types/user.ts** - User data structure
3. **tests/auth.test.ts** - Test examples

## Contact

Questions? Check:
- Phase summary: planning/phase-structure/phase-summary.md
- Code reviews: planning/code-reviews/
- Task updates: planning/task-updates/
```

---

### Step 10: Phase Completion Announcement

Present final summary to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 PHASE COMPLETE: {phase_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Duration: 3h 24m
Tasks completed: 8/8 ✅
Quality gates: 8/8 passed ✅
Git commits: 11

Code added: +1,879 lines
Test coverage: 87%
Zero lint/build errors: ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Phase artifacts created:
✅ Phase summary (planning/phase-structure/phase-summary.md)
✅ Next phase candidates (planning/phase-structure/next-phase-candidates.md)
✅ SLOC analysis (planning/phase-structure/system-changes.md)
✅ Final code review (planning/code-review-final.md)
✅ Handoff documentation (planning/phase-handoff.md)
✅ Phase archive (planning-archive-{phase_name}/)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Recommended next steps:
1. Update Memory Bank: /memorybank sync
2. Review phase summary
3. Plan Phase 2 from next-phase-candidates.md
4. Start Phase 2: /start-phase plan phase-2 ./planning/phase-2-tasks.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Great work! Phase {phase_name} complete. 🚀
```

---

## Configuration

### Enable/Disable Hook

```yaml
# In frontmatter
enabled: true     # Set to false to skip automatic closeout
silent: false     # Set to true for quiet summary
```

### Customization

```json
{
  "phase_complete": {
    "generate_summary": true,
    "collect_metrics": true,
    "archive_data": true,
    "handoff_docs": true,
    "update_memory_bank_prompt": true
  }
}
```

---

## Performance

- **Metrics collection:** ~5 seconds
- **Summary generation:** ~10 seconds
- **SLOC analysis:** ~5 seconds
- **Archive creation:** ~3 seconds
- **Total:** ~25 seconds

**Worth it:** Comprehensive phase documentation for future reference.

---

## Benefits

### For Current Phase

✅ **Complete record** - Everything documented
✅ **Quality metrics** - Know what was achieved
✅ **Lessons learned** - Improve next phase

### For Next Phase

✅ **Clear starting point** - Handoff docs
✅ **Prioritized backlog** - Next phase candidates
✅ **Known issues** - Don't repeat mistakes

### For Project

✅ **Historical record** - Phase archives
✅ **Metrics tracking** - Velocity, quality trends
✅ **Knowledge retention** - Decisions documented

---

## Example Flow

```bash
# All tasks complete
Task 8: Final review
→ Quality gate passed
→ Commit created

# Phase-complete hook triggers
🎉 All Tasks Complete!

# Collect metrics
→ Task metrics: 8/8 ✅
→ Quality metrics: 100% pass rate
→ Git metrics: 11 commits
→ Time metrics: 3h 24m

# Generate documents
→ phase-summary.md ✅
→ next-phase-candidates.md ✅
→ Final SLOC analysis ✅
→ phase-handoff.md ✅

# Archive
→ planning-archive-prototype-build-20260117/ ✅

# Announce
🎉 PHASE COMPLETE: prototype-build

Ready for Phase 2!
```

---

**Phase closeout ensures knowledge isn't lost and next phase starts strong.**

See `skills/start-phase/README.md` for complete documentation.
