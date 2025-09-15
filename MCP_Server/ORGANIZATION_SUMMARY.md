# 📁 MCP_Server Directory Organization

The MCP_Server directory has been completely reorganized for better maintainability and clarity.

## 🗂️ New Directory Structure

```
MCP_Server/
├── 📁 core/                           # Core system components
│   ├── 📁 agent/                      # PII detection and sanitization
│   │   └── sanitizer_agent.py        # Main sanitizer agent
│   ├── 📁 server/                     # MCP server implementations
│   │   ├── vuln_mcp_stdio.py         # STDIO MCP server
│   │   └── vuln_mcp_sse.py           # SSE MCP server
│   ├── requirements.txt              # Python dependencies
│   └── vulnerable_mcp.db             # Database file
│
├── 📁 llm/                           # LLM integrations
│   ├── 📁 gemini/                    # Google Gemini integration
│   │   ├── gemini_simple_demo.py     # Working demo (✅ Use this)
│   │   ├── gemini_interactive.py     # Interactive mode
│   │   └── gemini_llm_integration.py # Full integration
│   ├── 📁 ollama/                    # Ollama integration
│   │   └── ollama_llm_integration.py
│   └── 📁 simulated/                 # Simulated LLM demos
│       ├── final_demo.py             # Working simulated demo
│       ├── simple_llm_demo.py        # Basic demo
│       └── llm_mcp_integration.py    # Advanced simulated demo
│
├── 📁 cli/                           # Command-line interfaces
│   ├── 📁 tools/                     # Main CLI tools
│   │   ├── sanitize_cli.py           # Simple CLI (✅ Use this)
│   │   └── setup_real_llm.py         # Setup script
│   └── 📁 examples/                  # CLI examples
│       ├── mcp_client_example.py     # MCP client example
│       └── tool_runner.py            # Tool runner example
│
├── 📁 docs/                          # Documentation
│   ├── 📁 setup/                     # Setup guides
│   │   └── SETUP_GEMINI.md           # Gemini setup
│   ├── 📁 usage/                     # Usage guides
│   │   ├── README_FINAL.md           # Complete usage guide
│   │   ├── USAGE_GUIDE.md            # Detailed usage guide
│   │   └── README_MCP_USAGE.md       # MCP usage guide
│   ├── 📁 api/                       # API documentation
│   │   └── mcp_server_config.json    # MCP server config
│   └── IMPLEMENTATION_SUMMARY.md     # Implementation summary
│
├── 📁 tests/                         # Testing
│   ├── 📁 unit/                      # Unit tests
│   │   ├── test_sanitizer.py         # Sanitizer tests
│   │   ├── test_implementation.py    # Implementation tests
│   │   ├── test_mcp_protocol.py      # MCP protocol tests
│   │   └── __pycache__/              # Python cache
│   ├── 📁 integration/               # Integration tests
│   │   ├── attack_payloads.py        # Attack payload tests
│   │   └── comprehensive_attack_client.py # Attack client
│   └── 📁 demos/                     # Demo scripts
│       ├── demo_sanitizer_mcp.py     # Sanitizer demo
│       ├── demo_without_mcp.py       # Non-MCP demo
│       └── quick_tests.py            # Quick tests
│
├── 📁 examples/                      # Usage examples
│   ├── 📁 basic/                     # Basic examples
│   │   └── example_usage.py          # Basic usage example
│   └── 📁 advanced/                  # Advanced examples
│       └── batch_processing.py       # Batch processing example
│
├── 📄 README.md                      # Main documentation
├── 📄 ORGANIZATION_SUMMARY.md        # This file
│
└── 🔧 Convenience Scripts            # Easy-to-use scripts
    ├── sanitize                      # CLI tool wrapper
    ├── interactive                   # Interactive mode wrapper
    ├── demo                          # Demo mode wrapper
    └── setup                         # Setup script wrapper
```

## 🚀 Quick Usage (After Organization)

### Using Convenience Scripts
```bash
# Simple CLI usage
./sanitize detect "john@example.com"
./sanitize sanitize "Contact john@example.com" --type mask
./sanitize file /path/to/file.txt

# Interactive mode
./interactive

# Demo mode
./demo

# Setup
./setup
```

### Using Full Paths
```bash
# CLI tools
python cli/tools/sanitize_cli.py detect "john@example.com"
python cli/tools/setup_real_llm.py

# LLM integrations
python llm/gemini/gemini_simple_demo.py
python llm/gemini/gemini_interactive.py --interactive

# Examples
python examples/basic/example_usage.py
python examples/advanced/batch_processing.py

# Tests
python tests/unit/test_sanitizer.py
python tests/demos/quick_tests.py
```

## 📋 File Organization Logic

### Core Components (`core/`)
- **Agent**: PII detection and sanitization logic
- **Server**: MCP server implementations
- **Requirements**: Python dependencies
- **Database**: Data storage

### LLM Integrations (`llm/`)
- **Gemini**: Google AI integration (primary)
- **Ollama**: Local LLM integration
- **Simulated**: Rule-based demos for testing

### CLI Tools (`cli/`)
- **Tools**: Main command-line interfaces
- **Examples**: CLI usage examples

### Documentation (`docs/`)
- **Setup**: Installation and configuration guides
- **Usage**: How-to guides and examples
- **API**: Technical documentation

### Testing (`tests/`)
- **Unit**: Individual component tests
- **Integration**: End-to-end tests
- **Demos**: Demonstration scripts

### Examples (`examples/`)
- **Basic**: Simple usage examples
- **Advanced**: Complex scenarios

## ✅ Benefits of Organization

1. **Clear Separation**: Each component has its own directory
2. **Easy Navigation**: Logical grouping of related files
3. **Maintainability**: Easier to find and modify specific components
4. **Scalability**: Easy to add new features in appropriate directories
5. **Documentation**: All docs are organized by purpose
6. **Testing**: Clear separation of test types
7. **Convenience**: Easy-to-use scripts in root directory

## 🎯 Key Files to Remember

- **Main CLI**: `cli/tools/sanitize_cli.py` or `./sanitize`
- **Interactive Mode**: `llm/gemini/gemini_interactive.py` or `./interactive`
- **Working Demo**: `llm/gemini/gemini_simple_demo.py` or `./demo`
- **Setup**: `cli/tools/setup_real_llm.py` or `./setup`
- **Core Agent**: `core/agent/sanitizer_agent.py`
- **MCP Server**: `core/server/vuln_mcp_stdio.py`

---

**The directory is now clean, organized, and easy to navigate!** 🎉
