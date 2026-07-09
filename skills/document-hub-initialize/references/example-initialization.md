# Example: Complete Initialization

End-to-end Python example of the initialization workflow (check → create → detect → extract → generate → validate).

```python
import json
import subprocess
from pathlib import Path

project_path = Path("/path/to/project")
docs_path = project_path / "cline-docs"

# Step 1: Check if exists
if docs_path.exists():
    print("Documentation hub already exists. Validating...")
    result = subprocess.run(
        ["python", "scripts/validate_hub.py", str(project_path)],
        capture_output=True, text=True
    )
    validation = json.loads(result.stdout)
    if validation["valid"]:
        print("Hub is valid. Use /document-hub read to view it.")
        exit(0)

# Step 2: Create directory
docs_path.mkdir(exist_ok=True)

# Step 3: Detect technologies and modules
drift_result = subprocess.run(
    ["python", "scripts/detect_drift.py", str(project_path)],
    capture_output=True, text=True
)
drift_data = json.loads(drift_result.stdout)

# Step 4: Extract glossary terms
glossary_result = subprocess.run(
    ["python", "scripts/extract_glossary.py", str(project_path)],
    capture_output=True, text=True
)
glossary_data = json.loads(glossary_result.stdout)

# Step 5: Generate files
# [Create files using templates + detected data]

# Step 6: Validate
validate_result = subprocess.run(
    ["python", "scripts/validate_hub.py", str(project_path)],
    capture_output=True, text=True
)
validation = json.loads(validate_result.stdout)

if validation["valid"]:
    print("✓ Documentation hub initialized successfully!")
else:
    print("⚠ Issues detected:", validation["errors"])
```
