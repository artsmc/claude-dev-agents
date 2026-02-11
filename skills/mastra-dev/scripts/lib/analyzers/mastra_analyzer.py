"""Mastra codebase analyzer for agents, workflows, and tools."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import json
import sys


class MastraAnalyzer:
    """Analyzer for Mastra application structure."""

    def __init__(self, mastra_app: Path):
        """Initialize analyzer.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.src_dir = self.mastra_app / 'src'
        self.agents_dir = self.src_dir / 'agents'
        self.workflows_dir = self.src_dir / 'workflows'
        self.tools_dir = self.src_dir / 'tools'

    def list_agents(self, format: str = 'table') -> None:
        """List all Mastra agents.

        Args:
            format: Output format (table, json)
        """
        print("\n🤖 Mastra Agents")
        print("=" * 60)
        print()

        if not self.agents_dir.exists():
            print("ℹ️  No agents directory found")
            return

        agents = self._scan_agents()

        if not agents:
            print("ℹ️  No agents found")
            print(f"   Create one with: mastra-dev create-agent <name>")
            return

        if format == 'json':
            print(json.dumps(agents, indent=2))
        else:
            # Table format
            for agent in agents:
                print(f"📌 {agent['name']}")
                print(f"   File: {agent['file']}")
                if agent.get('model'):
                    print(f"   Model: {agent['model']}")
                if agent.get('description'):
                    print(f"   Description: {agent['description']}")
                print()

    def analyze_agent(self, name: str) -> None:
        """Analyze a specific agent configuration.

        Args:
            name: Agent name

        Raises:
            FileNotFoundError: If agent file not found
        """
        print(f"\n🔍 Analyzing agent: {name}")
        print("=" * 60)
        print()

        agent_file = self.agents_dir / f"{name}.ts"
        if not agent_file.exists():
            print(f"❌ Agent not found: {name}", file=sys.stderr)
            sys.exit(1)

        content = agent_file.read_text()

        # Extract configuration
        config = self._parse_agent(content)

        print(f"Name: {config.get('name', 'N/A')}")
        print(f"File: {agent_file.name}")
        print(f"Model: {config.get('model', 'N/A')}")
        print(f"Description: {config.get('description', 'N/A')}")
        print()

        # Extract tools
        tools = config.get('tools', [])
        if tools:
            print(f"Tools ({len(tools)}):")
            for tool in tools:
                print(f"  • {tool}")
            print()

        # Check if registered
        self._check_agent_registration(config.get('name', name))

    def list_workflows(self, format: str = 'table') -> None:
        """List all Mastra workflows.

        Args:
            format: Output format (table, json)
        """
        print("\n⚙️  Mastra Workflows")
        print("=" * 60)
        print()

        if not self.workflows_dir.exists():
            print("ℹ️  No workflows directory found")
            return

        workflows = self._scan_workflows()

        if not workflows:
            print("ℹ️  No workflows found")
            print(f"   Create one with: mastra-dev create-workflow <name>")
            return

        if format == 'json':
            print(json.dumps(workflows, indent=2))
        else:
            for workflow in workflows:
                print(f"📊 {workflow['name']}")
                print(f"   File: {workflow['file']}")
                if workflow.get('description'):
                    print(f"   Description: {workflow['description']}")
                if workflow.get('steps'):
                    print(f"   Steps: {len(workflow['steps'])}")
                print()

    def list_tools(self, format: str = 'table') -> None:
        """List all Mastra tools.

        Args:
            format: Output format (table, json)
        """
        print("\n🛠️  Mastra Tools")
        print("=" * 60)
        print()

        if not self.tools_dir.exists():
            print("ℹ️  No tools directory found")
            return

        tools = self._scan_tools()

        if not tools:
            print("ℹ️  No tools found")
            print(f"   Create one with: mastra-dev create-tool <name>")
            return

        if format == 'json':
            print(json.dumps(tools, indent=2))
        else:
            for tool in tools:
                print(f"🔧 {tool['name']}")
                print(f"   File: {tool['file']}")
                if tool.get('description'):
                    print(f"   Description: {tool['description']}")
                print()

    def analyze_all(
        self,
        format: str = 'report',
        output: Optional[str] = None
    ) -> None:
        """Analyze entire Mastra app.

        Args:
            format: Output format (report, json)
            output: Output file path (default: stdout)
        """
        print("\n📊 Mastra Application Analysis")
        print("=" * 60)
        print()

        # Scan all components
        agents = self._scan_agents()
        workflows = self._scan_workflows()
        tools = self._scan_tools()

        analysis = {
            'agents': agents,
            'workflows': workflows,
            'tools': tools,
            'summary': {
                'total_agents': len(agents),
                'total_workflows': len(workflows),
                'total_tools': len(tools)
            }
        }

        if format == 'json':
            output_text = json.dumps(analysis, indent=2)
        else:
            output_text = self._format_analysis_report(analysis)

        if output:
            Path(output).write_text(output_text)
            print(f"✅ Analysis saved to: {output}")
        else:
            print(output_text)

    def debug_workflow(
        self,
        name: str,
        execution_id: Optional[str] = None
    ) -> None:
        """Debug a workflow execution.

        Args:
            name: Workflow name
            execution_id: Optional execution ID

        Raises:
            NotImplementedError: Requires database connection
        """
        print(f"\n🐛 Debugging workflow: {name}")
        if execution_id:
            print(f"   Execution ID: {execution_id}")
        print()

        print("⚠️  Workflow debugging requires:")
        print("   1. Database connection to Mastra PostgreSQL")
        print("   2. Execution history in mastra.executions table")
        print()
        print("   Use Mastra Studio for interactive debugging:")
        print("   mastra-dev studio start")

    def show_graph(self, name: str, format: str = 'ascii') -> None:
        """Show workflow execution graph.

        Args:
            name: Workflow name
            format: Graph format (ascii, mermaid, json)

        Raises:
            FileNotFoundError: If workflow not found
        """
        print(f"\n📈 Workflow Graph: {name}")
        print("=" * 60)
        print()

        workflow_file = self.workflows_dir / f"{name}.ts"
        if not workflow_file.exists():
            print(f"❌ Workflow not found: {name}", file=sys.stderr)
            sys.exit(1)

        content = workflow_file.read_text()

        # Parse workflow structure
        steps = self._parse_workflow_steps(content)

        if format == 'json':
            print(json.dumps(steps, indent=2))
        elif format == 'mermaid':
            self._print_mermaid_graph(steps)
        else:
            self._print_ascii_graph(steps)

    def _scan_agents(self) -> List[Dict[str, Any]]:
        """Scan agents directory.

        Returns:
            List of agent metadata
        """
        if not self.agents_dir.exists():
            return []

        agents = []
        for file in self.agents_dir.glob('*.ts'):
            if file.name == '.gitkeep':
                continue

            content = file.read_text()
            config = self._parse_agent(content)
            config['file'] = file.name
            agents.append(config)

        return agents

    def _scan_workflows(self) -> List[Dict[str, Any]]:
        """Scan workflows directory.

        Returns:
            List of workflow metadata
        """
        if not self.workflows_dir.exists():
            return []

        workflows = []
        for file in self.workflows_dir.glob('*.ts'):
            if file.name == '.gitkeep':
                continue

            content = file.read_text()
            config = self._parse_workflow(content)
            config['file'] = file.name
            workflows.append(config)

        return workflows

    def _scan_tools(self) -> List[Dict[str, Any]]:
        """Scan tools directory.

        Returns:
            List of tool metadata
        """
        if not self.tools_dir.exists():
            return []

        tools = []
        for file in self.tools_dir.glob('*.ts'):
            if file.name == '.gitkeep':
                continue

            content = file.read_text()
            config = self._parse_tool(content)
            config['file'] = file.name
            tools.append(config)

        return tools

    def _parse_agent(self, content: str) -> Dict[str, Any]:
        """Parse agent configuration from TypeScript.

        Args:
            content: TypeScript file content

        Returns:
            Agent configuration dictionary
        """
        config = {}

        # Extract ID
        id_match = re.search(r"id:\s*['\"](.+?)['\"]", content)
        if id_match:
            config['name'] = id_match.group(1)

        # Extract model
        model_match = re.search(r"model:\s*['\"](.+?)['\"]", content)
        if model_match:
            config['model'] = model_match.group(1)

        # Extract description
        desc_match = re.search(r"description:\s*['\"](.+?)['\"]", content)
        if desc_match:
            config['description'] = desc_match.group(1)

        # Extract tools
        tools_match = re.search(r'tools:\s*\[([^\]]+)\]', content)
        if tools_match:
            tools_str = tools_match.group(1)
            config['tools'] = [t.strip() for t in tools_str.split(',') if t.strip()]

        return config

    def _parse_workflow(self, content: str) -> Dict[str, Any]:
        """Parse workflow configuration from TypeScript.

        Args:
            content: TypeScript file content

        Returns:
            Workflow configuration dictionary
        """
        config = {}

        # Extract ID
        id_match = re.search(r"id:\s*['\"](.+?)['\"]", content)
        if id_match:
            config['name'] = id_match.group(1)

        # Extract description
        desc_match = re.search(r"description:\s*['\"](.+?)['\"]", content)
        if desc_match:
            config['description'] = desc_match.group(1)

        # Extract steps
        config['steps'] = self._parse_workflow_steps(content)

        return config

    def _parse_tool(self, content: str) -> Dict[str, Any]:
        """Parse tool configuration from TypeScript.

        Args:
            content: TypeScript file content

        Returns:
            Tool configuration dictionary
        """
        config = {}

        # Extract ID
        id_match = re.search(r"id:\s*['\"](.+?)['\"]", content)
        if id_match:
            config['name'] = id_match.group(1)

        # Extract description
        desc_match = re.search(r"description:\s*['\"](.+?)['\"]", content)
        if desc_match:
            config['description'] = desc_match.group(1)

        return config

    def _parse_workflow_steps(self, content: str) -> List[str]:
        """Parse workflow steps from content.

        Args:
            content: Workflow file content

        Returns:
            List of step names
        """
        steps = []

        # Find .then(), .parallel(), .branch() calls
        step_pattern = r'\.(then|parallel|branch)\(([^)]+)\)'
        matches = re.findall(step_pattern, content)

        for method, step_ref in matches:
            steps.append(f"{method}({step_ref.strip()})")

        return steps

    def _check_agent_registration(self, name: str) -> None:
        """Check if agent is registered in mastra.config.ts.

        Args:
            name: Agent name
        """
        config_file = self.src_dir / 'config' / 'mastra.config.ts'

        if not config_file.exists():
            print("⚠️  mastra.config.ts not found")
            return

        content = config_file.read_text()

        if name in content:
            print(f"✅ Agent is registered in mastra.config.ts")
        else:
            print(f"⚠️  Agent is NOT registered in mastra.config.ts")
            print(f"   Register manually in agents object")

    def _format_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as text report.

        Args:
            analysis: Analysis data

        Returns:
            Formatted report
        """
        lines = []

        lines.append("SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Agents: {analysis['summary']['total_agents']}")
        lines.append(f"Workflows: {analysis['summary']['total_workflows']}")
        lines.append(f"Tools: {analysis['summary']['total_tools']}")
        lines.append("")

        if analysis['agents']:
            lines.append("AGENTS")
            lines.append("=" * 60)
            for agent in analysis['agents']:
                lines.append(f"• {agent.get('name', 'Unknown')}")
                lines.append(f"  Model: {agent.get('model', 'N/A')}")
            lines.append("")

        if analysis['workflows']:
            lines.append("WORKFLOWS")
            lines.append("=" * 60)
            for workflow in analysis['workflows']:
                lines.append(f"• {workflow.get('name', 'Unknown')}")
                lines.append(f"  Steps: {len(workflow.get('steps', []))}")
            lines.append("")

        if analysis['tools']:
            lines.append("TOOLS")
            lines.append("=" * 60)
            for tool in analysis['tools']:
                lines.append(f"• {tool.get('name', 'Unknown')}")
            lines.append("")

        return '\n'.join(lines)

    def _print_ascii_graph(self, steps: List[str]) -> None:
        """Print ASCII workflow graph.

        Args:
            steps: List of workflow steps
        """
        if not steps:
            print("ℹ️  No steps found in workflow")
            return

        print("Workflow Flow:")
        print()
        print("  START")
        for idx, step in enumerate(steps, 1):
            print(f"    ↓")
            print(f"  [{idx}] {step}")
        print(f"    ↓")
        print("  END")
        print()

    def _print_mermaid_graph(self, steps: List[str]) -> None:
        """Print Mermaid workflow graph.

        Args:
            steps: List of workflow steps
        """
        print("```mermaid")
        print("graph TD")
        print("  START[Start]")

        prev_node = "START"
        for idx, step in enumerate(steps, 1):
            node_id = f"STEP{idx}"
            print(f"  {node_id}[{step}]")
            print(f"  {prev_node} --> {node_id}")
            prev_node = node_id

        print(f"  {prev_node} --> END[End]")
        print("```")
        print()
