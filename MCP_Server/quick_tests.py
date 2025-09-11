#!/usr/bin/env python3
"""
Quick vulnerability tests - predefined tool combinations for easy testing.
"""

import asyncio
import sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class QuickTester:
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

    async def call_tool(self, tool_name: str, **kwargs):
        """Call a specific tool with given parameters."""
        try:
            result = await self.session.call_tool(tool_name, kwargs)
            content = getattr(result, "content", result)
            return content
        except Exception as e:
            print(f"❌ Error calling {tool_name}: {e}")
            return None

    async def test_sql_injection(self):
        """Test SQL injection vulnerabilities."""
        print("\n🔍 Testing SQL Injection...")

        # Basic injection
        result = await self.call_tool(
            "insert_record",
            name="hacker');--",
            address="123 Evil St",
            email="hack@evil.com",
        )
        print(f"  Basic injection: {result}")

        # Union injection
        result = await self.call_tool(
            "execute_sql",
            query="SELECT * FROM records UNION SELECT 1, 'PWNED', 'PWNED', 'PWNED', 'PWNED'",
        )
        print(f"  Union injection: {result}")

    async def test_file_access(self):
        """Test file system access vulnerabilities."""
        print("\n🔍 Testing File Access...")

        # Read current file
        result = await self.call_tool(
            "read_file", file_path="vuln_mcp_stdio.py"
        )
        print(f"  Read current file: {len(str(result))} characters")

        # List directory
        result = await self.call_tool("list_directory", path=".")
        print(f"  List directory: {result}")

    async def test_command_execution(self):
        """Test command execution vulnerabilities."""
        print("\n🔍 Testing Command Execution...")

        # Basic command
        result = await self.call_tool("execute_command", command="whoami")
        print(f"  Whoami: {result}")

        # List processes
        result = await self.call_tool("list_processes")
        print(f"  Process count: {len(str(result).split('PID:')) - 1}")

    async def test_network_attacks(self):
        """Test network-based attacks."""
        print("\n🔍 Testing Network Attacks...")

        # External request
        result = await self.call_tool(
            "make_request", url="http://httpbin.org/get"
        )
        print(
            f"  External request: {'Success' if 'Status: 200' in str(result) else 'Failed'}"
        )

        # Port scan
        result = await self.call_tool("scan_port", host="127.0.0.1", port=80)
        print(f"  Port 80 scan: {result}")

    async def test_environment_exposure(self):
        """Test environment variable exposure."""
        print("\n🔍 Testing Environment Exposure...")

        # Get specific variables
        result = await self.call_tool("get_env_variable", var_name="USER")
        print(f"  USER: {result}")

        result = await self.call_tool("get_env_variable", var_name="PATH")
        print(f"  PATH: {str(result)[:100]}...")

    async def test_system_info(self):
        """Test system information exposure."""
        print("\n🔍 Testing System Information...")

        result = await self.call_tool("get_system_info")
        print(f"  System info: {len(str(result))} characters")

    async def test_crypto_weaknesses(self):
        """Test cryptographic weaknesses."""
        print("\n🔍 Testing Cryptographic Weaknesses...")

        # Weak hash
        result = await self.call_tool(
            "generate_hash", data="test", algorithm="md5"
        )
        print(f"  MD5 hash: {result}")

        # Weak token
        result = await self.call_tool("generate_token", length=8)
        print(f"  Random token: {result}")

    async def run_all_tests(self):
        """Run all vulnerability tests."""
        print("🚀 Running All Vulnerability Tests")
        print("=" * 60)

        await self.test_sql_injection()
        await self.test_file_access()
        await self.test_command_execution()
        await self.test_network_attacks()
        await self.test_environment_exposure()
        await self.test_system_info()
        await self.test_crypto_weaknesses()

        print("\n✅ All tests completed!")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python quick_tests.py <server_script> [test_type]")
        print("  server_script: Path to the MCP server script")
        print(
            "  test_type: 'all', 'sql', 'file', 'command', 'network', 'env', 'system', 'crypto'"
        )
        print("\nExamples:")
        print("  python quick_tests.py vuln_mcp_stdio.py all")
        print("  python quick_tests.py vuln_mcp_stdio.py sql")
        sys.exit(1)

    server_script = sys.argv[1]
    test_type = sys.argv[2] if len(sys.argv) > 2 else "all"

    tester = QuickTester()
    try:
        await tester.connect_to_server(server_script)

        if test_type == "all":
            await tester.run_all_tests()
        elif test_type == "sql":
            await tester.test_sql_injection()
        elif test_type == "file":
            await tester.test_file_access()
        elif test_type == "command":
            await tester.test_command_execution()
        elif test_type == "network":
            await tester.test_network_attacks()
        elif test_type == "env":
            await tester.test_environment_exposure()
        elif test_type == "system":
            await tester.test_system_info()
        elif test_type == "crypto":
            await tester.test_crypto_weaknesses()
        else:
            print(f"Unknown test type: {test_type}")
            print(
                "Available: all, sql, file, command, network, env, system, crypto"
            )

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
