#!/usr/bin/env python3
"""
Auto-detect PII without relying on Gemini for decision making.
This version always calls detect_pii first, then uses Gemini for interpretation.
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


class AutoDetectGeminiMCP:
    """Auto-detect PII without relying on Gemini for decision making."""

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

    async def detect_pii(self, text):
        """Always call detect_pii tool first."""
        try:
            # Calculate correct path to MCP server
            mcp_server_path = (
                Path(__file__).parent.parent.parent
                / "core"
                / "server"
                / "vuln_mcp_stdio.py"
            )
            server_params = StdioServerParameters(
                command="python",
                args=[str(mcp_server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)},
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Always call detect_pii first
                    result = await session.call_tool(
                        "detect_pii", {"text": text}
                    )

                    if result.content:
                        return json.loads(result.content[0].text)
                    return None

        except Exception as e:
            print(f"❌ Error calling MCP tool: {e}")
            return None

    async def sanitize_text(self, text, redaction_type="generic"):
        """Sanitize text using MCP tools."""
        try:
            # Calculate correct path to MCP server
            mcp_server_path = (
                Path(__file__).parent.parent.parent
                / "core"
                / "server"
                / "vuln_mcp_stdio.py"
            )
            server_params = StdioServerParameters(
                command="python",
                args=[str(mcp_server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)},
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Call sanitize_text tool
                    result = await session.call_tool(
                        "sanitize_text",
                        {"text": text, "redaction_type": redaction_type},
                    )

                    if result.content:
                        return json.loads(result.content[0].text)
                    return None

        except Exception as e:
            print(f"❌ Error calling MCP tool: {e}")
            return None

    async def process_request(self, user_input):
        """Process a user request with auto-detection."""
        print(f"\n👤 User: {user_input}")

        # Always detect PII first
        print("🔍 Auto-detecting PII...")
        pii_result = await self.detect_pii(user_input)

        if pii_result:
            print(f"📊 PII Detection Results:")
            print(f"   Total detections: {pii_result['total_detections']}")
            print(f"   Categories: {pii_result['categories']}")
            if pii_result["total_detections"] > 0:
                print(f"   Details: {pii_result['detailed_findings']}")

            # Ask Gemini to interpret the results
            interpretation_prompt = f"""
The user provided this text: {user_input}

I ran it through a PII detection tool and found:
- Total detections: {pii_result['total_detections']}
- Categories: {pii_result['categories']}
- Details: {pii_result['detailed_findings']}

Please provide a helpful response explaining what PII was found and what the user should know about it.
"""
            interpretation = self.ask_gemini(interpretation_prompt)
            print(f"🤖 Gemini: {interpretation}")
        else:
            print("❌ Failed to detect PII")

        print()


async def interactive_mode():
    """Interactive mode - keep running and accept user input."""
    print("=" * 80)
    print("🤖 AUTO-DETECT GEMINI + MCP SANITIZER")
    print("=" * 80)
    print()
    print("This always detects PII first, then uses Gemini for interpretation.")
    print("Commands:")
    print("  - Type any text to analyze it")
    print("  - Type 'quit' or 'exit' to stop")
    print()

    try:
        # Initialize Gemini
        gemini = AutoDetectGeminiMCP()
        print("✅ Auto-detect system initialized successfully!")
        print()

        while True:
            try:
                user_input = input(
                    "👤 Enter text to analyze (or 'quit'): "
                ).strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                # Process the request
                await gemini.process_request(user_input)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(interactive_mode())
