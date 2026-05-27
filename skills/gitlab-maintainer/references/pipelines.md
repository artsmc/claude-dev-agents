# Pipeline diagnosis & autonomous fix

Detailed playbook for Workflow 2 from `SKILL.md`. Read this when you're about to fix a failing pipeline, or when a status check turned up failures you need to diagnose.

## The fix loop, in detail

```
get logs ──► diagnose ──► edit ──► (cheap local check?) ──► commit ──► push ──► watch ──► green? done : back to "get logs"
```

The loop terminates one of three ways:
- **Green pipeline** — report what changed and stop.
- **Three failed attempts** — stop and ask. You're probably missing context the user has.
- **A failure shape you didn't expect** — e.g., you fixed a lint error and now an unrelated integration test fails. Stop and surface; the second failure may not be in scope.

## Getting logs efficiently

For a single failing job, `glab ci trace <job-id>` is fine. For *all* failing jobs in the latest pipeline, use the bundled script — it handles the listing+fetching loop and trims each log to the last ~200 lines (where the real error usually lives):

```bash
bash scripts/pipeline-failing-logs.sh
```

Pass `--full` if a log was truncated and you need the whole thing. Pass a pipeline ID as the first arg to target a specific pipeline instead of the latest on the current branch.

## Reading logs — find the real error, not the noise

CI logs end with the runner saying "ERROR: Job failed: command terminated with exit code 1". That line is useless. The actual error is usually 10–200 lines before it. Look for:

- **Test runners**: the assertion failure block (`AssertionError`, `expect(...).toBe(...)`, `Error: expected X to equal Y`). Pytest prints a `FAILED` summary at the end — search bottom-up for `=` separators.
- **Linters**: file:line:col format (`src/foo.ts:42:10  error  ...`). Multiple errors? Look for the count summary line.
- **Builds (tsc, webpack, cargo)**: first error in dependency order is usually the cause; later errors are often cascading. Fix the first one and rerun.
- **Dependency install**: `ERR! 404`, `peer dep conflict`, `lockfile mismatch`. Often the fix is `npm ci` failing because `package-lock.json` is out of sync with `package.json` — surface this and ask before regenerating the lockfile, since that's invasive.
- **Timeouts / OOM**: the job was killed, not your code. Don't try to "fix" — surface and ask whether to retry the job (`glab ci retry`).

## Diagnosis patterns by failure class

### Test failure
1. Identify the specific test(s) that failed.
2. Read the test and the code under test. Decide: is the test wrong, or the code wrong?
   - Test wrong: assertion is outdated (the code's behavior changed intentionally) → update the test.
   - Code wrong: the test documents the intended behavior → fix the code.
3. If unclear, surface and ask. Don't guess on semantic intent.

### Lint / format failure
Usually mechanical — run the project's auto-fixer locally if available:
```bash
# typescript/js
npm run lint -- --fix       # or: eslint . --fix
npm run format              # or: prettier --write .
# python
ruff check --fix .
ruff format .
# go
gofmt -w .
```
Then commit. If auto-fix doesn't resolve it, read the rule that failed and fix by hand.

### Build / type failure
Read the first error in dependency order. Common patterns:
- Missing import / undefined symbol → add the import or fix the typo.
- Type mismatch → fix the type, not the value, unless the value is genuinely wrong.
- Removed API used → update to the new API (check git log on the affected file for the rename/move).

### Dependency / lockfile
- `npm ci` failing because `package-lock.json` is out of sync: don't just regenerate. Ask first — the user may have added a dep but forgotten to update the lockfile, or someone may have committed a deliberate version pin.
- A specific package failed to install: read the actual error. Sometimes it's a transient registry 503 → retry the job, don't change code.

### Flaky test
Signs: passes locally, intermittent failure, mentions of timing/async/random/network.
- **Don't mark `allow_failure: true`** to make the pipeline green.
- Surface the flake honestly: "Test X looks flaky — it passed the previous 5 runs and failed once on a timing assertion. Retry the job, or do you want me to look at making the test deterministic?"

### Pipeline config (`.gitlab-ci.yml`)
If the YAML itself is broken (syntax, invalid `extends:` reference, missing image), fixing the YAML *is* the fix. Run `glab ci lint` after editing to validate before pushing.

## The commit + push step

Use the project's commit conventions if they're obvious (look at recent commits). Otherwise, a short imperative message naming the fix:

```
fix(component): describe what changed in 6-10 words

Optional second paragraph if the fix is non-obvious — what was wrong,
why this fixes it.
```

Push:
```bash
git push   # plain push only; never --force
```

If push is rejected (someone else pushed to the branch), do a `git pull --rebase`, resolve any conflicts trivially (if non-trivial, stop and surface), and push again. If rebase produces a conflict you don't immediately understand, **stop** — silent conflict resolution destroys work.

## Watching the new pipeline

After push, the new pipeline takes a moment to register. Wait ~10 seconds, then:

```bash
glab ci status      # snapshot
# or for an active watch:
glab ci status --live    # if your glab supports it; otherwise loop:
while true; do glab ci status; sleep 30; done
```

Don't watch forever — if the pipeline has long jobs (10+ min builds), tell the user and stop the live watch. The user can re-check later.

## When to stop and ask vs. keep going

Keep going (autonomously) when:
- The next failure is the same class as the previous one in a different file.
- You're auto-fixing lint/format on a long list.
- The fix is mechanical (rename a removed API, add a missing import).

Stop and ask when:
- The fix would change observable behavior (modifying a test assertion, changing a public API signature).
- The failure suggests a deeper design issue (test logic vs. code logic disagreement).
- You've made 3 attempts and the pipeline is still red.
- The failure is in a file you don't have permission to confidently change (security-sensitive code, infra config, secret management).
- The pipeline failure is on a protected branch (`main`, `master`, `develop`, release branches).
