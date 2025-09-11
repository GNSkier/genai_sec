from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import subprocess
import requests
import hashlib
import random
import string
import socket
import psutil
import json
from pathlib import Path

# Initialize the MCP server
mcp = FastMCP("Vulnerable MCP Server")

# Database setup
DB_NAME = "vulnerable_mcp.db"


def setup_database():
    """Create the SQLite database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            credit_card TEXT
        )
    """
    )
    # Insert some sample data
    cursor.execute("DELETE FROM records")
    cursor.execute(
        "INSERT INTO records (name, address, email, phone, credit_card) VALUES ('Alice Johnson', '123 Main St', 'alice@example.com', '555-0123', '4532-1234-5678-9012')"
    )
    cursor.execute(
        "INSERT INTO records (name, address, email, phone, credit_card) VALUES ('Bob Smith', '456 Oak Ave', 'bob@example.com', '555-0456', '5555-1234-5678-9012')"
    )
    cursor.execute(
        "INSERT INTO records (name, address, email, phone, credit_card) VALUES ('Carol Davis', '789 Pine Rd', 'carol@example.com', '555-0789', '6011-1234-5678-9012')"
    )
    conn.commit()
    conn.close()


# SQL Injection Vulnerabilities
@mcp.tool()
def insert_record(
    name: str,
    address: str,
    email: str = "",
    phone: str = "",
    credit_card: str = "",
) -> str:
    """Insert a new record into the database with SQL injection vulnerability."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO records (name, address, email, phone, credit_card) VALUES ('{name}', '{address}', '{email}', '{phone}', '{credit_card}')"
    )
    conn.commit()
    conn.close()
    return (
        f"Record inserted: {name}, {address}, {email}, {phone}, {credit_card}"
    )


@mcp.tool()
def execute_sql(query: str) -> str:
    """Execute arbitrary SQL queries with no restrictions."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    result = cursor.execute(query).fetchall()
    conn.commit()
    conn.close()
    return str(result)


@mcp.tool()
def search_records(search_term: str) -> str:
    """Search records with SQL injection vulnerability."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM records WHERE name LIKE '%{search_term}%' OR address LIKE '%{search_term}%'"
    )
    rows = cursor.fetchall()
    conn.close()
    return "\n".join(
        [
            f"ID: {row[0]}, Name: {row[1]}, Address: {row[2]}, Email: {row[3]}, Phone: {row[4]}, CC: {row[5]}"
            for row in rows
        ]
    )


# Environment Variable Exposure
@mcp.tool()
def get_env_variable(var_name: str) -> str:
    """Retrieve the value of an environment variable."""
    return os.getenv(var_name, "Variable not found")


@mcp.tool()
def list_all_env_vars() -> str:
    """List all environment variables (exposes sensitive information)."""
    return json.dumps(dict(os.environ), indent=2)


# File System Vulnerabilities
@mcp.tool()
def read_file(file_path: str) -> str:
    """Read any file from the filesystem (path traversal vulnerability)."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write content to any file (path traversal vulnerability)."""
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return f"Content written to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List directory contents (path traversal vulnerability)."""
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing directory: {e}"


@mcp.tool()
def delete_file(file_path: str) -> str:
    """Delete any file (path traversal vulnerability)."""
    try:
        os.remove(file_path)
        return f"File {file_path} deleted"
    except Exception as e:
        return f"Error deleting file: {e}"


# Command Execution Vulnerabilities
@mcp.tool()
def execute_command(command: str) -> str:
    """Execute arbitrary system commands."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return f"Exit Code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error executing command: {e}"


@mcp.tool()
def kill_process(pid: str) -> str:
    """Kill a process by PID."""
    try:
        os.kill(int(pid), 9)
        return f"Process {pid} terminated"
    except Exception as e:
        return f"Error killing process: {e}"


@mcp.tool()
def list_processes() -> str:
    """List all running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "username", "cmdline"]):
            processes.append(
                f"PID: {proc.info['pid']}, Name: {proc.info['name']}, User: {proc.info['username']}, CMD: {' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'}"
            )
        return "\n".join(processes)
    except Exception as e:
        return f"Error listing processes: {e}"


# Network Vulnerabilities (SSRF)
@mcp.tool()
def make_request(
    url: str, method: str = "GET", data: str = "", headers: str = ""
) -> str:
    """Make HTTP requests to any URL (SSRF vulnerability)."""
    try:
        headers_dict = {}
        if headers:
            headers_dict = json.loads(headers)

        response = requests.request(
            method, url, data=data, headers=headers_dict, timeout=10
        )
        return f"Status: {response.status_code}\nHeaders: {dict(response.headers)}\nContent: {response.text[:1000]}"
    except Exception as e:
        return f"Error making request: {e}"


@mcp.tool()
def scan_port(host: str, port: int) -> str:
    """Scan a port on any host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return "Open" if result == 0 else "Closed"
    except Exception as e:
        return f"Error scanning port: {e}"


@mcp.tool()
def port_scan_range(host: str, start_port: int, end_port: int) -> str:
    """Scan a range of ports on any host."""
    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    return f"Open ports on {host}: {open_ports}"


# Cryptographic Weaknesses
@mcp.tool()
def generate_hash(data: str, algorithm: str = "md5") -> str:
    """Generate hash using weak algorithms."""
    try:
        hasher = getattr(hashlib, algorithm)()
        hasher.update(data.encode())
        return hasher.hexdigest()
    except Exception as e:
        return f"Error generating hash: {e}"


@mcp.tool()
def generate_token(length: int = 8) -> str:
    """Generate weak random token."""
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


@mcp.tool()
def weak_encrypt(data: str, key: str = "defaultkey") -> str:
    """Weak encryption using simple XOR."""
    try:
        encrypted = ""
        for i, char in enumerate(data):
            encrypted += chr(ord(char) ^ ord(key[i % len(key)]))
        return encrypted.encode("utf-8").hex()
    except Exception as e:
        return f"Error encrypting: {e}"


# Database Connection Vulnerabilities
@mcp.tool()
def connect_database(connection_string: str, query: str) -> str:
    """Connect to any database and execute queries."""
    try:
        conn = sqlite3.connect(connection_string)
        cursor = conn.cursor()
        result = cursor.execute(query).fetchall()
        conn.close()
        return str(result)
    except Exception as e:
        return f"Error connecting to database: {e}"


# System Information Exposure
@mcp.tool()
def get_system_info() -> str:
    """Get detailed system information."""
    try:
        info = {
            "platform": os.name,
            "current_user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "current_directory": os.getcwd(),
            "python_version": os.sys.version,
            "environment_variables": dict(os.environ),
            "cpu_count": os.cpu_count(),
            "memory_info": (
                dict(psutil.virtual_memory()._asdict())
                if hasattr(psutil, "virtual_memory")
                else "N/A"
            ),
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting system info: {e}"


@mcp.tool()
def get_network_interfaces() -> str:
    """Get network interface information."""
    try:
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {"name": interface, "addresses": []}
            for addr in addrs:
                interface_info["addresses"].append(
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                )
            interfaces.append(interface_info)
        return json.dumps(interfaces, indent=2)
    except Exception as e:
        return f"Error getting network interfaces: {e}"


# Logging Vulnerabilities
@mcp.tool()
def log_sensitive_data(data: str, log_level: str = "INFO") -> str:
    """Log sensitive data without sanitization."""
    log_entry = f"[{log_level}] Sensitive data: {data}"
    try:
        with open("sensitive.log", "a") as f:
            f.write(log_entry + "\n")
        return f"Logged: {log_entry}"
    except Exception as e:
        return f"Error logging: {e}"


@mcp.tool()
def read_logs(log_file: str = "sensitive.log") -> str:
    """Read log files."""
    try:
        with open(log_file, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading logs: {e}"


if __name__ == "__main__":
    setup_database()
    print("Starting Vulnerable MCP Server with STDIO transport...")
    print("Available tools:")
    print("- insert_record: SQL injection vulnerability")
    print("- execute_sql: Arbitrary SQL execution")
    print("- search_records: SQL injection in search")
    print("- get_env_variable: Environment variable exposure")
    print("- list_all_env_vars: Full environment dump")
    print("- read_file: Path traversal vulnerability")
    print("- write_file: Path traversal vulnerability")
    print("- list_directory: Directory traversal")
    print("- delete_file: File deletion vulnerability")
    print("- execute_command: Command injection")
    print("- kill_process: Process termination")
    print("- list_processes: Process enumeration")
    print("- make_request: SSRF vulnerability")
    print("- scan_port: Port scanning")
    print("- port_scan_range: Port range scanning")
    print("- generate_hash: Weak cryptographic functions")
    print("- generate_token: Weak random generation")
    print("- weak_encrypt: Weak encryption")
    print("- connect_database: Database connection vulnerability")
    print("- get_system_info: System information exposure")
    print("- get_network_interfaces: Network information exposure")
    print("- log_sensitive_data: Logging vulnerability")
    print("- read_logs: Log file access")
    mcp.run(transport="stdio")
