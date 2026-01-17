# Document Hub Phase 1: Tooling Analysis

## Question: Do Phase 1 Skills Need Python Scripts?

**Short Answer:** Yes, but selectively. Some skills benefit significantly from custom Python tools, while others work fine with built-in Claude Code tools.

## Anthropic Skills Pattern Analysis

From the [webapp-testing example](https://github.com/anthropics/skills/tree/main/skills/webapp-testing):

```
skills/webapp-testing/
├── skill.md           # Skill instructions (prompt)
└── scripts/
    ├── run_playwright_test.py
    └── analyze_test_results.py
```

**Pattern:** Python scripts act as custom tool calls that:
- Provide specialized functionality beyond basic Read/Write/Edit
- Handle complex operations reliably (parsing, validation, analysis)
- Return structured data Claude can work with
- Improve performance for repetitive operations

## Phase 1 Skills: Tool Requirements Analysis

### Skill 1: `/document-hub initialize`

**Current Approach:** Use built-in Write tool to create files

**Potential Python Tools:**

#### Script: `scripts/init_hub.py`
**Purpose:** Atomic initialization of all documentation hub files

**Benefits:**
- Ensures consistent file structure
- Validates directory permissions
- Creates files transactionally (all or nothing)
- Can read from templates in JSON/YAML

**Tool Call:**
```python
# Claude invokes this tool via:
{
  "name": "init_documentation_hub",
  "input": {
    "project_path": "/path/to/project",
    "project_name": "MyProject",
    "tech_stack": ["Next.js", "TypeScript", "PostgreSQL"],
    "overwrite": false
  }
}
```

**Return:**
```json
{
  "success": true,
  "files_created": [
    "/path/to/project/cline-docs/systemArchitecture.md",
    "/path/to/project/cline-docs/keyPairResponsibility.md",
    "/path/to/project/cline-docs/glossary.md",
    "/path/to/project/cline-docs/techStack.md"
  ],
  "message": "Documentation hub initialized successfully"
}
```

**Verdict:** ✅ **Recommended** - Ensures atomic, reliable initialization

---

#### Script: `scripts/validate_hub.py`
**Purpose:** Validate documentation hub structure and content

**Benefits:**
- Check all required files exist
- Validate Mermaid syntax
- Check cross-references between files
- Verify markdown formatting

**Tool Call:**
```python
{
  "name": "validate_documentation_hub",
  "input": {
    "project_path": "/path/to/project"
  }
}
```

**Return:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "file": "systemArchitecture.md",
      "line": 42,
      "message": "Mermaid diagram may be too complex (20+ nodes)"
    }
  ]
}
```

**Verdict:** ✅ **Highly Recommended** - Used by multiple skills

---

### Skill 2: `/document-hub update`

**Current Approach:** Invoke agents to read, analyze, and propose changes

**Potential Python Tools:**

#### Script: `scripts/analyze_changes.py`
**Purpose:** Analyze git changes since last documentation update

**Benefits:**
- Fast git history parsing
- Identifies which files changed
- Categorizes changes (architecture, module, config)
- Determines update scope

**Tool Call:**
```python
{
  "name": "analyze_recent_changes",
  "input": {
    "project_path": "/path/to/project",
    "since": "2024-01-01",  # or commit hash
    "include_patterns": ["src/**/*.ts", "*.config.js"]
  }
}
```

**Return:**
```json
{
  "changed_files": 42,
  "categories": {
    "architecture": ["Added new auth service", "Modified API gateway"],
    "modules": ["Created payment module"],
    "config": ["Updated Next.js config for image optimization"],
    "dependencies": ["Added Redis for caching"]
  },
  "suggested_updates": [
    "systemArchitecture.md: Add Redis caching layer",
    "keyPairResponsibility.md: Document payment module responsibilities",
    "techStack.md: Add Redis to infrastructure"
  ]
}
```

**Verdict:** ✅ **Highly Recommended** - Makes updates intelligent and scoped

---

#### Script: `scripts/extract_glossary.py`
**Purpose:** Extract domain-specific terms from codebase via AST parsing

**Benefits:**
- Proper parsing of TypeScript/JavaScript/Python
- Identifies variable names, class names, function names
- Filters out generic terms
- Extracts context from comments

**Tool Call:**
```python
{
  "name": "extract_glossary_terms",
  "input": {
    "project_path": "/path/to/project",
    "file_patterns": ["src/**/*.ts"],
    "exclude_patterns": ["**/*.test.ts", "**/*.spec.ts"],
    "min_occurrences": 3
  }
}
```

**Return:**
```json
{
  "terms": [
    {
      "term": "FulfillmentJob",
      "occurrences": 15,
      "contexts": [
        "Class representing a job in the fulfillment pipeline",
        "Tracks order processing status and completion"
      ],
      "files": ["src/fulfillment/job.ts", "src/api/jobs.ts"]
    },
    {
      "term": "CIP",
      "occurrences": 8,
      "contexts": ["Customer Information Portal"],
      "files": ["src/customer/portal.ts"]
    }
  ]
}
```

**Verdict:** ✅ **Highly Recommended** - Much better than regex/grep for term extraction

---

### Skill 3: `/document-hub read`

**Current Approach:** Use built-in Read tool on all hub files

**Potential Python Tools:**

#### Script: `scripts/summarize_hub.py`
**Purpose:** Generate structured summary of documentation hub

**Benefits:**
- Fast parsing of all markdown files
- Extracts key metrics (file sizes, term counts, diagram counts)
- Validates structure
- Generates table of contents

**Tool Call:**
```python
{
  "name": "summarize_documentation_hub",
  "input": {
    "project_path": "/path/to/project"
  }
}
```

**Return:**
```json
{
  "summary": {
    "total_files": 4,
    "total_diagrams": 6,
    "glossary_terms": 42,
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "files": {
    "systemArchitecture.md": {
      "size_kb": 12.5,
      "diagrams": 3,
      "sections": ["High-Level Architecture", "Database Schema", "Data Flow"]
    },
    "glossary.md": {
      "size_kb": 8.2,
      "terms": 42
    }
  },
  "health": {
    "status": "good",
    "issues": []
  }
}
```

**Verdict:** ⚠️ **Optional** - Nice to have, but not essential. Built-in tools work fine.

---

### Skill 4: `/document-hub analyze`

**Current Approach:** Invoke documentation-analyst agent

**Potential Python Tools:**

#### Script: `scripts/detect_drift.py`
**Purpose:** Detect drift between documentation and codebase

**Benefits:**
- Compares documented modules vs. actual directories
- Checks documented tech stack vs. package.json/requirements.txt
- Identifies undocumented APIs/routes
- Fast, deterministic results

**Tool Call:**
```python
{
  "name": "detect_documentation_drift",
  "input": {
    "project_path": "/path/to/project"
  }
}
```

**Return:**
```json
{
  "drift_score": 0.15,  # 0-1, lower is better
  "undocumented_modules": [
    "src/analytics",
    "src/webhooks"
  ],
  "undocumented_technologies": [
    "Redis",
    "BullMQ"
  ],
  "documented_but_missing": [
    "src/legacy (documented but directory doesn't exist)"
  ],
  "recommendations": [
    "Add analytics module to keyPairResponsibility.md",
    "Add Redis and BullMQ to techStack.md",
    "Remove legacy module from documentation"
  ]
}
```

**Verdict:** ✅ **Highly Recommended** - Core functionality for this skill

---

## Recommended Phase 1 Tooling

### Essential Tools (Implement First)

1. **`scripts/validate_hub.py`** - Used by all skills
   - Validates structure and Mermaid syntax
   - Cross-reference checking

2. **`scripts/analyze_changes.py`** - Powers `/document-hub update`
   - Git history analysis
   - Scope determination

3. **`scripts/detect_drift.py`** - Powers `/document-hub analyze`
   - Drift detection
   - Gap identification

4. **`scripts/extract_glossary.py`** - Used by update and analyze
   - AST-based term extraction
   - Context gathering

### Nice-to-Have Tools (Implement Later)

5. **`scripts/init_hub.py`** - Powers `/document-hub initialize`
   - Atomic initialization
   - Template management

6. **`scripts/summarize_hub.py`** - Powers `/document-hub read`
   - Quick summaries
   - Health checks

---

## Revised Phase 1 Implementation Plan

### Week 1: Core Python Tools

**Day 1-2: Setup Tool Infrastructure**
- Create `skills/document-hub/scripts/` directory
- Set up Python virtual environment
- Install dependencies (GitPython, tree-sitter for parsing, mermaid-py for validation)
- Create `scripts/requirements.txt`

**Day 3-4: Implement Essential Tools**
- Implement `validate_hub.py`
- Implement `detect_drift.py`
- Write unit tests for both

**Day 5-7: Implement Update Tools**
- Implement `analyze_changes.py`
- Implement `extract_glossary.py`
- Write unit tests

### Week 2: Skill Markdown Files

**Day 1-2: Skill: `/document-hub initialize`**
- Create `skills/document-hub/initialize.md`
- Integrate tool calls (if implementing init_hub.py)
- Test initialization flow

**Day 3-4: Skill: `/document-hub update`**
- Create `skills/document-hub/update.md`
- Integrate `analyze_changes.py` and `validate_hub.py`
- Test update flow

**Day 5-6: Skill: `/document-hub read`**
- Create `skills/document-hub/read.md`
- Integrate `summarize_hub.py` (if implemented)
- Test read flow

**Day 7: Skill: `/document-hub analyze`**
- Create `skills/document-hub/analyze.md`
- Integrate `detect_drift.py` and `extract_glossary.py`
- Test analyze flow

### Week 3: Integration Testing
- Test all skills end-to-end
- Test tool error handling
- Performance optimization
- Documentation

---

## Tool Implementation Examples

### Example: `scripts/validate_hub.py`

```python
#!/usr/bin/env python3
"""
Validate documentation hub structure and content.

Returns structured JSON with validation results.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import mermaid  # For Mermaid validation
except ImportError:
    mermaid = None


def validate_file_structure(project_path: Path) -> Dict:
    """Check if all required files exist."""
    docs_path = project_path / "cline-docs"
    required_files = [
        "systemArchitecture.md",
        "keyPairResponsibility.md",
        "glossary.md",
        "techStack.md"
    ]

    errors = []
    for file_name in required_files:
        if not (docs_path / file_name).exists():
            errors.append(f"Missing required file: {file_name}")

    return {
        "check": "file_structure",
        "passed": len(errors) == 0,
        "errors": errors
    }


def validate_mermaid_syntax(content: str, file_name: str) -> Dict:
    """Validate Mermaid diagram syntax."""
    errors = []
    warnings = []

    # Extract Mermaid blocks
    in_mermaid = False
    mermaid_blocks = []
    current_block = []

    for line_num, line in enumerate(content.split('\n'), 1):
        if line.strip() == '```mermaid':
            in_mermaid = True
            current_block = []
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            mermaid_blocks.append((line_num, '\n'.join(current_block)))
        elif in_mermaid:
            current_block.append(line)

    # Validate each block
    for line_num, block in mermaid_blocks:
        if not block.strip():
            errors.append({
                "file": file_name,
                "line": line_num,
                "message": "Empty Mermaid diagram"
            })
            continue

        # Check for common syntax issues
        if 'flowchart' in block or 'graph' in block:
            # Count nodes
            node_count = len([l for l in block.split('\n') if '-->' in l or '---' in l])
            if node_count > 20:
                warnings.append({
                    "file": file_name,
                    "line": line_num,
                    "message": f"Complex diagram with {node_count} connections. Consider splitting."
                })

    return {
        "check": "mermaid_syntax",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_cross_references(project_path: Path) -> Dict:
    """Check cross-references between files."""
    docs_path = project_path / "cline-docs"
    errors = []

    # Build list of all section headers
    all_sections = {}
    for md_file in docs_path.glob("*.md"):
        with open(md_file) as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('#'):
                    header = line.lstrip('#').strip()
                    all_sections[header.lower()] = md_file.name

    # Check all markdown links
    for md_file in docs_path.glob("*.md"):
        with open(md_file) as f:
            content = f.read()
            # Simple regex for markdown links [text](link)
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            for text, link in links:
                if link.startswith('#'):
                    # Internal link
                    section = link[1:].lower()
                    if section not in all_sections:
                        errors.append({
                            "file": md_file.name,
                            "message": f"Broken internal link: {link}"
                        })

    return {
        "check": "cross_references",
        "passed": len(errors) == 0,
        "errors": errors
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Project path required"}))
        sys.exit(1)

    project_path = Path(sys.argv[1])

    if not project_path.exists():
        print(json.dumps({"error": f"Project path not found: {project_path}"}))
        sys.exit(1)

    docs_path = project_path / "cline-docs"
    if not docs_path.exists():
        print(json.dumps({
            "valid": False,
            "errors": ["Documentation hub not found. Run /document-hub initialize first."]
        }))
        sys.exit(0)

    # Run all validation checks
    results = []
    results.append(validate_file_structure(project_path))

    # Validate Mermaid syntax in all files
    for md_file in docs_path.glob("*.md"):
        with open(md_file) as f:
            content = f.read()
            results.append(validate_mermaid_syntax(content, md_file.name))

    results.append(validate_cross_references(project_path))

    # Aggregate results
    all_errors = []
    all_warnings = []
    for result in results:
        all_errors.extend(result.get('errors', []))
        all_warnings.extend(result.get('warnings', []))

    output = {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "checks_run": len(results)
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
```

**Usage from Skill:**
```markdown
# In skills/document-hub/update.md

## Validation Step

Before proposing updates, validate the current documentation hub:

Use the `validate_documentation_hub` tool:
- Input: Project path
- This tool checks file structure, Mermaid syntax, and cross-references
- If validation fails, fix errors before proceeding with updates
```

---

## Directory Structure (Post Phase 1)

```
.claude/
├── skills/
│   └── document-hub/
│       ├── initialize.md
│       ├── update.md
│       ├── read.md
│       ├── analyze.md
│       └── scripts/
│           ├── requirements.txt
│           ├── validate_hub.py
│           ├── analyze_changes.py
│           ├── detect_drift.py
│           ├── extract_glossary.py
│           ├── init_hub.py (optional)
│           ├── summarize_hub.py (optional)
│           └── __init__.py
```

---

## Benefits of Python Tools

### 1. **Reliability**
- Deterministic parsing (AST instead of regex)
- Proper error handling
- Testable with unit tests

### 2. **Performance**
- Fast git history analysis
- Efficient file scanning
- Can cache results

### 3. **Complexity Handling**
- Mermaid syntax validation
- TypeScript/Python AST parsing
- Complex cross-reference checking

### 4. **Structured Output**
- Returns JSON Claude can easily parse
- Consistent error format
- Machine-readable results

### 5. **Reusability**
- Can be used by multiple skills
- Can be called from hooks
- Can be used standalone for debugging

---

## Alternative: MCP (Model Context Protocol) Servers

Instead of Python scripts in each skill, we could create an **MCP server** for documentation hub operations:

```
document-hub-mcp-server/
├── server.py
└── tools/
    ├── validate.py
    ├── analyze_changes.py
    ├── detect_drift.py
    └── extract_glossary.py
```

**Benefits:**
- Centralized tool management
- Can be used across multiple Claude Code sessions
- Better for complex stateful operations

**Tradeoffs:**
- More setup complexity
- Requires MCP server configuration
- Overkill for simple operations

**Recommendation:** Start with Python scripts in `skills/document-hub/scripts/`, migrate to MCP server if complexity grows.

---

## Conclusion

**Yes, Phase 1 skills should include Python scripts** for:
1. **Validation** (`validate_hub.py`) - Essential for all skills
2. **Change Analysis** (`analyze_changes.py`) - Powers intelligent updates
3. **Drift Detection** (`detect_drift.py`) - Core of analyze skill
4. **Glossary Extraction** (`extract_glossary.py`) - Better than regex

These tools make the skills more reliable, faster, and produce better results than using only built-in Claude Code tools.

**Revised Phase 1 Timeline:** 3 weeks (1 week for tools, 2 weeks for skills)
