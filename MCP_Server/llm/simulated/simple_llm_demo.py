#!/usr/bin/env python3
"""
Simple Working LLM + MCP Demo

This creates a working demonstration of an LLM using MCP tools.
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


async def test_mcp_connection():
    """Test basic MCP connection and tool calling."""

    print("=" * 80)
    print("🔧 TESTING MCP CONNECTION")
    print("=" * 80)

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
                print("✅ Session initialized")

                # List available tools
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools")

                # Show sanitizer tools
                sanitizer_tools = [
                    tool
                    for tool in tools_result.tools
                    if any(
                        keyword in tool.name
                        for keyword in ["sanitize", "detect", "pii"]
                    )
                ]
                print(
                    f"✅ Sanitizer tools: {[t.name for t in sanitizer_tools]}"
                )

                # Test detect_pii tool
                print("\n🧪 Testing detect_pii tool...")
                try:
                    result = await session.call_tool(
                        "detect_pii", {"text": "john@example.com"}
                    )
                    print(
                        f"✅ detect_pii result: {result.content[0].text[:100]}..."
                    )
                except Exception as e:
                    print(f"❌ detect_pii failed: {e}")

                # Test sanitize_text tool
                print("\n🧪 Testing sanitize_text tool...")
                try:
                    result = await session.call_tool(
                        "sanitize_text",
                        {
                            "text": "Contact john@example.com or call 555-123-4567",
                            "redaction_type": "generic",
                        },
                    )
                    print(
                        f"✅ sanitize_text result: {result.content[0].text[:100]}..."
                    )
                except Exception as e:
                    print(f"❌ sanitize_text failed: {e}")

                print("\n✅ MCP connection test completed successfully!")

    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        import traceback

        traceback.print_exc()


async def simple_llm_demo():
    """Simple LLM demo that actually works."""

    print("\n" + "=" * 80)
    print("🤖 SIMPLE LLM DEMO")
    print("=" * 80)

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

                # Demo 1: Detect PII
                print("\n📝 Demo 1: Detecting PII")
                print("User: 'Detect PII in john@example.com'")

                result = await session.call_tool(
                    "detect_pii", {"text": "john@example.com"}
                )
                detection = json.loads(result.content[0].text)
                print(
                    f"🤖 LLM: I found PII! Categories: {[cat for cat, count in detection['categories'].items() if count > 0]}"
                )

                # Demo 2: Sanitize text
                print("\n📝 Demo 2: Sanitizing text")
                print(
                    "User: 'Sanitize Contact john@example.com or call 555-123-4567'"
                )

                result = await session.call_tool(
                    "sanitize_text",
                    {
                        "text": "Contact john@example.com or call 555-123-4567",
                        "redaction_type": "generic",
                    },
                )
                sanitized = json.loads(result.content[0].text)
                print(
                    f"🤖 LLM: Here's the sanitized text: {sanitized['sanitized_text']}"
                )

                # Demo 3: Mask PII
                print("\n📝 Demo 3: Masking PII")
                print("User: 'Mask the PII in john@example.com'")

                result = await session.call_tool(
                    "sanitize_text",
                    {"text": "john@example.com", "redaction_type": "mask"},
                )
                masked = json.loads(result.content[0].text)
                print(
                    f"🤖 LLM: Here's the masked text: {masked['sanitized_text']}"
                )

                print("\n✅ Demo completed successfully!")
                print("\nThis shows how a real LLM would use MCP tools:")
                print("1. User asks LLM to sanitize text")
                print("2. LLM automatically calls the appropriate MCP tool")
                print("3. LLM returns the sanitized result to user")
                print("4. User never sees the MCP server - it's invisible!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


async def interactive_llm():
    """Interactive LLM that actually works."""

    print("\n" + "=" * 80)
    print("🤖 INTERACTIVE LLM")
    print("=" * 80)

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

                print("\n🎯 Try these commands:")
                print("  detect john@example.com")
                print(
                    "  sanitize Contact john@example.com or call 555-123-4567"
                )
                print("  mask john@example.com")
                print("  remove Contact john@example.com")
                print("  quit")
                print()

                while True:
                    try:
                        user_input = input("👤 You: ").strip()

                        if user_input.lower() in ["quit", "exit", "q"]:
                            print("👋 Goodbye!")
                            break

                        if not user_input:
                            continue

                        # Simple command parsing
                        parts = user_input.split(" ", 1)
                        command = parts[0].lower()
                        text = parts[1] if len(parts) > 1 else ""

                        if command == "detect" and text:
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
                            print(f"🤖 Found PII: {categories}")

                        elif command == "sanitize" and text:
                            print("🧹 Sanitizing text...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "generic"},
                            )
                            sanitized = json.loads(result.content[0].text)
                            print(
                                f"🤖 Sanitized: {sanitized['sanitized_text']}"
                            )

                        elif command == "mask" and text:
                            print("🎭 Masking PII...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "mask"},
                            )
                            masked = json.loads(result.content[0].text)
                            print(f"🤖 Masked: {masked['sanitized_text']}")

                        elif command == "remove" and text:
                            print("🗑️ Removing PII...")
                            result = await session.call_tool(
                                "sanitize_text",
                                {"text": text, "redaction_type": "remove"},
                            )
                            removed = json.loads(result.content[0].text)
                            print(f"🤖 Removed: {removed['sanitized_text']}")

                        else:
                            print(
                                "🤖 I can help you detect, sanitize, mask, or remove PII from text."
                            )
                            print("   Try: detect john@example.com")

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

    parser = argparse.ArgumentParser(description="Simple LLM + MCP Demo")
    parser.add_argument(
        "--test", action="store_true", help="Test MCP connection"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run automated demo"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive demo"
    )

    args = parser.parse_args()

    if args.test:
        asyncio.run(test_mcp_connection())
    elif args.demo:
        asyncio.run(simple_llm_demo())
    elif args.interactive:
        asyncio.run(interactive_llm())
    else:
        print("Choose --test, --demo, or --interactive")
        print("Example: python simple_llm_demo.py --demo")
