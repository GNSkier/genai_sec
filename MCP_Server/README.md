# MCP Vulnerability Demonstration System

A comprehensive Model Context Protocol (MCP) vulnerability demonstration system designed for educational security research and penetration testing. This system implements multiple vulnerable MCP servers with extensive attack vectors and automated testing capabilities.

## ⚠️ WARNING

**THIS SYSTEM IS DESIGNED FOR EDUCATIONAL AND SECURITY TESTING PURPOSES ONLY**

- **DO NOT** deploy in production environments
- **DO NOT** use on systems containing real sensitive data
- **DO NOT** expose to untrusted networks
- Use only in isolated, controlled environments for security research

## 🏗️ Architecture

The system consists of several components:

### Core Vulnerable Servers

1. **STDIO Transport Server** (`vuln_mcp_stdio.py`)
   - Comprehensive MCP server with 20+ vulnerable tools
   - SQL injection, file system, command execution, and network vulnerabilities
   - Direct STDIO communication for MCP clients

2. **SSE Transport Server** (`vuln_mcp_sse.py`)
   - FastAPI-based server with Server-Sent Events (SSE) transport
   - Direct attack endpoints for automated testing
   - Same vulnerable tools as STDIO server plus HTTP endpoints

### Attack and Testing Tools

3. **Comprehensive Attack Client** (`comprehensive_attack_client.py`)
   - Automated vulnerability testing with success tracking
   - Tests 10+ different vulnerability categories
   - Detailed reporting and metrics

4. **Attack Payload Database** (`attack_payloads.py`)
   - Extensive collection of attack payloads
   - Organized by vulnerability type
   - 500+ payloads across multiple attack vectors

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python 3.8+ and pip
# Clone or download the MCP_Server directory
cd MCP_Server

# Install dependencies
pip install -r requirements.txt
```

### Running the Servers

#### STDIO Server
```bash
python vuln_mcp_stdio.py
```

#### SSE Server
```bash
python vuln_mcp_sse.py
# Server will start on http://localhost:9000
```

### Running Attack Tests

#### Option 1: Interactive Tool Runner (Recommended)
```bash
# Interactive mode - call specific tools
python tool_runner.py vuln_mcp_stdio.py

# Demo mode - run predefined tests
python tool_runner.py vuln_mcp_stdio.py demo
```

#### Option 2: Quick Tests
```bash
# Run all tests
python quick_tests.py vuln_mcp_stdio.py all

# Run specific test categories
python quick_tests.py vuln_mcp_stdio.py sql
python quick_tests.py vuln_mcp_stdio.py file
python quick_tests.py vuln_mcp_stdio.py command
python quick_tests.py vuln_mcp_stdio.py network
```

#### Option 3: Comprehensive Attack Client
```bash
# Full comprehensive testing
python comprehensive_attack_client.py vuln_mcp_stdio.py

# Test SSE server (requires server to be running)
python comprehensive_attack_client.py vuln_mcp_sse.py
```

## 🔍 Vulnerability Categories

### 1. SQL Injection
- **Tools**: `insert_record`, `execute_sql`, `search_records`
- **Vulnerabilities**: Direct SQL injection, union-based attacks, stacked queries
- **Impact**: Data extraction, database manipulation, privilege escalation

### 2. File System Vulnerabilities
- **Tools**: `read_file`, `write_file`, `list_directory`, `delete_file`
- **Vulnerabilities**: Path traversal, arbitrary file access
- **Impact**: Sensitive file disclosure, system compromise

### 3. Command Execution
- **Tools**: `execute_command`, `kill_process`, `list_processes`
- **Vulnerabilities**: Command injection, process manipulation
- **Impact**: Remote code execution, system takeover

### 4. Network Attacks (SSRF)
- **Tools**: `make_request`, `scan_port`, `port_scan_range`
- **Vulnerabilities**: Server-side request forgery, port scanning
- **Impact**: Internal network reconnaissance, service enumeration

### 5. Environment Variable Exposure
- **Tools**: `get_env_variable`, `list_all_env_vars`
- **Vulnerabilities**: Sensitive environment variable disclosure
- **Impact**: Credential theft, configuration exposure

### 6. Cryptographic Weaknesses
- **Tools**: `generate_hash`, `generate_token`, `weak_encrypt`
- **Vulnerabilities**: Weak algorithms, predictable randomness
- **Impact**: Cryptographic bypass, token prediction

### 7. System Information Disclosure
- **Tools**: `get_system_info`, `get_network_interfaces`
- **Vulnerabilities**: Excessive system information exposure
- **Impact**: Reconnaissance, attack surface enumeration

### 8. Logging Vulnerabilities
- **Tools**: `log_sensitive_data`, `read_logs`
- **Vulnerabilities**: Sensitive data logging, log file access
- **Impact**: Data leakage, audit trail manipulation

## 🛠️ Available Tools

### Database Operations
- `insert_record(name, address, email, phone, credit_card)` - SQL injection vulnerable
- `execute_sql(query)` - Arbitrary SQL execution
- `search_records(search_term)` - SQL injection in search
- `connect_database(connection_string, query)` - Database connection vulnerability

### File System Operations
- `read_file(file_path)` - Path traversal vulnerable
- `write_file(file_path, content)` - Path traversal vulnerable
- `list_directory(path)` - Directory traversal
- `delete_file(file_path)` - File deletion vulnerability

### Command Execution
- `execute_command(command)` - Command injection vulnerable
- `kill_process(pid)` - Process termination
- `list_processes()` - Process enumeration

### Network Operations
- `make_request(url, method, data, headers)` - SSRF vulnerable
- `scan_port(host, port)` - Port scanning
- `port_scan_range(host, start_port, end_port)` - Port range scanning

### System Information
- `get_env_variable(var_name)` - Environment variable access
- `list_all_env_vars()` - Full environment dump
- `get_system_info()` - System information exposure
- `get_network_interfaces()` - Network interface information

### Cryptographic Functions
- `generate_hash(data, algorithm)` - Hash generation (weak algorithms)
- `generate_token(length)` - Token generation (weak randomness)
- `weak_encrypt(data, key)` - Weak encryption implementation

### Logging Operations
- `log_sensitive_data(data, log_level)` - Sensitive data logging
- `read_logs(log_file)` - Log file access

## 📊 Attack Testing

The comprehensive attack client tests multiple vulnerability categories:

```bash
python comprehensive_attack_client.py vuln_mcp_stdio.py
```

### Test Categories
1. **SQL Injection** - 12 different payloads
2. **Arbitrary SQL** - 7 different queries
3. **File Access** - 8 different file paths
4. **Command Execution** - 9 different commands
5. **Network Attacks** - 8 different SSRF targets
6. **Crypto Weaknesses** - 3 weak algorithms
7. **Environment Exposure** - 20+ environment variables
8. **System Information** - System info disclosure
9. **Path Traversal** - 5 different traversal paths
10. **Process Manipulation** - Process listing and manipulation

### Sample Output
```
============================================================
COMPREHENSIVE MCP ATTACK REPORT
============================================================
Overall Success Rate: 45/67 (67.2%)

SQL Injection           : 10/12 ( 83.3%) ✓ VULNERABLE
Arbitrary Sql           :  7/ 7 (100.0%) ✓ VULNERABLE
File Access             :  3/ 8 ( 37.5%) ✓ VULNERABLE
Command Execution       :  6/ 9 ( 66.7%) ✓ VULNERABLE
Network Attacks         :  4/ 8 ( 50.0%) ✓ VULNERABLE
Crypto Weaknesses       :  3/ 3 (100.0%) ✓ VULNERABLE
Env Exposure            : 12/20 ( 60.0%) ✓ VULNERABLE
System Info             :  1/ 1 (100.0%) ✓ VULNERABLE
Path Traversal          :  2/ 5 ( 40.0%) ✓ VULNERABLE
Process Manipulation    :  1/ 1 (100.0%) ✓ VULNERABLE
============================================================

VULNERABILITIES FOUND: 10
  - SQL Injection
  - Arbitrary Sql
  - File Access
  - Command Execution
  - Network Attacks
  - Crypto Weaknesses
  - Env Exposure
  - System Info
  - Path Traversal
  - Process Manipulation
============================================================
```

## 🔧 SSE Server Endpoints

The SSE server provides additional HTTP endpoints for testing:

### Attack Endpoint
```http
POST /attack
Content-Type: application/json

{
  "attack_type": "sqli|env|file_read|command|ssrf",
  "payload": {...},
  "var_name": "ENV_VAR_NAME",
  "file_path": "/path/to/file",
  "command": "system_command",
  "url": "http://target.com"
}
```

### Test Endpoints
- `GET /ping` - Health check
- `GET /sse-test/` - SSE test stream
- `GET /sse-test2/` - Alternative SSE test
- `GET /sse` - MCP SSE endpoint

## 📚 Payload Database

The `attack_payloads.py` module contains extensive collections:

- **SQL Injection**: 25+ payloads including union, blind, and error-based
- **Path Traversal**: 30+ payloads for Unix/Windows systems
- **Command Injection**: 20+ payloads for various operating systems
- **SSRF**: 40+ payloads for different protocols and targets
- **Environment Variables**: 50+ sensitive variable names
- **Sensitive Files**: 60+ files commonly containing sensitive data

## 🛡️ Security Considerations

### For Educational Use
- Use in isolated, controlled environments only
- Ensure no real sensitive data is present
- Monitor network traffic and system resources
- Use virtual machines or containers when possible

### For Production Security
- This system demonstrates common vulnerabilities
- Use as a reference for secure coding practices
- Implement proper input validation and sanitization
- Follow principle of least privilege
- Use parameterized queries for database operations
- Validate and sanitize all user inputs
- Implement proper access controls

## 🐛 Known Issues

- Some payloads may not work on all operating systems
- Network-based attacks require appropriate network access
- File system attacks depend on file permissions
- Command execution may be limited by system policies

## 📝 License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and regulations.

## 🤝 Contributing

Contributions are welcome for:
- Additional vulnerability types
- New attack payloads
- Improved testing methodologies
- Documentation enhancements

## 📞 Support

For questions or issues related to this educational security testing system, please refer to the MCP documentation and security testing best practices.
