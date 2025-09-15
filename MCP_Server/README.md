# 🤖 MCP Sanitizer System

A complete LLM + MCP integration for PII sanitization using Google Gemini AI and the Model Context Protocol.

## 📁 Directory Structure

```
MCP_Server/
├── core/                           # Core system components
│   ├── agent/                      # PII detection and sanitization
│   │   └── sanitizer_agent.py     # Main sanitizer agent
│   ├── server/                     # MCP server implementations
│   │   ├── vuln_mcp_stdio.py      # STDIO MCP server
│   │   └── vuln_mcp_sse.py        # SSE MCP server
│   ├── requirements.txt           # Python dependencies
│   └── vulnerable_mcp.db          # Database file
│
├── llm/                           # LLM integrations
│   ├── gemini/                    # Google Gemini integration
│   │   ├── gemini_simple_demo.py  # Working demo (✅ Use this)
│   │   ├── gemini_interactive.py  # Interactive mode
│   │   └── gemini_llm_integration.py # Full integration
│   ├── ollama/                    # Ollama integration
│   │   └── ollama_llm_integration.py
│   └── simulated/                 # Simulated LLM demos
│       ├── final_demo.py          # Working simulated demo
│       ├── simple_llm_demo.py     # Basic demo
│       └── llm_mcp_integration.py # Advanced simulated demo
│
├── cli/                           # Command-line interfaces
│   ├── tools/                     # Main CLI tools
│   │   ├── sanitize_cli.py        # Simple CLI (✅ Use this)
│   │   └── setup_real_llm.py      # Setup script
│   └── examples/                  # CLI examples
│       ├── mcp_client_example.py  # MCP client example
│       └── tool_runner.py         # Tool runner example
│
├── docs/                          # Documentation
│   ├── setup/                     # Setup guides
│   │   └── SETUP_GEMINI.md        # Gemini setup
│   ├── usage/                     # Usage guides
│   │   ├── README_FINAL.md        # Complete usage guide
│   │   ├── USAGE_GUIDE.md         # Detailed usage guide
│   │   └── README_MCP_USAGE.md    # MCP usage guide
│   ├── api/                       # API documentation
│   │   └── mcp_server_config.json # MCP server config
│   └── IMPLEMENTATION_SUMMARY.md  # Implementation summary
│
├── tests/                         # Testing
│   ├── unit/                      # Unit tests
│   │   ├── test_sanitizer.py      # Sanitizer tests
│   │   ├── test_implementation.py # Implementation tests
│   │   ├── test_mcp_protocol.py   # MCP protocol tests
│   │   └── __pycache__/           # Python cache
│   ├── integration/               # Integration tests
│   │   ├── attack_payloads.py     # Attack payload tests
│   │   └── comprehensive_attack_client.py # Attack client
│   └── demos/                     # Demo scripts
│       ├── demo_sanitizer_mcp.py  # Sanitizer demo
│       ├── demo_without_mcp.py    # Non-MCP demo
│       └── quick_tests.py         # Quick tests
│
└── examples/                      # Usage examples
    ├── basic/                     # Basic examples
    └── advanced/                  # Advanced examples
```

## 🚀 Quick Start

### 1. Set up API key
```bash
echo "GCP_KEY=your-gemini-api-key-here" > ../.env
```

### 2. Choose your usage method

#### Option A: Simple CLI (Recommended)
```bash
# Detect PII
python cli/tools/sanitize_cli.py detect "john@example.com"

# Sanitize text
python cli/tools/sanitize_cli.py sanitize "Contact john@example.com or call 555-123-4567"

# Sanitize file
python cli/tools/sanitize_cli.py file /path/to/file.txt
```

#### Option B: Interactive Mode
```bash
python llm/gemini/gemini_interactive.py --interactive
```

#### Option C: Demo Mode
```bash
python llm/gemini/gemini_simple_demo.py
```

## 📚 Documentation

- **Complete Usage Guide**: `docs/usage/README_FINAL.md`
- **Detailed Usage Guide**: `docs/usage/USAGE_GUIDE.md`
- **Setup Instructions**: `docs/setup/SETUP_GEMINI.md`
- **Implementation Summary**: `docs/IMPLEMENTATION_SUMMARY.md`

## 🔧 Core Components

- **Sanitizer Agent**: `core/agent/sanitizer_agent.py`
- **MCP Servers**: `core/server/`
- **Dependencies**: `core/requirements.txt`

## 🧪 Testing

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **Demo Scripts**: `tests/demos/`

## 🎯 Key Features

- ✅ **Real LLM Integration**: Uses Google Gemini AI
- ✅ **MCP Protocol**: Proper client-server communication
- ✅ **PII Detection**: Comprehensive pattern matching
- ✅ **PII Sanitization**: Multiple redaction types
- ✅ **File Processing**: Can handle entire files
- ✅ **Multiple Interfaces**: CLI, interactive, and programmatic
- ✅ **Production Ready**: Error handling and user-friendly output

## 🔄 Redaction Types

| Type | Description | Example |
|------|-------------|---------|
| `generic` | Replace with generic tags | `john@example.com` → `[REDACTED_EMAIL]` |
| `mask` | Show partial content | `john@example.com` → `j***@e***.c***` |
| `remove` | Remove completely | `My SSN is 123-45-6789` → `My SSN is` |

---

**This is a complete, working LLM + MCP integration for PII sanitization!** 🎉
