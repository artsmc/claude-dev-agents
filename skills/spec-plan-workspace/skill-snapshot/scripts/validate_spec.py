#!/usr/bin/env python3
"""
Spec Validation Tool

Validates generated feature specifications for completeness, structure, and quality.
Supports tiered validation for quick, standard, and full specification outputs.

Usage:
    python validate_spec.py /path/to/feature-folder [--tier quick|standard|full]

When --tier is omitted, the tier is auto-detected from the files present.

Returns JSON with validation results.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SpecValidator:
    """Validates feature specification structure and content."""

    QUICK_FILES = [
        "docs/task-list.md"
    ]

    STANDARD_FILES = [
        "docs/FRD.md",
        "docs/TR.md",
        "docs/task-list.md"
    ]

    FULL_FILES = [
        "docs/FRD.md",
        "docs/FRS.md",
        "docs/GS.md",
        "docs/TR.md",
        "docs/task-list.md"
    ]

    VALID_TIERS = ("quick", "standard", "full")

    MIN_FILE_SIZE = 100  # bytes

    def __init__(self, feature_path: Path, tier: Optional[str] = None):
        self.feature_path = feature_path
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.total_checks = 0

        if tier is not None:
            self.tier = tier
        else:
            self.tier = self._detect_tier()

        self.required_files = self._files_for_tier(self.tier)

    def _files_for_tier(self, tier: str) -> List[str]:
        """Return the required files list for a given tier."""
        if tier == "quick":
            return list(self.QUICK_FILES)
        elif tier == "standard":
            return list(self.STANDARD_FILES)
        else:
            return list(self.FULL_FILES)

    def _detect_tier(self) -> str:
        """Auto-detect tier based on which specification files exist."""
        existing = set()
        for f in self.FULL_FILES:
            if (self.feature_path / f).exists():
                existing.add(f)

        full_set = set(self.FULL_FILES)
        standard_set = set(self.STANDARD_FILES)
        quick_set = set(self.QUICK_FILES)

        if existing == full_set:
            return "full"
        if existing == standard_set:
            return "standard"
        if existing == quick_set:
            return "quick"

        # Infer from what's present with a warning about unexpected combinations
        if full_set.issubset(existing):
            return "full"
        if standard_set.issubset(existing):
            # Extra files beyond standard but not full — warn
            extra = existing - standard_set
            if extra:
                self.warnings.append(
                    f"Unexpected file combination: standard tier files present with extras: {sorted(extra)}"
                )
            return "standard"
        if quick_set.issubset(existing):
            extra = existing - quick_set
            if extra:
                self.warnings.append(
                    f"Unexpected file combination: task-list.md present with extras: {sorted(extra)}"
                )
            return "standard" if "docs/FRD.md" in existing or "docs/TR.md" in existing else "quick"

        # Fallback: nothing recognisable, default to full so all missing files are flagged
        if existing:
            self.warnings.append(
                f"Could not determine tier from existing files: {sorted(existing)}. Defaulting to full."
            )
        return "full"

    def validate(self) -> Dict:
        """Run validation checks appropriate for the detected tier."""
        # --- All tiers: file existence, task list quality, gitignore ---
        self._check_file_existence()
        self._check_task_list_quality()
        self._check_gitignore()

        # --- Standard and full: file content checks for tier-relevant docs ---
        if self.tier in ("standard", "full"):
            self._check_file_content()
            self._check_cross_references()

        # --- Full only: Gherkin syntax validation ---
        if self.tier == "full":
            self._validate_gherkin_syntax()

        completeness_score = self.checks_passed / self.total_checks if self.total_checks > 0 else 0.0

        return {
            "valid": len(self.errors) == 0,
            "tier": self.tier,
            "errors": self.errors,
            "warnings": self.warnings,
            "completeness_score": round(completeness_score, 2),
            "checks_passed": self.checks_passed,
            "total_checks": self.total_checks
        }

    def _check_file_existence(self):
        """Check if all required files for the current tier exist."""
        self.total_checks += len(self.required_files)

        for file_path in self.required_files:
            full_path = self.feature_path / file_path
            if full_path.exists():
                self.checks_passed += 1
            else:
                self.errors.append(f"Missing required file: {file_path}")

    def _check_file_content(self):
        """Check that files are not empty and have proper structure."""
        for file_path in self.required_files:
            full_path = self.feature_path / file_path

            if not full_path.exists():
                continue

            # Check file size
            self.total_checks += 1
            file_size = full_path.stat().st_size

            if file_size < self.MIN_FILE_SIZE:
                self.errors.append(f"{file_path} is too small ({file_size} bytes, minimum {self.MIN_FILE_SIZE})")
            else:
                self.checks_passed += 1

            # Check for section headers
            self.total_checks += 1
            content = full_path.read_text(encoding='utf-8')

            if not re.search(r'^#+\s+.+', content, re.MULTILINE):
                self.warnings.append(f"{file_path} has no section headers")
            else:
                self.checks_passed += 1

    def _validate_gherkin_syntax(self):
        """Validate Gherkin syntax in GS.md."""
        gs_path = self.feature_path / "docs/GS.md"

        if not gs_path.exists():
            return

        content = gs_path.read_text(encoding='utf-8')

        # Check for Feature keyword
        self.total_checks += 1
        if re.search(r'^Feature:', content, re.MULTILINE):
            self.checks_passed += 1
        else:
            self.errors.append("GS.md missing 'Feature:' declaration")

        # Check for Scenario keyword
        self.total_checks += 1
        if re.search(r'^\s*Scenario:', content, re.MULTILINE):
            self.checks_passed += 1
        else:
            self.warnings.append("GS.md has no 'Scenario:' declarations")

        # Check for Given/When/Then steps
        self.total_checks += 1
        has_given = bool(re.search(r'^\s*Given\s+', content, re.MULTILINE))
        has_when = bool(re.search(r'^\s*When\s+', content, re.MULTILINE))
        has_then = bool(re.search(r'^\s*Then\s+', content, re.MULTILINE))

        if has_given and has_when and has_then:
            self.checks_passed += 1
        else:
            missing = []
            if not has_given:
                missing.append("Given")
            if not has_when:
                missing.append("When")
            if not has_then:
                missing.append("Then")
            self.warnings.append(f"GS.md missing Gherkin steps: {', '.join(missing)}")

        # Check for Background (optional but recommended)
        if not re.search(r'^\s*Background:', content, re.MULTILINE):
            self.warnings.append("GS.md has no 'Background:' section (optional but recommended)")

    def _check_task_list_quality(self):
        """Check task list has actionable items."""
        task_list_path = self.feature_path / "docs/task-list.md"

        if not task_list_path.exists():
            return

        content = task_list_path.read_text(encoding='utf-8')

        # Check for task items (bullets or checkboxes)
        self.total_checks += 1
        task_pattern = r'^\s*[-*]\s+\[[ x]\]\s+.+|^\s*[-*]\s+.+'
        tasks = re.findall(task_pattern, content, re.MULTILINE)

        if len(tasks) >= 3:
            self.checks_passed += 1
        elif len(tasks) > 0:
            self.warnings.append(f"Task list has only {len(tasks)} items (expected at least 3)")
        else:
            self.errors.append("Task list has no actionable items")

        # Check for vague tasks
        self.total_checks += 1
        vague_keywords = ['implement', 'create', 'add', 'build', 'develop']
        vague_count = sum(1 for task in tasks if any(kw in task.lower() for kw in vague_keywords) and len(task) < 100)

        if vague_count <= len(tasks) * 0.3:  # Less than 30% vague tasks
            self.checks_passed += 1
        else:
            self.warnings.append(f"{vague_count}/{len(tasks)} tasks are potentially vague (short with generic verbs)")

        # Check for task descriptions
        self.total_checks += 1
        tasks_with_details = sum(1 for task in tasks if len(task) > 50)

        if tasks_with_details >= len(tasks) * 0.5:  # At least 50% have details
            self.checks_passed += 1
        else:
            self.warnings.append("Many tasks lack detailed descriptions (< 50 chars)")

    def _check_gitignore(self):
        """Check .gitignore includes /job-queue."""
        # Check in project root and feature folder
        project_root = self._find_project_root()

        gitignore_paths = [
            project_root / ".gitignore" if project_root else None,
            self.feature_path / ".gitignore"
        ]

        self.total_checks += 1
        found = False

        for gitignore_path in gitignore_paths:
            if gitignore_path and gitignore_path.exists():
                content = gitignore_path.read_text(encoding='utf-8')
                if re.search(r'^/?job-queue', content, re.MULTILINE):
                    found = True
                    self.checks_passed += 1
                    break

        if not found:
            self.warnings.append(".gitignore does not contain /job-queue entry")

    def _check_cross_references(self):
        """Check cross-references between documents (tier-aware)."""
        if self.tier == "standard":
            # Standard tier: only FRD and TR exist, check TR references FRD
            self._check_reference("docs/TR.md", "FRD", ["FRD.md", "Feature Requirement"])
        elif self.tier == "full":
            # Full tier: all original cross-reference checks
            self._check_reference("docs/FRS.md", "FRD", ["FRD.md", "Feature Requirement"])
            self._check_reference("docs/TR.md", "FRS", ["FRS.md", "Functional Requirement"])
            self._check_gherkin_coverage()

    def _check_reference(self, doc_path: str, target_doc: str, search_terms: List[str]):
        """Check if a document references another document."""
        full_path = self.feature_path / doc_path

        if not full_path.exists():
            return

        self.total_checks += 1
        content = full_path.read_text(encoding='utf-8')

        found = any(term.lower() in content.lower() for term in search_terms)

        if found:
            self.checks_passed += 1
        else:
            self.warnings.append(f"{doc_path} does not reference {target_doc}")

    def _check_gherkin_coverage(self):
        """Check if Gherkin scenarios cover FRS features."""
        frs_path = self.feature_path / "docs/FRS.md"
        gs_path = self.feature_path / "docs/GS.md"

        if not frs_path.exists() or not gs_path.exists():
            return

        self.total_checks += 1

        # Extract feature requirements from FRS
        frs_content = frs_path.read_text(encoding='utf-8')
        frs_requirements = re.findall(r'(?:FR-\d+|Requirement \d+|Feature \d+)', frs_content, re.IGNORECASE)

        # Extract scenarios from GS
        gs_content = gs_path.read_text(encoding='utf-8')
        scenarios = re.findall(r'^\s*Scenario:', gs_content, re.MULTILINE)

        if len(frs_requirements) > 0 and len(scenarios) >= len(frs_requirements) * 0.5:
            self.checks_passed += 1
        elif len(scenarios) == 0:
            self.warnings.append("GS.md has no scenarios to cover FRS requirements")
        else:
            self.warnings.append(f"GS.md has {len(scenarios)} scenarios but FRS has {len(frs_requirements)} requirements")

    def _find_project_root(self) -> Path | None:
        """Find project root by looking for .git directory."""
        current = self.feature_path

        for _ in range(10):  # Limit search depth
            if (current / ".git").exists():
                return current
            if current.parent == current:
                break
            current = current.parent

        return None


def _parse_args(argv: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Parse CLI arguments without argparse (stdlib-light approach).

    Returns (feature_path, tier) tuple. Either may be None if not provided.
    """
    feature_path = None
    tier = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--tier":
            if i + 1 < len(argv):
                tier = argv[i + 1]
                i += 2
                continue
            else:
                print(json.dumps({
                    "valid": False,
                    "errors": ["--tier requires a value: quick, standard, or full"],
                    "warnings": [],
                    "completeness_score": 0.0
                }, indent=2))
                sys.exit(1)
        elif arg.startswith("--tier="):
            tier = arg.split("=", 1)[1]
            i += 1
            continue
        elif not arg.startswith("-"):
            feature_path = arg
        i += 1

    return feature_path, tier


def main():
    """Main entry point."""
    feature_path_str, tier = _parse_args(sys.argv[1:])

    if feature_path_str is None:
        print(json.dumps({
            "valid": False,
            "errors": ["Usage: python validate_spec.py /path/to/feature-folder [--tier quick|standard|full]"],
            "warnings": [],
            "completeness_score": 0.0
        }, indent=2))
        sys.exit(1)

    feature_path = Path(feature_path_str)

    if not feature_path.exists():
        print(json.dumps({
            "valid": False,
            "errors": [f"Feature folder not found: {feature_path}"],
            "warnings": [],
            "completeness_score": 0.0
        }, indent=2))
        sys.exit(1)

    # Validate tier argument if provided
    if tier is not None and tier not in SpecValidator.VALID_TIERS:
        print(json.dumps({
            "valid": False,
            "errors": [f"Invalid tier '{tier}'. Must be one of: {', '.join(SpecValidator.VALID_TIERS)}"],
            "warnings": [],
            "completeness_score": 0.0
        }, indent=2))
        sys.exit(1)

    validator = SpecValidator(feature_path, tier=tier)
    result = validator.validate()

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
