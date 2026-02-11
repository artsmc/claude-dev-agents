#!/usr/bin/env python3
"""
Mastra Development CLI

Main entry point for the mastra-dev skill providing comprehensive tooling
for Mastra workflow engine development.
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
SCRIPT_DIR = Path(__file__).parent
LIB_DIR = SCRIPT_DIR / 'lib'
sys.path.insert(0, str(LIB_DIR))

# Import command handlers
from agent_generator import AgentGenerator
from workflow_generator import WorkflowGenerator
from tool_generator import ToolGenerator
from server_manager import ServerManager
from mcp_manager import MCPManager
from lib.analyzers.mastra_analyzer import MastraAnalyzer

# Constants
VERSION = '1.0.0'
MONOREPO_ROOT = Path('/home/artsmc/applications/low-code')
MASTRA_APP = MONOREPO_ROOT / 'apps' / 'mastra'


def create_parser():
    """Create the main argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog='mastra-dev',
        description='Mastra Workflow Development Toolkit',
        epilog='For detailed help on a command, use: mastra-dev <command> --help'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {VERSION}'
    )
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress banner output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # =========================================================================
    # Agent Commands
    # =========================================================================
    agent_parser = subparsers.add_parser(
        'create-agent',
        help='Create a new Mastra agent'
    )
    agent_parser.add_argument(
        'name',
        help='Agent name (snake_case)'
    )
    agent_parser.add_argument(
        '--model',
        default='gpt-4o-mini',
        help='LLM model to use (default: gpt-4o-mini)'
    )
    agent_parser.add_argument(
        '--description',
        required=True,
        help='Agent description'
    )
    agent_parser.add_argument(
        '--tools',
        nargs='*',
        default=[],
        help='List of tool names to attach to agent'
    )
    agent_parser.add_argument(
        '--system-prompt',
        help='System prompt for the agent'
    )

    list_agents_parser = subparsers.add_parser(
        'list-agents',
        help='List all Mastra agents'
    )
    list_agents_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    analyze_agent_parser = subparsers.add_parser(
        'analyze-agent',
        help='Analyze an agent configuration'
    )
    analyze_agent_parser.add_argument(
        'name',
        help='Agent name to analyze'
    )

    # =========================================================================
    # Workflow Commands
    # =========================================================================
    workflow_parser = subparsers.add_parser(
        'create-workflow',
        help='Create a new Mastra workflow'
    )
    workflow_parser.add_argument(
        'name',
        help='Workflow name (kebab-case)'
    )
    workflow_parser.add_argument(
        '--description',
        required=True,
        help='Workflow description'
    )
    workflow_parser.add_argument(
        '--input-schema',
        help='JSON string for input schema definition'
    )
    workflow_parser.add_argument(
        '--output-schema',
        help='JSON string for output schema definition'
    )

    add_step_parser = subparsers.add_parser(
        'add-step',
        help='Add a step to an existing workflow'
    )
    add_step_parser.add_argument(
        'workflow',
        help='Workflow name'
    )
    add_step_parser.add_argument(
        'step_name',
        help='Step name (kebab-case)'
    )
    add_step_parser.add_argument(
        '--type',
        choices=['then', 'parallel', 'branch'],
        default='then',
        help='Step execution type (default: then)'
    )
    add_step_parser.add_argument(
        '--input-schema',
        help='JSON string for step input schema'
    )
    add_step_parser.add_argument(
        '--output-schema',
        help='JSON string for step output schema'
    )

    test_workflow_parser = subparsers.add_parser(
        'test-workflow',
        help='Test a workflow with sample input'
    )
    test_workflow_parser.add_argument(
        'name',
        help='Workflow name'
    )
    test_workflow_parser.add_argument(
        '--input',
        required=True,
        help='JSON string with workflow input data'
    )

    list_workflows_parser = subparsers.add_parser(
        'list-workflows',
        help='List all Mastra workflows'
    )
    list_workflows_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    # =========================================================================
    # Tool Commands
    # =========================================================================
    tool_parser = subparsers.add_parser(
        'create-tool',
        help='Create a new Mastra tool'
    )
    tool_parser.add_argument(
        'name',
        help='Tool name (camelCase)'
    )
    tool_parser.add_argument(
        '--description',
        required=True,
        help='Tool description'
    )
    tool_parser.add_argument(
        '--input-schema',
        help='JSON string for input schema definition'
    )
    tool_parser.add_argument(
        '--output-schema',
        help='JSON string for output schema definition'
    )

    list_tools_parser = subparsers.add_parser(
        'list-tools',
        help='List all Mastra tools'
    )
    list_tools_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    test_tool_parser = subparsers.add_parser(
        'test-tool',
        help='Test a tool with sample input'
    )
    test_tool_parser.add_argument(
        'name',
        help='Tool name'
    )
    test_tool_parser.add_argument(
        '--input',
        required=True,
        help='JSON string with tool input data'
    )

    # =========================================================================
    # Server Commands
    # =========================================================================
    server_parser = subparsers.add_parser(
        'server',
        help='Manage Mastra server'
    )
    server_subparsers = server_parser.add_subparsers(
        dest='server_command',
        help='Server operations'
    )

    server_subparsers.add_parser('start', help='Start Mastra server')
    server_subparsers.add_parser('stop', help='Stop Mastra server')
    server_subparsers.add_parser('status', help='Check server status')

    server_logs_parser = server_subparsers.add_parser(
        'logs',
        help='View server logs'
    )
    server_logs_parser.add_argument(
        '--lines',
        type=int,
        default=50,
        help='Number of log lines to display (default: 50)'
    )
    server_logs_parser.add_argument(
        '--follow',
        action='store_true',
        help='Follow log output'
    )

    # =========================================================================
    # Studio Commands
    # =========================================================================
    studio_parser = subparsers.add_parser(
        'studio',
        help='Manage Mastra Studio'
    )
    studio_subparsers = studio_parser.add_subparsers(
        dest='studio_command',
        help='Studio operations'
    )

    studio_start_parser = studio_subparsers.add_parser(
        'start',
        help='Start Mastra Studio'
    )
    studio_start_parser.add_argument(
        '--port',
        type=int,
        default=4111,
        help='Studio port (default: 4111)'
    )

    # =========================================================================
    # MCP Commands
    # =========================================================================
    mcp_parser = subparsers.add_parser(
        'mcp',
        help='Manage Model Context Protocol configuration'
    )
    mcp_subparsers = mcp_parser.add_subparsers(
        dest='mcp_command',
        help='MCP operations'
    )

    mcp_add_client_parser = mcp_subparsers.add_parser(
        'add-client',
        help='Add an MCP client configuration'
    )
    mcp_add_client_parser.add_argument(
        'name',
        help='Client name'
    )
    mcp_add_client_parser.add_argument(
        '--url',
        required=True,
        help='Client URL'
    )
    mcp_add_client_parser.add_argument(
        '--api-key',
        help='API key for authentication'
    )

    mcp_configure_server_parser = mcp_subparsers.add_parser(
        'configure-server',
        help='Configure MCP server settings'
    )
    mcp_configure_server_parser.add_argument(
        '--id',
        help='Server ID'
    )
    mcp_configure_server_parser.add_argument(
        '--name',
        help='Server name'
    )
    mcp_configure_server_parser.add_argument(
        '--description',
        help='Server description'
    )

    mcp_subparsers.add_parser(
        'list-servers',
        help='List MCP server configurations'
    )

    mcp_test_parser = mcp_subparsers.add_parser(
        'test',
        help='Test MCP server connection'
    )
    mcp_test_parser.add_argument(
        'server_id',
        help='Server ID to test'
    )

    # =========================================================================
    # Analysis Commands
    # =========================================================================
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze Mastra app for agents, workflows, and tools'
    )
    analyze_parser.add_argument(
        '--format',
        choices=['report', 'json'],
        default='report',
        help='Output format'
    )
    analyze_parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )

    debug_workflow_parser = subparsers.add_parser(
        'debug-workflow',
        help='Debug a workflow execution'
    )
    debug_workflow_parser.add_argument(
        'name',
        help='Workflow name to debug'
    )
    debug_workflow_parser.add_argument(
        '--execution-id',
        help='Specific execution ID to analyze'
    )

    show_graph_parser = subparsers.add_parser(
        'show-graph',
        help='Show workflow execution graph'
    )
    show_graph_parser.add_argument(
        'name',
        help='Workflow name'
    )
    show_graph_parser.add_argument(
        '--format',
        choices=['ascii', 'mermaid', 'json'],
        default='ascii',
        help='Graph output format'
    )

    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate Mastra configurations'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation mode'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        # Route to appropriate handler
        if args.command == 'create-agent':
            generator = AgentGenerator(MASTRA_APP)
            generator.create(
                name=args.name,
                model=args.model,
                description=args.description,
                tools=args.tools,
                system_prompt=args.system_prompt
            )
            return 0

        elif args.command == 'list-agents':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.list_agents(format=args.format)
            return 0

        elif args.command == 'analyze-agent':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.analyze_agent(args.name)
            return 0

        elif args.command == 'create-workflow':
            generator = WorkflowGenerator(MASTRA_APP)
            generator.create(
                name=args.name,
                description=args.description,
                input_schema=args.input_schema,
                output_schema=args.output_schema
            )
            return 0

        elif args.command == 'add-step':
            generator = WorkflowGenerator(MASTRA_APP)
            generator.add_step(
                workflow_name=args.workflow,
                step_name=args.step_name,
                step_type=args.type,
                input_schema=args.input_schema,
                output_schema=args.output_schema
            )
            return 0

        elif args.command == 'test-workflow':
            generator = WorkflowGenerator(MASTRA_APP)
            generator.test(args.name, args.input)
            return 0

        elif args.command == 'list-workflows':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.list_workflows(format=args.format)
            return 0

        elif args.command == 'create-tool':
            generator = ToolGenerator(MASTRA_APP)
            generator.create(
                name=args.name,
                description=args.description,
                input_schema=args.input_schema,
                output_schema=args.output_schema
            )
            return 0

        elif args.command == 'list-tools':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.list_tools(format=args.format)
            return 0

        elif args.command == 'test-tool':
            generator = ToolGenerator(MASTRA_APP)
            generator.test(args.name, args.input)
            return 0

        elif args.command == 'server':
            manager = ServerManager(MASTRA_APP)
            if args.server_command == 'start':
                manager.start()
            elif args.server_command == 'stop':
                manager.stop()
            elif args.server_command == 'status':
                manager.status()
            elif args.server_command == 'logs':
                manager.logs(lines=args.lines, follow=args.follow)
            else:
                parser.parse_args(['server', '--help'])
            return 0

        elif args.command == 'studio':
            manager = ServerManager(MASTRA_APP)
            if args.studio_command == 'start':
                manager.start_studio(port=args.port)
            else:
                parser.parse_args(['studio', '--help'])
            return 0

        elif args.command == 'mcp':
            manager = MCPManager(MASTRA_APP)
            if args.mcp_command == 'add-client':
                manager.add_client(
                    name=args.name,
                    url=args.url,
                    api_key=args.api_key
                )
            elif args.mcp_command == 'configure-server':
                manager.configure_server(
                    id=args.id,
                    name=args.name,
                    description=args.description
                )
            elif args.mcp_command == 'list-servers':
                manager.list_servers()
            elif args.mcp_command == 'test':
                manager.test(args.server_id)
            else:
                parser.parse_args(['mcp', '--help'])
            return 0

        elif args.command == 'analyze':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.analyze_all(format=args.format, output=args.output)
            return 0

        elif args.command == 'debug-workflow':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.debug_workflow(
                name=args.name,
                execution_id=args.execution_id
            )
            return 0

        elif args.command == 'show-graph':
            analyzer = MastraAnalyzer(MASTRA_APP)
            analyzer.show_graph(name=args.name, format=args.format)
            return 0

        elif args.command == 'validate':
            from lib.utils.validator import Validator
            validator = Validator(MASTRA_APP)
            validator.validate_all(strict=args.strict)
            return 0

        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
