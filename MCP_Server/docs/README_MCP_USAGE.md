# MCP Server Usage Guide

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows LLMs to securely connect to external tools and data sources. The MCP server exposes tools that an LLM can call when needed.

## Architecture

```
User → LLM (Claude/GPT) → MCP Client → MCP Server → Sanitizer Tools
```

## How to Use This MCP Server

### 1. Start the MCP Server

The server runs as a background service that exposes sanitizer tools:

```bash
# STDIO Transport (for direct integration)
python vuln_mcp_stdio.py

# SSE Transport (for web-based integration)
python vuln_mcp_sse.py
```

### 2. Configure Your LLM Client

#### For Claude Desktop:
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pii-sanitizer": {
      "command": "python",
      "args": ["/path/to/vuln_mcp_stdio.py"],
      "env": {
        "PYTHONPATH": "/path/to/MCP_Server"
      }
    }
  }
}
```

#### For Other MCP Clients:
Use the server configuration in `mcp_server_config.json`.

### 3. Available Tools

The MCP server exposes these sanitizer tools:

- **`detect_pii(text: str)`** - Detect PII in text
- **`sanitize_text(text: str, redaction_type: str)`** - Sanitize text
- **`get_sanitization_report(text: str)`** - Get detailed PII report
- **`sanitize_file(file_path: str, redaction_type: str)`** - Sanitize file

### 4. Example Usage

When you ask an LLM to sanitize text, it will automatically call the appropriate MCP tool:

**User:** "Please sanitize this text: 'Contact john@example.com or call 555-123-4567'"

**LLM Response:** The LLM will call `sanitize_text` tool and return:
```
"Contact [REDACTED_EMAIL] or call [REDACTED_PHONE]"
```

### 5. Redaction Types

- **`generic`** (default): `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`
- **`mask`**: `j***@e***.com`, `555***4567`
- **`remove`**: Completely removes PII

### 6. Testing the MCP Server

You can test the server directly using MCP client tools:

```bash
# Test STDIO server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python vuln_mcp_stdio.py

# Test SSE server (requires server running)
curl -X POST http://localhost:9000/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## Important Notes

1. **The MCP server is NOT a CLI tool** - it's a service that LLMs call
2. **The server runs continuously** - it doesn't exit after one request
3. **Tools are called by the LLM** - not by users directly
4. **The server handles multiple requests** - it's designed for concurrent usage

## Security Considerations

- This is a **vulnerable MCP server** for educational purposes
- **DO NOT** use in production environments
- The server includes intentionally vulnerable tools for security testing
- Use only in isolated, controlled environments
