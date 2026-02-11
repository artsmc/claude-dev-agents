"""Workflow configuration data models."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class WorkflowStep:
    """Configuration for a workflow step."""

    name: str
    step_type: str = 'then'  # then, parallel, branch
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

    def validate(self) -> None:
        """Validate step configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.name:
            raise ValueError("Step name is required")

        if self.step_type not in ['then', 'parallel', 'branch']:
            raise ValueError(
                f"Invalid step type '{self.step_type}': "
                "must be one of: then, parallel, branch"
            )

    @property
    def id(self) -> str:
        """Get step ID (kebab-case)."""
        return self.name.lower().replace('_', '-')


@dataclass
class WorkflowConfig:
    """Configuration for a Mastra workflow."""

    name: str
    description: str = ''
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStep] = field(default_factory=list)

    def validate(self) -> None:
        """Validate workflow configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.name:
            raise ValueError("Workflow name is required")

        if not self.name.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                f"Invalid workflow name '{self.name}': "
                "must contain only alphanumeric characters and hyphens"
            )

        if not self.description:
            raise ValueError("Workflow description is required")

        # Validate all steps
        for step in self.steps:
            step.validate()

    @property
    def id(self) -> str:
        """Get workflow ID (kebab-case)."""
        return self.name.lower().replace('_', '-')

    @property
    def camel_case_name(self) -> str:
        """Convert kebab-case name to camelCase."""
        parts = self.id.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    @property
    def pascal_case_name(self) -> str:
        """Convert kebab-case name to PascalCase."""
        return ''.join(word.capitalize() for word in self.id.split('-'))

    def parse_schema(self, schema_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse JSON schema string.

        Args:
            schema_str: JSON string or None

        Returns:
            Parsed schema dictionary or None

        Raises:
            ValueError: If JSON is invalid
        """
        if not schema_str:
            return None

        try:
            return json.loads(schema_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON schema: {e}")
