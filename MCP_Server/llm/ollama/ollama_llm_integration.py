#!/usr/bin/env python3
"""
Ollama LLM Integration with MCP Sanitizer

This integrates Ollama (local LLM) with our MCP sanitizer tools.
"""

import asyncio
import json
import sys
import requests
from pathlib import Path

# Add MCP to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Installing MCP...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client


class OllamaLLMWithMCP:
    """Ollama LLM integrated with MCP sanitizer tools."""

    def __init__(
        self, model_name="llama3.2", ollama_url="http://localhost:11434"
    ):
        """Initialize Ollama with model name and URL."""
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.mcp_session = None
        self.available_tools = {}

        # Test Ollama connection
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connected to Ollama at {ollama_url}")
            else:
                print(f"❌ Ollama not responding at {ollama_url}")
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")

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
            return None

    def call_ollama(self, prompt, system_prompt=None):
        """Call Ollama LLM."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9},
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.ollama_url}/api/generate", json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error calling Ollama: {e}")
            return None

    def create_system_prompt(self):
        """Create system prompt for Ollama with MCP tools."""
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
        """Process user request using Ollama + MCP tools."""
        print(f"\n👤 User: {user_input}")

        # Create conversation with system prompt
        system_prompt = self.create_system_prompt()

        # Ask Ollama what to do
        prompt = f"{system_prompt}\n\nUser request: {user_input}\n\nWhat tool should I call and with what arguments?"

        try:
            response = self.call_ollama(prompt, system_prompt)
            if not response:
                return "❌ Failed to get response from Ollama"

            print(f"🤖 Ollama: {response}")

            # Parse Ollama's response for tool calls
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
                            print("❌ Could not parse arguments")

                if tool_name and arguments:
                    print(
                        f"🔧 Calling tool: {tool_name} with args: {arguments}"
                    )
                    result = await self.call_mcp_tool(tool_name, arguments)

                    if result:
                        print(f"📄 Tool result: {result[:200]}...")

                        # Ask Ollama to interpret the result
                        interpretation_prompt = f"""
The user asked: {user_input}
I called tool {tool_name} and got this result: {result}

Please provide a helpful response to the user explaining what was found/done.
"""
                        interpretation = self.call_ollama(interpretation_prompt)
                        print(f"🤖 Ollama: {interpretation}")
                        return interpretation
                    else:
                        return "❌ Tool call failed"
                else:
                    return "❌ Could not determine tool to call"
            else:
                return response

        except Exception as e:
            print(f"❌ Error with Ollama: {e}")
            return f"❌ Error: {e}"


async def ollama_demo():
    """Demo Ollama LLM with MCP tools."""

    print("=" * 80)
    print("🤖 OLLAMA LLM + MCP SANITIZER DEMO")
    print("=" * 80)
    print()
    print(
        "This uses Ollama (local LLM) to intelligently decide which MCP tools to call."
    )
    print()

    try:
        # Initialize Ollama LLM
        llm = OllamaLLMWithMCP()

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

        print("🎬 Running Ollama + MCP demo...")
        print()

        for i, request in enumerate(demo_requests, 1):
            print(f"--- Demo {i} ---")
            response = await llm.process_user_request(request)
            print()

        print("✅ Ollama + MCP demo completed!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


async def interactive_ollama():
    """Interactive Ollama LLM demo."""

    print("=" * 80)
    print("🤖 INTERACTIVE OLLAMA + MCP")
    print("=" * 80)
    print()
    print("Chat with Ollama! It can intelligently use PII sanitization tools.")
    print("Try: 'Detect PII in john@example.com' or 'Sanitize my email'")
    print("Type 'quit' to exit")
    print()

    try:
        # Initialize Ollama LLM
        llm = OllamaLLMWithMCP()

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

                # Process with Ollama + MCP
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


def check_ollama_models():
    """Check what Ollama models are available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("Available Ollama models:")
            for model in models:
                print(f"  - {model['name']}")
            return [model["name"] for model in models]
        else:
            print("❌ Could not get Ollama models")
            return []
    except Exception as e:
        print(f"❌ Error checking Ollama models: {e}")
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ollama LLM + MCP Integration")
    parser.add_argument(
        "--demo", action="store_true", help="Run automated demo"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive demo"
    )
    parser.add_argument(
        "--models", action="store_true", help="List available Ollama models"
    )
    parser.add_argument(
        "--model", default="llama3.2", help="Ollama model to use"
    )

    args = parser.parse_args()

    if args.models:
        check_ollama_models()
    elif args.demo:
        asyncio.run(ollama_demo())
    elif args.interactive:
        asyncio.run(interactive_ollama())
    else:
        print("Choose --demo, --interactive, or --models")
        print("Make sure Ollama is running: ollama serve")
        print("Example: python ollama_llm_integration.py --demo")
