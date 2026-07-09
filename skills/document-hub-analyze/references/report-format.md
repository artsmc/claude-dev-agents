# Analysis Report Format

Full template for the analysis report, plus a complete Python example that runs all helper scripts and assembles the report. Read this before presenting findings.

## Report Template

Present findings in a structured report:

```
Documentation Hub Analysis Report
==================================

Overall Health: 77/100 (Good)
Drift Score: 0.23

STRUCTURE VALIDATION
--------------------
✓ All required files present
✓ Mermaid syntax valid
⚠ 1 warning: systemArchitecture.md diagram complex (22 nodes)

MODULE DRIFT ANALYSIS
---------------------
Drift Score: 0.30 (Medium)

Undocumented Modules (2):
  • src/analytics - 8 files, appears to be user analytics tracking
  • src/webhooks - 4 files, webhook event handling

Documented but Missing (1):
  • src/legacy - Referenced in docs but directory doesn't exist
    Last seen: commit abc123 (3 months ago)

TECHNOLOGY DRIFT ANALYSIS
--------------------------
Drift Score: 0.15 (Low)

Missing from techStack.md (2):
  • Redis - Found in package.json, added 2 weeks ago
  • BullMQ - Found in package.json, used for job queues

Documented but Not Found (1):
  • MongoDB - Still in techStack.md but removed from dependencies

GLOSSARY GAPS
-------------
Found 18 potential domain-specific terms not in glossary:

High Relevance:
  1. BatchProcessor (score: 45) - "Processes items in configurable batch sizes"
  2. FulfillmentQueue (score: 42) - "Queue for order fulfillment jobs"
  3. CIPIntegration (score: 38) - "Customer Information Portal integration"

Medium Relevance:
  [Additional terms...]

RECOMMENDATIONS
---------------

HIGH PRIORITY (Do these first):
  1. Document analytics module in keyPairResponsibility.md
  2. Document webhooks module in keyPairResponsibility.md
  3. Add Redis to techStack.md
  4. Remove legacy module reference from docs

MEDIUM PRIORITY (Do when possible):
  5. Add BullMQ to techStack.md
  6. Add top 10 glossary terms
  7. Consider splitting systemArchitecture.md diagram

LOW PRIORITY (Nice to have):
  8. Add remaining glossary terms
  9. Update MongoDB reference or re-add dependency

NEXT STEPS
----------
Run /document-hub update to apply these recommendations automatically.
```

## Example: Complete Analysis

```python
import json
import subprocess
from pathlib import Path

project_path = Path("/path/to/project")

# 1. Validate
validate = subprocess.run(
    ["python", "scripts/validate_hub.py", str(project_path)],
    capture_output=True, text=True
)
validation = json.loads(validate.stdout)

# 2. Detect drift
drift = subprocess.run(
    ["python", "scripts/detect_drift.py", str(project_path)],
    capture_output=True, text=True
)
drift_data = json.loads(drift.stdout)

# 3. Extract glossary gaps
glossary = subprocess.run(
    ["python", "scripts/extract_glossary.py", str(project_path)],
    capture_output=True, text=True
)
glossary_data = json.loads(glossary.stdout)

# Read existing glossary
glossary_file = project_path / "cline-docs" / "glossary.md"
existing_terms = set()
if glossary_file.exists():
    with open(glossary_file) as f:
        # Extract terms from glossary
        # [Parsing logic...]
        pass

# Find gaps
missing_terms = [
    t for t in glossary_data["terms"]
    if t["term"] not in existing_terms
]

# 4. Calculate health score
health_score = 100 - (drift_data["drift_score"] * 100)

# 5. Generate report
print("Documentation Hub Analysis Report")
print("=" * 50)
print(f"Overall Health: {health_score:.0f}/100")
print(f"Drift Score: {drift_data['drift_score']:.2f}")
print()
print("UNDOCUMENTED MODULES:")
for module in drift_data["module_drift"]["undocumented"]:
    print(f"  • {module}")
print()
print("GLOSSARY GAPS:")
for term in missing_terms[:10]:
    print(f"  • {term['term']} (score: {term['score']})")
```
