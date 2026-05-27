# Merge Request review workflows

Detailed playbook for Workflow 3 from `SKILL.md`. Covers reading reviewer feedback, responding with code changes, and casting approve / request-changes votes.

## Locating the MR

If the user said "the MR" without specifying which:
1. If they're on a branch with an open MR, that's it: `glab mr view` shows it.
2. If they pasted a URL or MR ID, use that: `glab mr view <id>`.
3. If ambiguous, list open MRs assigned to or authored by them: `glab mr list --mine` / `glab mr list --assignee=@me` / `glab mr list --reviewer=@me`.

## Reading review threads

`glab mr view` shows the MR overview but truncates discussions. For full thread data with resolved/unresolved state:

```bash
bash scripts/mr-threads.sh <mr-id-or-branch>
```

That script returns JSON with one entry per discussion thread, each containing:
- `id` (discussion ID, needed to reply or resolve)
- `resolved` (bool — focus on `false`)
- `position` (file path + line, if the thread is attached to a diff line)
- `notes` (array of comments in the thread, oldest first)

**Reading priority:**
1. **Unresolved threads on diff lines** — these are direct asks about specific code.
2. **Unresolved general comments** — broader feedback (architecture, naming, scope).
3. **Resolved threads** — usually skip, unless the user is asking "what's been addressed?".

Summarize the unresolved asks concisely. Group related comments (e.g., three threads all asking to rename `foo` to `bar` → one ask).

## Responding to MR feedback

This is a multi-step loop: read → make code changes → push → reply on each thread → optionally resolve.

### 1. Read the asks (above).

### 2. Make code changes.

Treat reviewer feedback the same way you'd treat a bug report. If a comment says "this should handle null", verify the claim (is null actually reachable?) before changing the code. Reviewers are often right, but not always — if you disagree with a comment, *say so in the reply* rather than silently complying or silently ignoring.

For each thread, decide:
- **Accept** — make the change.
- **Discuss** — reply explaining your reasoning, don't make the change yet.
- **Defer** — agree but propose handling it in a follow-up MR (mention the reason; usually scope).

### 3. Commit and push.

Group related changes into a single commit per logical fix where possible — easier for the reviewer to re-review. Commit message names the change, not the reviewer ("rename foo to bar per review" is fine; just "address review" is unhelpful because the reviewer can't see what specifically you addressed from the commit subject).

### 4. Reply on each thread.

`glab mr note --note "..."` posts a *new top-level comment* on the MR — that's not a thread reply, it's a fresh comment, and reviewers will lose track. Use the API for thread-scoped replies:

```bash
# reply to a specific discussion thread
glab api --method POST \
  "projects/:id/merge_requests/<MR_IID>/discussions/<DISCUSSION_ID>/notes" \
  --field body="Done — renamed in 4a3b2c1."
```

The script `scripts/mr-threads.sh` outputs the `discussion_id` you need. Project ID can be `:id` literally when run inside a git repo — glab resolves it from the remote.

### 5. Resolve threads you've addressed.

Reviewer will appreciate not having to manually click "Resolve" on each thread you handled:

```bash
glab api --method PUT \
  "projects/:id/merge_requests/<MR_IID>/discussions/<DISCUSSION_ID>?resolved=true"
```

Only resolve threads where you actually did what was asked. If you replied "I disagree because X", leave it unresolved — the reviewer needs to decide whether to push back or accept your reasoning.

## Approving / requesting changes

### Approve

```bash
glab mr approve <mr-id-or-branch>
```

Before approving, the skill should have done a real review — not just "the tests pass so approve". A minimum bar:
1. Read the MR description and verify it matches the diff scope (no scope creep).
2. Skim the diff: `glab mr diff <mr>`. Look for obvious smells (commented-out code, debug prints, hard-coded credentials, TODOs without tickets, missing tests for new logic).
3. Check pipeline status: don't approve a red pipeline unless the user explicitly says they'll fix CI separately.

### Request changes

GitLab doesn't have a formal "request changes" verb in the API (unlike GitHub). The convention is to leave an unresolved discussion explaining what you want changed:

```bash
glab mr note <mr> --note "Requesting changes: <one-line summary>. Specifics in inline comments."
```

Then add inline comments on specific lines if applicable. To add an inline (line-scoped) comment requires the API since glab doesn't expose it directly:

```bash
glab api --method POST \
  "projects/:id/merge_requests/<MR_IID>/discussions" \
  --field body="This early return skips the audit log call." \
  --field "position[base_sha]=<base-sha>" \
  --field "position[head_sha]=<head-sha>" \
  --field "position[start_sha]=<start-sha>" \
  --field "position[position_type]=text" \
  --field "position[new_path]=src/auth.ts" \
  --field "position[new_line]=42"
```

Get the SHAs from `glab mr view <mr> --output json | jq '.diff_refs'`.

For most "request changes" cases, a single top-level note describing the asks is cleaner than peppering the diff with inline comments. Reserve inline comments for points that are inherently about a specific line ("this conditional is inverted" doesn't make sense without the line).

## Self-review guard

Before approving, check who authored the MR:

```bash
glab mr view <mr> --output json | jq -r '.author.username'
glab api user | jq -r '.username'
```

If they match, **stop** — the user is asking you to "approve the MR" but the only MR they could approve is one *someone else* authored. Two likely meanings:
- They meant: review someone else's MR (which one?). Ask.
- They meant: their MR is ready, merge it. That's *not* approve — that's `glab mr merge`. Confirm before merging since merge changes production state.

## Common gotchas

- **Stale diff_refs**: if someone pushed to the MR branch since you fetched the MR, your `head_sha` is stale and inline comment posting will fail. Re-fetch `diff_refs` right before posting.
- **Discussion vs. note**: in GitLab API, every discussion has one or more notes; a top-level comment is a discussion with one note. Don't conflate the two when reading scripts.
- **Resolved ≠ accepted**: a resolved thread just means someone clicked "Resolve". The fix might still be wrong. When responding, check the *content* of the resolution, not just the flag.
- **Approval rules**: some projects require N approvals from specific groups (codeowners). `glab mr approve` will succeed for you but the MR may still not be mergeable. `glab mr view <mr> --output json | jq '.approvals_left'` shows what's still needed.
