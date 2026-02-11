"""Workflow generator for creating Mastra workflows."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import sys

from lib.models.workflow_config import WorkflowConfig, WorkflowStep
from lib.utils.file_writer import FileWriter


class WorkflowGenerator:
    """Generator for Mastra workflows."""

    def __init__(self, mastra_app: Path):
        """Initialize workflow generator.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.writer = FileWriter(mastra_app)
        self.workflows_dir = self.mastra_app / 'src' / 'workflows'
        self.mcp_config_file = self.mastra_app / 'src' / 'config' / 'mcp.config.ts'

    def create(
        self,
        name: str,
        description: str,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None
    ) -> None:
        """Create a new Mastra workflow.

        Args:
            name: Workflow name (kebab-case)
            description: Workflow description
            input_schema: JSON string for input schema
            output_schema: JSON string for output schema

        Raises:
            ValueError: If configuration is invalid
            IOError: If file operations fail
        """
        # Create and validate config
        config = WorkflowConfig(
            name=name,
            description=description
        )

        # Parse schemas
        if input_schema:
            config.input_schema = config.parse_schema(input_schema)
        if output_schema:
            config.output_schema = config.parse_schema(output_schema)

        config.validate()

        print(f"\n📦 Creating workflow: {config.id}")
        print(f"   Description: {description}")
        print()

        # Ensure workflows directory exists
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        # Generate workflow file
        self._generate_workflow_file(config)

        # Register in mcp.config.ts
        self._register_workflow(config)

        print(f"\n✅ Workflow '{config.id}' created successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Add steps with: mastra-dev add-step {config.id} <step-name>")
        print(f"   2. Review the file: src/workflows/{config.id}.ts")
        print(f"   3. Test with: mastra-dev test-workflow {config.id} --input '{{...}}'")

    def add_step(
        self,
        workflow_name: str,
        step_name: str,
        step_type: str = 'then',
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None
    ) -> None:
        """Add a step to an existing workflow.

        Args:
            workflow_name: Workflow name
            step_name: Step name (kebab-case)
            step_type: Step type (then, parallel, branch)
            input_schema: JSON string for input schema
            output_schema: JSON string for output schema

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If workflow file does not exist
        """
        workflow_file = self.workflows_dir / f"{workflow_name}.ts"

        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_name}")

        # Create step
        step = WorkflowStep(
            name=step_name,
            step_type=step_type
        )

        if input_schema:
            step.input_schema = json.loads(input_schema)
        if output_schema:
            step.output_schema = json.loads(output_schema)

        step.validate()

        print(f"\n📝 Adding step '{step.id}' to workflow '{workflow_name}'")
        print(f"   Type: {step_type}")
        print()

        # Read current workflow
        content = workflow_file.read_text()

        # Generate step code
        step_code = self._generate_step_code(step)

        # Insert step before .commit()
        if '.commit()' not in content:
            raise ValueError(f"Workflow '{workflow_name}' does not have .commit() call")

        # Find position to insert
        commit_idx = content.find('.commit()')
        if commit_idx == -1:
            raise ValueError(f"Could not find .commit() in {workflow_name}")

        # Insert step
        before_commit = content[:commit_idx]
        after_commit = content[commit_idx:]

        # Determine chain method
        chain_method = f".{step_type}({step.id}Step)"

        updated_content = f"{before_commit}\n  {chain_method}\n  {after_commit}"

        # Also insert step definition before export
        export_idx = updated_content.find(f'export const {workflow_name.replace("-", "")}')
        if export_idx == -1:
            export_idx = updated_content.find('export const')

        if export_idx > 0:
            before_export = updated_content[:export_idx]
            after_export = updated_content[export_idx:]
            updated_content = f"{before_export}\n{step_code}\n\n{after_export}"

        # Write updated workflow
        self.writer.update_typescript(workflow_file, updated_content)

        print(f"✅ Step '{step.id}' added successfully!")

    def test(self, name: str, input_data: str) -> None:
        """Test a workflow with sample input.

        Args:
            name: Workflow name
            input_data: JSON string with input data

        Raises:
            NotImplementedError: Testing requires running Mastra server
        """
        print(f"\n🧪 Testing workflow: {name}")
        print(f"   Input: {input_data}")
        print()

        print("⚠️  Workflow testing requires the Mastra server to be running.")
        print("   Start the server with: mastra-dev server start")
        print("   Then use the Mastra Studio to test workflows interactively.")
        print()

    def _generate_workflow_file(self, config: WorkflowConfig) -> None:
        """Generate workflow TypeScript file.

        Args:
            config: Workflow configuration
        """
        output_path = self.workflows_dir / f"{config.id}.ts"

        # Check if file already exists
        if output_path.exists():
            print(f"⚠️  Workflow file already exists: {output_path.name}")
            response = input("   Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("   Skipping workflow file creation")
                return

        # Build schemas
        input_schema_code = self._build_schema_code(config.input_schema, 'input')
        output_schema_code = self._build_schema_code(config.output_schema, 'output')

        # Template variables
        variables = {
            'id': config.id,
            'camelCaseName': config.camel_case_name,
            'description': config.description,
            'inputSchema': input_schema_code,
            'outputSchema': output_schema_code
        }

        # Try template, fallback to inline
        try:
            self.writer.generate_from_template(
                'workflow.template.ts',
                output_path,
                variables
            )
        except FileNotFoundError:
            content = self._generate_workflow_content(variables)
            self.writer.write_typescript(output_path, content)

    def _generate_workflow_content(self, vars: dict) -> str:
        """Generate workflow file content inline.

        Args:
            vars: Template variables

        Returns:
            Workflow file content
        """
        return f"""import {{ createWorkflow, createStep }} from '@mastra/core/workflows';
import {{ z }} from 'zod';

/**
 * {vars['camelCaseName']} Workflow
 *
 * {vars['description']}
 */

// Input/Output schemas
{vars['inputSchema']}

{vars['outputSchema']}

// TODO: Add workflow steps here using createStep()
// Example:
// const exampleStep = createStep({{
//   id: 'example-step',
//   inputSchema: z.object({{ ... }}),
//   outputSchema: z.object({{ ... }}),
//   execute: async ({{ inputData }}) => {{
//     // Step logic here
//     return {{ ... }};
//   }},
// }});

// Compose workflow from steps
export const {vars['camelCaseName']}Workflow = createWorkflow({{
  id: '{vars['id']}',
  description: '{vars['description']}',
  inputSchema,
  outputSchema,
}})
  // .then(exampleStep)
  .commit();

export default {vars['camelCaseName']}Workflow;
"""

    def _generate_step_code(self, step: WorkflowStep) -> str:
        """Generate step definition code.

        Args:
            step: Workflow step configuration

        Returns:
            TypeScript code for step
        """
        input_schema = self._build_schema_code(step.input_schema, f'{step.id}-input')
        output_schema = self._build_schema_code(step.output_schema, f'{step.id}-output')

        return f"""// Step: {step.id}
const {step.id.replace('-', '')}Step = createStep({{
  id: '{step.id}',
  inputSchema: {input_schema},
  outputSchema: {output_schema},
  execute: async ({{ inputData }}) => {{
    // TODO: Implement step logic
    return {{}};
  }},
}});
"""

    def _build_schema_code(
        self,
        schema: Optional[Dict[str, Any]],
        schema_type: str
    ) -> str:
        """Build Zod schema code from JSON schema.

        Args:
            schema: JSON schema dictionary
            schema_type: Schema type (input/output)

        Returns:
            TypeScript code for Zod schema
        """
        if not schema:
            # Default empty schema
            return f"""const {schema_type}Schema = z.object({{}});"""

        # Convert JSON schema to Zod schema (simplified)
        fields = []
        for key, value in schema.items():
            if isinstance(value, dict):
                field_type = value.get('type', 'string')
                description = value.get('description', '')

                # Map JSON schema types to Zod
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
        return f"""const {schema_type}Schema = z.object({{\n{fields_code}\n}});"""

    def _register_workflow(self, config: WorkflowConfig) -> None:
        """Register workflow in mcp.config.ts.

        Args:
            config: Workflow configuration
        """
        if not self.mcp_config_file.exists():
            print(f"⚠️  MCP config file not found: {self.mcp_config_file}")
            return

        try:
            # Add import
            import_stmt = f"import {{ {config.camel_case_name}Workflow }} from '../workflows/{config.id}.js';"
            self.writer.insert_import(self.mcp_config_file, import_stmt)

            # Add to workflows object
            self.writer.append_to_object(
                self.mcp_config_file,
                r'workflows:\s*{',
                config.camel_case_name,
                f"{config.camel_case_name}Workflow"
            )

        except Exception as e:
            print(f"⚠️  Failed to update mcp.config.ts: {e}")
            print(f"   Please manually add:")
            print(f"   1. Import: import {{ {config.camel_case_name}Workflow }} from '../workflows/{config.id}.js';")
            print(f"   2. Register: workflows: {{ {config.camel_case_name}: {config.camel_case_name}Workflow }}")
