# Stage 1 Templates: Clarifying Questions & big-idea.md

Used by the orchestrator during Stage 1 (Big Idea & High-Level Research).

## Initial Clarifying Questions (AskUserQuestion)

**Questions to ask:**

1. **Product Vision**
   - Header: "Vision"
   - Question: "What is the primary goal of this product?"
   - Options:
     - "Solve a specific problem for users" - "Focus on targeted pain points"
     - "Innovate in an existing space" - "Bring new approach to established market"
     - "Integrate multiple services" - "Connect disparate systems"
     - "Explore new technology" - "Research/experimental project"

2. **Scale & Audience**
   - Header: "Scale"
   - Question: "What scale are you targeting?"
   - Options:
     - "Prototype/MVP (100s of users)" - "Proof of concept"
     - "Small-Medium (1,000s of users)" - "Early stage product"
     - "Medium-Large (100,000s of users)" - "Established product"
     - "Enterprise scale (1M+ users)" - "High-scale production"

3. **Deployment Context**
   - Header: "Deployment"
   - Question: "Where will this product run?"
   - Options:
     - "Cloud-hosted (AWS/GCP/Azure)" - "Managed infrastructure"
     - "Self-hosted/On-prem" - "Customer infrastructure"
     - "Edge/Distributed" - "CDN, edge compute"
     - "Hybrid" - "Mix of cloud and local"

## big-idea.md Content Structure

```markdown
# Big Idea: [Product Name]

## Product Overview
[2-3 paragraphs describing what the product does, who it's for, and why it matters]

## Core Value Proposition
[What makes this product unique or valuable]

## High-Level Architecture Approach
[Based on research, what architectural style makes sense?]
- Monolithic vs Microservices
- Serverless vs Server-based
- Event-driven vs Request-response
- [Any other key architectural decisions]

## Technology Landscape
[Summary of technology options researched]

### Frontend Options
- Option 1: [technology] - [pros/cons]
- Option 2: [technology] - [pros/cons]
- Option 3: [technology] - [pros/cons]

### Backend Options
- Option 1: [technology] - [pros/cons]
- Option 2: [technology] - [pros/cons]
- Option 3: [technology] - [pros/cons]

### Database Options
- Option 1: [technology] - [pros/cons]
- Option 2: [technology] - [pros/cons]

### Deployment Options
- Option 1: [platform] - [pros/cons]
- Option 2: [platform] - [pros/cons]

## Key Challenges Identified
1. [Challenge 1 and mitigation approach]
2. [Challenge 2 and mitigation approach]
3. [Challenge 3 and mitigation approach]

## Next Steps
- Deep dive into runtime execution patterns
- Research abstraction layer approaches
- Evaluate integration strategies
- Design output rendering pipeline

## Research Sources
[List of URLs and documentation consulted]
```

Save to: `/job-queue/product-{name}/big-idea.md`
