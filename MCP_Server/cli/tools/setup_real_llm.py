#!/usr/bin/env python3
"""
Setup Script for Real LLM Integration

This script helps you set up either Gemini or Ollama as the LLM
for the MCP sanitizer integration.
"""

import os
import subprocess
import sys
import requests
from pathlib import Path

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


def check_gemini_setup():
    """Check if Gemini is properly set up."""
    print("🔍 Checking Gemini setup...")

    # Check for API key (try GCP_KEY first, then GEMINI_API_KEY)
    api_key = os.getenv("GCP_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GCP_KEY or GEMINI_API_KEY not found")
        print(
            "   Get your API key from: https://makersuite.google.com/app/apikey"
        )
        print(
            "   Add GCP_KEY=your-api-key-here to .env file in master directory"
        )
        print("   Or run: export GEMINI_API_KEY='your-api-key-here'")
        return False

    if os.getenv("GCP_KEY"):
        print("✅ GCP_KEY found in .env file")
    else:
        print("✅ GEMINI_API_KEY found")

    # Check if google-generativeai is installed
    try:
        import google.generativeai as genai

        print("✅ google-generativeai is installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "google-generativeai"]
        )
        print("✅ google-generativeai installed")

    # Test API key
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, test message")
        print("✅ Gemini API key is working")
        return True
    except Exception as e:
        print(f"❌ Gemini API key test failed: {e}")
        return False


def check_ollama_setup():
    """Check if Ollama is properly set up."""
    print("🔍 Checking Ollama setup...")

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

    # Check available models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        if models:
            print("✅ Available Ollama models:")
            for model in models:
                print(f"   - {model['name']}")
        else:
            print("❌ No Ollama models found")
            print("   Install a model: ollama pull llama3.2")
            return False

        return True
    except Exception as e:
        print(f"❌ Error checking Ollama models: {e}")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")

    dependencies = [
        "google-generativeai",  # For Gemini
        "requests",  # For Ollama
        "mcp",  # For MCP integration
        "python-dotenv",  # For .env file support
    ]

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep} is already installed")
        except ImportError:
            print(f"📥 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed")


def test_mcp_server():
    """Test if MCP server is working."""
    print("🔍 Testing MCP server...")

    try:
        # Test the sanitizer agent directly
        from sanitizer_agent import SanitizerAgent

        agent = SanitizerAgent()
        result = agent.sanitize_text("john@example.com", "generic")

        if result["sanitized_text"] == "[REDACTED_EMAIL]":
            print("✅ MCP sanitizer is working")
            return True
        else:
            print("❌ MCP sanitizer test failed")
            return False
    except Exception as e:
        print(f"❌ MCP sanitizer test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 80)
    print("🚀 REAL LLM + MCP SANITIZER SETUP")
    print("=" * 80)
    print()
    print("This script helps you set up either Gemini or Ollama as the LLM")
    print("for the MCP sanitizer integration.")
    print()

    # Install dependencies
    install_dependencies()
    print()

    # Test MCP server
    if not test_mcp_server():
        print("❌ MCP server setup failed. Please check the sanitizer agent.")
        return
    print()

    # Check LLM options
    print("🤖 Choose your LLM:")
    print("1. Gemini (Google) - Requires API key")
    print("2. Ollama (Local) - Requires Ollama installation")
    print("3. Both")
    print()

    choice = input("Enter choice (1/2/3): ").strip()

    if choice in ["1", "3"]:
        print("\n" + "=" * 50)
        print("🔧 GEMINI SETUP")
        print("=" * 50)
        if check_gemini_setup():
            print("\n✅ Gemini setup complete!")
            print("   Run: python gemini_llm_integration.py --demo")
        else:
            print("\n❌ Gemini setup failed")
        print()

    if choice in ["2", "3"]:
        print("\n" + "=" * 50)
        print("🔧 OLLAMA SETUP")
        print("=" * 50)
        if check_ollama_setup():
            print("\n✅ Ollama setup complete!")
            print("   Run: python ollama_llm_integration.py --demo")
        else:
            print("\n❌ Ollama setup failed")
        print()

    print("=" * 80)
    print("📚 USAGE EXAMPLES")
    print("=" * 80)
    print()
    print("Gemini:")
    print("  # Option 1: Add to .env file in master directory")
    print("  echo 'GCP_KEY=your-key' >> ../.env")
    print("  python gemini_llm_integration.py --demo")
    print("  # Option 2: Use environment variable")
    print("  export GEMINI_API_KEY='your-key'")
    print("  python gemini_llm_integration.py --interactive")
    print()
    print("Ollama:")
    print("  ollama serve")
    print("  python ollama_llm_integration.py --demo")
    print("  python ollama_llm_integration.py --interactive")
    print()
    print("Check available Ollama models:")
    print("  python ollama_llm_integration.py --models")
    print()


if __name__ == "__main__":
    main()
