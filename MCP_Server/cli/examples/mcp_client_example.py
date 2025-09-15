#!/usr/bin/env python3
"""
Example MCP Client for PII Sanitizer

This demonstrates how an LLM or application would interact with the MCP server
to use the sanitizer tools.
"""

import json
import subprocess
import sys
from pathlib import Path


class MCPClient:
    """Simple MCP client for demonstration purposes."""

    def __init__(self, server_script="vuln_mcp_stdio.py"):
        self.server_script = server_script
        self.server_process = None

    def start_server(self):
        """Start the MCP server process."""
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"MCP server started with PID: {self.server_process.pid}")
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
        return True

    def stop_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("MCP server stopped")

    def call_tool(self, tool_name, **kwargs):
        """Call a tool on the MCP server."""
        if not self.server_process:
            return {"error": "Server not started"}

        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": kwargs},
        }

        try:
            # Send request to server
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()

            # Read response
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return response
            else:
                return {"error": "No response from server"}

        except Exception as e:
            return {"error": f"Failed to call tool: {e}"}

    def list_tools(self):
        """List available tools."""
        if not self.server_process:
            return {"error": "Server not started"}

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        try:
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()

            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response from server"}

        except Exception as e:
            return {"error": f"Failed to list tools: {e}"}


def demonstrate_llm_usage():
    """Demonstrate how an LLM would use the MCP sanitizer tools."""

    print("=" * 80)
    print("LLM MCP CLIENT DEMONSTRATION")
    print("=" * 80)
    print()
    print("This simulates how an LLM would interact with the MCP server")
    print("to provide PII sanitization capabilities to users.")
    print()

    # Initialize MCP client
    client = MCPClient()

    if not client.start_server():
        print("Failed to start MCP server")
        return

    try:
        # Simulate LLM discovering available tools
        print("1. LLM discovers available tools:")
        print("-" * 40)
        tools_response = client.list_tools()
        if "result" in tools_response:
            tools = tools_response["result"]["tools"]
            sanitizer_tools = [
                t
                for t in tools
                if "sanitize" in t["name"] or "detect" in t["name"]
            ]
            for tool in sanitizer_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        print()

        # Simulate user asking LLM to sanitize text
        print(
            "2. User asks: 'Please sanitize this text: Contact john@example.com or call 555-123-4567'"
        )
        print("-" * 40)

        # LLM calls detect_pii first
        print("   LLM calls detect_pii tool...")
        detect_result = client.call_tool(
            "detect_pii", text="Contact john@example.com or call 555-123-4567"
        )
        if "result" in detect_result:
            detection = json.loads(
                detect_result["result"]["content"][0]["text"]
            )
            print(f"   PII detected: {detection['total_detections'] > 0}")
            print(
                f"   Categories: {[cat for cat, count in detection['categories'].items() if count > 0]}"
            )
        print()

        # LLM calls sanitize_text
        print("   LLM calls sanitize_text tool...")
        sanitize_result = client.call_tool(
            "sanitize_text",
            text="Contact john@example.com or call 555-123-4567",
            redaction_type="generic",
        )
        if "result" in sanitize_result:
            result = json.loads(sanitize_result["result"]["content"][0]["text"])
            print(f"   Sanitized text: {result['sanitized_text']}")
        print()

        # Simulate another user request
        print(
            "3. User asks: 'Mask the PII in this log file: test_data/log_with_pii.txt'"
        )
        print("-" * 40)

        # LLM calls sanitize_file
        print("   LLM calls sanitize_file tool...")
        file_result = client.call_tool(
            "sanitize_file",
            file_path="../PII_testing/test_data/log_with_pii.txt",
            redaction_type="mask",
        )
        if "result" in file_result:
            result = json.loads(file_result["result"]["content"][0]["text"])
            print(f"   Original file: {result['original_file']}")
            print(f"   Sanitized file: {result['sanitized_file']}")
            print(f"   PII detected: {result['pii_detected']}")
        print()

        print("4. LLM responds to user:")
        print("-" * 40)
        print("   'I've successfully sanitized your text and log file.'")
        print("   'The sensitive information has been masked while preserving'")
        print("   'the structure and readability of your content.'")

    finally:
        client.stop_server()

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("In a real scenario:")
    print("- The MCP server runs as a background service")
    print("- The LLM (Claude, GPT, etc.) connects to it automatically")
    print("- Users interact with the LLM, not the MCP server directly")
    print("- The LLM decides when and how to call the sanitizer tools")


if __name__ == "__main__":
    demonstrate_llm_usage()
