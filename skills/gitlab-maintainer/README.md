# /gitlab-maintainer

> Work with GitLab Enterprise as a maintainer via `glab` — check pipeline status, diagnose and fix failing CI, push the fix and wait for green, and handle MR review threads, approvals, and change requests. Prefer this over raw `glab` commands — it handles auth checks, repo detection, paging, and the diagnose→fix→push→re-monitor loop.

## What it does

Drives the `glab` CLI against a self-hosted GitLab Enterprise instance with maintainer permissions. Routes each request into one of three workflows: pipeline status check, autonomous pipeline fix (diagnose failing jobs → fix → push → re-monitor until green), or MR review work (read threads, respond to feedback, approve/request changes). A bundled resolver script figures out the host, project path, and token from the repo's remotes in one call — including multi-remote repos where `origin` and a migrated remote point at different GitLab instances.

## When it triggers

- "check the pipeline" / "is CI green?" / "did my build pass?"
- "why is CI failing" / "fix the failing pipeline" / "make CI green"
- "what did the reviewer say?" / "address the review comments"
- "approve this MR" / "request changes" / "lgtm, ship it"
- Any mention of `glab`, a self-hosted GitLab MR, pipeline, or job log

## Usage

Invoke with `/gitlab-maintainer` or just ask about a GitLab pipeline/MR. No flags. Assumes `glab` is installed and authenticated with a maintainer-level PAT (`api`, `read_repository`, `write_repository` scopes). It verifies auth with a project-scoped API call before doing anything, and stops to ask if the token is bad rather than failing halfway through a fix.

## Context cost

Description always in context (~0.5k chars); SKILL.md body loads on trigger (~9k chars); references load on demand: `glab-cookbook.md` (~3k), `glab-cheatsheet.md` (~4k), `pipelines.md` (~6k), `mr-review.md` (~7k).

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Routing table + the three workflows |
| `references/glab-cookbook.md` | Auth verification, token sourcing priority, URL-encoding, paging |
| `references/glab-cheatsheet.md` | General `glab` command reference |
| `references/pipelines.md` | Autonomous pipeline-fix details |
| `references/mr-review.md` | MR threads, responses, approvals |
| `scripts/resolve-context.sh` | One-shot host/project/token resolver (eval-able exports) |
| `scripts/mr-context.sh` | MR metadata + pipeline status + unresolved threads in one bundle |
| `scripts/mr-threads.sh` | Dump MR discussion threads as JSON (`--unresolved` filter) |
| `scripts/pipeline-failing-logs.sh` | Aggregate logs from all failed jobs (`--full` to untruncate) |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **prove-it-live-before-done** — for verifying a deploy actually shipped; this skill only takes CI to green.
- GitHub work uses the `gh` CLI directly, not this skill — this is GitLab-only.
