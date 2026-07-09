# Common Closing Sections (Stages 2-5 architecture documents)

All four architecture documents (runtime-execution.md, abstraction-layer.md, integration-layer.md, output-rendering.md) end with the same three sections: **Technology Comparison → Implementation Considerations → Research Sources**. This file is the single canonical template — each stage prompt template contains a `[COMMON CLOSING SECTIONS]` marker where the orchestrator inserts this structure with that stage's variant subsection titles and table columns.

## Canonical structure

```markdown
## Technology Comparison

### [Evaluated-options heading — stage variant]
[Comparison table of the evaluated candidates — stage variant columns]

## Implementation Considerations

### [Subsection 1 — stage variant]
### [Subsection 2 — stage variant]
### [Subsection 3 — stage variant]

## Research Sources
[URLs consulted during research]
```

## Stage variants

### Stage 2 — runtime-execution.md

- Technology Comparison: `### Evaluated Options`, table:

  | Technology | Pros | Cons | Fit Score |
  |------------|------|------|-----------|
  | [Tech 1]   | ...  | ...  | 8/10      |
  | [Tech 2]   | ...  | ...  | 6/10      |
  | [Tech 3]   | ...  | ...  | 4/10      |

  followed by `### Decision Rationale` — [Why we chose what we chose]
- Implementation Considerations: `### Development Setup` [How to run locally] / `### Testing Strategy` [How to test runtime behavior] / `### Monitoring Needs` [What metrics to track]

### Stage 3 — abstraction-layer.md

- Technology Comparison: `### Evaluated Approaches`, table:

  | Approach       | Flexibility | Performance | DX  | Chosen |
  |----------------|-------------|-------------|-----|--------|
  | [Approach 1]   | High        | Medium      | Low | ❌     |
  | [Approach 2]   | Medium      | High        | High| ✅     |

- Implementation Considerations: `### Schema Evolution` [How to version the abstraction layer] / `### Backward Compatibility` [How to handle breaking changes] / `### Documentation Strategy` [How users learn the abstraction]

### Stage 4 — integration-layer.md

- Technology Comparison: `### Evaluated Integration Patterns`, table:

  | Pattern           | Complexity | Reliability | Chosen |
  |-------------------|------------|-------------|--------|
  | Direct API calls  | Low        | Medium      | ✅     |
  | Message queue     | Medium     | High        | ❌     |
  | Service mesh      | High       | High        | ❌     |

- Implementation Considerations: `### Local Development` [How to run external dependencies locally] / `### Testing Strategy` [Mocking, test containers, integration tests] / `### Monitoring & Observability` [Metrics, logs, traces for integrations]

### Stage 5 — output-rendering.md

- Technology Comparison: `### Evaluated Rendering Approaches`, table:

  | Approach | SEO | Performance | Complexity | Chosen |
  |----------|-----|-------------|------------|--------|
  | SSR      | ✅  | Medium      | Medium     | ✅     |
  | CSR      | ❌  | Slow        | Low        | ❌     |
  | SSG      | ✅  | Fast        | Low        | ✅     |

- Implementation Considerations: `### Development Experience` [Hot reload, dev server, debugging] / `### Testing Strategy` [Component tests, visual regression, E2E] / `### Monitoring` [Performance metrics, Core Web Vitals]
