"""Agent configuration data models."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AgentConfig:
    """Configuration for a Mastra agent."""

    name: str
    model: str = 'gpt-4o-mini'
    description: str = ''
    tools: List[str] = field(default_factory=list)
    system_prompt: Optional[str] = None

    def validate(self) -> None:
        """Validate agent configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.name:
            raise ValueError("Agent name is required")

        if not self.name.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                f"Invalid agent name '{self.name}': "
                "must contain only alphanumeric characters, hyphens, and underscores"
            )

        if not self.model:
            raise ValueError("Agent model is required")

        if not self.description:
            raise ValueError("Agent description is required")

    @property
    def camel_case_name(self) -> str:
        """Convert snake_case name to camelCase."""
        parts = self.name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    @property
    def pascal_case_name(self) -> str:
        """Convert snake_case name to PascalCase."""
        return ''.join(word.capitalize() for word in self.name.split('_'))
