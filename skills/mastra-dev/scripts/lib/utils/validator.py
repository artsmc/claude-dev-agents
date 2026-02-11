"""Configuration validation utilities."""

from pathlib import Path
from typing import List, Tuple
import re


class Validator:
    """Validator for Mastra configurations and TypeScript files."""

    def __init__(self, mastra_app: Path):
        """Initialize validator.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self, strict: bool = False) -> int:
        """Validate all Mastra configurations.

        Args:
            strict: If True, warnings are treated as errors

        Returns:
            Exit code (0 = success, 1 = validation errors)
        """
        self.errors = []
        self.warnings = []

        print("🔍 Validating Mastra configurations...")
        print()

        # Validate directory structure
        self._validate_structure()

        # Validate configuration files
        self._validate_config_files()

        # Validate TypeScript files
        self._validate_typescript_files()

        # Print results
        self._print_results(strict)

        # Return exit code
        if self.errors or (strict and self.warnings):
            return 1
        return 0

    def _validate_structure(self) -> None:
        """Validate directory structure."""
        required_dirs = [
            'src',
            'src/config',
            'src/workflows',
            'src/agents',
        ]

        for dir_path in required_dirs:
            full_path = self.mastra_app / dir_path
            if not full_path.exists():
                self.errors.append(f"Missing directory: {dir_path}")

    def _validate_config_files(self) -> None:
        """Validate configuration files."""
        config_files = [
            'src/config/mastra.config.ts',
            'src/config/mcp.config.ts',
        ]

        for config_file in config_files:
            full_path = self.mastra_app / config_file
            if not full_path.exists():
                self.errors.append(f"Missing config file: {config_file}")
            else:
                # Basic TypeScript syntax check
                self._validate_typescript_syntax(full_path)

    def _validate_typescript_files(self) -> None:
        """Validate TypeScript files in agents, workflows, and tools."""
        # Check agents
        agents_dir = self.mastra_app / 'src' / 'agents'
        if agents_dir.exists():
            for ts_file in agents_dir.glob('*.ts'):
                if ts_file.name != '.gitkeep':
                    self._validate_agent_file(ts_file)

        # Check workflows
        workflows_dir = self.mastra_app / 'src' / 'workflows'
        if workflows_dir.exists():
            for ts_file in workflows_dir.glob('*.ts'):
                if ts_file.name != '.gitkeep':
                    self._validate_workflow_file(ts_file)

        # Check tools
        tools_dir = self.mastra_app / 'src' / 'tools'
        if tools_dir.exists():
            for ts_file in tools_dir.glob('*.ts'):
                if ts_file.name != '.gitkeep':
                    self._validate_tool_file(ts_file)

    def _validate_typescript_syntax(self, file_path: Path) -> None:
        """Basic TypeScript syntax validation.

        Args:
            file_path: Path to TypeScript file
        """
        try:
            content = file_path.read_text()

            # Check for unmatched braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.errors.append(
                    f"{file_path.name}: Unmatched braces "
                    f"(open: {open_braces}, close: {close_braces})"
                )

            # Check for unmatched parentheses
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                self.errors.append(
                    f"{file_path.name}: Unmatched parentheses "
                    f"(open: {open_parens}, close: {close_parens})"
                )

            # Check for import statements
            if 'import' not in content and 'export' not in content:
                self.warnings.append(
                    f"{file_path.name}: No import/export statements found"
                )

        except Exception as e:
            self.errors.append(f"{file_path.name}: Failed to read file ({e})")

    def _validate_agent_file(self, file_path: Path) -> None:
        """Validate agent TypeScript file.

        Args:
            file_path: Path to agent file
        """
        try:
            content = file_path.read_text()

            # Check for required imports
            if 'Agent' not in content:
                self.warnings.append(
                    f"{file_path.name}: Missing Agent import or usage"
                )

            # Check for export
            if 'export' not in content:
                self.errors.append(f"{file_path.name}: Missing export statement")

        except Exception as e:
            self.errors.append(f"{file_path.name}: Failed to validate ({e})")

    def _validate_workflow_file(self, file_path: Path) -> None:
        """Validate workflow TypeScript file.

        Args:
            file_path: Path to workflow file
        """
        try:
            content = file_path.read_text()

            # Check for required imports
            if 'createWorkflow' not in content:
                self.errors.append(
                    f"{file_path.name}: Missing createWorkflow import or usage"
                )

            # Check for commit()
            if '.commit()' not in content:
                self.errors.append(
                    f"{file_path.name}: Workflow must end with .commit()"
                )

            # Check for export
            if 'export' not in content:
                self.errors.append(f"{file_path.name}: Missing export statement")

        except Exception as e:
            self.errors.append(f"{file_path.name}: Failed to validate ({e})")

    def _validate_tool_file(self, file_path: Path) -> None:
        """Validate tool TypeScript file.

        Args:
            file_path: Path to tool file
        """
        try:
            content = file_path.read_text()

            # Check for required imports
            if 'createTool' not in content:
                self.warnings.append(
                    f"{file_path.name}: Missing createTool import or usage"
                )

            # Check for export
            if 'export' not in content:
                self.errors.append(f"{file_path.name}: Missing export statement")

        except Exception as e:
            self.errors.append(f"{file_path.name}: Failed to validate ({e})")

    def _print_results(self, strict: bool) -> None:
        """Print validation results.

        Args:
            strict: If True, warnings are treated as errors
        """
        total_issues = len(self.errors) + len(self.warnings)

        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            symbol = "❌" if strict else "⚠️"
            label = "ERRORS" if strict else "WARNINGS"
            print(f"{symbol} {label}:")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ All validations passed!")
        else:
            error_count = len(self.errors)
            warning_count = len(self.warnings)
            if strict:
                print(f"❌ Validation failed with {total_issues} issues")
            else:
                print(f"Validation completed with {error_count} errors and {warning_count} warnings")
