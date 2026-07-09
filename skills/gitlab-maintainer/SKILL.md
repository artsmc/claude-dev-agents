---
name: gitlab-maintainer
description: Work with GitLab Enterprise as a maintainer via glab — check pipeline status, diagnose and fix failing CI (build/test/lint), push the fix and wait for green, and handle MR review threads, approvals, and change requests. Use for "check the pipeline", "why is CI failing", "address review comments", "approve this MR", or any mention of glab, a self-hosted GitLab MR, pipeline, or job log. Prefer this over raw glab commands — it handles auth checks, repo detection, paging, and the diagnose→fix→push→re-monitor loop.
---

# GitLab Maintainer

This skill assumes the user has the `glab` CLI installed and authenticated against their GitLab Enterprise host with a **maintainer-level personal access token** that has `api`, `read_repository`, and `write_repository` scopes. With those permissions the user expects you to act decisively — diagnose failures, push fixes, approve MRs — rather than narrating what they could do themselves.

## Prerequisites — check first, every time

Before running any glab command, confirm the environment is workable. Skipping this step leads to confusing 401s halfway through a multi-step fix.

```bash
git rev-parse --show-toplevel 2>/dev/null      # are we in a git repo?
git remote -v 2>/dev/null                      # what remotes / which GitLab host?
```

Identify the **target host** — the GitLab hostname you'll be talking to. Usually it's `git remote get-url origin`, but check all remotes: a repo can have multiple GitLab remotes pointing at different instances (e.g., `origin` on the old host, `new_origin` on a migrated host). If the user named a specific remote ("test on new_origin"), use that one.

### One-shot context resolver

The bundled script resolves everything in one call — parse the remote, extract host + project + (if present) embedded token, and emit shell exports:

```bash
eval "$(bash scripts/resolve-context.sh)"               # uses 'origin'
eval "$(bash scripts/resolve-context.sh new_origin)"    # uses a named remote
```

After eval, `$GITLAB_HOST`, `$GITLAB_PROJECT`, `$GITLAB_PROJECT_ENC`, and `$GITLAB_TOKEN` (if extractable) are set. Then verify with a single project-scoped API call:

```bash
glab api --hostname "$GITLAB_HOST" "projects/$GITLAB_PROJECT_ENC" | head -c 200
```

JSON back = good to go. `401` = token bad, expired, or missing scope — stop and ask the user to refresh. `404` = token lacks access to this project or the project path is wrong. If not in a git repo at all, ask the user to `cd` into one or pass project + host explicitly.

For the manual recipes behind the script — verifying auth on a project-scoped endpoint (and why not `glab auth status`), project-path URL-encoding, token sourcing priority (env var → glab config → token embedded in a remote URL), passing `--hostname` explicitly, and API paging — read `references/glab-cookbook.md`. Read it whenever auth fails, the token setup is unusual, or you need raw `glab api` calls.

## Routing — pick the workflow

Decide which workflow the user is asking for. Phrases overlap, so read intent broadly.

| User says something like… | Go to |
|---|---|
| "is CI green / failing?", "what's the pipeline status?", "did my build pass?" | **Pipeline status check** (below) |
| "fix the failing pipeline", "make CI green", "the build is broken — sort it out" | **Autonomous pipeline fix** (below; reference: `references/pipelines.md`) |
| "what's on the MR?", "did anyone review my MR?", "what did the reviewer say?" | **Read MR review threads** (reference: `references/mr-review.md`) |
| "address the review comments", "respond to the reviewer", "fix what they asked for" | **Respond to MR feedback** (reference: `references/mr-review.md`) |
| "approve the MR", "request changes on this MR", "lgtm, ship it" | **Cast MR vote** (reference: `references/mr-review.md`) |

If intent is genuinely unclear (e.g., "look at the MR"), state what you're about to do in one sentence and proceed — don't ask a clarifying question for something the user can correct cheaply.

## Workflow 1: Pipeline status check

The minimum useful answer is *which jobs failed and why*, not just "pipeline failed". Aim for that in one pass.

```bash
glab ci status                          # current branch's latest pipeline summary
glab ci view                            # detailed job tree for the current pipeline
```

If everything is green or running, say so plainly and stop. If jobs failed, pull logs for each failing job (don't make the user ask twice):

```bash
bash scripts/pipeline-failing-logs.sh   # aggregates logs from all failed jobs
```

When summarizing failures, lead with the failing job name and the first real error line — not the trailing "Job failed: command terminated with exit code 1" noise. Group related failures (e.g., three test files failing the same way → one root cause).

## Workflow 2: Autonomous pipeline fix

The user has explicitly authorized this skill to fix, commit, and push. That trust comes with two non-negotiable boundaries:

1. **Never push directly to a protected branch.** Default branches (`main`, `master`, `develop`, anything matching the project's protected branch rules) are off limits. If the failing pipeline is on a protected branch, stop and surface this — ask whether to open an MR with the fix instead.
2. **Never force-push.** A regular `git push` to the current MR branch is the only acceptable shape. If a plain push is rejected, stop and report — don't try `--force` or `--force-with-lease` without explicit user say-so.

The fix loop is described in detail in `references/pipelines.md`. The shape is:

```
1. Get failing job logs (script above)
2. Diagnose — identify the smallest set of files to change. State the diagnosis in one paragraph before editing.
3. Apply the fix using Edit/Write tools, not sed.
4. Run the equivalent check locally if cheap (e.g., `npm run lint`, `pytest -k <test>`). If it's expensive (full E2E suite, 10-minute build), skip and rely on CI.
5. Commit with a message that names the fix, not the symptom. Good: "fix(api): handle null user in /auth/me". Bad: "fix CI".
6. Push to the current branch.
7. Watch the new pipeline: `glab ci status --live` or poll with `glab ci status` every ~30s.
8. If it goes green: done, report. If it fails again: read the new logs and decide whether to iterate (same class of error → keep going) or stop (different unexpected failure → surface and ask).
```

Iterate up to ~3 fix attempts before stopping to ask. If you find yourself going in circles or the fixes are getting speculative, that's the signal to stop and explain what you've tried.

Read `references/pipelines.md` for diagnosis patterns by failure type (test failures, lint, build, dependency, flaky, timeout).

## Workflow 3: Merge Request review

Three sub-modes — reading existing feedback, responding to it, and casting a vote. Full details in `references/mr-review.md`. Quick orientation:

**Reading**: use `bash scripts/mr-threads.sh <mr-id-or-branch>` to dump all discussion threads as structured JSON. Pay attention to `resolved: false` threads — those are the open asks.

**Responding**: read the threads, make the code changes, push, then reply on each thread with `glab mr note --note "..."` (note: glab doesn't natively reply-to-thread; use the API via `glab api` for thread-scoped replies — script is in references). After replying, resolve the thread via the API.

**Approving / requesting changes**:
```bash
glab mr approve <mr>                    # approve
glab mr note <mr> --note "Requesting changes: ..."  # informal request-changes (glab has no formal request-changes verb; the convention is an unresolved thread)
```

Don't approve your own MR — GitLab blocks it anyway, but more importantly the user is asking you to *act as the maintainer reviewing someone else's MR*. If the current branch's MR was authored by the same user the token belongs to, surface that and ask whether they really mean approve-on-someone-else's-MR or merge-my-own.

## What this skill won't do

These are out of scope on purpose; if the user wants them, suggest a different approach rather than reaching for them:

- **Modify `.gitlab-ci.yml` to make tests pass.** That's covering up a real failure. Fix the underlying code instead. (If the YAML itself is broken — lint error, syntax — fixing the YAML *is* the fix; that's fine.)
- **Skip tests, mark them as expected-failure, or add `allow_failure: true`.** Same reason.
- **Rebase or rewrite history on a shared branch.** Not authorized by the "fix the failing pipeline" mandate.
- **Merge the MR.** The user can hit the green button themselves once it's ready; merging changes production state and isn't covered by "review" or "fix pipeline".

If a fix legitimately requires one of these (rare), stop and explain why, and let the user decide.

## Output style

The user is a developer who knows their codebase. Be terse. After a pipeline fix, a good final message looks like:

> Fixed: `test_user_serializer.py` was asserting `email` but the model field is now `email_address` (renamed in commit 4a3b2c1). Updated the test, pushed to `feat/user-rename`, pipeline #98432 is green.

Not three paragraphs of narration. The diff is in git; the user can read it.
