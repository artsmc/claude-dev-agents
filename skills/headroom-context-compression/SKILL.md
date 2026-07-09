---
name: headroom-context-compression
description: >-
  Shrink large text before it travels or gets re-read, using the headroom MCP
  (mcp__headroom__headroom_compress / _retrieve / _stats). Use it BEFORE
  pasting a 200+ line blob (logs, files, search results, JSON) into a subagent
  Task prompt, stashing content you'll re-read later, or re-carrying big output
  through a pipeline — even if the user never says "compress." Every compress
  returns a hash headroom_retrieve expands, so use it in reverse too: handed a
  `hash=` marker, recover exact details from the original. NOT gzip/zip,
  image/video compression, making code concise, or database column compression.
---

# Headroom context compression

Headroom is a local MCP server that compresses text and caches the original so
you can get it back on demand. Three tools:

| Tool | Input | Returns |
|------|-------|---------|
| `mcp__headroom__headroom_compress` | `content` (string) | JSON: `compressed`, `hash`, `original_tokens`, `compressed_tokens`, `tokens_saved`, `savings_percent`, `transforms`, `note` |
| `mcp__headroom__headroom_retrieve` | `hash` (string), `query` (optional string) | Without `query`: `{ source, original_content }` — the full original. With `query`: `{ source, query, results: [{type, text}], count }` — BM25-matched slices (note: **different field**, and `count` can be 0) |
| `mcp__headroom__headroom_stats` | — | session totals: compressions, tokens saved, cost saved |

## The one idea that matters: lossy, but reversible

Compression is **lossy**. It dedupes repeated lines, drops low-signal tokens,
reorders, and elides whole runs of similar content. A compressed log will be
missing lines; a compressed JSON will be missing fields. **Do not treat the
compressed text as ground truth for anything exact** — a specific number, an
ID, an error code, a secret, a precise line you need to quote.

But the original is never gone. Every compression caches the full original
under a `hash` (a local LRU store; no proxy needed). When you need precision,
call `headroom_retrieve(hash)` and you get the complete original back. This is
CCR — Compress, Cache, Retrieve. Think of `compress` as putting the bulky
original in a drawer and keeping a labelled index card in your pocket: the card
is enough to reason and plan with, and the drawer is one reach away when a
detail on the card turns out to be too thin.

This is *why* compression is safe to use liberally for the cases below — you're
never making an irreversible decision.

## When to compress (and when not to)

The honest constraint: this setup is **MCP-only** (no proxy). A tool result is
already in your context the moment the tool returns — compressing it *after*
the fact does **not** reclaim that context. So don't compress things just
because they're big and already sitting in front of you. Compress when the
content is about to **travel or be re-read**, where shrinking it pays off:

- **Subagent handoffs** — before pasting a large file, log, or search result
  into a `Task` prompt, compress it and pass `compressed` + the `hash`. Tell the
  subagent it can call `headroom_retrieve` with that hash if it needs the full
  thing. This keeps the subagent's prompt lean without hiding anything.
- **Content you'll re-read across many steps** — a big config, schema dump, or
  spec you keep coming back to in a long pipeline. Compress once, carry the
  compressed view + hash, expand only the slice you need each time (use the
  `query` arg).
- **Deliberate stashing** — when you're about to write a large intermediate
  blob into a notes/scratch file you'll load again later.

**Don't bother compressing** when: the content is small (under ~50 lines / a
few hundred tokens — the overhead isn't worth it), you only need it once and
right now, or you need every byte exact for the immediate next step (just use
it directly).

## Reading the result

`headroom_compress` returns JSON. The fields you act on:

- `compressed` — the shrunk text. Its tail carries a recovery marker like:
  `[201 items compressed to 91. Retrieve more: hash=3bfd8310c71ccb929e852bca]`
  That `201 → 91` is your **elision signal**: 110 items were dropped from the
  view. The bigger that gap, the more was left out, and the more likely a
  detail you need lives in the dropped part.
- `hash` — the handle for retrieval. Keep it with the compressed text wherever
  the compressed text goes. If you forward `compressed` into a subagent prompt
  or a file, forward the `hash` right beside it, or retrieval becomes
  impossible.
- `savings_percent` / `transforms` — savings and which strategy fired (e.g.
  `router:log:...`, `router:text:...`). Useful for a quick sanity check; not
  something you usually need to act on.

## When (and how) to retrieve — "something was missed"

Retrieve when the compressed view isn't enough. Concrete triggers:

- The marker shows a meaningful elision (`N → M` with a large gap) **and** the
  task needs detail from the dropped region.
- You're about to **quote, copy, or act on an exact value** (a number, path,
  ID, stack frame, secret) — the compressed view may have mangled or dropped
  it. Retrieve and read it from the original.
- A compressed answer feels **suspiciously thin or doesn't add up** — fewer
  results than expected, a field you know should exist is absent, counts don't
  match.
- A subagent (or future you) is handed only the compressed view and hits a wall
  needing specifics.

How:

- **Whole original (the reliable default):** `headroom_retrieve(hash)` →
  reads `original_content`. Use this whenever you need certainty.
- **Just a slice (optional optimization):** pass a `query` —
  `headroom_retrieve(hash, query="ECONNREFUSED")` runs BM25 over the cached
  original and returns matches under a **`results` array** (each item is
  `{type, text}`), *not* `original_content`. Read `results[].text`, not
  `original_content`, on query calls.

  Important: query matching is fuzzy and imperfect — a multi-word or
  structured query can come back with `count: 0` **even when the data is
  there** (single keywords match far more reliably than phrases). Treat an
  empty `results` as "my query didn't match," **not** "the content is gone."
  When in doubt, drop the query and do a full `headroom_retrieve(hash)`. The
  full retrieve is the source of truth; `query` is just a way to keep context
  lean when you have one clear keyword.

A retrieve that returns `source: "local"` came from this session's store. If a
hash returns an `error` ("Content not found"), it likely expired (the store
has a TTL) or came from a different process — re-compress the source if you
still have it.

## Worked example + verifying savings

A step-by-step subagent-handoff example (compress → pass hash → retrieve) and
how to confirm real token savings with `headroom_stats` live in
`references/worked-example.md` — read it the first time you run this pattern or
when checking that compression is actually paying off.

## Automatic compression (optional, advanced)

Everything above is *on-demand* — you choose what to compress. Headroom can
also run as a **proxy** that auto-compresses all tool output inline (the source
of its headline savings), with real tradeoffs around prompt caching and being
in the API critical path. If the user wants always-on compression rather than
deliberate handoffs, read `references/proxy-mode.md` for how to enable it and
what to watch for.

## Quick check on the tools

If `mcp__headroom__*` tools aren't available, the MCP server isn't loaded —
confirm `headroom` shows in `/mcp` (it's registered in `~/.claude.json`). It
only appears after a Claude Code restart following installation. Without it,
fall back to normal handling (summarize manually) rather than guessing.

Critically: if the tools are missing, **say so plainly** — never invent a
`hash`, a `savings_percent`, or any other figure these tools would have
returned. A fabricated hash is worse than no compression: it looks retrievable
but nothing is stored behind it. Report the real situation and proceed without
the tool.
