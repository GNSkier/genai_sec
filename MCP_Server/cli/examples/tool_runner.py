#!/usr/bin/env python3
"""
Interactive MCP Tool Runner
Allows you to call specific tools or run all vulnerability tests.
"""

import asyncio
import sys
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolRunner:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Connect to MCP server via STDIO transport."""
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()
        print("✓ Connected to MCP server")

    async def list_available_tools(self):
        """List all available tools."""
        try:
            response = await self.session.list_tools()
            tools = getattr(response, "tools", None)
            if tools and len(tools) > 0:
                print("\nAvailable tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"  {i:2}. {tool.name}")
                    if hasattr(tool, "description") and tool.description:
                        print(f"      {tool.description}")
                return [tool.name for tool in tools]
            else:
                print("No tools found")
                return []
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []

    async def call_tool(self, tool_name: str, **kwargs):
        """Call a specific tool with given parameters."""
        try:
            print(f"\n🔧 Calling tool: {tool_name}")
            print(f"📝 Parameters: {kwargs}")

            result = await self.session.call_tool(tool_name, kwargs)
            content = getattr(result, "content", result)

            print(f"✅ Result:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            return content
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None

    async def run_demo_tests(self):
        """Run a set of demo tests to showcase vulnerabilities."""
        print("\n🚀 Running Demo Vulnerability Tests")
        print("=" * 60)

        # SQL Injection Demo
        print("\n1. SQL Injection Test")
        await self.call_tool(
            "insert_record",
            name="test');--",
            address="123 Exploit St",
            email="hacker@evil.com",
            phone="555-0123",
            credit_card="4532-1234-5678-9012",
        )

        # File Access Demo
        print("\n2. File Access Test")
        await self.call_tool("read_file", file_path="vuln_mcp_stdio.py")

        # Command Execution Demo
        print("\n3. Command Execution Test")
        await self.call_tool("execute_command", command="whoami")

        # Environment Variable Demo
        print("\n4. Environment Variable Test")
        await self.call_tool("get_env_variable", var_name="USER")

        # Network Request Demo
        print("\n5. Network Request Test")
        await self.call_tool("make_request", url="http://httpbin.org/get")

        # System Info Demo
        print("\n6. System Information Test")
        await self.call_tool("get_system_info")

        print("\n✅ Demo tests completed!")

    async def interactive_mode(self):
        """Interactive mode for calling tools manually."""
        tools = await self.list_available_tools()
        if not tools:
            return

        print("\n" + "=" * 60)
        print("INTERACTIVE TOOL RUNNER")
        print("=" * 60)
        print("Commands:")
        print("  list                    - List available tools")
        print("  call <tool> [params]    - Call a specific tool")
        print("  demo                    - Run demo vulnerability tests")
        print("  help                    - Show this help")
        print("  quit/exit               - Exit")
        print("=" * 60)

        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue

                cmd = command[0].lower()

                if cmd in ["quit", "exit", "q"]:
                    break
                elif cmd == "list":
                    await self.list_available_tools()
                elif cmd == "demo":
                    await self.run_demo_tests()
                elif cmd == "help":
                    print("\nCommands:")
                    print("  list                    - List available tools")
                    print("  call <tool> [params]    - Call a specific tool")
                    print(
                        "  demo                    - Run demo vulnerability tests"
                    )
                    print("  help                    - Show this help")
                    print("  quit/exit               - Exit")
                elif cmd == "call":
                    if len(command) < 2:
                        print(
                            "Usage: call <tool_name> [param1=value1] [param2=value2] ..."
                        )
                        continue

                    tool_name = command[1]
                    if tool_name not in tools:
                        print(
                            f"Tool '{tool_name}' not found. Use 'list' to see available tools."
                        )
                        continue

                    # Parse parameters
                    params = {}
                    for arg in command[2:]:
                        if "=" in arg:
                            key, value = arg.split("=", 1)
                            # Try to parse as JSON, otherwise treat as string
                            try:
                                params[key] = json.loads(value)
                            except:
                                params[key] = value

                    await self.call_tool(tool_name, **params)
                else:
                    print(
                        f"Unknown command: {cmd}. Type 'help' for available commands."
                    )

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python tool_runner.py <server_script> [mode]")
        print(
            "  server_script: Path to the MCP server script (e.g., vuln_mcp_stdio.py)"
        )
        print("  mode: 'interactive' (default) or 'demo'")
        print("\nExamples:")
        print("  python tool_runner.py vuln_mcp_stdio.py")
        print("  python tool_runner.py vuln_mcp_stdio.py demo")
        sys.exit(1)

    server_script = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "interactive"

    runner = MCPToolRunner()
    try:
        await runner.connect_to_server(server_script)

        if mode == "demo":
            await runner.run_demo_tests()
        else:
            await runner.interactive_mode()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
