# Database Schema Specialist — Query Optimization Module

Load this module when the task involves slow query diagnosis, EXPLAIN ANALYZE interpretation, covering indexes, connection pooling, or N+1 elimination.

---

## Identify Slow Queries

### PostgreSQL slow query log

```sql
-- Log queries taking longer than 1 second (set in postgresql.conf or via ALTER SYSTEM)
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Find current slow queries (running right now)
SELECT pid, now() - query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '1 second'
ORDER BY duration DESC;

-- Most time-consuming queries (pg_stat_statements extension required)
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

---

## EXPLAIN ANALYZE

Always run `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` — not just `EXPLAIN` — to see actual row counts and buffer hits:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON p.author_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name
ORDER BY post_count DESC
LIMIT 10;
```

### Reading the output

| Node type | What to look for |
|-----------|-----------------|
| `Seq Scan` | Full table scan — usually means a missing index |
| `Index Scan` | Good for selective queries |
| `Index Only Scan` | Best — data served from index, no heap fetch |
| `Nested Loop` | Fine for small result sets; slow when outer side is large |
| `Hash Join` | Good for larger joins |
| `Rows Removed by Filter: N` | Large N = index not selective enough |
| `actual rows=X / estimated rows=Y` | Large mismatch = stale statistics; run `ANALYZE <table>` |

**Stale statistics fix:**
```sql
ANALYZE users;         -- Update statistics for one table
ANALYZE;               -- Update all tables (safe, fast)
VACUUM ANALYZE users;  -- Reclaim space + update statistics
```

---

## Index Types and When to Use Them

```sql
-- B-tree (default) — equality, range, ORDER BY
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- Partial index — only index the rows that matter
CREATE INDEX idx_posts_published ON posts(author_id, created_at DESC)
WHERE published = true;
-- Cuts index size dramatically when only a subset is queried

-- Covering index — include all columns the query needs (avoids heap fetch)
CREATE INDEX idx_users_lookup ON users(email) INCLUDE (name, role);
-- This query now uses Index Only Scan:
SELECT email, name, role FROM users WHERE email = 'user@example.com';

-- GIN index — full-text search or JSONB containment
CREATE INDEX idx_documents_content ON documents USING GIN(to_tsvector('english', content));
CREATE INDEX idx_metadata_gin ON records USING GIN(metadata jsonb_path_ops);

-- CONCURRENTLY — create index without locking writes (use in production migrations)
CREATE INDEX CONCURRENTLY idx_large_table_col ON large_table(col);
```

---

## N+1 Elimination

The N+1 problem: fetching a list, then querying once per row inside a loop.

```sql
-- BEFORE: N+1 (1 query for users, then 1 per user for their posts)
SELECT * FROM users WHERE id = 1;
SELECT * FROM posts WHERE author_id = 1;
-- ...repeated for every user

-- AFTER: single JOIN
SELECT u.id, u.name, u.email, p.id AS post_id, p.title
FROM users u
LEFT JOIN posts p ON p.author_id = u.id
WHERE u.id = ANY(ARRAY[1, 2, 3, 4, 5]);
```

In Prisma, use `include` or `select` with nested relations — Prisma generates JOIN or batched queries automatically:

```typescript
// N+1 prone
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } }); // N queries
}

// Correct: let Prisma batch it
const users = await prisma.user.findMany({
  include: { posts: true }  // 2 queries: 1 for users, 1 batched for posts
});
```

---

## Pagination

Never use `OFFSET` for large tables — it scans and discards rows up to the offset.

```sql
-- Keyset (cursor) pagination — O(log N) with an index
SELECT id, title, created_at
FROM posts
WHERE published = true
  AND (created_at, id) < ($last_created_at, $last_id)   -- cursor from previous page
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

```typescript
// Prisma cursor pagination
const page = await prisma.post.findMany({
  where:   { published: true },
  orderBy: [{ createdAt: 'desc' }, { id: 'desc' }],
  take:    20,
  cursor:  cursor ? { id: cursor } : undefined,
  skip:    cursor ? 1 : 0,    // skip the cursor row itself on subsequent pages
});
const nextCursor = page.length === 20 ? page[page.length - 1].id : null;
```

---

## Connection Pooling

PostgreSQL has a hard limit on concurrent connections (default: 100). Each Node.js process holding a `PrismaClient` or `Pool` instance contributes connections.

```typescript
// Prisma connection pool (apps/api/src/services/prisma.service.ts)
// Singleton pattern — one client per process
import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    datasources: {
      db: { url: process.env.DATABASE_URL }
    },
    // Pool size via DATABASE_URL: ?connection_limit=10&pool_timeout=10
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
```

Configure pool size in the `DATABASE_URL`:
```
postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=10
```

For high-concurrency deployments, use **PgBouncer** (already used by apps/mastra via PGBoss) in transaction pooling mode to multiplex many application connections over fewer server connections.

---

## Optimization Decision Checklist

Before declaring a query optimized:

- [ ] `EXPLAIN (ANALYZE, BUFFERS)` reviewed — no unexpected Seq Scans on large tables
- [ ] Estimated vs actual rows are close (if not, run `ANALYZE <table>`)
- [ ] No N+1 patterns in application layer
- [ ] Pagination uses keyset (cursor), not `OFFSET`
- [ ] Indexes cover common `WHERE`, `JOIN`, `ORDER BY` columns
- [ ] Partial indexes used where only a data subset is queried
- [ ] Covering indexes used where Index Only Scan is beneficial
- [ ] No `SELECT *` in production queries — select only needed columns
- [ ] Result sets are bounded (`LIMIT` or pagination in place)
- [ ] Connection pool size appropriate for expected concurrency
