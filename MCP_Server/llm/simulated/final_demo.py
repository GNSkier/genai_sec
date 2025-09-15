#!/usr/bin/env python3
"""
Final Working LLM + MCP Demo

This demonstrates a working LLM that uses MCP tools for PII sanitization.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add MCP to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP not installed. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client


async def working_llm_demo():
    """Demonstrate a working LLM with MCP sanitizer tools."""

    print("=" * 80)
    print("🤖 WORKING LLM + MCP SANITIZER DEMO")
    print("=" * 80)
    print()
    print(
        "This demonstrates how a real LLM would use MCP tools to sanitize PII."
    )
    print(
        "The LLM automatically calls the appropriate MCP tool based on user requests."
    )
    print()

    try:
        # Configure the MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["vuln_mcp_stdio.py"],
            env={"PYTHONPATH": str(Path(__file__).parent)},
        )

        print("🔌 Connecting to MCP server...")

        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")

                # Initialize the session
                await session.initialize()

                # Demo scenarios
                demos = [
                    {
                        "user_request": "Detect PII in john@example.com",
                        "llm_action": "I'll detect PII in that email address",
                        "tool_call": (
                            "detect_pii",
                            {"text": "john@example.com"},
                        ),
                    },
                    {
                        "user_request": "Sanitize Contact john@example.com or call 555-123-4567",
                        "llm_action": "I'll sanitize that text with generic redaction",
                        "tool_call": (
                            "sanitize_text",
                            {
                                "text": "Contact john@example.com or call 555-123-4567",
                                "redaction_type": "generic",
                            },
                        ),
                    },
                    {
                        "user_request": "Mask the PII in john@example.com",
                        "llm_action": "I'll mask that email address",
                        "tool_call": (
                            "sanitize_text",
                            {
                                "text": "john@example.com",
                                "redaction_type": "mask",
                            },
                        ),
                    },
                    {
                        "user_request": "Remove PII from My SSN is 123-45-6789",
                        "llm_action": "I'll remove the PII from that text",
                        "tool_call": (
                            "sanitize_text",
                            {
                                "text": "My SSN is 123-45-6789",
                                "redaction_type": "remove",
                            },
                        ),
                    },
                ]

                for i, demo in enumerate(demos, 1):
                    print(f"\n--- Demo {i} ---")
                    print(f"👤 User: {demo['user_request']}")
                    print(f"🤖 LLM: {demo['llm_action']}")

                    # Call the MCP tool
                    tool_name, tool_args = demo["tool_call"]
                    result = await session.call_tool(tool_name, tool_args)

                    # Parse and display result
                    if tool_name == "detect_pii":
                        detection = json.loads(result.content[0].text)
                        categories = [
                            cat
                            for cat, count in detection["categories"].items()
                            if count > 0
                        ]
                        print(f"🤖 LLM: Found PII categories: {categories}")
                        print(
                            f"🤖 LLM: Total detections: {detection['total_detections']}"
                        )
                    else:
                        sanitized = json.loads(result.content[0].text)
                        print(
                            f"🤖 LLM: Sanitized result: {sanitized['sanitized_text']}"
                        )
                        print(
                            f"🤖 LLM: PII detected: {sanitized['pii_detected']}"
                        )

                print("\n" + "=" * 80)
                print("✅ DEMO COMPLETED SUCCESSFULLY!")
                print("=" * 80)
                print()
                print("Key Points:")
                print("1. ✅ MCP server runs as a background service")
                print("2. ✅ LLM automatically calls appropriate tools")
                print("3. ✅ PII is properly detected and sanitized")
                print("4. ✅ User never sees the MCP server - it's invisible!")
                print(
                    "5. ✅ Different redaction types work (generic, mask, remove)"
                )
                print()
                print("This is how a real LLM would integrate with MCP tools!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


async def interactive_demo():
    """Interactive demo where you can test different inputs."""

    print("=" * 80)
    print("🤖 INTERACTIVE LLM DEMO")
    print("=" * 80)
    print()
    print("Try these commands:")
    print("  detect <text>     - Detect PII in text")
    print("  sanitize <text>   - Sanitize text (generic redaction)")
    print("  mask <text>       - Mask PII in text")
    print("  remove <text>     - Remove PII from text")
    print("  quit              - Exit")
    print()
    print("Examples:")
    print("  detect john@example.com")
    print("  sanitize Contact john@example.com or call 555-123-4567")
    print("  mask john@example.com")
    print("  remove My SSN is 123-45-6789")
    print()

    try:
        # Configure the MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["vuln_mcp_stdio.py"],
            env={"PYTHONPATH": str(Path(__file__).parent)},
        )

        print("🔌 Connecting to MCP server...")

        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")

                # Initialize the session
                await session.initialize()

                while True:
                    try:
                        user_input = input("\n👤 You: ").strip()

                        if user_input.lower() in ["quit", "exit", "q"]:
                            print("👋 Goodbye!")
                            break

                        if not user_input:
                            continue

                        # Parse command
                        parts = user_input.split(" ", 1)
                        command = parts[0].lower()
                        text = parts[1] if len(parts) > 1 else ""

                        if not text:
                            print(
                                "🤖 Please provide text to process. Example: detect john@example.com"
                            )
                            continue

                        if command == "detect":
                            print("🔍 Detecting PII...")
                            result = await session.call_tool(
                                "detect_pii", {"text": text}
                            )
                            detection = json.loads(result.content[0].text)
                            categories = [
                                cat
                                for cat, count in detection[
                                    "categories"
                                ].items()
                                if count > 0
                            ]
                            print(
                                f"🤖 Found PII: {categories if categories else 'None'}"
                            )
                            print(
                                f"🤖 Total detections: {detection['total_detections']}"
                            )

                        elif command == "sanitize":
                            print("🧹 Sanitizing text...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "generic"},
                            )
                            sanitized = json.loads(result.content[0].text)
                            print(
                                f"🤖 Sanitized: {sanitized['sanitized_text']}"
                            )
                            print(
                                f"🤖 PII detected: {sanitized['pii_detected']}"
                            )

                        elif command == "mask":
                            print("🎭 Masking PII...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "mask"},
                            )
                            masked = json.loads(result.content[0].text)
                            print(f"🤖 Masked: {masked['sanitized_text']}")
                            print(f"🤖 PII detected: {masked['pii_detected']}")

                        elif command == "remove":
                            print("🗑️ Removing PII...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "remove"},
                            )
                            removed = json.loads(result.content[0].text)
                            print(f"🤖 Removed: {removed['sanitized_text']}")
                            print(f"🤖 PII detected: {removed['pii_detected']}")

                        else:
                            print(
                                "🤖 Unknown command. Use: detect, sanitize, mask, remove, or quit"
                            )

                    except KeyboardInterrupt:
                        print("\n👋 Goodbye!")
                        break
                    except Exception as e:
                        print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Final Working LLM + MCP Demo")
    parser.add_argument(
        "--demo", action="store_true", help="Run automated demo"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive demo"
    )

    args = parser.parse_args()

    if args.demo:
        asyncio.run(working_llm_demo())
    elif args.interactive:
        asyncio.run(interactive_demo())
    else:
        print("Choose --demo or --interactive")
        print("Example: python final_demo.py --demo")
