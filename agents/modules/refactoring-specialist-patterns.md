# Refactoring Specialist — Patterns Module

Load this module when the task requires detailed refactoring procedures, risk tier examples, the Strangler Fig pattern, or anti-pattern reference.

---

## Core Refactoring Patterns

| Pattern | When to Use | Approach |
|---------|-------------|----------|
| Extract Method | Function is too long or does multiple things | Copy logic to a new function; replace original body with a call to it |
| Extract Class | Class has too many responsibilities | Move a coherent subset of fields and methods to a new class; delegate from the original |
| Replace Conditional with Polymorphism | Large if/else or switch chains dispatch on type | Create strategy objects implementing a shared interface; dispatch via the interface |
| Introduce Parameter Object | Function has too many related parameters | Group related params into a typed object or dataclass; update all call sites |
| Replace Magic Numbers | Unexplained numeric or string literals | Extract to named constants at the module level with a comment explaining the value |
| Strangler Fig | Breaking apart a monolith or replacing a subsystem | See Strangler Fig section below |

---

## Detailed Execution Procedures

### Extract Method / Class

1. Copy the logic to the new function or class — do not delete the original yet
2. Implement the new structure fully (including its own tests if it has meaningful logic)
3. Update call sites one at a time, running tests after each update
4. Delete the original only after every caller has been migrated and tests still pass

### Dependency Updates (Major Versions)

1. Create a dedicated branch: `git checkout -b update-[package]-[version]`
2. Update exactly one package — do not batch multiple upgrades in one branch
3. Fix each breaking change individually; consult the official migration guide
4. Run the full test suite; all tests must pass before proceeding
5. Test in a staging environment that mirrors production
6. Merge only after comprehensive verification; tag the merge commit

### Architecture Changes (with Feature Flag)

1. Introduce the new abstraction without changing any existing code
2. Implement new functionality using the new architecture
3. Add a feature flag to allow switching between old and new paths
4. Migrate one feature or module at a time; keep the old path working in parallel
5. Monitor the new path in production; watch for regressions or performance changes
6. After the new path proves stable, complete the migration for all remaining callers
7. Remove the old code and the feature flag

### Strangler Fig Pattern (Monolith Decomposition)

Use when breaking apart a large monolith into separate services or modules:

1. **Identify the seam:** Find a natural boundary — a domain concept, a data ownership boundary, or a team ownership line
2. **Build the new service alongside the old:** Do not touch the monolith yet
3. **Add a proxy or facade:** Route calls to the new service for a subset of requests (e.g., by tenant, by feature flag, by data type)
4. **Migrate incrementally:** Move one consumer at a time to the new service; verify each migration before continuing
5. **Monitor both paths:** Track error rates, latencies, and correctness in both old and new paths simultaneously
6. **Strangle the old code:** Once all consumers are on the new path and monitoring is green, delete the old code
7. **Remove the proxy/facade:** Clean up the routing layer after the migration is complete

---

## Risk Tier Examples

### Low Risk (safe to proceed immediately)

- Renaming a local variable within a single function
- Extracting a small, pure helper function from a larger function
- Adding TypeScript type annotations to existing JavaScript
- Applying formatter or linter auto-fixes
- Adding or improving code comments

### Medium Risk (establish tests first, then proceed)

- Refactoring multiple related functions in the same module
- Changing an internal data structure used within one service
- Updating a dependency to a minor version with deprecation warnings
- Extracting a class or module from an existing one
- Reorganizing imports or splitting a large file into smaller ones

### High Risk (needs comprehensive plan + full test coverage before starting)

- Changing a public API (adding required params, removing fields, changing types)
- Major dependency updates (framework upgrades, ORM version changes)
- Architectural restructuring (moving a module between layers, introducing a new service boundary)
- Database schema changes (adding columns, renaming, changing types)
- Breaking apart a monolith or replacing a core subsystem

---

## Anti-Patterns Reference

### Do Not

- Refactor without tests — characterization tests first, always
- Mix refactoring with new feature work in the same commit or branch
- Make large, sweeping changes across many files simultaneously
- Ignore deprecation warnings — they become breaking changes in the next major version
- Skip documentation updates — code that no one understands will be refactored again next year
- Refactor code you do not fully understand — read it, trace it, test it first
- Optimize prematurely — profile before assuming a bottleneck exists
- Gold-plate / over-engineer — YAGNI: you are not going to need it

### Do

- Establish the safety net first (tests must pass before and after every change)
- Keep refactoring and feature work on separate branches
- Make one incremental change at a time; commit (or at minimum stage) after each verified step
- Address deprecations proactively before they accumulate into a painful migration
- Update code comments and Memory Bank files as you go — not at the end
- Understand what the code does AND why it exists before touching it
- Profile before optimizing; measure the improvement after
- Keep it simple — the simplest correct solution is always the right starting point

---

## Commit Message Template

When the user explicitly requests a commit after refactoring:

```bash
git commit -m "refactor(module): improve [specific aspect]

- Extracted X into separate class for better SRP
- Updated Y to use modern async/await pattern
- Removed deprecated Z dependency

Benefits: [measurable improvements]
Testing: [how it was verified]"
```

Only stage files you changed. Never use `git add .` or `git add -A` without reviewing the diff first.
