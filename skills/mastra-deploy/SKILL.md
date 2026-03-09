---
name: mastra-deploy
description: Mastra Deployment and Server guide - server adapters, authentication, middleware, client SDK, cloud providers, and production deployment
---

# Mastra Deployment and Server Configuration

Comprehensive guide for deploying Mastra applications. Covers MastraServer with adapter packages (@mastra/express, @mastra/hono, @mastra/fastify, @mastra/koa), authentication providers, custom API routes, middleware, MastraClient SDK, and cloud deployment (Vercel, Cloudflare, Netlify, AWS, Azure, Digital Ocean).

## Usage

```bash
/mastra-deploy
```

Provides context for:
- `MastraServer` from adapter packages (not `createServer`)
- Server adapters: Express, Hono, Fastify, Koa
- Auth: `MastraAuthBetterAuth`, `MastraAuthClerk`, `MastraAuthSupabase`
- `registerApiRoute()` with Hono-style context
- `MastraClient` SDK (`getAgent()`, `getWorkflow()`)
- Cloud deployers: `VercelDeployer`, `CloudflareDeployer`, `NetlifyDeployer`
- Middleware and request context patterns
