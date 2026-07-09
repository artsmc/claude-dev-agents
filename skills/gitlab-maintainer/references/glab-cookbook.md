# glab cookbook — auth verification, token sourcing, URL-encoding, paging

Manual recipes for when `scripts/resolve-context.sh` isn't enough — auth failures, unusual token setups, or raw API calls. The general command reference lives in `glab-cheatsheet.md`.

## Verify auth with a project-scoped endpoint

Verify auth against the target host using a **project-scoped endpoint**, not `/user`:

```bash
# Encode the project path: group/subgroup/repo → group%2Fsubgroup%2Frepo
glab api --hostname "$HOST" "projects/$PROJECT_ENC" 2>&1 | head -c 200
```

Why not `glab auth status`? It hits `/user`, which 401s for **project access tokens** (bot tokens like `project_NNN_bot_*`). Those tokens work fine for project endpoints but have no `/user`. The skill must work for both PATs and project tokens, so test what we'll actually use.

Three outcomes:

1. **Returns JSON with project info** → auth works, proceed.
2. **Returns `401 Unauthorized`** → token bad, expired, or missing project scope. Stop and ask the user to refresh (see token sourcing below).
3. **Returns `404 Not Found`** → token works but lacks access to this project, OR the project path is wrong. Confirm `$PROJECT_ENC` matches the remote URL path, then ask.

## Where the token comes from (in priority order)

The skill should find a working token without storing anything new in user config:

1. **`GITLAB_TOKEN` env var** (if already set in the shell) — use it as-is.
2. **glab's stored config** for the target host (`~/.config/glab-cli/config.yml` or `~/snap/glab/current/.config/glab-cli/config.yml`) — glab uses this automatically when you don't pass `--hostname`.
3. **Embedded in a git remote URL** (`https://user:TOKEN@host/...`) — if `git remote get-url <name>` shows a token in the URL, extract it for the matching host:
   ```bash
   TOKEN=$(git remote get-url <remote> | sed -nE 's|https://[^:]+:([^@]+)@.*|\1|p')
   ```
   This is common in CI-cloned repos and dev-laptop setups. Don't echo the token to the user; just use it.

When using sources 1 or 3, pass the host explicitly on every call:

```bash
GITLAB_TOKEN="$TOKEN" glab api --hostname "$HOST" <endpoint>
GITLAB_TOKEN="$TOKEN" glab ci status --hostname "$HOST"     # most glab commands accept --hostname
```

If no token can be found anywhere, stop and ask the user to either run `glab auth login --hostname <host>` (persistent) or `export GITLAB_TOKEN=...` (session-only).

## Paging

GitLab list endpoints (discussions, jobs, pipelines) return 20 items per page by default — long MR review threads and big pipelines get silently truncated. Either follow all pages or bump the page size:

```bash
glab api --paginate "projects/:id/merge_requests/<iid>/discussions"
glab api "projects/:id/pipelines?per_page=100"
```
