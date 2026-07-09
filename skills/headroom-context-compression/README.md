# /headroom-context-compression

> Shrink large text before it travels or gets re-read, using the headroom MCP (`mcp__headroom__headroom_compress` / `_retrieve` / `_stats`). Every compress returns a hash that `headroom_retrieve` expands, so it works in reverse too: handed a `hash=` marker, recover exact details from the original. NOT gzip/zip, image compression, or making code concise.

## What it does

Teaches when and how to use the headroom MCP server — a local service that compresses text (lossy, semantically-summarized) while caching the exact original under a hash. The main move: before pasting a 200+ line blob (logs, files, search results, JSON) into a subagent Task prompt or re-carrying it through a pipeline, compress it and pass the compact form plus the hash; the receiver retrieves the original only if it actually needs the details. The skill covers when NOT to compress, how to read compressed output, the "something was missed → retrieve" recovery path, and verifying real token savings via `headroom_stats`.

## When it triggers

- About to hand a big log dump / file / search result to a subagent
- Stashing content you'll re-read later in a long session
- Re-carrying large tool output through a multi-step pipeline
- You (or a subagent) receive text containing a `hash=` marker and need the original
- Fires proactively — the user never has to say "compress"

## Usage

Invoke with `/headroom-context-compression`, though it's designed to trigger on its own when large blobs move around. Requires the headroom MCP installed and registered on this machine — see `INSTALL.md` (the MCP itself is machine-local, not committed to this repo). An optional advanced mode runs headroom as a proxy that compresses tool outputs automatically; see `references/proxy-mode.md`.

## Context cost

Description always in context (~0.6k chars); SKILL.md body loads on trigger (~8k chars); references load on demand: `worked-example.md` (~2k, end-to-end subagent-handoff walkthrough), `proxy-mode.md` (~3k, automatic proxy compression). `INSTALL.md` (~3k) is setup docs for humans, not loaded by the skill.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Tool table, compress/don't-compress rules, retrieval, savings verification |
| `INSTALL.md` | One-time machine setup: pipx install + MCP registration |
| `references/worked-example.md` | Worked subagent-handoff example + payoff verification |
| `references/proxy-mode.md` | Level 2: automatic compression via the headroom proxy |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |
| `evals/evals.json` | Behavioral eval cases |
| `evals/judge_trigger_eval.py` | LLM-judge harness for the trigger eval |
| `evals/e2e_mcp_probe.py` | End-to-end probe against the live MCP |

## Related skills

- **scope-question-and-delegate** — decides how to split work and budget the context window; this skill shrinks the payloads those handoffs carry.
- **fleet-dispatch-and-watch** — compress the state snapshot before handing it to remote workers.
