# Stage 3 Agent Prompt: Abstraction Layer Research

Orchestrator: the prompt below is passed verbatim to a `Task` agent (`subagent_type="general-purpose"`). Substitute [Product Name], paste the full big-idea.md content into CONTEXT, and replace the [COMMON CLOSING SECTIONS] marker with the block from `common-closing-sections.md` (Stage 3 variants).

---

You are researching abstraction layer architecture for: [Product Name]

CONTEXT:
[Include big-idea.md content]

YOUR GOAL:
Create a comprehensive `abstraction-layer.md` document that explains how user intent translates to executable logic.

RESEARCH APPROACH:
1. Research how modern frameworks handle abstraction
2. Use WebSearch for:
   - "[technology] abstraction patterns 2026"
   - "[technology] DSL design 2026"
   - "no-code/low-code architecture 2026" (if applicable)
   - "[technology] configuration vs code 2026"

3. Use WebFetch to read architectural docs

4. Ask user clarifying questions

QUESTIONS TO ASK USER:

1. **Input Format**
   - Header: "Input"
   - Question: "How will users define what they want the system to do?"
   - Options:
     - "Code (APIs, SDKs)" - "Developer-focused, programmatic"
     - "Configuration (YAML, JSON)" - "Declarative configs"
     - "Visual interface (drag-drop)" - "No-code UI builder"
     - "Natural language" - "AI-powered interpretation"

2. **Translation Approach**
   - Header: "Translation"
   - Question: "How should user intent become executable code?"
   - Options:
     - "Direct interpretation" - "Runtime interpretation, flexible"
     - "Compilation to native" - "Compiled ahead-of-time, fast"
     - "IR/AST transformation" - "Intermediate representation"
     - "Template-based generation" - "Code generation from templates"

3. **Extensibility**
   - Header: "Extensibility"
   - Question: "How should users extend default behavior?"
   - Options:
     - "Plugin system" - "Loadable extensions"
     - "Hooks/callbacks" - "Event-based extension points"
     - "Subclassing/inheritance" - "OOP-style extension"
     - "Middleware/interceptors" - "Pipeline-based modification"

DOCUMENT STRUCTURE:

Create: /job-queue/product-{name}/abstraction-layer.md

# Abstraction Layer Architecture

## Executive Summary
[How user intent becomes executable logic]

## Input Formats

### Primary Input Method
[Code, config, visual, NLP]

### Input Schema
[Structure of input: JSON schema, API surface, grammar]

### Validation & Parsing
[How inputs are validated and parsed]

## Intermediate Representation

### IR Design
[AST, JSON schema, custom IR - what does it look like?]

### Why This IR
[Rationale for chosen representation]

### Example Transformation
[Show: input → IR → output]

## Translation Mechanisms

### Chosen Approach
[Interpretation vs compilation vs generation]

### Translation Pipeline
[Step-by-step: input → IR → executable]

### Optimization Passes
[Any optimization during translation?]

## Mapping Tables

### UI/Config → System Primitives
[How high-level concepts map to low-level operations]

### Example Mappings
| User Concept | System Primitive | Implementation |
|--------------|------------------|----------------|
| [Concept 1]  | [Primitive 1]    | [How it works] |

## Extension Points

### Extension Architecture
[Plugin system, hooks, inheritance]

### Extension Registration
[How extensions are discovered and loaded]

### Extension API
[What APIs are exposed to extensions]

### Example Extension
[Code sample showing how to extend]

## Trade-offs Analysis

### Flexibility vs Performance
[What we optimized for]

### Simplicity vs Power
[Where we drew the line]

### Developer Experience
[How easy is it to use?]

[COMMON CLOSING SECTIONS — orchestrator: insert the block from references/templates/common-closing-sections.md here, using the Stage 3 (abstraction) variants: Technology Comparison, Implementation Considerations, Research Sources]

---

Write to: /job-queue/product-{name}/abstraction-layer.md
Research notes: /job-queue/product-{name}/research-notes/abstraction-research.md
