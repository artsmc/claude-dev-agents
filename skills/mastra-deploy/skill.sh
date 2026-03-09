#!/usr/bin/env bash
################################################################################
# mastra-deploy - Mastra Deployment & Server Configuration Skill
#
# Outputs comprehensive guidance for deploying Mastra applications,
# configuring servers, adapters, authentication, and cloud providers.
# Usage: bash skill.sh
################################################################################

cat << 'SKILL_EOF'
# Mastra Deployment & Server Configuration Guide

## Table of Contents
1. Deployment Overview
2. Mastra Server Setup (Standalone)
3. Server Adapters (Express, Hono, Fastify, Koa)
4. Custom API Routes
5. Middleware
6. Request Context
7. Authentication
8. Mastra Client SDK
9. Cloud Provider Deployment
10. Best Practices

---

## 1. Deployment Overview

Mastra applications can be deployed in multiple ways:

- **Standalone Server** - `mastra build` generates a Hono-based HTTP server with all endpoints
- **Framework Adapter** - Integrate into Express, Hono, Fastify, or Koa using `MastraServer`
- **Serverless** - Deploy with built-in deployers for Vercel, Cloudflare, Netlify
- **Containers/VMs** - Docker deployment on AWS EC2, DigitalOcean, GCP, Azure
- **Mastra Cloud** - Fully managed deployment

The Mastra server exposes API endpoints for agents, workflows, tools, and MCP servers automatically.

---

## 2. Mastra Server Setup (Standalone)

### Basic Mastra Instance

```typescript
import { Mastra } from '@mastra/core';
import { createTool } from '@mastra/core/tools';
import { Agent } from '@mastra/core/agent';

const myAgent = new Agent({
  id: 'my-agent',
  name: 'My Agent',
  description: 'A helpful assistant',
  instructions: 'You are a helpful assistant.',
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
});

export const mastra = new Mastra({
  agents: { myAgent },
});
```

### Build and Run Standalone

```bash
# Build standalone Hono server
npx mastra build

# Start the built server
node .mastra/output/index.mjs
```

### Auto-Generated Endpoints

The Mastra server automatically creates these REST endpoints under `/api`:

| Endpoint Pattern                              | Method | Description                    |
|-----------------------------------------------|--------|--------------------------------|
| `/api/agents`                                 | GET    | List all registered agents     |
| `/api/agents/:agentId/generate`               | POST   | Generate text with an agent    |
| `/api/agents/:agentId/stream`                 | POST   | Stream text from an agent      |
| `/api/workflows`                              | GET    | List all registered workflows  |
| `/api/workflows/:workflowId/execute`          | POST   | Execute a workflow             |
| `/api/workflows/:workflowId/status/:runId`    | GET    | Check workflow run status      |
| `/health`                                     | GET    | Health check endpoint          |

Docs: https://mastra.ai/docs/deployment/mastra-server

---

## 3. Server Adapters (Express, Hono, Fastify, Koa)

Adapters let you integrate Mastra into an existing HTTP framework. Each adapter imports `MastraServer` from its respective package, takes your framework app + Mastra instance, and calls `init()`.

### Express Adapter

```bash
npm install @mastra/express@latest express
```

```typescript
import express from 'express';
import { MastraServer } from '@mastra/express';
import { mastra } from './mastra';

const app = express();
app.use(express.json()); // REQUIRED for Express

const server = new MastraServer({ app, mastra });
await server.init();

// Add custom Express routes (after init, they can access res.locals.mastra)
app.get('/custom', (req, res) => {
  res.json({ message: 'Custom route alongside Mastra' });
});

app.listen(3001, () => {
  console.log('Server running on port 3001');
});
```

### Hono Adapter

```bash
npm install @mastra/hono@latest hono
```

```typescript
import { Hono } from 'hono';
import { MastraServer } from '@mastra/hono';
import type { HonoBindings, HonoVariables } from '@mastra/hono';
import { mastra } from './mastra';

const app = new Hono<{ Bindings: HonoBindings; Variables: HonoVariables }>();

const server = new MastraServer({ app, mastra });
await server.init();

export default app;
```

### Fastify Adapter

```bash
npm install @mastra/fastify@latest fastify
```

```typescript
import Fastify from 'fastify';
import { MastraServer } from '@mastra/fastify';
import { mastra } from './mastra';

const app = Fastify();

const server = new MastraServer({ app, mastra });
await server.init();

await app.listen({ port: 3001 });
```

### Koa Adapter

```bash
npm install @mastra/koa@latest koa
```

```typescript
import Koa from 'koa';
import { MastraServer } from '@mastra/koa';
import { mastra } from './mastra';

const app = new Koa();

const server = new MastraServer({ app, mastra });
await server.init();

app.listen(3001);
```

### MastraServer Constructor Options

```typescript
const server = new MastraServer({
  app,                    // Framework app instance (required)
  mastra,                 // Mastra instance (required)
  prefix: '/api',         // Route prefix (default: '/api')
  openapiPath: '/openapi.json', // OpenAPI spec endpoint
  streamOptions: {},      // Stream data redaction options
  customRouteAuthConfig: {
    'GET:/public': false,  // Disable auth for specific routes
  },
});
```

### Advanced: Manual Initialization Steps

For custom middleware ordering, call init steps individually:

```typescript
const server = new MastraServer({ app, mastra });

// Step 1: Attach Mastra instance to every request
server.registerContextMiddleware();

// Insert your own middleware here (e.g., logging, custom headers)
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Step 2: Add auth middleware (only if server.auth is configured)
server.registerAuthMiddleware();

// Step 3: Register all Mastra API routes + MCP routes
server.registerRoutes();
```

Docs: https://mastra.ai/docs/server/server-adapters

---

## 4. Custom API Routes

Extend the Mastra server with custom endpoints using `registerApiRoute` from `@mastra/core/server`. Handlers receive Hono's Context object.

### Basic Custom Route

```typescript
import { Mastra } from '@mastra/core';
import { registerApiRoute } from '@mastra/core/server';

export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    apiRoutes: [
      registerApiRoute('/my-custom-route', {
        method: 'GET',
        handler: async (c) => {
          // Access Mastra instance via Hono context
          const mastra = c.get('mastra');
          const agent = mastra.getAgent('myAgent');
          const result = await agent.generate('Hello!');
          return c.json({ response: result.text });
        },
      }),
    ],
  },
});
```

### Route with Middleware

```typescript
registerApiRoute('/protected-route', {
  method: 'POST',
  middleware: [
    async (c, next) => {
      console.log(`${c.req.method} ${c.req.url}`);
      await next();
    },
    async (c, next) => {
      const apiKey = c.req.header('x-api-key');
      if (!apiKey) {
        return c.json({ error: 'Missing API key' }, 401);
      }
      await next();
    },
  ],
  handler: async (c) => {
    const body = await c.req.json();
    const mastra = c.get('mastra');
    const agent = mastra.getAgent('myAgent');
    const result = await agent.generate(body.message);
    return c.json({ response: result.text });
  },
});
```

### Route with OpenAPI Documentation

```typescript
registerApiRoute('/analyze', {
  method: 'POST',
  openapi: {
    summary: 'Analyze text',
    description: 'Analyze text using an AI agent',
    requestBody: {
      content: {
        'application/json': {
          schema: z.object({
            text: z.string(),
          }),
        },
      },
    },
    responses: {
      200: {
        description: 'Analysis result',
        content: {
          'application/json': {
            schema: z.object({
              analysis: z.string(),
            }),
          },
        },
      },
    },
  },
  handler: async (c) => {
    const { text } = await c.req.json();
    return c.json({ analysis: 'Result here' });
  },
});
```

### Public Route (Skip Auth)

```typescript
registerApiRoute('/health-check', {
  method: 'GET',
  requiresAuth: false, // Bypass authentication
  handler: async (c) => {
    return c.json({ status: 'healthy' });
  },
});
```

Docs: https://mastra.ai/docs/server/custom-api-routes

---

## 5. Middleware

### Server-Level Middleware

Middleware is configured through the Mastra constructor or injected via the adapter init steps.

```typescript
export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    // Body size limit (in bytes)
    bodySizeLimit: 10 * 1024 * 1024, // 10MB

    // Custom API routes with inline middleware
    apiRoutes: [
      registerApiRoute('/my-route', {
        method: 'GET',
        middleware: [
          async (c, next) => {
            const start = Date.now();
            await next();
            console.log(`Request took ${Date.now() - start}ms`);
          },
        ],
        handler: async (c) => c.json({ ok: true }),
      }),
    ],
  },
});
```

### Express Adapter Middleware Ordering

```typescript
import express from 'express';
import { MastraServer } from '@mastra/express';
import { mastra } from './mastra';

const app = express();
app.use(express.json());

// Middleware BEFORE Mastra init (runs before Mastra context)
app.use((req, res, next) => {
  console.log('Before Mastra context');
  next();
});

const server = new MastraServer({ app, mastra });

// Manual init for precise ordering
server.registerContextMiddleware();

// Middleware BETWEEN context and auth
app.use((req, res, next) => {
  console.log('After Mastra context, before auth');
  next();
});

server.registerAuthMiddleware();

// Middleware BETWEEN auth and routes
app.use((req, res, next) => {
  if (!req.headers.authorization) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

server.registerRoutes();

app.listen(3001);
```

### CORS Configuration (Express)

```typescript
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(cors({
  origin: ['http://localhost:3500', 'https://myapp.com'],
  credentials: true,
}));

const server = new MastraServer({ app, mastra });
await server.init();
```

Docs: https://mastra.ai/docs/server-db/middleware

---

## 6. Request Context

### Express Adapter Context Access

In Express adapter, context is available via `res.locals`:

```typescript
app.get('/my-route', (req, res) => {
  const mastra = res.locals.mastra;         // Mastra instance
  const requestContext = res.locals.requestContext; // Request context map
  const abortSignal = res.locals.abortSignal;     // Cancellation signal
  const tools = res.locals.tools;
  const user = res.locals.user;             // Authenticated user (if auth configured)

  const agent = mastra.getAgent('myAgent');
  // ... use agent
});
```

### Hono Context Access

In the standalone Hono server or Hono adapter, use `c.get()`:

```typescript
registerApiRoute('/my-route', {
  method: 'GET',
  handler: async (c) => {
    const mastra = c.get('mastra');
    const requestContext = c.get('requestContext');
    const user = c.get('requestContext')?.get('user');

    const agent = mastra.getAgent('myAgent');
    const result = await agent.generate('Hello');
    return c.json({ text: result.text });
  },
});
```

---

## 7. Authentication

Mastra supports pluggable authentication. Auth providers integrate via the Mastra constructor's `server` config. Install the corresponding `@mastra/auth-*` package for each provider.

### JWT Authentication (Built-in)

```typescript
import { Mastra } from '@mastra/core';
import { MastraJwtAuth } from '@mastra/core/server';

export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    auth: new MastraJwtAuth({
      secret: process.env.JWT_SECRET!,
    }),
  },
});
```

### Better Auth

```bash
npm install @mastra/auth-better-auth better-auth
```

```typescript
import { Mastra } from '@mastra/core';
import { MastraAuthBetterAuth } from '@mastra/auth-better-auth';
import { auth } from './lib/auth'; // Your betterAuth instance

const mastraAuth = new MastraAuthBetterAuth({ auth });

export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    auth: mastraAuth, // Uses server.auth (not experimental_auth)
  },
});
```

### Clerk

```bash
npm install @mastra/auth-clerk
```

```typescript
import { Mastra } from '@mastra/core';
import { MastraAuthClerk } from '@mastra/auth-clerk';

export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    experimental_auth: new MastraAuthClerk({
      publishableKey: process.env.CLERK_PUBLISHABLE_KEY!,
      secretKey: process.env.CLERK_SECRET_KEY!,
      jwksUri: process.env.CLERK_JWKS_URI!,
    }),
  },
});
```

### Supabase

```bash
npm install @mastra/auth-supabase
```

```typescript
import { Mastra } from '@mastra/core';
import { MastraAuthSupabase } from '@mastra/auth-supabase';

export const mastra = new Mastra({
  agents: { myAgent },
  server: {
    experimental_auth: new MastraAuthSupabase({
      url: process.env.SUPABASE_URL!,
      anonKey: process.env.SUPABASE_ANON_KEY!,
    }),
  },
});
```

### Accessing Authenticated User

```typescript
// In custom route handler (Hono context)
registerApiRoute('/profile', {
  method: 'GET',
  handler: async (c) => {
    const user = c.get('requestContext')?.get('user');
    return c.json({ user });
  },
});

// In Express route (after init)
app.get('/profile', (req, res) => {
  const user = res.locals.user;
  res.json({ user });
});
```

Docs: https://mastra.ai/docs/auth

---

## 8. Mastra Client SDK

The `@mastra/client-js` package provides a typed client for interacting with a Mastra server.

### Installation

```bash
npm install @mastra/client-js
```

### Client Setup

```typescript
import { MastraClient } from '@mastra/client-js';

const client = new MastraClient({
  baseUrl: 'http://localhost:4111',
  // Optional configuration
  headers: {
    Authorization: `Bearer ${token}`,
  },
  retries: 3,          // Retry attempts (default: 3)
  backoffMs: 300,      // Initial backoff (default: 300)
  maxBackoffMs: 5000,  // Max backoff (default: 5000)
});
```

### Agent Interactions

```typescript
// Get an agent handle
const agent = client.getAgent('my-agent');

// Generate text
const result = await agent.generate({
  messages: [{ role: 'user', content: 'Hello, how are you?' }],
});
console.log(result.text);

// Stream text
const stream = await agent.stream({
  messages: [{ role: 'user', content: 'Tell me a story' }],
});
stream.processDataStream({
  onTextPart: (text) => {
    process.stdout.write(text);
  },
});
```

### Workflow Interactions

```typescript
// Get a workflow handle
const workflow = client.getWorkflow('my-workflow');

// Create and run a workflow
const run = await workflow.createRun();
const result = await workflow.startAsync({
  runId: run.runId,
  inputData: { query: 'some data' },
});
console.log(result);
```

Docs: https://mastra.ai/docs/server/mastra-client

---

## 9. Cloud Provider Deployment

### 1. Vercel (Serverless Functions)

```bash
npm install @mastra/deployer-vercel
```

```typescript
// src/mastra/index.ts
import { Mastra } from '@mastra/core';
import { VercelDeployer } from '@mastra/deployer-vercel';

export const mastra = new Mastra({
  agents: { myAgent },
  deployer: new VercelDeployer({
    teamSlug: 'my-team',
    projectName: 'my-mastra-app',
    token: process.env.VERCEL_TOKEN!,
  }),
});
```

```bash
npx mastra deploy
```

### 2. Cloudflare Workers

```bash
npm install @mastra/deployer-cloudflare
```

```typescript
import { Mastra } from '@mastra/core';
import { CloudflareDeployer } from '@mastra/deployer-cloudflare';

export const mastra = new Mastra({
  agents: { myAgent },
  deployer: new CloudflareDeployer({
    scope: process.env.CF_ACCOUNT_ID!,
    projectName: 'my-mastra-worker',
  }),
});
```

```bash
npx mastra deploy
```

### 3. Netlify (Serverless)

```bash
npm install @mastra/deployer-netlify
```

```typescript
import { Mastra } from '@mastra/core';
import { NetlifyDeployer } from '@mastra/deployer-netlify';

export const mastra = new Mastra({
  agents: { myAgent },
  deployer: new NetlifyDeployer({
    scope: 'my-team-slug',
    projectName: 'my-mastra-app',
    token: process.env.NETLIFY_TOKEN!,
  }),
});
```

```bash
npx mastra deploy
```

### 4. Docker (VMs: EC2, DigitalOcean, Azure, GCP)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npx mastra build
EXPOSE 3000
CMD ["node", ".mastra/output/index.mjs"]
```

```bash
docker build -t mastra-api .
docker run -p 3000:3000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  mastra-api
```

### 5. Deploy with Framework Adapter (Any Platform)

Since adapters produce a standard Node.js server, deploy anywhere:

```typescript
// server.ts
import express from 'express';
import { MastraServer } from '@mastra/express';
import { mastra } from './mastra';

const app = express();
app.use(express.json());

const server = new MastraServer({ app, mastra });
await server.init();

const port = parseInt(process.env.PORT || '3000');
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

Docs: https://mastra.ai/docs/deployment/overview

---

## 10. Best Practices

### Security
- Use environment variables for ALL secrets - never hardcode API keys
- Configure authentication for public-facing endpoints
- Set up CORS to only allow your frontend domains
- Use HTTPS in production (terminate TLS at load balancer)

### Performance
- Set up health check endpoints for load balancers
- Use connection pooling for database connections
- Configure appropriate body size limits
- Use streaming for long agent responses

### Architecture
- Use the right adapter for your existing stack
- Keep Mastra configuration in a shared module
- Use `registerApiRoute` for custom endpoints instead of bypassing Mastra
- Use manual init steps when you need precise middleware ordering

### Deployment Checklist
1. Environment variables configured
2. Authentication enabled and tested
3. CORS origins restricted to production domains
4. Health check endpoint responding
5. Database migrations applied
6. Monitoring and alerting configured
7. SSL/TLS termination configured

---

## Quick Reference Links

- Deployment Overview: https://mastra.ai/docs/deployment/overview
- Mastra Server: https://mastra.ai/docs/deployment/mastra-server
- Server Adapters: https://mastra.ai/docs/server/server-adapters
- Express Adapter Reference: https://mastra.ai/reference/server/express-adapter
- Custom API Routes: https://mastra.ai/docs/server/custom-api-routes
- Middleware: https://mastra.ai/docs/server-db/middleware
- Authentication: https://mastra.ai/docs/auth
- Client SDK: https://mastra.ai/docs/server/mastra-client
- Cloud Providers: https://mastra.ai/docs/deployment/cloud-providers
- Vercel Deployer: https://mastra.ai/docs/deployment/cloud-providers/vercel-deployer
- Cloudflare Deployer: https://mastra.ai/docs/deployment/cloud-providers/cloudflare-deployer
- Netlify Deployer: https://mastra.ai/docs/deployment/cloud-providers/netlify-deployer

SKILL_EOF
