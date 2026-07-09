# Mastra Dev Use Cases

> Part of the `mastra-dev` skill. Three end-to-end command walkthroughs: government contract analysis system, government form auto-filling, multi-agent research system. Moved verbatim from SKILL.md.

## Use Cases

### Use Case 1: Building a Government Contract Analysis System

**Scenario:** Create an AI system that analyzes federal contracts for compliance and risk.

```bash
# 1. Create contract analysis agent
/mastra-dev create-agent \
  --name "contract-analyzer" \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --description "Expert in federal contract analysis" \
  --instructions "Analyze contracts for FAR/DFARS compliance, identify risks, and extract key terms"

# 2. Create tools for contract processing
/mastra-dev create-tool \
  --name "pdf-parser" \
  --description "Extract text from PDF contracts"

/mastra-dev create-tool \
  --name "far-lookup" \
  --description "Look up FAR/DFARS clauses"

/mastra-dev create-tool \
  --name "risk-calculator" \
  --description "Calculate contract risk score"

# 3. Create contract analysis workflow
/mastra-dev create-workflow \
  --name "contract-analysis" \
  --description "End-to-end contract analysis pipeline"

# 4. Add workflow steps
/mastra-dev add-step --workflow "contract-analysis" --step-name "extract-text"
/mastra-dev add-step --workflow "contract-analysis" --step-name "identify-clauses"
/mastra-dev add-step --workflow "contract-analysis" --step-name "check-compliance"
/mastra-dev add-step --workflow "contract-analysis" --step-name "assess-risks"
/mastra-dev add-step --workflow "contract-analysis" --step-name "generate-report"

# 5. Test the workflow
/mastra-dev test-workflow \
  --name "contract-analysis" \
  --input '{"contractUrl": "https://example.com/contract.pdf"}'

# 6. Start Mastra Studio to monitor execution
/mastra-dev studio start
```

### Use Case 2: Automating Government Form Filling

**Scenario:** Auto-fill complex government forms using SAM.gov API data.

```bash
# 1. Add SAM.gov MCP server for data access
/mastra-dev mcp add-client \
  --name "sam-gov" \
  --url "https://api.sam.gov/mcp"

# 2. Create form generation workflow
/mastra-dev create-workflow \
  --name "form-generation" \
  --description "Auto-fill government forms from opportunity data"

# 3. Add steps
/mastra-dev add-step --workflow "form-generation" --step-name "fetch-opportunity"
/mastra-dev add-step --workflow "form-generation" --step-name "extract-requirements"
/mastra-dev add-step --workflow "form-generation" --step-name "fill-form-fields"
/mastra-dev add-step --workflow "form-generation" --step-name "generate-pdf"

# 4. Create PDF generator tool
/mastra-dev create-tool \
  --name "pdf-generator" \
  --description "Generate PDF from form data"

# 5. Expose workflow via MCP for external access
/mastra-dev mcp configure-server --workflows "form-generation"

# 6. Test end-to-end
/mastra-dev test-workflow \
  --name "form-generation" \
  --input '{"opportunityId": "abc-123"}'
```

### Use Case 3: Multi-Agent Research System

**Scenario:** Build a research system with specialized agents working together.

```bash
# 1. Create specialized agents
/mastra-dev create-agent \
  --name "researcher" \
  --model "anthropic/claude-3-opus-20240229" \
  --description "Deep research expert"

/mastra-dev create-agent \
  --name "summarizer" \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --description "Expert summarizer"

/mastra-dev create-agent \
  --name "fact-checker" \
  --model "openai/gpt-4-turbo" \
  --description "Fact verification specialist"

# 2. Add external research tools via MCP
/mastra-dev mcp add-client --name "wikipedia" --command "npx" --args "-y,wikipedia-mcp"
/mastra-dev mcp add-client --name "arxiv" --command "npx" --args "-y,arxiv-mcp"

# 3. Create research workflow
/mastra-dev create-workflow \
  --name "research-pipeline" \
  --description "Multi-agent research system"

# 4. Add parallel research steps
/mastra-dev add-step --workflow "research-pipeline" --step-name "gather-sources"
/mastra-dev add-step --workflow "research-pipeline" --step-name "parallel-research" --step-type "parallel"
/mastra-dev add-step --workflow "research-pipeline" --step-name "synthesize-findings"
/mastra-dev add-step --workflow "research-pipeline" --step-name "fact-check"
/mastra-dev add-step --workflow "research-pipeline" --step-name "generate-report"

# 5. Validate setup
/mastra-dev validate

# 6. Start server and Studio
/mastra-dev server start
/mastra-dev studio start
```

