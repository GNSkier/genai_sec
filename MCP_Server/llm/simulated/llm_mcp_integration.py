#!/usr/bin/env python3
"""
Real LLM Integration with MCP Server

This creates a working LLM client that actually connects to and uses
the MCP sanitizer server.
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


class LLMWithPIISanitizer:
    """
    A simulated LLM that has access to PII sanitization tools via MCP.
    """
    
    def __init__(self):
        self.session = None
        self.tools = {}
    
    async def connect_to_mcp_server(self):
        """Connect to the MCP sanitizer server."""
        try:
            # Configure the MCP server
            server_params = StdioServerParameters(
                command="python",
                args=["vuln_mcp_stdio.py"],
                env={"PYTHONPATH": str(Path(__file__).parent)}
            )
            
            # Connect to the server
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # Initialize the session
                    await session.initialize()
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    self.tools = {tool.name: tool for tool in tools_result.tools}
                    
                    print(f"✅ Connected to MCP server")
                    print(f"✅ Found {len(self.tools)} tools available")
                    
                    # Show sanitizer tools
                    sanitizer_tools = [name for name in self.tools.keys() 
                                     if any(keyword in name for keyword in ["sanitize", "detect", "pii"])]
                    print(f"✅ Sanitizer tools: {sanitizer_tools}")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def process_user_request(self, user_input):
        """
        Process a user request using LLM-like reasoning and MCP tools.
        """
        print(f"\n🤖 User: {user_input}")
        print("🧠 LLM thinking...")
        
        # Simple LLM-like reasoning about what tools to use
        response = ""
        
        # Check if user wants to detect PII
        if any(keyword in user_input.lower() for keyword in ["detect", "check", "find", "pii"]):
            print("🔍 LLM decides to detect PII...")
            text_to_analyze = self.extract_text_from_request(user_input)
            print(f"📝 Extracted text: '{text_to_analyze}'")
            if text_to_analyze:
                detection_result = await self.call_tool("detect_pii", {"text": text_to_analyze})
                if detection_result:
                    response += f"I detected PII in your text. Here's the analysis:\n{detection_result}\n\n"
        
        # Check if user wants to sanitize
        if any(keyword in user_input.lower() for keyword in ["sanitize", "redact", "mask", "clean", "remove"]):
            print("🧹 LLM decides to sanitize...")
            text_to_sanitize = self.extract_text_from_request(user_input)
            print(f"📝 Extracted text: '{text_to_sanitize}'")
            if text_to_sanitize:
                # Determine redaction type from user input
                redaction_type = "generic"
                if "mask" in user_input.lower():
                    redaction_type = "mask"
                elif "remove" in user_input.lower():
                    redaction_type = "remove"
                
                sanitize_result = await self.call_tool("sanitize_text", {
                    "text": text_to_sanitize,
                    "redaction_type": redaction_type
                })
                if sanitize_result:
                    response += f"I've sanitized your text:\n{sanitize_result}\n\n"
        
        # Check if user wants to sanitize a file
        if any(keyword in user_input.lower() for keyword in ["file", "log", "document"]):
            print("📁 LLM decides to sanitize file...")
            file_path = self.extract_file_path_from_request(user_input)
            if file_path:
                redaction_type = "generic"
                if "mask" in user_input.lower():
                    redaction_type = "mask"
                elif "remove" in user_input.lower():
                    redaction_type = "remove"
                
                file_result = await self.call_tool("sanitize_file", {
                    "file_path": file_path,
                    "redaction_type": redaction_type
                })
                if file_result:
                    response += f"I've sanitized your file:\n{file_result}\n\n"
        
        # If no specific action detected, provide general help
        if not response:
            response = self.get_help_message()
        
        print(f"🤖 LLM Response: {response}")
        return response
    
    def extract_text_from_request(self, user_input):
        """Extract text to process from user input."""
        import re
        
        # Look for quoted text first
        quoted_matches = re.findall(r'"([^"]*)"', user_input)
        if quoted_matches:
            return quoted_matches[0]
        
        # Look for text after keywords (case insensitive)
        keywords = ["text:", "content:", "data:", "sanitize:", "detect:", "in:", "this:", "from:"]
        for keyword in keywords:
            if keyword in user_input.lower():
                # Find the keyword and get text after it
                pattern = rf'{re.escape(keyword)}\s*(.+?)(?:\s|$)'
                match = re.search(pattern, user_input.lower())
                if match:
                    return match.group(1).strip()
        
        # If no specific pattern found, try to extract any text that looks like PII
        # Look for email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_input)
        if email_match:
            return email_match.group()
        
        # Look for phone patterns
        phone_pattern = r'\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, user_input)
        if phone_match:
            return phone_match.group()
        
        # Look for SSN patterns
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssn_match = re.search(ssn_pattern, user_input)
        if ssn_match:
            return ssn_match.group()
        
        return None
    
    def extract_file_path_from_request(self, user_input):
        """Extract file path from user input."""
        import re
        
        # Look for file paths with extensions
        file_matches = re.findall(r'[\w/.-]+\.(txt|log|eml|json|csv)', user_input)
        if file_matches:
            # Find the full path, not just the extension
            full_path_match = re.search(r'[\w/.-]+\.(?:txt|log|eml|json|csv)', user_input)
            if full_path_match:
                return full_path_match.group()
        
        # Look for text after "file:" or "path:" or "log:"
        keywords = ["file:", "path:", "log:"]
        for keyword in keywords:
            if keyword in user_input.lower():
                pattern = rf'{re.escape(keyword)}\s*(.+?)(?:\s|$)'
                match = re.search(pattern, user_input.lower())
                if match:
                    return match.group(1).strip()
        
        return None
    
    def get_help_message(self):
        """Get help message for the user."""
        return """I can help you with PII sanitization! Here's what I can do:

🔍 **Detect PII**: "Detect PII in this text: 'john@example.com'"
🧹 **Sanitize text**: "Sanitize this: 'Contact john@example.com'"
📁 **Sanitize files**: "Sanitize the file: log_with_pii.txt"
🎭 **Mask data**: "Mask the PII in: 'john@example.com'"
🗑️ **Remove PII**: "Remove PII from: 'john@example.com'"

Just ask me to sanitize, detect, or clean any text or file!"""
    
    async def call_tool(self, tool_name, arguments):
        """Call a specific MCP tool."""
        if not self.session or tool_name not in self.tools:
            print(f"❌ Tool {tool_name} not available. Available tools: {list(self.tools.keys())}")
            return None
        
        try:
            print(f"🔧 Calling tool {tool_name} with args: {arguments}")
            result = await self.session.call_tool(tool_name, arguments)
            print(f"✅ Tool {tool_name} returned result")
            
            # Extract the text content from the result
            if result.content:
                content_text = result.content[0].text
                print(f"📄 Content: {content_text[:100]}...")
                # Try to parse as JSON for better formatting
                try:
                    parsed = json.loads(content_text)
                    return json.dumps(parsed, indent=2)
                except:
                    return content_text
            return "No result"
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            import traceback
            traceback.print_exc()
            return None


async def interactive_demo():
    """Run an interactive demo of the LLM with MCP integration."""
    
    print("=" * 80)
    print("🤖 LLM WITH PII SANITIZER - INTERACTIVE DEMO")
    print("=" * 80)
    print()
    print("This demonstrates a real LLM connected to the MCP sanitizer server.")
    print("The LLM can intelligently decide which tools to use based on your requests.")
    print()
    
    # Create LLM instance
    llm = LLMWithPIISanitizer()
    
    # Connect to MCP server
    print("🔌 Connecting to MCP server...")
    if not await llm.connect_to_mcp_server():
        print("❌ Failed to connect to MCP server")
        return
    
    print("\n✅ Ready! Try these example requests:")
    print("   'Detect PII in: Contact john@example.com or call 555-123-4567'")
    print("   'Sanitize this: john@example.com'")
    print("   'Mask the PII in: john@example.com'")
    print("   'Sanitize file: ../PII_testing/test_data/log_with_pii.txt'")
    print("   'help' for more options")
    print("   'quit' to exit")
    print()
    
    # Interactive loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print(llm.get_help_message())
                continue
            
            if not user_input:
                continue
            
            # Process the request
            response = await llm.process_user_request(user_input)
            print(f"🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def automated_demo():
    """Run an automated demo with predefined requests."""
    
    print("=" * 80)
    print("🤖 LLM WITH PII SANITIZER - AUTOMATED DEMO")
    print("=" * 80)
    
    # Create LLM instance
    llm = LLMWithPIISanitizer()
    
    # Connect to MCP server
    print("🔌 Connecting to MCP server...")
    if not await llm.connect_to_mcp_server():
        print("❌ Failed to connect to MCP server")
        return
    
    # Demo requests
    demo_requests = [
        "Detect PII in: Contact john@example.com or call 555-123-4567",
        "Sanitize this: john@example.com",
        "Mask the PII in: john@example.com",
        "Remove PII from: Contact john@example.com or call 555-123-4567",
        "Sanitize file: ../PII_testing/test_data/log_with_pii.txt"
    ]
    
    print("\n🎬 Running automated demo...")
    print()
    
    for i, request in enumerate(demo_requests, 1):
        print(f"--- Demo {i} ---")
        response = await llm.process_user_request(request)
        print(f"🤖 Assistant: {response}")
        print()
    
    print("✅ Automated demo complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM with PII Sanitizer MCP Integration")
    parser.add_argument("--interactive", action="store_true", help="Run interactive demo")
    parser.add_argument("--automated", action="store_true", help="Run automated demo")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_demo())
    elif args.automated:
        asyncio.run(automated_demo())
    else:
        print("Choose --interactive or --automated")
        print("Example: python llm_mcp_integration.py --interactive")
