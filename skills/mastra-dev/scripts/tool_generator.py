"""Tool generator for creating Mastra tools."""

from pathlib import Path
from typing import Optional, Dict, Any
import json

from lib.models.tool_config import ToolConfig
from lib.utils.file_writer import FileWriter


class ToolGenerator:
    """Generator for Mastra tools."""

    def __init__(self, mastra_app: Path):
        """Initialize tool generator.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.writer = FileWriter(mastra_app)
        self.tools_dir = self.mastra_app / 'src' / 'tools'

    def create(
        self,
        name: str,
        description: str,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None
    ) -> None:
        """Create a new Mastra tool.

        Args:
            name: Tool name (camelCase)
            description: Tool description
            input_schema: JSON string for input schema
            output_schema: JSON string for output schema

        Raises:
            ValueError: If configuration is invalid
            IOError: If file operations fail
        """
        # Create and validate config
        config = ToolConfig(
            name=name,
            description=description
        )

        # Parse schemas
        if input_schema:
            config.input_schema = config.parse_schema(input_schema)
        if output_schema:
            config.output_schema = config.parse_schema(output_schema)

        config.validate()

        print(f"\n📦 Creating tool: {config.name}")
        print(f"   Description: {description}")
        print()

        # Ensure tools directory exists
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        # Generate tool file
        self._generate_tool_file(config)

        print(f"\n✅ Tool '{config.name}' created successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Implement tool logic in: src/tools/{config.name}.ts")
        print(f"   2. Test with: mastra-dev test-tool {config.name} --input '{{...}}'")
        print(f"   3. Attach to agents with: mastra-dev create-agent --tools {config.name}")

    def test(self, name: str, input_data: str) -> None:
        """Test a tool with sample input.

        Args:
            name: Tool name
            input_data: JSON string with input data

        Raises:
            NotImplementedError: Testing requires running Mastra server
        """
        print(f"\n🧪 Testing tool: {name}")
        print(f"   Input: {input_data}")
        print()

        print("⚠️  Tool testing requires the Mastra server to be running.")
        print("   Start the server with: mastra-dev server start")
        print("   Then use the Mastra Studio to test tools interactively.")
        print()

    def _generate_tool_file(self, config: ToolConfig) -> None:
        """Generate tool TypeScript file.

        Args:
            config: Tool configuration
        """
        output_path = self.tools_dir / f"{config.name}.ts"

        # Check if file already exists
        if output_path.exists():
            print(f"⚠️  Tool file already exists: {output_path.name}")
            response = input("   Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("   Skipping tool file creation")
                return

        # Build schemas
        input_schema_code = self._build_schema_code(config.input_schema)
        output_schema_code = self._build_schema_code(config.output_schema)

        # Template variables
        variables = {
            'name': config.name,
            'pascalCaseName': config.pascal_case_name,
            'description': config.description,
            'inputSchema': input_schema_code,
            'outputSchema': output_schema_code
        }

        # Try template, fallback to inline
        try:
            self.writer.generate_from_template(
                'tool.template.ts',
                output_path,
                variables
            )
        except FileNotFoundError:
            content = self._generate_tool_content(variables)
            self.writer.write_typescript(output_path, content)

    def _generate_tool_content(self, vars: dict) -> str:
        """Generate tool file content inline.

        Args:
            vars: Template variables

        Returns:
            Tool file content
        """
        return f"""import {{ createTool }} from '@mastra/core';
import {{ z }} from 'zod';

/**
 * {vars['pascalCaseName']} Tool
 *
 * {vars['description']}
 */

{vars['inputSchema']}

{vars['outputSchema']}

export const {vars['name']} = createTool({{
  id: '{vars['name']}',
  name: '{vars['pascalCaseName']}',
  description: '{vars['description']}',
  inputSchema,
  outputSchema,
  execute: async ({{ inputData }}) => {{
    // TODO: Implement tool logic here

    // Example:
    // const result = await someOperation(inputData);
    // return result;

    throw new Error('Tool implementation pending');
  }},
}});

export default {vars['name']};
"""

    def _build_schema_code(
        self,
        schema: Optional[Dict[str, Any]]
    ) -> str:
        """Build Zod schema code from JSON schema.

        Args:
            schema: JSON schema dictionary

        Returns:
            TypeScript code for Zod schema
        """
        if not schema:
            return "const inputSchema = z.object({});"

        # Convert JSON schema to Zod (simplified)
        fields = []
        for key, value in schema.items():
            if isinstance(value, dict):
                field_type = value.get('type', 'string')
                description = value.get('description', '')

                zod_type = {
                    'string': 'z.string()',
                    'number': 'z.number()',
                    'integer': 'z.number().int()',
                    'boolean': 'z.boolean()',
                    'array': 'z.array(z.any())',
                    'object': 'z.object({})'
                }.get(field_type, 'z.string()')

                if description:
                    zod_type += f'.describe("{description}")'

                fields.append(f"  {key}: {zod_type}")

        fields_code = ',\n'.join(fields)
        return f"const inputSchema = z.object({{\n{fields_code}\n}});\nconst outputSchema = z.object({{\n{fields_code}\n}});"
