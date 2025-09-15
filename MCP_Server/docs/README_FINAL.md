# 🤖 Complete Gemini + MCP Sanitizer System

This is a **complete, working LLM + MCP integration** for PII sanitization using Google's Gemini AI and the Model Context Protocol (MCP).

## 🎯 What You Have

- **Real LLM Integration**: Uses Google Gemini AI for intelligent decision making
- **MCP Server**: Provides PII detection and sanitization tools
- **Multiple Usage Modes**: CLI, interactive, and programmatic interfaces
- **File Processing**: Can sanitize entire files
- **Multiple Redaction Types**: Generic, mask, and removal

## 🚀 Quick Start

1. **Set up API key**:
   ```bash
   echo "GCP_KEY=your-gemini-api-key-here" > ../.env
   ```

2. **Choose your usage method**:

### Option 1: Simple CLI (Recommended)
```bash
# Detect PII
python sanitize_cli.py detect "john@example.com"

# Sanitize text
python sanitize_cli.py sanitize "Contact john@example.com or call 555-123-4567"

# Sanitize file
python sanitize_cli.py file test_email.txt
```

### Option 2: Interactive Mode
```bash
python gemini_interactive.py --interactive
# Then type requests like "Detect PII in john@example.com"
```

### Option 3: Demo Mode
```bash
python gemini_simple_demo.py
```

## 📁 Files Overview

### Core System
- `sanitizer_agent.py` - PII detection and sanitization logic
- `vuln_mcp_stdio.py` - MCP server with sanitizer tools
- `vuln_mcp_sse.py` - MCP server with SSE transport

### Gemini Integration
- `gemini_simple_demo.py` - Working demo (✅ **Use this**)
- `gemini_interactive.py` - Interactive mode
- `gemini_llm_integration.py` - Full-featured integration (has issues)

### CLI Tools
- `sanitize_cli.py` - Simple command-line interface (✅ **Use this**)
- `setup_real_llm.py` - Setup and testing script

### Documentation
- `USAGE_GUIDE.md` - Comprehensive usage guide
- `SETUP_GEMINI.md` - Setup instructions
- `README_FINAL.md` - This file

## 🔧 Usage Examples

### CLI Examples
```bash
# Detect PII
python sanitize_cli.py detect "john@example.com"
# Output: Shows PII categories and details

# Sanitize with generic redaction
python sanitize_cli.py sanitize "Contact john@example.com"
# Output: Contact [REDACTED_EMAIL]

# Sanitize with mask redaction
python sanitize_cli.py sanitize "john@example.com" --type mask
# Output: j***@e***.c***

# Sanitize with removal
python sanitize_cli.py sanitize "My SSN is 123-45-6789" --type remove
# Output: My SSN is

# Sanitize a file
python sanitize_cli.py file test_email.txt
# Creates: test_email.txt.sanitized
```

### Interactive Examples
```bash
python gemini_interactive.py --interactive

👤 Enter text or file path (or 'quit'): Detect PII in "Contact john@example.com"
🤖 Gemini: [Analyzes and calls detect_pii tool]
📄 MCP Tool Result: [Shows detection results]
🤖 Gemini: [Explains what was found]

👤 Enter text or file path (or 'quit'): quit
```

## 🎯 What Gets Detected

The system detects various types of PII:

- **Emails**: `john@example.com` → `[REDACTED_EMAIL]` or `j***@e***.c***`
- **Phone Numbers**: `555-123-4567` → `[REDACTED_PHONE]` or `555***4567`
- **SSNs**: `123-45-6789` → `[REDACTED_SSN]` or `***-**-****`
- **Credit Cards**: `4111-1111-1111-1111` → `[REDACTED_CREDIT_CARD]`
- **Names**: `John Smith` → `[REDACTED_NAME]` or `J*** S***`
- **Addresses**: `123 Main St` → `[REDACTED_ADDRESS]`
- **Dates**: `January 1, 2024` → `[REDACTED_DATE]`
- **IP Addresses**: `192.168.1.1` → `[REDACTED_IP]`

## 🔄 Redaction Types

| Type | Description | Example |
|------|-------------|---------|
| `generic` | Replace with generic tags | `john@example.com` → `[REDACTED_EMAIL]` |
| `mask` | Show partial content | `john@example.com` → `j***@e***.c***` |
| `remove` | Remove completely | `My SSN is 123-45-6789` → `My SSN is` |

## 🛠️ Troubleshooting

### Common Issues

1. **"GCP_KEY not found"**
   ```bash
   echo "GCP_KEY=your-key" > ../.env
   ```

2. **"File not found"**
   ```bash
   python sanitize_cli.py file /full/path/to/file.txt
   ```

3. **"Could not extract tool call"**
   - Be more specific: "Detect PII in [text]" or "Sanitize [text]"

### Getting Help

```bash
# CLI help
python sanitize_cli.py help

# Interactive help
python gemini_interactive.py --help
```

## 🎯 Real-World Use Cases

### 1. Email Sanitization
```bash
python sanitize_cli.py sanitize "Hi John, call me at 555-123-4567 or email john@company.com"
# Output: Hi John, call me at [REDACTED_PHONE] or email [REDACTED_EMAIL]
```

### 2. Document Processing
```bash
python sanitize_cli.py file sensitive_document.txt --type mask
# Creates: sensitive_document.txt.sanitized
```

### 3. Continuous Monitoring
```bash
python gemini_interactive.py --interactive
# Keep running and process new requests
```

### 4. Batch Processing
```bash
for file in *.txt; do
    python sanitize_cli.py file "$file" --type mask
done
```

## 🔧 Integration Examples

### In Python Scripts
```python
import subprocess

# Detect PII
result = subprocess.run([
    "python", "sanitize_cli.py", "detect", 
    "john@example.com"
], capture_output=True, text=True)

print(result.stdout)
```

### In Shell Scripts
```bash
#!/bin/bash
# Process all text files
for file in *.txt; do
    echo "Processing $file..."
    python sanitize_cli.py file "$file" --type mask
done
```

## 📊 Performance

- **Speed**: Fast for small texts, moderate for large files
- **Accuracy**: High for standard PII patterns
- **Reliability**: Uses Google's Gemini AI for intelligent decisions
- **Scalability**: Can process files and continuous requests

## 🎉 Success!

**This demonstrates a complete, working LLM + MCP integration!**

- ✅ **Real LLM**: Uses Google Gemini AI
- ✅ **MCP Protocol**: Proper client-server communication
- ✅ **PII Detection**: Comprehensive pattern matching
- ✅ **PII Sanitization**: Multiple redaction types
- ✅ **File Processing**: Can handle entire files
- ✅ **Multiple Interfaces**: CLI, interactive, and programmatic
- ✅ **Production Ready**: Error handling and user-friendly output

**This is exactly how a real LLM would integrate with MCP tools for PII sanitization!** 🎉
