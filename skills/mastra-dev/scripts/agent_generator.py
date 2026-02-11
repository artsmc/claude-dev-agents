"""Agent generator for creating Mastra agents."""

from pathlib import Path
from typing import List, Optional
import sys

from lib.models.agent_config import AgentConfig
from lib.utils.file_writer import FileWriter


class AgentGenerator:
    """Generator for Mastra agents."""

    def __init__(self, mastra_app: Path):
        """Initialize agent generator.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.writer = FileWriter(mastra_app)
        self.agents_dir = self.mastra_app / 'src' / 'agents'
        self.config_file = self.mastra_app / 'src' / 'config' / 'mastra.config.ts'

    def create(
        self,
        name: str,
        model: str,
        description: str,
        tools: List[str],
        system_prompt: Optional[str] = None
    ) -> None:
        """Create a new Mastra agent.

        Args:
            name: Agent name (snake_case)
            model: LLM model to use
            description: Agent description
            tools: List of tool names
            system_prompt: Optional system prompt

        Raises:
            ValueError: If configuration is invalid
            IOError: If file operations fail
        """
        # Create and validate config
        config = AgentConfig(
            name=name,
            model=model,
            description=description,
            tools=tools,
            system_prompt=system_prompt
        )
        config.validate()

        print(f"\n📦 Creating agent: {config.name}")
        print(f"   Model: {model}")
        print(f"   Description: {description}")
        if tools:
            print(f"   Tools: {', '.join(tools)}")
        print()

        # Ensure agents directory exists
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # Generate agent file
        self._generate_agent_file(config)

        # Update mastra.config.ts registration
        self._register_agent(config)

        print(f"\n✅ Agent '{config.name}' created successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Review the generated file: src/agents/{config.name}.ts")
        print(f"   2. Customize the system prompt if needed")
        print(f"   3. Test the agent with: mastra-dev analyze-agent {config.name}")

    def _generate_agent_file(self, config: AgentConfig) -> None:
        """Generate agent TypeScript file.

        Args:
            config: Agent configuration
        """
        output_path = self.agents_dir / f"{config.name}.ts"

        # Check if file already exists
        if output_path.exists():
            print(f"⚠️  Agent file already exists: {output_path.name}")
            response = input("   Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("   Skipping agent file creation")
                return

        # Build tools import and array
        tools_import = ""
        tools_array = "[]"

        if config.tools:
            # Import tools
            tool_imports = []
            for tool in config.tools:
                tool_imports.append(f"import {{ {tool} }} from '../tools/{tool}.js';")
            tools_import = '\n'.join(tool_imports)

            # Build tools array
            tools_array = f"[{', '.join(config.tools)}]"

        # Build system prompt
        system_prompt = config.system_prompt or f"You are a helpful AI assistant specialized in {config.description}."

        # Template variables
        variables = {
            'name': config.name,
            'camelCaseName': config.camel_case_name,
            'pascalCaseName': config.pascal_case_name,
            'model': config.model,
            'description': config.description,
            'systemPrompt': system_prompt,
            'toolsImport': tools_import,
            'tools': tools_array
        }

        # Try to use template, fallback to inline
        try:
            self.writer.generate_from_template(
                'agent.template.ts',
                output_path,
                variables
            )
        except FileNotFoundError:
            # Template not found, generate inline
            content = self._generate_agent_content(variables)
            self.writer.write_typescript(output_path, content)

    def _generate_agent_content(self, vars: dict) -> str:
        """Generate agent file content inline (fallback).

        Args:
            vars: Template variables

        Returns:
            Agent file content
        """
        tools_import_section = f"{vars['toolsImport']}\n" if vars['toolsImport'] else ""

        return f"""import {{ Agent }} from '@mastra/core';
{tools_import_section}
/**
 * {vars['pascalCaseName']} Agent
 *
 * {vars['description']}
 */
export const {vars['camelCaseName']}Agent = new Agent({{
  id: '{vars['name']}',
  name: '{vars['pascalCaseName']} Agent',
  description: '{vars['description']}',
  model: '{vars['model']}',
  systemPrompt: `{vars['systemPrompt']}`,
  tools: {vars['tools']},
}});

export default {vars['camelCaseName']}Agent;
"""

    def _register_agent(self, config: AgentConfig) -> None:
        """Register agent in mastra.config.ts.

        Args:
            config: Agent configuration
        """
        if not self.config_file.exists():
            print(f"⚠️  Config file not found: {self.config_file}")
            return

        try:
            # Add import statement
            import_stmt = f"import {{ {config.camel_case_name}Agent }} from '../agents/{config.name}.js';"
            self.writer.insert_import(self.config_file, import_stmt)

            # Add to agents object
            # Note: This is a simplified approach - in production, use proper AST parsing
            content = self.config_file.read_text()

            # Check if agents property exists
            if 'agents:' in content:
                # Find agents object and add entry
                agent_entry = f"{config.camel_case_name}: {config.camel_case_name}Agent"
                self.writer.append_to_object(
                    self.config_file,
                    r'agents:\s*{',
                    config.camel_case_name,
                    f"{config.camel_case_name}Agent"
                )
            else:
                print("⚠️  No 'agents' property found in mastra.config.ts")
                print(f"   Add manually: agents: {{ {config.camel_case_name}: {config.camel_case_name}Agent }}")

        except Exception as e:
            print(f"⚠️  Failed to update mastra.config.ts: {e}")
            print(f"   Please manually add:")
            print(f"   1. Import: import {{ {config.camel_case_name}Agent }} from '../agents/{config.name}.js';")
            print(f"   2. Register: agents: {{ {config.camel_case_name}: {config.camel_case_name}Agent }}")
