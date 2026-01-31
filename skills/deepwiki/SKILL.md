---
name: deepwiki
description: Query GitHub repositories using DeepWiki AI for capability research
---

# Deep

Wiki Integration Skill

Query GitHub repositories using DeepWiki's AI-powered documentation analysis to research library capabilities instantly.

## What It Does

The `/deepwiki` skill enables automated capability research for GitHub repositories by:
- Accepting GitHub repository URLs and natural language queries
- Using DeepWiki.com's AI to analyze repository documentation
- Caching results locally for instant reuse (70%+ hit rate target)
- Supporting batch queries for comparing multiple libraries
- Returning structured JSON or human-readable Markdown output

**Use Case:** When planning features, quickly research if a library supports specific capabilities without manually reading documentation.

**Example:** "Can KonvaJS create a stage sized to a div with auto-refresh?" → Get instant AI-generated answer with source links.

---

## Usage

### Basic Query

```bash
/deepwiki <github-url> <query>
```

**Example:**
```bash
/deepwiki https://github.com/konvajs/konva "can this create a stage sized to a div with auto-refresh?"
```

**Output:** Structured JSON with answer, sources, and metadata.

---

### Batch Queries (Compare Multiple Libraries)

**Comma-separated queries:**
```bash
/deepwiki https://github.com/d3/d3 --queries "does it support SSR?,what is the bundle size?,is it tree-shakeable?"
```

**Query file (recommended for >3 queries):**
```bash
/deepwiki https://github.com/chartjs/Chart.js --queries-file queries.json
```

**queries.json format:**
```json
{
  "queries": [
    "does it support SSR?",
    "what is the bundle size?",
    "is it tree-shakeable?",
    "does it support TypeScript?",
    "what frameworks are supported?"
  ]
}
```

---

### Command-Line Options

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `<github-url>` | Required | GitHub repository URL | - |
| `<query>` | Optional* | Natural language question | - |
| `--queries` | Optional | Comma-separated list of queries | - |
| `--queries-file` | Optional | Path to JSON file with queries | - |
| `--format` | Optional | Output format: `json` or `markdown` | `json` |
| `--force-refresh` | Flag | Bypass cache, force fresh query | false |
| `--clear-cache` | Flag | Clear all cached results before query | false |
| `--verbose` | Flag | Enable detailed logging | false |
| `--timeout` | Optional | Query timeout in seconds (10-600) | 60 |
| `--cache-stats` | Flag | Show cache statistics (no query) | false |
| `--cache-clear [url]` | Flag | Clear cache (all or specific repo) | false |

\* Either `<query>`, `--queries`, or `--queries-file` is required.

---

## Output Formats

### JSON Output (Default)

```json
{
  "status": "success",
  "repo": {
    "url": "https://github.com/konvajs/konva",
    "deepwiki_url": "https://deepwiki.com/konvajs/konva"
  },
  "queries": [
    {
      "query": "can this create a stage sized to a div with auto-refresh?",
      "answer": "Yes, Konva supports creating a stage that matches the size of a container div. You can use stage.width() and stage.height() to set dimensions dynamically...",
      "sources": [
        "https://konvajs.org/docs/overview.html",
        "https://konvajs.org/docs/shapes/Rect.html"
      ],
      "cached": false,
      "timestamp": "2026-01-31T04:15:32Z"
    }
  ],
  "metadata": {
    "total_queries": 1,
    "cache_hits": 0,
    "cache_misses": 1,
    "total_duration_seconds": 42,
    "retry_attempts": 0
  }
}
```

### Markdown Output

```bash
/deepwiki https://github.com/konvajs/konva "WebGL support?" --format markdown
```

**Output:**
```markdown
# DeepWiki Query Results

**Repository:** https://github.com/konvajs/konva
**DeepWiki URL:** https://deepwiki.com/konvajs/konva

## Query 1: WebGL support?

**Answer:**
Konva supports WebGL rendering through its webgl layer option...

**Sources:**
- [Konva Overview](https://konvajs.org/docs/overview.html)
- [Performance Guide](https://konvajs.org/docs/performance/All_Performance_Tips.html)

**Cached:** No
**Timestamp:** 2026-01-31T04:15:32Z
```

---

## Cache Management

### View Cache Statistics

```bash
/deepwiki --cache-stats
```

**Output:**
```json
{
  "total_entries": 47,
  "unique_repos": 12,
  "oldest_entry": "2026-01-15T08:23:11Z",
  "newest_entry": "2026-01-31T04:15:32Z",
  "total_size_bytes": 284567,
  "total_size_human": "278 KB",
  "top_repos": [
    {"repo": "https://github.com/konvajs/konva", "queries": 8},
    {"repo": "https://github.com/d3/d3", "queries": 6},
    {"repo": "https://github.com/fabricjs/fabric.js", "queries": 5}
  ]
}
```

### Clear Cache

**Clear all cached results:**
```bash
/deepwiki --cache-clear
```

**Clear specific repository:**
```bash
/deepwiki --cache-clear https://github.com/konvajs/konva
```

**Force fresh query (bypass cache once):**
```bash
/deepwiki https://github.com/konvajs/konva "WebGL support?" --force-refresh
```

---

## Workflow Integration

### Use with /spec-plan

Research libraries during feature planning:

```bash
# Step 1: Research library capabilities
/deepwiki https://github.com/konvajs/konva "can this create a stage sized to a div with auto-refresh?"

# Step 2: Use results in planning
/spec-plan "Build canvas editor using library researched above"
```

### Batch Compare Frameworks

Compare multiple libraries to choose the best fit:

```bash
# Create comparison query file
cat > canvas-comparison.json <<EOF
{
  "queries": [
    "does it support SSR?",
    "what is the bundle size?",
    "does it support TypeScript?",
    "WebGL acceleration support?",
    "touch/mobile gesture support?"
  ]
}
EOF

# Query all candidates
/deepwiki https://github.com/konvajs/konva --queries-file canvas-comparison.json
/deepwiki https://github.com/fabricjs/fabric.js --queries-file canvas-comparison.json
/deepwiki https://github.com/pixijs/pixijs --queries-file canvas-comparison.json

# Results cached for instant comparison
```

---

## Troubleshooting

### Common Errors

#### "Invalid GitHub URL format"

**Cause:** URL doesn't match expected pattern.

**Fix:** Ensure URL follows format:
- ✅ `https://github.com/owner/repo`
- ✅ `github.com/owner/repo` (auto-adds https://)
- ❌ `https://gitlab.com/owner/repo` (not GitHub)
- ❌ `https://github.com/owner` (missing repo)

---

#### "Repository not found (404)"

**Cause:** Repository doesn't exist or is misspelled.

**Fix:**
1. Verify repository URL in browser
2. Check for typos in owner/repo names
3. Ensure repository is public (private repos not supported)

---

#### "Query timeout after 60 seconds"

**Cause:** DeepWiki processing took longer than expected.

**Remediation:**
1. Wait a few minutes and try again (DeepWiki may be indexing)
2. Increase timeout: `/deepwiki <url> <query> --timeout 120`
3. Check if repository is very large (may take longer to process)

---

#### "Rate limit exceeded. Wait 60 seconds."

**Cause:** Too many requests in short time period.

**Remediation:**
1. Wait 60 seconds before retrying
2. Use cached results (queries are automatically retried after delay)
3. Reduce batch query sizes

---

#### "Playwright MCP server not available"

**Cause:** Playwright browser automation not set up.

**Fix:**
1. Ensure Playwright MCP server is running
2. Check Claude Code MCP configuration
3. Verify `mcp__puppeteer__*` tools are available

---

### Performance Tips

**Leverage caching:**
- Cache hit: < 1 second (instant)
- Cache miss: 30-60 seconds (first query)
- 70%+ hit rate after regular use

**Optimize batch queries:**
- Batch 5 queries: ~3 minutes (all cache miss)
- Batch 5 queries: ~5 seconds (all cache hit)
- Use `--queries-file` for >3 queries

**Best practices:**
- Query similar repositories together (leverages cache)
- Use descriptive queries (better AI responses)
- Cache persists across sessions (reuse freely)

---

## FAQ

**Q: How long do cached results last?**
A: Currently, cached results persist indefinitely. Future versions may add configurable TTL.

**Q: Where is the cache stored?**
A: `~/.claude/cache/deepwiki/cache.db` (SQLite database, ~1-10 MB typical size)

**Q: Can I query private repositories?**
A: Not currently. DeepWiki only supports public repositories.

**Q: Does this use the DeepWiki API?**
A: No, this skill uses browser automation (Playwright) to interact with DeepWiki's web interface. Future versions may support the DeepWiki MCP API.

**Q: What if DeepWiki's UI changes?**
A: The skill uses multiple selector strategies to adapt. If queries fail persistently, please report an issue.

**Q: Can I use this for non-GitHub repositories?**
A: Not currently. Only GitHub repositories are supported.

**Q: Is there a rate limit?**
A: Yes, DeepWiki has rate limits. The skill implements exponential backoff (5s, 10s, 20s) and batch delays (2s between queries) to avoid limits.

---

## Technical Details

**Dependencies:**
- Python 3.8+ (stdlib only - zero pip dependencies!)
- Playwright MCP server (via Claude Code)
- SQLite 3 (built into Python)

**Cache Database:**
- Location: `~/.claude/cache/deepwiki/cache.db`
- Permissions: 600 (owner read/write only)
- Schema: `query_cache` table with URL normalization and query hashing

**Security:**
- Input validation (URL regex, query sanitization)
- SQL injection prevention (parameterized queries)
- XSS prevention (textContent, not innerHTML)
- Secure file permissions (directory: 700, database: 600)

**Performance:**
- Cache lookup: < 100ms
- Query execution: 30-60s (first time)
- Retry logic: 3 attempts with exponential backoff
- Batch delay: 2s between queries (rate limit protection)

---

## Examples

### Example 1: Quick Capability Check

```bash
# Check if library supports SSR
/deepwiki https://github.com/d3/d3 "does D3 support server-side rendering?"
```

### Example 2: Compare Canvas Libraries

```bash
# Research Konva
/deepwiki https://github.com/konvajs/konva "WebGL support, TypeScript, bundle size"

# Research Fabric.js (queries cached instantly if repeated)
/deepwiki https://github.com/fabricjs/fabric.js "WebGL support, TypeScript, bundle size"

# Research PixiJS
/deepwiki https://github.com/pixijs/pixijs "WebGL support, TypeScript, bundle size"
```

### Example 3: Deep Dive with Batch Queries

```bash
# Create detailed research file
cat > chartjs-research.json <<EOF
{
  "queries": [
    "what chart types are supported?",
    "does it support real-time data updates?",
    "can I customize tooltips?",
    "is there built-in zoom/pan?",
    "does it work with React?",
    "what is the bundle size?",
    "does it support SSR?",
    "is accessibility (a11y) supported?"
  ]
}
EOF

# Execute all queries
/deepwiki https://github.com/chartjs/Chart.js --queries-file chartjs-research.json --format markdown > chartjs-research.md

# View results
cat chartjs-research.md
```

### Example 4: Cache Management

```bash
# View cache statistics
/deepwiki --cache-stats

# Clear cache for specific repo
/deepwiki --cache-clear https://github.com/konvajs/konva

# Force fresh query (bypass cache once)
/deepwiki https://github.com/konvajs/konva "new feature support?" --force-refresh
```

---

## Related Skills

- `/spec-plan` - Use DeepWiki results during feature planning
- `/memory-bank-sync` - Document research findings in Memory Bank
- `/pm-db` - Track skill usage and success metrics

---

## Support

**Issues:** Report problems or request features at the Claude Code GitHub repository.

**Documentation:** See the comprehensive specification files in the skill directory.

**Verbose Mode:** Run with `--verbose` flag for detailed logging and troubleshooting.

---

**Version:** 1.0
**Last Updated:** 2026-01-31
**License:** Same as Claude Code framework
