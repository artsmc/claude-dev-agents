# Helper Script Reference

**validate_hub.py** - Check documentation structure
```bash
python scripts/validate_hub.py /path/to/project
# Returns: {"valid": bool, "errors": [], "warnings": []}
```

**detect_drift.py** - Find undocumented code
```bash
python scripts/detect_drift.py /path/to/project
# Returns: {"module_drift": {...}, "technology_drift": {...}}
```

**extract_glossary.py** - Extract domain terms
```bash
python scripts/extract_glossary.py /path/to/project
# Returns: {"terms": [{term, contexts, score}...]}
```

See `scripts/README.md` for complete documentation.
