# Worked example + verifying the payoff

Moved from SKILL.md. Read this when you want the end-to-end subagent-handoff
pattern spelled out, or to sanity-check that compression is actually saving
tokens.

## Worked example

You ran a command that produced ~200 lines of connection-retry logs and you
want a subagent to diagnose the root cause without drowning its prompt.

1. `headroom_compress(content=<the 200 lines>)`
   → `{ "compressed": "...[201 items compressed to 91. Retrieve more:
   hash=3bfd…2bca]", "hash": "3bfd…2bca", "savings_percent": 47.4, ... }`
2. Spawn the subagent with the `compressed` text **and** this line:
   *"Full log is recoverable: call `mcp__headroom__headroom_retrieve` with
   hash=3bfd…2bca (add a `query` to pull a specific slice) if you need an exact
   line."*
3. The subagent spots a gap around attempt 4 in the compressed view, suspects a
   dropped line, and calls `headroom_retrieve(hash="3bfd…2bca")` → reads the
   full original from `original_content`, finds the exact line, confirms the
   cause. (If it only wanted the matching lines it could pass
   `query="attempt"` and read `results[].text` — but for a definite answer the
   full retrieve is surest.)

Nothing was lost; the prompt stayed small; precision was one call away when it
mattered.

## Verify it's actually paying off

Compression has overhead, and savings vary wildly by content (logs/text shrink
a lot; already-dense JSON less so). After a session that leaned on it, glance at
`headroom_stats` to confirm real tokens were saved — don't compress on faith.
