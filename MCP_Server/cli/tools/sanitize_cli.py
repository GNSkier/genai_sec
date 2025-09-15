#!/usr/bin/env python3
"""
Simple CLI for Gemini + MCP Sanitizer

Easy-to-use command line interface for PII sanitization.
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
except ImportError:
    pass


class SanitizerCLI:
    """Simple CLI for PII sanitization."""

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

    async def sanitize_text(self, text, redaction_type="generic"):
        """Sanitize text using MCP tools."""
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
            print(f"❌ Error: {e}")
            return None

    async def detect_pii(self, text):
        """Detect PII in text using MCP tools."""
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
                env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)},
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Call detect_pii tool
                    result = await session.call_tool(
                        "detect_pii", {"text": text}
                    )

                    if result.content:
                        return json.loads(result.content[0].text)
                    return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    async def sanitize_file(self, file_path, redaction_type="generic"):
        """Sanitize file using MCP tools."""
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
                env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)},
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Call sanitize_file tool
                    result = await session.call_tool(
                        "sanitize_file",
                        {
                            "file_path": file_path,
                            "redaction_type": redaction_type,
                        },
                    )

                    if result.content:
                        return json.loads(result.content[0].text)
                    return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None


def print_usage():
    """Print usage information."""
    print(
        """
🤖 PII Sanitizer CLI

Usage:
  python sanitize_cli.py <command> [options] <input>

Commands:
  detect <text>                    Detect PII in text
  sanitize <text> [--type TYPE]    Sanitize text (default: generic)
  file <path> [--type TYPE]        Sanitize file (default: generic)

Redaction Types:
  generic    - Replace with [REDACTED_EMAIL], etc.
  mask       - Replace with j***@e***.c***, etc.
  remove     - Remove PII completely

Examples:
  python sanitize_cli.py detect "john@example.com"
  python sanitize_cli.py sanitize "Contact john@example.com"
  python sanitize_cli.py sanitize "Contact john@example.com" --type mask
  python sanitize_cli.py file /path/to/file.txt
  python sanitize_cli.py file /path/to/file.txt --type remove
"""
    )


async def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command in ["help", "-h", "--help"]:
        print_usage()
        return

    try:
        cli = SanitizerCLI()
    except ValueError as e:
        print(f"❌ {e}")
        print(
            "Please set GCP_KEY in .env file or GEMINI_API_KEY environment variable"
        )
        return

    # Parse arguments
    redaction_type = "generic"
    if "--type" in sys.argv:
        try:
            type_index = sys.argv.index("--type")
            if type_index + 1 < len(sys.argv):
                redaction_type = sys.argv[type_index + 1]
        except (ValueError, IndexError):
            print("❌ Invalid --type argument")
            return

    if command == "detect":
        if len(sys.argv) < 3:
            print("❌ Please provide text to detect PII in")
            return

        text = " ".join(sys.argv[2:])
        print(f"🔍 Detecting PII in: {text}")

        result = await cli.detect_pii(text)
        if result:
            print(f"📊 PII Detection Results:")
            print(f"   Total detections: {result['total_detections']}")
            print(f"   Categories: {result['categories']}")
            if result["total_detections"] > 0:
                print(f"   Details: {result['detailed_findings']}")
        else:
            print("❌ Failed to detect PII")

    elif command == "sanitize":
        if len(sys.argv) < 3:
            print("❌ Please provide text to sanitize")
            return

        text = " ".join(sys.argv[2:])
        print(f"🧹 Sanitizing text: {text}")
        print(f"   Redaction type: {redaction_type}")

        result = await cli.sanitize_text(text, redaction_type)
        if result:
            print(f"✅ Sanitized result: {result['sanitized_text']}")
            print(f"   PII detected: {result['pii_detected']}")
        else:
            print("❌ Failed to sanitize text")

    elif command == "file":
        if len(sys.argv) < 3:
            print("❌ Please provide file path")
            return

        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"📁 Sanitizing file: {file_path}")
        print(f"   Redaction type: {redaction_type}")

        result = await cli.sanitize_file(file_path, redaction_type)
        if result:
            print(f"✅ File sanitized successfully!")
            print(f"   Output: {result}")
        else:
            print("❌ Failed to sanitize file")

    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
