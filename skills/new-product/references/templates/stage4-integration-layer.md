# Stage 4 Agent Prompt: Integration Layer Research

Orchestrator: the prompt below is passed verbatim to a `Task` agent (`subagent_type="general-purpose"`). Substitute [Product Name], paste the full big-idea.md content into CONTEXT, and replace the [COMMON CLOSING SECTIONS] marker with the block from `common-closing-sections.md` (Stage 4 variants).

---

You are researching integration layer architecture for: [Product Name]

CONTEXT:
[Include big-idea.md content]

YOUR GOAL:
Create a comprehensive `integration-layer.md` document that explains how the system connects to external resources.

RESEARCH APPROACH:
1. Research connector patterns and integration architectures
2. Use WebSearch for:
   - "[technology] connector architecture 2026"
   - "API integration best practices 2026"
   - "[technology] authentication patterns 2026"
   - "service mesh architecture 2026" (if microservices)

3. Use WebFetch for vendor-specific docs (if integrating with known services)

4. Ask user clarifying questions

QUESTIONS TO ASK USER:

1. **Integration Scope**
   - Header: "Integrations"
   - Question: "What external systems will this product integrate with?"
   - MultiSelect: true
   - Options:
     - "Databases" - "PostgreSQL, MySQL, MongoDB, etc."
     - "APIs (REST/GraphQL)" - "External HTTP APIs"
     - "Message queues" - "RabbitMQ, Kafka, SQS, etc."
     - "Storage services" - "S3, GCS, Azure Storage"

2. **Authentication Strategy**
   - Header: "Auth"
   - Question: "How should the system authenticate to external services?"
   - Options:
     - "API keys" - "Simple token-based auth"
     - "OAuth 2.0" - "Delegated authorization"
     - "Mutual TLS" - "Certificate-based auth"
     - "Service accounts" - "Cloud provider IAM"

3. **Discovery Mechanism**
   - Header: "Discovery"
   - Question: "How should the system discover external services?"
   - Options:
     - "Static configuration" - "Hardcoded endpoints"
     - "Environment variables" - "Deploy-time config"
     - "Service discovery" - "Consul, Eureka, k8s DNS"
     - "Dynamic registry" - "Runtime service registration"

DOCUMENT STRUCTURE:

Create: /job-queue/product-{name}/integration-layer.md

# Integration Layer Architecture

## Executive Summary
[How the system connects to external resources]

## Connector Architecture

### Connector Pattern
[Plugin-based, driver-based, adapter pattern]

### Supported Protocols
- REST API
- GraphQL
- gRPC
- Message queues
- Database protocols
- Custom protocols

### Connector Lifecycle
[How connectors are initialized, used, closed]

## Authentication & Credential Management

### Authentication Methods
[API keys, OAuth, mTLS, service accounts]

### Credential Storage
[Where credentials live: env vars, secrets manager, vault]

### Rotation Strategy
[How credentials are rotated without downtime]

### Security Boundaries
[How credentials are isolated per service]

## Service Discovery

### Discovery Mechanism
[Static, env-based, service discovery, dynamic]

### Configuration Format
```json
{
  "services": {
    "database": {
      "type": "postgresql",
      "discovery": "static",
      "endpoint": "..."
    }
  }
}
```

### Health Checking
[How to detect unhealthy services]

## Data Flow Patterns

### Pull Pattern
[Request-response, polling]

### Push Pattern
[Webhooks, callbacks]

### Streaming Pattern
[WebSockets, SSE, gRPC streams]

### Chosen Approach per Integration
| Integration | Pattern | Rationale |
|-------------|---------|-----------|
| [Service 1] | Pull    | [Why]     |
| [Service 2] | Stream  | [Why]     |

## Error Handling & Retry Logic

### Error Classification
- Transient errors (retry)
- Permanent errors (fail fast)
- Rate limit errors (backoff)

### Retry Strategy
- Exponential backoff
- Circuit breaker pattern
- Fallback mechanisms

### Example: Retry Configuration
```json
{
  "retry": {
    "maxAttempts": 3,
    "backoff": "exponential",
    "initialDelay": "100ms"
  }
}
```

## Security & Isolation

### Network Segmentation
[How integrations are network-isolated]

### Data Encryption
[TLS for transit, encryption at rest]

### Least Privilege
[IAM policies, scoped credentials]

[COMMON CLOSING SECTIONS — orchestrator: insert the block from references/templates/common-closing-sections.md here, using the Stage 4 (integration) variants: Technology Comparison, Implementation Considerations, Research Sources]

---

Write to: /job-queue/product-{name}/integration-layer.md
Research notes: /job-queue/product-{name}/research-notes/integration-research.md
