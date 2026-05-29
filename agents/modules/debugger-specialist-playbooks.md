# Debugger Specialist — Playbooks Module

Load this module when investigating a specific class of problem. Each section contains a step-by-step investigation playbook and common root causes.

---

## Hypothesis Template

Use this structure when forming hypotheses in Plan Mode:

```markdown
## Debugging Hypotheses (ranked by likelihood)

### Hypothesis 1: [Descriptive name]
**Evidence supporting this:**
- [What in the symptoms or logs points here]

**Test to confirm or rule out:**
- [Specific, actionable check that produces a yes/no answer]

**Expected outcome if true:**
- [What you would observe]

---

### Hypothesis 2: [Descriptive name]
**Evidence supporting this:**
- [...]

**Test:**
- [...]
```

Rank by likelihood, then test highest-probability hypothesis first. Eliminate rather than confirm — a test that rules something out is as valuable as one that confirms it.

---

## Bug Report Template

Use when creating a minimal reproduction to share with the team or document before fixing:

```markdown
## Bug Report

### Description
[Clear, one-sentence description of the problem]

### Steps to Reproduce
1. [First step]
2. [Second step]
3. Observe: [What goes wrong]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Environment
- OS: [e.g., macOS 14.2 / Ubuntu 22.04]
- Browser: [e.g., Chrome 125 / Node.js 20.11.0]
- App version / commit SHA: [e.g., abc1234]
- Environment: [dev / staging / production]

### Stack Trace
```
[Paste full stack trace here — never truncate]
```

### Frequency
[Always / ~50% of the time / Only on specific users or conditions]

### Additional Context
[Screenshots, videos, monitoring data, recent deployments]
```

---

## Performance Debugging Playbook

**When:** Slow page loads, high API latency, UI jank, CPU saturation.

### Step 1: Establish a baseline measurement

Never optimize before measuring. You need a number to compare against.

```typescript
// Browser / Node.js performance API
performance.mark('operation-start');
await doTheSlowThing();
performance.mark('operation-end');
performance.measure('operation', 'operation-start', 'operation-end');
const [entry] = performance.getEntriesByName('operation');
console.log(`Duration: ${entry.duration}ms`);
```

Or use Chrome DevTools Performance tab: record, reproduce the slowness, stop recording.

### Step 2: Find the hottest path

In the Chrome DevTools flame graph:
- Yellow = JavaScript execution time
- Purple = layout/reflow
- Green = paint/composite

Look for the widest (not tallest) bars — width represents time. The widest bar is the hottest path.

### Step 3: Common frontend culprits

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Re-renders on every keystroke | Missing `useMemo` / `useCallback` | Memoize expensive computations and stable callbacks |
| Slow list rendering | No virtualization | Use `react-window` or `react-virtual` |
| Slow initial load | Large bundle | Code split with `next/dynamic` or `React.lazy` |
| Layout thrash | Reading layout properties in a loop | Batch reads before writes; use `requestAnimationFrame` |

### Step 4: Common backend culprits

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Slow API with many items | N+1 query | Use `include` (Prisma) or `JOIN`; add `select` with `_count` |
| Slow with large datasets | Missing index | `EXPLAIN ANALYZE` the slow query; add index on filter/sort columns |
| Slow under concurrent load | Connection pool exhaustion | Increase pool size; audit long-running transactions |
| Repeated identical queries | No caching | Add Redis cache layer for read-heavy, rarely-changing data |

### Step 5: Verify the improvement

Re-run the same measurement from Step 1 after optimizing. Document the before/after numbers. If improvement is less than 20%, the optimization may not be worth the complexity cost.

---

## Memory Leak Debugging Playbook

**When:** Memory usage grows steadily over time; app slows down or crashes after extended use.

### Step 1: Confirm there is a leak

Open Chrome DevTools → Memory tab. Take three heap snapshots:
1. Before the suspected operation
2. After repeating the operation 5-10 times
3. After triggering garbage collection (click the GC button) and waiting 10 seconds

If Snapshot 3 is significantly larger than Snapshot 1, you have a leak.

### Step 2: Find what is growing

In Snapshot 3, sort by "# New" column (objects retained since Snapshot 1). Look for unexpected growth in:
- Your application's class instances (components, services)
- DOM nodes
- Arrays or Maps that should be bounded

Click a growing type to see the retention path — this shows what is holding the reference preventing GC.

### Step 3: Common React leak patterns

```typescript
// Pattern 1: Event listener not removed on unmount
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize); // REQUIRED cleanup
}, []);

// Pattern 2: Timer not cleared on unmount
useEffect(() => {
  const id = setInterval(poll, 5000);
  return () => clearInterval(id); // REQUIRED cleanup
}, []);

// Pattern 3: Subscription not cancelled on unmount
useEffect(() => {
  const subscription = observable.subscribe(handler);
  return () => subscription.unsubscribe(); // REQUIRED cleanup
}, []);

// Pattern 4: Async state update after unmount
useEffect(() => {
  let cancelled = false;
  fetchData().then(data => {
    if (!cancelled) setState(data); // Guard against unmounted component
  });
  return () => { cancelled = true; };
}, []);
```

### Step 4: Node.js leak patterns

- Growing arrays/maps that accumulate entries (event emitters, in-memory caches without eviction)
- Closures in long-lived functions capturing large objects
- Unclosed streams or database connections

Use `--inspect` with Chrome DevTools to take heap snapshots of Node.js processes the same way as browser.

---

## Race Condition Debugging Playbook

**When:** Bug is non-deterministic; changes behavior under load; timing-sensitive; works in isolation but fails with concurrency.

### Step 1: Characterize the race

Answer these questions:
- Does the bug always occur, or only sometimes?
- Is it worse under high load or slow network?
- Does adding `await` or a delay change behavior?
- Does it correlate with specific sequences of user actions?

Non-deterministic behavior that worsens under load is almost always a race condition.

### Step 2: Common async race patterns in React

```typescript
// Problem: stale async result sets state after props have changed
useEffect(() => {
  fetchUser(userId).then(user => setState(user)); // userId may have changed by now
}, [userId]);

// Fix: cancellation flag
useEffect(() => {
  let cancelled = false;
  fetchUser(userId).then(user => {
    if (!cancelled) setState(user);
  });
  return () => { cancelled = true; };
}, [userId]);

// Fix: AbortController (preferred for fetch)
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(r => r.json())
    .then(user => setState(user))
    .catch(err => { if (err.name !== 'AbortError') throw err; });
  return () => controller.abort();
}, [userId]);
```

### Step 3: Common backend race patterns

```typescript
// Problem: check-then-act race (TOCTOU)
const existing = await db.user.findFirst({ where: { email } });
if (!existing) {
  await db.user.create({ data: { email } }); // another request may create between these two lines
}

// Fix: database constraint + catch duplicate error
try {
  await db.user.create({ data: { email } }); // unique constraint on email in schema
} catch (err) {
  if (err.code === 'P2002') throw new ConflictError('Email already registered');
  throw err;
}

// Problem: non-atomic read-modify-write
const counter = await db.counter.findFirst();
await db.counter.update({ data: { value: counter.value + 1 } }); // lost update under concurrency

// Fix: atomic increment
await db.counter.update({ data: { value: { increment: 1 } } });
```

### Step 4: Reproduce deterministically

Races are hard to reproduce. Try:
- Add artificial `await sleep(100)` at suspect points to widen the window
- Use a test that fires concurrent requests: `await Promise.all([req1(), req2(), req3()])`
- Increase concurrency in the test environment

---

## Production Incident Investigation Playbook

**When:** Production system degraded or down; active user impact; time pressure.

### Phase 1: Triage (first 5 minutes)

1. **Determine scope:** What is broken? Which users are affected (all, subset, specific region)? What is the error rate?
2. **Establish timeline:** When did it start? What deployed or changed near that time?
3. **Collect signals:**
   - Error tracking: Sentry, DataDog, LogRocket — exact error messages and stack traces
   - Monitoring: CPU, memory, database connections, queue depth
   - Logs: recent log output from affected services

### Phase 2: Mitigate first, investigate second

If there is a known rollback or disable path, take it to restore service before investigating root cause. A working system with the wrong version is better than a broken system with the right version.

Rollback options (fastest to slowest):
1. Toggle a feature flag off
2. Revert the last deploy (re-deploy previous image/commit)
3. Scale up resources (if overload)
4. Redirect traffic away from degraded region

### Phase 3: Root cause investigation

Only after user impact is mitigated:

```bash
# Find what changed near the incident start time
git log --since="2 hours ago" --oneline --all

# Check deployment timestamps
# (check your CD platform's deploy history)

# Examine logs around the incident start time
# Filter by: error level, affected service, time window
```

Apply the 5 Whys technique documented in the core agent file. Work backward from the symptom to the root cause.

### Phase 4: Incident report

Document within 24-48 hours of resolution:

```markdown
## Incident Report: [Title]

**Date:** [Date]
**Duration:** [Start time] → [End time] ([X hours Y minutes])
**Severity:** [P1 / P2 / P3]
**Impact:** [Number of users affected, business impact]

### Timeline

| Time | Event |
|------|-------|
| HH:MM | Monitoring alert fired |
| HH:MM | On-call acknowledged |
| HH:MM | Root cause identified |
| HH:MM | Mitigation applied |
| HH:MM | Service restored |

### Root Cause

[5 Whys analysis — what actually caused the failure, not just the symptom]

### Mitigation Applied

[What was done to restore service]

### Permanent Fix

[What change prevents recurrence — code fix, config change, process change]

### Prevention / Follow-up Actions

| Action | Owner | Due date |
|--------|-------|----------|
| [e.g., Add alert for X metric] | [Name] | [Date] |
| [e.g., Add regression test] | [Name] | [Date] |
| [e.g., Improve runbook for this failure mode] | [Name] | [Date] |
```
