#!/usr/bin/env python3
"""
Simple Gemini LLM Integration with MCP Sanitizer

This uses the same pattern as the working demo but with Gemini LLM.
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


class SimpleGeminiMCP:
    """Simple Gemini LLM with MCP integration."""

    def __init__(self):
        """Initialize Gemini."""
        # Get API key
        api_key = os.getenv("GCP_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Please set GCP_KEY or GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def ask_gemini(self, prompt):
        """Ask Gemini a question."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini error: {e}"

    def extract_tool_call(self, response):
        """Extract tool call from Gemini response."""
        if "TOOL_CALL:" in response:
            lines = response.split("\n")
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
                        pass

            return tool_name, arguments
        return None, {}


async def simple_gemini_demo():
    """Simple demo using Gemini + MCP."""

    print("=" * 80)
    print("🤖 SIMPLE GEMINI + MCP DEMO")
    print("=" * 80)
    print()
    print("This uses Gemini to decide which MCP tools to call.")
    print()

    try:
        # Initialize Gemini
        gemini = SimpleGeminiMCP()

        # Demo requests
        demo_requests = [
            "Detect PII in john@example.com",
            "Sanitize Contact john@example.com or call 555-123-4567",
            "Mask the PII in john@example.com",
            "Remove PII from My SSN is 123-45-6789",
        ]

        print("🎬 Running Simple Gemini + MCP demo...")
        print()

        for i, request in enumerate(demo_requests, 1):
            print(f"--- Demo {i} ---")
            print(f"👤 User: {request}")

            # Ask Gemini what to do
            system_prompt = """You are a helpful AI assistant with access to PII sanitization tools.

Available tools:
- detect_pii(text): Detect PII in text
- sanitize_text(text, redaction_type): Sanitize text (redaction_type: generic, mask, remove)
- get_sanitization_report(text): Get detailed PII report
- sanitize_file(file_path, redaction_type): Sanitize file content

IMPORTANT: Always call detect_pii tool for ANY text that might contain:
- Dates (9/27, Friday, weekend, etc.)
- Locations (LA, cities, addresses)
- Names (Grant Nitta, etc.)
- Times (morning, evening, etc.)
- Any other potentially sensitive information

When users ask you to:
- "detect PII" or "check for PII" → use detect_pii tool
- "sanitize" or "redact" → use sanitize_text with generic redaction
- "mask" → use sanitize_text with mask redaction  
- "remove PII" → use sanitize_text with remove redaction
- "sanitize file" → use sanitize_file tool

ALWAYS call detect_pii first to check for PII, even if you think there might not be any.

Format your response as:
TOOL_CALL: tool_name
ARGUMENTS: {"arg1": "value1", "arg2": "value2"}"""

            prompt = f"{system_prompt}\n\nUser request: {request}\n\nWhat tool should I call and with what arguments?"

            gemini_response = gemini.ask_gemini(prompt)
            print(f"🤖 Gemini: {gemini_response}")

            # Extract tool call
            tool_name, arguments = gemini.extract_tool_call(gemini_response)

            if tool_name and arguments:
                print(
                    f"🔧 Gemini wants to call: {tool_name} with args: {arguments}"
                )

                # Now call the MCP tool using the same pattern as working demo
                try:
                    server_params = StdioServerParameters(
                        command="python",
                        args=[
                            str(
                                Path(__file__).parent.parent.parent
                                / "core"
                                / "server"
                                / "vuln_mcp_stdio.py"
                            )
                        ],
                        env={
                            "PYTHONPATH": str(
                                Path(__file__).parent.parent.parent
                            )
                        },
                    )

                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()

                            # Call the tool
                            result = await session.call_tool(
                                tool_name, arguments
                            )

                            if result.content:
                                tool_result = result.content[0].text
                                print(f"📄 MCP Tool Result: {tool_result}")

                                # Ask Gemini to interpret the result
                                interpretation_prompt = f"""
The user asked: {request}
I called tool {tool_name} and got this result: {tool_result}

Please provide a helpful response to the user explaining what was found/done.
"""
                                interpretation = gemini.ask_gemini(
                                    interpretation_prompt
                                )
                                print(f"🤖 Gemini: {interpretation}")
                            else:
                                print("❌ No result from MCP tool")
                    print()

                except Exception as e:
                    print(f"❌ Error calling MCP tool: {e}")
                    print()
            else:
                # Gemini decided no tool was needed - this is normal behavior
                print(
                    "✅ Gemini determined no PII detection/sanitization needed"
                )
                print(
                    "🤖 Gemini: No sensitive information detected in the provided text."
                )
                print()

        print("✅ Simple Gemini + MCP demo completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(simple_gemini_demo())
