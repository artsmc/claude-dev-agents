# Level 2: automatic compression via the headroom proxy

The MCP tools this skill is built around are **on-demand** — you choose to
compress a specific blob before forwarding or stashing it. That's deliberate
and safe, but it only compresses what you explicitly hand to it.

Headroom also ships a **proxy** that compresses *automatically*: it sits
between Claude Code and the Anthropic API and shrinks large tool outputs
(file listings, search results, command output) inline, before they ever
reach the model. This is where headroom's headline "60–95% token reduction"
comes from. Claude sees compressed summaries with the same `hash=` markers,
and `headroom_retrieve` pulls originals from the proxy's store on demand —
the same mental model as the MCP path, just applied to everything.

## When to consider it

- You're routinely burning context on large, repetitive tool outputs and want
  the savings without remembering to call `headroom_compress` each time.
- Long sessions or big multi-agent runs where context pressure is constant.

## How to enable

The proxy and the MCP server are complementary — keep the MCP installed (it
provides the retrieve tool the proxy's markers point at) and add the proxy:

```bash
# Terminal 1 — start the proxy (default port 8787)
headroom proxy

# Terminal 2 — launch Claude Code routed through it
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 claude
```

`headroom mcp status` will show the proxy as running, and compress/retrieve
stats will include proxy-compressed traffic.

## Tradeoffs — why this is opt-in, not the default

- **It proxies ALL your API traffic.** Everything routes through the local
  proxy process. It stays on your machine (nothing leaves), but it's a moving
  part in the critical path — if the proxy is down or wedged, Claude Code
  can't reach the API until you unset `ANTHROPIC_BASE_URL`.
- **It can disrupt prompt caching.** Anthropic prompt-cache hits depend on the
  upstream content being byte-stable. A proxy that rewrites/compresses content
  between turns can invalidate cache prefixes, which may *raise* cost/latency
  on cache-heavy workloads even as it cuts raw token counts. Measure with
  `headroom_stats` before trusting the savings on your actual workload.
- **Shorter retrieval TTL.** Proxy-compressed content has a shorter cache TTL
  (~5 min) than content you compress yourself via the MCP. A hash from earlier
  in a long session may have expired — retrieve early, or re-trigger the source.
- **Lossy on the hot path.** With the MCP path you choose what to compress;
  with the proxy, automatic compression touches outputs you didn't vet. The
  reversibility guarantee still holds (retrieve by hash), but the "compressed
  view is not authoritative" rule from the main skill matters more, not less.

Treat it as a deliberate experiment: turn it on, run a representative session,
read `headroom_stats`, and confirm the net cost/latency actually improved
before adopting it as your default launch path.
