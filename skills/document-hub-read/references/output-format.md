# Output Format: Documentation Hub Summary

Full output template for Step 4 (Present Summary) of the read workflow, plus a complete example read operation.

## Summary Template

Format the summary in a clear, scannable structure:

```
Documentation Hub Summary
=========================

Status: ✓ Valid (or ⚠ Issues detected)

## System Architecture
- Description: [1-2 sentence summary]
- Diagrams: 3 Mermaid diagrams
- Key Components: API Gateway, Auth Service, Database

## Module Responsibilities
- Total Modules: 8
- Key Modules:
  • auth - User authentication and authorization
  • payments - Payment processing integration
  • notifications - Email and push notifications

## Technology Stack
- Framework: Next.js 14
- Database: PostgreSQL + Redis
- Infrastructure: Docker, AWS
- [X more technologies]

## Glossary
- Total Terms: 42
- Key Terms: FulfillmentJob, CIP, Ledger, BatchProcessor, ...

## Health Check
- Validation: ✓ Passed
- Warnings: 1 (Complex diagram in systemArchitecture.md)
- Last Updated: [Git last modified date if available]
```

## Example: Complete Read Operation

```python
import json
import subprocess
from pathlib import Path

project_path = Path("/path/to/project")
docs_path = project_path / "cline-docs"

# Step 1: Validate
validate = subprocess.run(
    ["python", "scripts/validate_hub.py", str(project_path)],
    capture_output=True, text=True
)
validation = json.loads(validate.stdout)

# Step 2: Check if hub exists
if not docs_path.exists():
    print("Documentation hub not found.")
    print("Run /document-hub initialize to create it.")
    exit(0)

# Step 3: Read files
files = {
    "arch": docs_path / "systemArchitecture.md",
    "resp": docs_path / "keyPairResponsibility.md",
    "glossary": docs_path / "glossary.md",
    "tech": docs_path / "techStack.md"
}

content = {}
for key, file_path in files.items():
    if file_path.exists():
        with open(file_path) as f:
            content[key] = f.read()

# Step 4: Extract and summarize
# [Parse content and extract key information]

# Step 5: Present summary
print("Documentation Hub Summary")
print("=" * 50)
print(f"Status: {'✓ Valid' if validation['valid'] else '⚠ Issues'}")
# [Rest of summary...]
```
