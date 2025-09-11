# GenAI Security Course Projects

This repository contains multiple different repositories related to GenAI Security. All repositories were created for educational purposes and testing. 

## 📁 Directory Structure

```
genai_sec/
├── MCP_Server/          # Model Context Protocol vulnerability demonstration
├── PII_testing/         # PII detection and protection research
└── README.md           # This file
```

## 📂 Project Folders

### MCP_Server
Model Context Protocol vulnerability demonstration system for educational security research.

**Key Components:**
- `vuln_mcp_stdio.py` - STDIO transport vulnerable server
- `vuln_mcp_sse.py` - SSE transport vulnerable server  
- `tool_runner.py` - Interactive tool testing interface
- `quick_tests.py` - Automated vulnerability testing
- `comprehensive_attack_client.py` - Full attack suite
- `attack_payloads.py` - 500+ attack payloads database

**Vulnerability Categories:** SQL injection, file system attacks, command execution, SSRF, environment exposure, cryptographic weaknesses, system information disclosure, logging vulnerabilities

### PII_testing
PII detection and protection research project with multiple detection methods.

**Key Components:**
- `PII_Logging_2.ipynb` - Enhanced detector demo notebook
- `pii_logging.py` - Core PII detection implementation
- `test_pii_logging.py` - Comprehensive test suite
- `test_data/` - Sample files for testing (logs, emails)

**Detection Methods:** Regex patterns, spaCy NER, proximity analysis, graph-based clustering, deduplication

## 🚀 Quick Start

Each project folder contains its own detailed README with setup and usage instructions:
- [MCP_Server README](MCP_Server/README.md)
- [PII_testing README](PII_testing/README.md)
