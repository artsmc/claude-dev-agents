# Database Schema Specialist — Patterns Module

Load this module when you need full boilerplate for Prisma schema design, migration SQL, seeding, or the standard recurring patterns (timestamps, enums, join tables, soft deletes, audit logs, optimistic locking).

---

## Full Prisma Schema Example

```prisma
// apps/api/prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  password  String
  role      Role     @default(USER)
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  posts     Post[]
  comments  Comment[]
  profile   Profile?

  @@index([email])
  @@map("users")
}

model Post {
  id        Int       @id @default(autoincrement())
  title     String
  content   String    @db.Text
  published Boolean   @default(false)
  deletedAt DateTime? @map("deleted_at")
  authorId  Int       @map("author_id")
  version   Int       @default(1)
  createdAt DateTime  @default(now()) @map("created_at")
  updatedAt DateTime  @updatedAt @map("updated_at")

  author   User      @relation(fields: [authorId], references: [id], onDelete: Cascade)
  comments Comment[]
  tags     PostTag[]

  @@index([authorId])
  @@index([published, createdAt])
  @@map("posts")
}

model Comment {
  id        Int      @id @default(autoincrement())
  content   String
  postId    Int      @map("post_id")
  authorId  Int      @map("author_id")
  createdAt DateTime @default(now()) @map("created_at")

  post   Post @relation(fields: [postId], references: [id], onDelete: Cascade)
  author User @relation(fields: [authorId], references: [id], onDelete: Cascade)

  @@index([postId])
  @@index([authorId])
  @@map("comments")
}

model Profile {
  id     Int     @id @default(autoincrement())
  bio    String?
  avatar String?
  userId Int     @unique @map("user_id")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("profiles")
}

model Tag {
  id    Int       @id @default(autoincrement())
  name  String    @unique
  posts PostTag[]

  @@map("tags")
}

// Many-to-many via explicit join table
model PostTag {
  postId Int @map("post_id")
  tagId  Int @map("tag_id")

  post Post @relation(fields: [postId], references: [id], onDelete: Cascade)
  tag  Tag  @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@id([postId, tagId])
  @@map("post_tags")
}

model AuditLog {
  id        Int      @id @default(autoincrement())
  tableName String   @map("table_name")
  recordId  Int      @map("record_id")
  action    String   // 'CREATE' | 'UPDATE' | 'DELETE'
  changes   Json?    // { before: {...}, after: {...} }
  userId    Int      @map("user_id")
  timestamp DateTime @default(now())

  @@index([tableName, recordId])
  @@index([userId])
  @@map("audit_logs")
}

enum Role {
  USER
  ADMIN
  CONTRACTOR
}

enum OrderStatus {
  PENDING
  PAID
  SHIPPED
  DELIVERED
  CANCELLED
}
```

---

## Migration SQL Patterns

### New table (up + down)

```sql
-- Up: migrations/001_create_users_table.up.sql
CREATE TABLE users (
    id           SERIAL PRIMARY KEY,
    email        VARCHAR(255) UNIQUE NOT NULL,
    name         VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role         VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'contractor')),
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Down: migrations/001_create_users_table.down.sql
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP FUNCTION IF EXISTS update_updated_at_column;
DROP TABLE IF EXISTS users;
```

### Add column to existing table

```sql
-- Up
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
CREATE INDEX CONCURRENTLY idx_users_last_login ON users(last_login);

-- Down
DROP INDEX CONCURRENTLY idx_users_last_login;
ALTER TABLE users DROP COLUMN last_login;
```

### Large table: add index in separate migration

When a table has millions of rows, index creation with `CONCURRENTLY` avoids locking writes. Always do this in its own migration file so it can be re-run independently if it fails.

---

## Soft Deletes

```prisma
// Schema
model Post {
  deletedAt DateTime? @map("deleted_at")
}
```

```typescript
// Query only active records
const activePosts = await prisma.post.findMany({
  where: { deletedAt: null }
});

// Soft delete (reversible)
await prisma.post.update({
  where: { id: 1 },
  data: { deletedAt: new Date() }
});
```

Never use hard deletes for user-generated content unless explicitly required. Soft deletes preserve audit trails and enable undo.

---

## Optimistic Locking

```prisma
model Document {
  id      Int    @id @default(autoincrement())
  title   String
  content String
  version Int    @default(1)
}
```

```typescript
const doc = await prisma.document.findUnique({ where: { id: 1 } });

const updated = await prisma.document.updateMany({
  where: {
    id: 1,
    version: doc.version  // Only succeeds if nobody else updated first
  },
  data: {
    content: newContent,
    version: { increment: 1 }
  }
});

if (updated.count === 0) {
  throw new Error('Conflict: document was modified by another process');
}
```

Use when multiple processes or users may update the same record concurrently. Cheaper than pessimistic locking for read-heavy workloads.

---

## Audit Trail Pattern

Every change to sensitive entities (users, roles, workflows, executions) should be recorded:

```typescript
// In a service method, after updating the entity:
await prisma.auditLog.create({
  data: {
    tableName: 'users',
    recordId:  user.id,
    action:    'UPDATE',
    changes:   { before: oldValues, after: newValues },
    userId:    requestingUser.id,
  }
});
```

For FedRAMP/HIPAA compliance, retain audit logs for 7 years in immutable storage (S3 Object Lock in COMPLIANCE mode). See security-auditor-compliance.md for the full retention checklist.

---

## Database Seeding (Prisma)

```typescript
// apps/api/prisma/seed.ts
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  const alice = await prisma.user.upsert({
    where: { email: 'alice@example.com' },
    update: {},
    create: {
      email:    'alice@example.com',
      name:     'Alice',
      password: 'hashed_password',
      role:     'ADMIN',
    },
  });

  await prisma.post.createMany({
    data: [
      { title: 'First Post', content: 'Hello World!', published: true,  authorId: alice.id },
      { title: 'Draft Post', content: 'WIP...',        published: false, authorId: alice.id },
    ],
    skipDuplicates: true,
  });
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

```json
// apps/api/package.json (or root package.json prisma section)
{
  "prisma": {
    "seed": "ts-node apps/api/prisma/seed.ts"
  }
}
```

```bash
npx prisma db seed
```

Use `upsert` in seeds so they are idempotent — safe to re-run in CI and development resets.
