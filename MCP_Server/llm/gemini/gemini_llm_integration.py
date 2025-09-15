#!/usr/bin/env python3
"""
Gemini LLM Integration with MCP Sanitizer

This integrates Google's Gemini LLM with our MCP sanitizer tools.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add MCP to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import google.generativeai as genai
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Installing required packages...")
    import subprocess

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "google-generativeai",
            "mcp",
            "python-dotenv",
        ]
    )
    import google.generativeai as genai
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Load .env from the master directory (parent of MCP_Server)
    master_dir = Path(__file__).parent.parent.parent.parent
    env_path = master_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
except ImportError:
    print(
        "⚠️  python-dotenv not installed, using system environment variables only"
    )


class GeminiLLMWithMCP:
    """Gemini LLM integrated with MCP sanitizer tools."""

    def __init__(self, api_key=None):
        """Initialize Gemini with API key."""
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Try to get from environment variables
            # First try GCP_KEY from .env file, then fallback to GEMINI_API_KEY
            api_key = os.getenv("GCP_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Please provide GCP_KEY or GEMINI_API_KEY environment variable, or pass api_key parameter"
                )
            genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.mcp_session = None
        self.available_tools = {}

    async def connect_to_mcp(self):
        """Connect to the MCP sanitizer server."""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["vuln_mcp_stdio.py"],
                env={"PYTHONPATH": str(Path(__file__).parent)},
            )

            print("🔌 Connecting to MCP server...")
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.mcp_session = session
                    await session.initialize()

                    # Get available tools
                    tools_result = await session.list_tools()
                    self.available_tools = {
                        tool.name: tool for tool in tools_result.tools
                    }

                    print("✅ Connected to MCP server")
                    print(
                        f"✅ Available tools: {list(self.available_tools.keys())}"
                    )
                    return True

        except Exception as e:
            print(f"❌ Failed to connect to MCP: {e}")
            return False

    async def call_mcp_tool(self, tool_name, arguments):
        """Call an MCP tool."""
        if not self.mcp_session or tool_name not in self.available_tools:
            return None

        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            if result.content:
                return result.content[0].text
            return None
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            import traceback

            traceback.print_exc()
            return None

    def create_system_prompt(self):
        """Create system prompt for Gemini with MCP tools."""
        return """You are a helpful AI assistant with access to PII sanitization tools.

Available tools:
- detect_pii(text): Detect PII in text
- sanitize_text(text, redaction_type): Sanitize text (redaction_type: generic, mask, remove)
- get_sanitization_report(text): Get detailed PII report
- sanitize_file(file_path, redaction_type): Sanitize file content

When users ask you to:
- "detect PII" or "check for PII" → use detect_pii tool
- "sanitize" or "redact" → use sanitize_text with generic redaction
- "mask" → use sanitize_text with mask redaction  
- "remove PII" → use sanitize_text with remove redaction
- "sanitize file" → use sanitize_file tool

Always call the appropriate tool and explain what you found/did.

Format your tool calls as:
TOOL_CALL: tool_name
ARGUMENTS: {"arg1": "value1", "arg2": "value2"}

Then I'll execute the tool and give you the result."""

    async def process_user_request(self, user_input):
        """Process user request using Gemini + MCP tools."""
        print(f"\n👤 User: {user_input}")

        # Create conversation with system prompt
        system_prompt = self.create_system_prompt()

        # Ask Gemini what to do
        prompt = f"{system_prompt}\n\nUser request: {user_input}\n\nWhat tool should I call and with what arguments?"

        try:
            response = self.model.generate_content(prompt)
            print(f"🤖 Gemini: {response.text}")

            # Parse Gemini's response for tool calls
            if "TOOL_CALL:" in response.text:
                lines = response.text.split("\n")
                tool_name = None
                arguments = {}

                for line in lines:
                    if line.startswith("TOOL_CALL:"):
                        tool_name = line.split(":", 1)[1].strip()
                    elif line.startswith("ARGUMENTS:"):
                        try:
                            args_str = line.split(":", 1)[1].strip()
                            arguments = json.loads(args_str)
                        except:
                            print("❌ Could not parse arguments")

                if tool_name and arguments:
                    print(
                        f"🔧 Calling tool: {tool_name} with args: {arguments}"
                    )
                    result = await self.call_mcp_tool(tool_name, arguments)

                    if result:
                        print(f"📄 Tool result: {result[:200]}...")

                        # Ask Gemini to interpret the result
                        interpretation_prompt = f"""
The user asked: {user_input}
I called tool {tool_name} and got this result: {result}

Please provide a helpful response to the user explaining what was found/done.
"""
                        interpretation = self.model.generate_content(
                            interpretation_prompt
                        )
                        print(f"🤖 Gemini: {interpretation.text}")
                        return interpretation.text
                    else:
                        return "❌ Tool call failed"
                else:
                    return "❌ Could not determine tool to call"
            else:
                return response.text

        except Exception as e:
            print(f"❌ Error with Gemini: {e}")
            return f"❌ Error: {e}"


async def gemini_demo():
    """Demo Gemini LLM with MCP tools."""

    print("=" * 80)
    print("🤖 GEMINI LLM + MCP SANITIZER DEMO")
    print("=" * 80)
    print()
    print(
        "This uses Google's Gemini LLM to intelligently decide which MCP tools to call."
    )
    print()

    # Check for API key
    api_key = os.getenv("GCP_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GCP_KEY or GEMINI_API_KEY environment variable")
        print(
            "   Get your API key from: https://makersuite.google.com/app/apikey"
        )
        print(
            "   Add GCP_KEY=your-api-key-here to .env file in master directory"
        )
        print("   Or run: export GEMINI_API_KEY='your-api-key-here'")
        return

    try:
        # Initialize Gemini LLM
        llm = GeminiLLMWithMCP()

        # Connect to MCP
        if not await llm.connect_to_mcp():
            return

        # Demo requests
        demo_requests = [
            "Detect PII in john@example.com",
            "Sanitize Contact john@example.com or call 555-123-4567",
            "Mask the PII in john@example.com",
            "Remove PII from My SSN is 123-45-6789",
        ]

        print("🎬 Running Gemini + MCP demo...")
        print()

        for i, request in enumerate(demo_requests, 1):
            print(f"--- Demo {i} ---")
            response = await llm.process_user_request(request)
            print()

        print("✅ Gemini + MCP demo completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


async def interactive_gemini():
    """Interactive Gemini LLM demo."""

    print("=" * 80)
    print("🤖 INTERACTIVE GEMINI + MCP")
    print("=" * 80)
    print()
    print("Chat with Gemini! It can intelligently use PII sanitization tools.")
    print("Try: 'Detect PII in john@example.com' or 'Sanitize my email'")
    print("Type 'quit' to exit")
    print()

    # Check for API key
    api_key = os.getenv("GCP_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GCP_KEY or GEMINI_API_KEY environment variable")
        print(
            "   Add GCP_KEY=your-api-key-here to .env file in master directory"
        )
        return

    try:
        # Initialize Gemini LLM
        llm = GeminiLLMWithMCP()

        # Connect to MCP
        if not await llm.connect_to_mcp():
            return

        print("✅ Ready! Ask me anything about PII sanitization.")
        print()

        while True:
            try:
                user_input = input("👤 You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                # Process with Gemini + MCP
                response = await llm.process_user_request(user_input)

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

    parser = argparse.ArgumentParser(description="Gemini LLM + MCP Integration")
    parser.add_argument(
        "--demo", action="store_true", help="Run automated demo"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive demo"
    )

    args = parser.parse_args()

    if args.demo:
        asyncio.run(gemini_demo())
    elif args.interactive:
        asyncio.run(interactive_gemini())
    else:
        print("Choose --demo or --interactive")
        print(
            "Don't forget to set GCP_KEY in .env file or GEMINI_API_KEY environment variable!"
        )
        print("Example: Add GCP_KEY=your-key to .env file in master directory")
        print(
            "Or: export GEMINI_API_KEY='your-key' && python gemini_llm_integration.py --demo"
        )
