# glab cheatsheet

Quick reference for the glab commands this skill uses most. Read this if you're unsure about a flag or want a working example.

## Auth & repo context

```bash
glab auth status                            # check token for all configured hosts
glab auth login -h gitlab.<company>.com     # interactive login for a new host
glab repo view                              # show the current repo's GitLab project info
glab repo view -R group/project             # explicit project override
```

Most commands accept `-R group/project` to target a project outside the current git directory.

## CI / pipelines

```bash
glab ci status                              # current branch, latest pipeline summary
glab ci status --live                       # watch (Ctrl-C to stop)
glab ci view                                # detailed job tree for the latest pipeline
glab ci view <branch>                       # for a specific branch
glab ci list                                # list recent pipelines
glab ci list --status=failed --per-page=10  # filter
glab ci get                                 # JSON for the latest pipeline (machine-readable)

glab ci trace                               # tail the running job's log
glab ci trace <job-id>                      # specific job log
glab ci trace <job-name>                    # by name (e.g., "test:unit")

glab ci retry <job-id>                      # retry a single failed job
glab ci cancel                              # cancel the currently running pipeline
glab ci run                                 # trigger a new pipeline on current branch
glab ci run --branch <branch> --variables KEY=val

glab ci lint                                # validate .gitlab-ci.yml
glab ci artifact <ref> <job-name>           # download artifacts
```

JSON output for scripting:

```bash
glab ci get --output json | jq '.jobs[] | select(.status=="failed") | .id'
```

## Merge requests

```bash
glab mr list                                # open MRs in the project
glab mr list --mine                         # MRs you authored
glab mr list --assignee=@me                 # assigned to you
glab mr list --reviewer=@me                 # you're a reviewer
glab mr list --state=opened --label=bug

glab mr view                                # current branch's MR
glab mr view <id-or-branch>
glab mr view <mr> --output json             # full JSON (use with jq)

glab mr diff <mr>                           # diff
glab mr diff <mr> --raw                     # patch format

glab mr note <mr> --note "comment text"     # top-level comment (NOT a thread reply)

glab mr approve <mr>                        # approve
glab mr revoke <mr>                         # revoke your approval
glab mr merge <mr>                          # merge (changes prod — be careful)
glab mr close <mr>
glab mr reopen <mr>

glab mr update <mr> --description "..." --assignee=@me --label="..."
```

## The API escape hatch

`glab api` makes authenticated calls to the GitLab REST API. Use this when the high-level commands don't expose what you need (thread replies, inline diff comments, resolving discussions).

```bash
glab api projects/:id                       # ":id" resolves to current repo's project
glab api projects/:id/merge_requests/<iid>
glab api projects/:id/merge_requests/<iid>/discussions

glab api --method POST <endpoint> --field key=value --field nested[key]=value
glab api --method PUT <endpoint>?param=value
```

For URL-encoded query params in PUT/DELETE, append them to the path (as shown). For body params in POST/PUT, use `--field` (form-encoded) or `--raw-field` (raw value, useful for booleans and numbers that shouldn't be auto-coerced).

GraphQL is also available:

```bash
glab api graphql --raw-field query='query { currentUser { username } }'
```

## Useful jq one-liners

```bash
# all failing job IDs in latest pipeline
glab ci get --output json | jq '[.jobs[] | select(.status=="failed") | .id]'

# unresolved discussion IDs on an MR
glab api projects/:id/merge_requests/<iid>/discussions \
  | jq '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false) | .id]'

# MR diff_refs (needed for inline comments)
glab mr view <mr> --output json | jq '.diff_refs'

# pipeline URL for sharing
glab ci get --output json | jq -r '.web_url'
```
