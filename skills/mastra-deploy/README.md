# /mastra-deploy

> Mastra Deployment and Server guide - server adapters, authentication, middleware, client SDK, cloud providers, and production deployment

## What it does

Loads validated patterns for shipping Mastra apps: `MastraServer` from adapter packages (`@mastra/express`, `@mastra/hono`, `@mastra/fastify`, `@mastra/koa`), auth providers (BetterAuth, Clerk, Supabase), custom routes with `registerApiRoute()`, middleware, the `MastraClient` SDK, and cloud deployers (Vercel, Cloudflare, Netlify, AWS, Azure, Digital Ocean). One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Deploy my Mastra app to Vercel/Cloudflare"
- "Add auth to the Mastra server"
- "Expose a custom API route from Mastra"
- "Call my Mastra agents from the frontend" (MastraClient)
- "Which server adapter should I use?"

## Usage

```bash
/mastra-deploy
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~150 chars); SKILL.md body loads on trigger (~1k chars); full guide via `skill.sh` (~19k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~1k chars) |
| `skill.sh` | Prints the full deployment/server guide (~19k chars) |

## Related skills

- `/mastra-dev` — CLI hub; its `server start|stop|status` commands manage the local AIForge server
- `/mastra-streaming` — SSE/AI SDK routes if the deployment serves streaming UIs
- `/mastra-mcp-tools` — exposing agents over MCP instead of HTTP
