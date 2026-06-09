# Install — headroom-context-compression

This skill drives the **headroom** context-compression MCP. The skill files
travel with this repo, but the MCP itself and its registration are **machine-
local** and are NOT committed here. On a fresh machine/clone, do these steps
once.

## 1. Install headroom

Use pipx so the `headroom` CLI lands on your PATH:

```bash
pipx install "headroom-ai[mcp,proxy]"
```

> Don't install `headroom-ai[mcp]` alone — the CLI eagerly imports the proxy
> module, so without the `proxy` extra even `headroom --version` crashes with
> `ModuleNotFoundError: fastapi`. The `[mcp,proxy]` combo is the minimum that
> works (avoids dragging in the heavy `[all]` ML deps).

## 2. Register the MCP with Claude Code

```bash
headroom mcp install --agent claude
```

This writes a `headroom` entry into `~/.claude.json` (`mcpServers`). Then pin it
to the absolute path so it still launches from cron, the desktop app, or a
stripped shell where `~/.local/bin` may not be on PATH:

```bash
python3 - <<'PY'
import json, os
f = os.path.expanduser("~/.claude.json")
d = json.load(open(f))
d["mcpServers"]["headroom"]["command"] = os.path.expanduser("~/.local/bin/headroom")
json.dump(d, open(f, "w"), indent=2)
print("pinned:", d["mcpServers"]["headroom"])
PY
```

> Note: `headroom mcp status` checks a different path and may report
> "No config file" — that's a false negative; verify with `claude mcp list`
> instead (should show `headroom … ✔ Connected`).

## 3. Restart Claude Code

The MCP and this skill only load on a fresh start. After restart, `/mcp` should
list `headroom` with 3 tools (compress / retrieve / stats).

## 4. (Optional) Add the delegation pointer to CLAUDE.md

To nudge agents to compress large context before subagent/team handoffs, add a
line to your workspace `CLAUDE.md` (machine-local, not in this repo):

```
- `headroom-context-compression` — compress large content (logs, JSON, files,
  search results) before forwarding into a Task/team agent prompt or re-reading
  it across steps. Lossy but reversible by hash. Compress before the handoff.
```

## 5. (Optional) Automatic compression

For always-on compression of all tool traffic (vs. on-demand), see
`references/proxy-mode.md` — it covers the `headroom proxy` setup and its
tradeoffs (prompt-cache disruption, API critical-path risk).

## Running the eval harnesses

`claude -p` (headless) does NOT inherit `~/.claude.json` MCP servers, so the
behavior probe loads headroom explicitly via `--mcp-config`.

```bash
cd evals
python3 judge_trigger_eval.py --model claude-opus-4-8   # triggering (precision/recall)
python3 e2e_mcp_probe.py      --model claude-opus-4-8   # real compress round-trip
```

See the docstrings in each script for why they exist (the skill-creator
`run_loop` optimizer can't score MCP-dependent skills — its sandbox has no MCP,
files, or subagents, so it reports recall=0 for every description).
