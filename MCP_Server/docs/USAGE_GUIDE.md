# 🤖 Gemini + MCP Sanitizer Usage Guide

This guide shows you how to use the Gemini + MCP sanitizer system in different ways.

## 🚀 Quick Start

1. **Set up your API key**:
   ```bash
   echo "GCP_KEY=your-gemini-api-key-here" > ../.env
   ```

2. **Choose your usage method** (see options below)

## 📋 Usage Options

### 1. **Simple CLI** - One-shot commands
Perfect for quick sanitization tasks.

```bash
# Detect PII in text
python sanitize_cli.py detect "john@example.com"

# Sanitize text (generic redaction)
python sanitize_cli.py sanitize "Contact john@example.com or call 555-123-4567"

# Sanitize with mask redaction
python sanitize_cli.py sanitize "john@example.com" --type mask

# Sanitize with removal
python sanitize_cli.py sanitize "My SSN is 123-45-6789" --type remove

# Sanitize a file
python sanitize_cli.py file /path/to/file.txt
python sanitize_cli.py file /path/to/file.txt --type mask
```

### 2. **Interactive Mode** - Keep running and feed requests
Perfect for continuous use.

```bash
# Start interactive mode
python gemini_interactive.py --interactive

# Then type requests like:
# "Detect PII in john@example.com"
# "Sanitize Contact john@example.com"
# "file:/path/to/file.txt"
# "quit" to exit
```

### 3. **Single Request Mode** - Process one thing and exit
```bash
# Process a single text
python gemini_interactive.py "Sanitize john@example.com"

# Process a single file
python gemini_interactive.py "file:/path/to/file.txt"
```

### 4. **Demo Mode** - See it in action
```bash
# Run automated demo
python gemini_simple_demo.py
```

## 🔧 Redaction Types

| Type | Description | Example |
|------|-------------|---------|
| `generic` | Replace with generic tags | `john@example.com` → `[REDACTED_EMAIL]` |
| `mask` | Show partial content | `john@example.com` → `j***@e***.c***` |
| `remove` | Remove completely | `My SSN is 123-45-6789` → `My SSN is` |

## 📁 File Processing

The system can process files and create sanitized versions:

```bash
# Sanitize a file (creates .sanitized version)
python sanitize_cli.py file /path/to/email.txt

# This creates: /path/to/email.txt.sanitized
```

## 🎯 Real-World Examples

### Example 1: Email Sanitization
```bash
python sanitize_cli.py sanitize "Hi John, please call me at 555-123-4567 or email john@company.com"
# Output: Hi John, please call me at [REDACTED_PHONE] or email [REDACTED_EMAIL]
```

### Example 2: Document Processing
```bash
python sanitize_cli.py file /path/to/sensitive_document.txt --type mask
# Creates: /path/to/sensitive_document.txt.sanitized
```

### Example 3: Interactive Session
```bash
python gemini_interactive.py --interactive

👤 Enter text or file path (or 'quit'): Detect PII in "Contact us at support@company.com"
🤖 Gemini: [Analyzes and calls detect_pii tool]
📄 MCP Tool Result: [Shows PII detection results]
🤖 Gemini: [Explains what was found]

👤 Enter text or file path (or 'quit'): quit
👋 Goodbye!
```

## 🔍 What Gets Detected

The system detects various types of PII:

- **Emails**: `john@example.com`
- **Phone Numbers**: `555-123-4567`, `(555) 123-4567`
- **SSNs**: `123-45-6789`
- **Credit Cards**: `4111-1111-1111-1111`
- **Names**: `John Smith` (via NER)
- **Addresses**: `123 Main St, City, State`
- **Dates**: `January 1, 2024`
- **IP Addresses**: `192.168.1.1`

## 🛠️ Troubleshooting

### Common Issues

1. **"GCP_KEY not found"**
   ```bash
   # Make sure .env file exists in master directory
   echo "GCP_KEY=your-key" > ../.env
   ```

2. **"File not found"**
   ```bash
   # Use absolute path or check file exists
   python sanitize_cli.py file /full/path/to/file.txt
   ```

3. **"Could not extract tool call"**
   - This happens when Gemini doesn't understand the request
   - Try being more specific: "Detect PII in [text]" or "Sanitize [text]"

### Getting Help

```bash
# Show help for CLI
python sanitize_cli.py help

# Show help for interactive mode
python gemini_interactive.py --help
```

## 🎯 Best Practices

1. **Be specific**: "Detect PII in [text]" works better than just "[text]"
2. **Use quotes**: Wrap text in quotes to avoid shell interpretation
3. **Check files**: Make sure file paths are correct and accessible
4. **Review results**: The system is good but not perfect - review sanitized output

## 🔄 Integration Examples

### In a Script
```python
import subprocess
import json

# Detect PII
result = subprocess.run([
    "python", "sanitize_cli.py", "detect", 
    "john@example.com"
], capture_output=True, text=True)

print(result.stdout)
```

### In a Pipeline
```bash
# Process multiple files
for file in *.txt; do
    python sanitize_cli.py file "$file" --type mask
done
```

### Continuous Monitoring
```bash
# Keep running and process new files
python gemini_interactive.py --interactive
# Then feed file paths as they come in
```

---

**This gives you a complete, working LLM + MCP sanitization system!** 🎉
