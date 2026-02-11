"""Tool configuration data models."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class ToolConfig:
    """Configuration for a Mastra tool."""

    name: str
    description: str = ''
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

    def validate(self) -> None:
        """Validate tool configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.name:
            raise ValueError("Tool name is required")

        # Tool names should be camelCase
        if not self.name[0].islower() or not self.name.replace('_', '').isalnum():
            raise ValueError(
                f"Invalid tool name '{self.name}': "
                "must be camelCase (e.g., 'fetchUserData')"
            )

        if not self.description:
            raise ValueError("Tool description is required")

    @property
    def id(self) -> str:
        """Get tool ID (same as name for camelCase)."""
        return self.name

    @property
    def pascal_case_name(self) -> str:
        """Convert camelCase name to PascalCase."""
        if not self.name:
            return ''
        return self.name[0].upper() + self.name[1:]

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
