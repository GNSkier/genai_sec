#!/usr/bin/env python3
"""
Demo script showing how to use the PII Sanitizer through MCP tools

This script demonstrates calling the sanitizer tools through the MCP server.
"""

import json
import subprocess
import sys
from pathlib import Path


def call_mcp_tool(tool_name, **kwargs):
    """Call an MCP tool and return the result."""
    # This is a simplified example - in practice you'd use an MCP client
    # For this demo, we'll simulate the tool calls by importing and calling directly

    # Import the sanitizer agent directly for demo purposes
    sys.path.insert(0, str(Path(__file__).parent))
    from sanitizer_agent import SanitizerAgent

    agent = SanitizerAgent()

    if tool_name == "detect_pii":
        result = agent.detect_pii(kwargs["text"])
        return json.dumps(result, indent=2)

    elif tool_name == "sanitize_text":
        result = agent.sanitize_text(
            kwargs["text"], kwargs.get("redaction_type", "generic")
        )
        return json.dumps(result, indent=2)

    elif tool_name == "get_sanitization_report":
        result = agent.get_sanitization_report(kwargs["text"])
        return json.dumps(result, indent=2)

    elif tool_name == "sanitize_file":
        with open(
            kwargs["file_path"], "r", encoding="utf-8", errors="ignore"
        ) as f:
            content = f.read()

        result = agent.sanitize_text(
            content, kwargs.get("redaction_type", "generic")
        )

        # Write sanitized content to a new file
        sanitized_path = kwargs["file_path"] + ".sanitized"
        with open(sanitized_path, "w", encoding="utf-8") as f:
            f.write(result["sanitized_text"])

        return json.dumps(
            {
                "original_file": kwargs["file_path"],
                "sanitized_file": sanitized_path,
                "pii_detected": result["pii_detected"],
                "detection_summary": result["detection_summary"],
            },
            indent=2,
        )

    else:
        return f"Unknown tool: {tool_name}"


def demo_mcp_sanitizer():
    """Demonstrate MCP sanitizer tools."""

    print("=" * 80)
    print("MCP PII SANITIZER DEMO")
    print("=" * 80)

    # Sample text with PII
    sample_text = """
    User Login Report:
    =================
    
    User: John Smith (john.smith@example.com)
    Phone: 555-123-4567
    SSN: 123-45-6789
    Credit Card: 4532-1234-5678-9012
    Address: 123 Main Street, Anytown, ST 12345
    
    Login Time: 2024-01-15 10:30:00
    IP Address: 192.168.1.100
    
    Transaction Details:
    - Amount: $99.99
    - Card Expiry: 12/26
    - CVV: 123
    """

    print("1. DETECT PII")
    print("-" * 40)
    print("Calling detect_pii tool...")
    result = call_mcp_tool("detect_pii", text=sample_text)
    print("Result:")
    print(result)
    print()

    print("2. GET SANITIZATION REPORT")
    print("-" * 40)
    print("Calling get_sanitization_report tool...")
    result = call_mcp_tool("get_sanitization_report", text=sample_text)
    print("Result:")
    print(result)
    print()

    print("3. SANITIZE TEXT (GENERIC REDACTION)")
    print("-" * 40)
    print("Calling sanitize_text tool with generic redaction...")
    result = call_mcp_tool(
        "sanitize_text", text=sample_text, redaction_type="generic"
    )
    print("Result:")
    print(result)
    print()

    print("4. SANITIZE TEXT (MASK REDACTION)")
    print("-" * 40)
    print("Calling sanitize_text tool with mask redaction...")
    result = call_mcp_tool(
        "sanitize_text", text=sample_text, redaction_type="mask"
    )
    print("Result:")
    print(result)
    print()

    print("5. SANITIZE TEXT (REMOVE REDACTION)")
    print("-" * 40)
    print("Calling sanitize_text tool with remove redaction...")
    result = call_mcp_tool(
        "sanitize_text", text=sample_text, redaction_type="remove"
    )
    print("Result:")
    print(result)
    print()

    print("6. SANITIZE FILE")
    print("-" * 40)

    # Create a test file
    test_file = "test_user_data.txt"
    with open(test_file, "w") as f:
        f.write(sample_text)

    print(f"Created test file: {test_file}")
    print("Calling sanitize_file tool...")
    result = call_mcp_tool(
        "sanitize_file", file_path=test_file, redaction_type="generic"
    )
    print("Result:")
    print(result)

    # Clean up
    import os

    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(test_file + ".sanitized"):
        os.remove(test_file + ".sanitized")
    print("Test files cleaned up.")

    print("\n" + "=" * 80)
    print("MCP SANITIZER DEMO COMPLETED!")
    print("=" * 80)


def show_mcp_server_usage():
    """Show how to use the MCP server with sanitizer tools."""

    print("\n" + "=" * 80)
    print("USING THE MCP SERVER")
    print("=" * 80)

    print("To use the sanitizer through the MCP server, you can:")
    print()
    print("1. Start the STDIO server:")
    print("   python vuln_mcp_stdio.py")
    print()
    print("2. Start the SSE server:")
    print("   python vuln_mcp_sse.py")
    print("   (Server will be available at http://localhost:9000)")
    print()
    print("3. Available sanitizer tools:")
    print("   - detect_pii(text: str) -> str")
    print("   - sanitize_text(text: str, redaction_type: str) -> str")
    print("   - get_sanitization_report(text: str) -> str")
    print("   - sanitize_file(file_path: str, redaction_type: str) -> str")
    print()
    print("4. Redaction types:")
    print("   - 'generic': Replace with [REDACTED_*] tags")
    print("   - 'mask': Partially mask the data (e.g., j***@e***.com)")
    print("   - 'remove': Completely remove the PII")
    print()
    print("5. Example MCP client usage:")
    print("   # Detect PII")
    print(
        "   result = mcp_client.call_tool('detect_pii', {'text': 'Contact john@example.com'})"
    )
    print()
    print("   # Sanitize text")
    print("   result = mcp_client.call_tool('sanitize_text', {")
    print("       'text': 'Contact john@example.com',")
    print("       'redaction_type': 'generic'")
    print("   })")


if __name__ == "__main__":
    try:
        demo_mcp_sanitizer()
        show_mcp_server_usage()
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
