"""File writing utilities with template substitution."""

from pathlib import Path
from typing import Dict, Any
import re


class FileWriter:
    """Utility for writing TypeScript files with template substitution."""

    def __init__(self, mastra_app: Path):
        """Initialize file writer.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.templates_dir = Path(__file__).parent.parent.parent.parent / 'templates'

    def read_template(self, template_name: str) -> str:
        """Read template file.

        Args:
            template_name: Name of template file (e.g., 'agent.template.ts')

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template does not exist
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path.read_text()

    def substitute_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Substitute variables in template.

        Args:
            template: Template content
            variables: Dictionary of variable name -> value mappings

        Returns:
            Template with substituted values

        Examples:
            >>> substitute_template("Hello {{name}}", {"name": "World"})
            "Hello World"
        """
        result = template

        for key, value in variables.items():
            # Handle both {{key}} and {{ key }} formats
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            result = re.sub(pattern, str(value), result)

        return result

    def write_typescript(
        self,
        file_path: Path,
        content: str
    ) -> None:
        """Write TypeScript file with proper formatting.

        Args:
            file_path: Path to output file
            content: TypeScript content

        Raises:
            IOError: If file cannot be written
        """
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_text(content)

        print(f"✓ Created: {file_path.relative_to(self.mastra_app)}")

    def generate_from_template(
        self,
        template_name: str,
        output_path: Path,
        variables: Dict[str, Any]
    ) -> None:
        """Generate file from template.

        Args:
            template_name: Template file name
            output_path: Output file path
            variables: Template variables

        Raises:
            FileNotFoundError: If template not found
            IOError: If file cannot be written
        """
        template = self.read_template(template_name)
        content = self.substitute_template(template, variables)
        self.write_typescript(output_path, content)

    def read_typescript(self, file_path: Path) -> str:
        """Read TypeScript file.

        Args:
            file_path: Path to TypeScript file

        Returns:
            File content

        Raises:
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return file_path.read_text()

    def update_typescript(
        self,
        file_path: Path,
        content: str
    ) -> None:
        """Update existing TypeScript file.

        Args:
            file_path: Path to file
            content: New content

        Raises:
            IOError: If file cannot be written
        """
        file_path.write_text(content)
        print(f"✓ Updated: {file_path.relative_to(self.mastra_app)}")

    def insert_import(
        self,
        file_path: Path,
        import_statement: str
    ) -> None:
        """Insert import statement at the top of a TypeScript file.

        Args:
            file_path: Path to TypeScript file
            import_statement: Import statement to add

        Raises:
            FileNotFoundError: If file does not exist
        """
        content = self.read_typescript(file_path)

        # Check if import already exists
        if import_statement.strip() in content:
            return

        # Find last import statement
        lines = content.split('\n')
        last_import_idx = -1

        for idx, line in enumerate(lines):
            if line.strip().startswith('import '):
                last_import_idx = idx

        # Insert after last import
        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, import_statement)
        else:
            # No imports found, add at top
            lines.insert(0, import_statement)
            lines.insert(1, '')

        self.update_typescript(file_path, '\n'.join(lines))

    def append_to_object(
        self,
        file_path: Path,
        object_pattern: str,
        key: str,
        value: str
    ) -> None:
        """Append key-value pair to a TypeScript object.

        Args:
            file_path: Path to TypeScript file
            object_pattern: Regex pattern to find object
            key: Object key to add
            value: Object value to add

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If object pattern not found
        """
        content = self.read_typescript(file_path)

        # Check if key already exists
        key_pattern = rf'{re.escape(key)}\s*:'
        if re.search(key_pattern, content):
            print(f"⚠ Key '{key}' already exists in {file_path.name}")
            return

        # Find object and insert before closing brace
        pattern = rf'({object_pattern}.*?)\}}'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            raise ValueError(f"Object pattern '{object_pattern}' not found in {file_path}")

        # Extract object content
        object_content = match.group(1)

        # Check if object is empty
        if re.search(r'{\s*$', object_content):
            # Empty object
            new_content = f"{object_content}\n    {key}: {value},\n  }}"
        else:
            # Has existing entries
            new_content = f"{object_content}\n    {key}: {value},\n  }}"

        # Replace in content
        updated_content = content.replace(match.group(0), new_content)
        self.update_typescript(file_path, updated_content)
