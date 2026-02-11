"""MCP (Model Context Protocol) configuration manager."""

from pathlib import Path
from typing import Optional
import sys

from lib.utils.file_writer import FileWriter


class MCPManager:
    """Manager for MCP client/server configurations."""

    def __init__(self, mastra_app: Path):
        """Initialize MCP manager.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.writer = FileWriter(mastra_app)
        self.mcp_config = self.mastra_app / 'src' / 'config' / 'mcp.config.ts'

    def add_client(
        self,
        name: str,
        url: str,
        api_key: Optional[str] = None
    ) -> None:
        """Add an MCP client configuration.

        Args:
            name: Client name
            url: Client URL
            api_key: Optional API key for authentication

        Raises:
            FileNotFoundError: If config file does not exist
        """
        print(f"\n🔌 Adding MCP client: {name}")
        print(f"   URL: {url}")
        if api_key:
            print(f"   API Key: ***{api_key[-4:]}")
        print()

        if not self.mcp_config.exists():
            print(f"❌ MCP config not found: {self.mcp_config}", file=sys.stderr)
            sys.exit(1)

        # Read current config
        content = self.mcp_config.read_text()

        # Build client configuration
        client_config = f"""{{
    url: '{url}',
    {f"apiKey: '{api_key}'," if api_key else ''}
  }}"""

        try:
            # Add to clients object (if it exists)
            if 'clients:' in content:
                self.writer.append_to_object(
                    self.mcp_config,
                    r'clients:\s*{',
                    name,
                    client_config
                )
                print(f"✅ MCP client '{name}' added successfully!")
            else:
                print("⚠️  No 'clients' property found in mcp.config.ts")
                print(f"   Add manually: clients: {{ {name}: {client_config} }}")

        except Exception as e:
            print(f"❌ Failed to update mcp.config.ts: {e}", file=sys.stderr)
            sys.exit(2)

    def configure_server(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Configure MCP server settings.

        Args:
            id: Server ID
            name: Server name
            description: Server description

        Raises:
            FileNotFoundError: If config file does not exist
        """
        print("\n⚙️  Configuring MCP server...")
        print()

        if not self.mcp_config.exists():
            print(f"❌ MCP config not found: {self.mcp_config}", file=sys.stderr)
            sys.exit(1)

        content = self.mcp_config.read_text()

        updates = []
        if id:
            updates.append(f"ID: {id}")
        if name:
            updates.append(f"Name: {name}")
        if description:
            updates.append(f"Description: {description}")

        if not updates:
            print("ℹ️  No updates provided")
            return

        print("   Updates:")
        for update in updates:
            print(f"   • {update}")
        print()

        # Update configuration (simplified - in production, use AST parsing)
        print("⚠️  Manual configuration required:")
        print(f"   Edit: {self.mcp_config.relative_to(self.mastra_app)}")
        print("   Update the MCPServer constructor:")
        if id:
            print(f"   - id: '{id}'")
        if name:
            print(f"   - name: '{name}'")
        if description:
            print(f"   - description: '{description}'")

    def list_servers(self) -> None:
        """List MCP server configurations."""
        print("\n📋 MCP Server Configurations")
        print("=" * 60)
        print()

        if not self.mcp_config.exists():
            print(f"❌ MCP config not found: {self.mcp_config}", file=sys.stderr)
            sys.exit(1)

        content = self.mcp_config.read_text()

        # Extract server configuration (simplified parsing)
        import re

        # Find MCPServer instantiation
        server_match = re.search(
            r'new MCPServer\(\{(.*?)\}\)',
            content,
            re.DOTALL
        )

        if not server_match:
            print("ℹ️  No MCP server configuration found")
            return

        server_config = server_match.group(1)

        # Extract properties
        id_match = re.search(r"id:\s*['\"](.+?)['\"]", server_config)
        name_match = re.search(r"name:\s*['\"](.+?)['\"]", server_config)
        desc_match = re.search(r"description:\s*['\"](.+?)['\"]", server_config)

        print("Current Configuration:")
        if id_match:
            print(f"  ID: {id_match.group(1)}")
        if name_match:
            print(f"  Name: {name_match.group(1)}")
        if desc_match:
            print(f"  Description: {desc_match.group(1)}")

        # Count workflows
        workflow_matches = re.findall(r'workflows:\s*\{([^}]+)\}', content)
        if workflow_matches:
            workflows = [w.strip() for w in workflow_matches[0].split(',') if w.strip()]
            print(f"\n  Registered Workflows: {len(workflows)}")
            for workflow in workflows:
                print(f"    • {workflow.split(':')[0].strip()}")

        print()

    def test(self, server_id: str) -> None:
        """Test MCP server connection.

        Args:
            server_id: Server ID to test

        Raises:
            NotImplementedError: Testing requires running server
        """
        print(f"\n🧪 Testing MCP server: {server_id}")
        print()

        print("⚠️  MCP server testing requires:")
        print("   1. Mastra server running (mastra-dev server start)")
        print("   2. HTTP client or curl to test endpoints")
        print()
        print("   Example test:")
        print("   curl http://localhost:3000/api/mastra/mcp/tools")
        print()
