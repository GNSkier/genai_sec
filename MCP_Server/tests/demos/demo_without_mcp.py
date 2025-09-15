#!/usr/bin/env python3
"""
Demonstration script that shows the MCP vulnerability system without requiring MCP installation.
This script simulates the vulnerable tools and demonstrates the attack patterns.
"""

import sqlite3
import os
import subprocess
import requests
import hashlib
import random
import string
import json
import sys
from pathlib import Path


class VulnerableMCPSimulator:
    """Simulates the vulnerable MCP server functionality for demonstration."""

    def __init__(self):
        self.db_name = "demo_vulnerable_mcp.db"
        self.setup_database()

    def setup_database(self):
        """Create the SQLite database and table if they don't exist."""
        conn = sqlite3.connect(self.db_name)
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
        print("✓ Database initialized with sample data")

    def vulnerable_insert_record(
        self, name, address, email="", phone="", credit_card=""
    ):
        """Vulnerable insert function with SQL injection."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            # VULNERABLE: Direct string concatenation
            cursor.execute(
                f"INSERT INTO records (name, address, email, phone, credit_card) VALUES ('{name}', '{address}', '{email}', '{phone}', '{credit_card}')"
            )
            conn.commit()
            return f"Record inserted: {name}, {address}, {email}, {phone}, {credit_card}"
        except Exception as e:
            return f"SQL ERROR: {e}"
        finally:
            conn.close()

    def vulnerable_execute_sql(self, query):
        """Vulnerable SQL execution function."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            result = cursor.execute(query).fetchall()
            conn.commit()
            return str(result)
        except Exception as e:
            return f"SQL ERROR: {e}"
        finally:
            conn.close()

    def vulnerable_read_file(self, file_path):
        """Vulnerable file reading with path traversal."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def vulnerable_execute_command(self, command):
        """Vulnerable command execution."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=5
            )
            return f"Exit Code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error executing command: {e}"

    def vulnerable_make_request(self, url):
        """Vulnerable HTTP request (SSRF)."""
        try:
            response = requests.get(url, timeout=5)
            return f"Status: {response.status_code}\nContent: {response.text[:200]}"
        except Exception as e:
            return f"Error making request: {e}"

    def get_env_variable(self, var_name):
        """Get environment variable."""
        return os.getenv(var_name, "Variable not found")

    def weak_generate_hash(self, data, algorithm="md5"):
        """Generate hash using weak algorithms."""
        try:
            hasher = getattr(hashlib, algorithm)()
            hasher.update(data.encode())
            return hasher.hexdigest()
        except Exception as e:
            return f"Error generating hash: {e}"


def demonstrate_sql_injection():
    """Demonstrate SQL injection attacks."""
    print("\n" + "=" * 60)
    print("SQL INJECTION DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    # Normal usage
    print("\n1. Normal usage:")
    result = simulator.vulnerable_insert_record(
        "John Doe",
        "123 Main St",
        "john@example.com",
        "555-0123",
        "4532-1234-5678-9012",
    )
    print(f"   Result: {result}")

    # SQL injection attacks
    print("\n2. SQL Injection attacks:")
    injection_payloads = [
        "test');--",
        "' OR 1=1 --",
        "Robert'); DROP TABLE records;--",
        "' UNION SELECT 1, 'pwned', 'pwned', 'pwned', 'pwned'--",
    ]

    for i, payload in enumerate(injection_payloads, 1):
        print(f"\n   Attack {i}: {payload}")
        result = simulator.vulnerable_insert_record(payload, "123 Exploit St")
        print(f"   Result: {result}")

    # Show current database state
    print("\n3. Current database state:")
    result = simulator.vulnerable_execute_sql("SELECT * FROM records")
    print(f"   Records: {result}")


def demonstrate_file_traversal():
    """Demonstrate path traversal attacks."""
    print("\n" + "=" * 60)
    print("PATH TRAVERSAL DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    # Create a test file
    with open("test_file.txt", "w") as f:
        f.write("This is a test file with sensitive information.")

    print("\n1. Normal file reading:")
    result = simulator.vulnerable_read_file("test_file.txt")
    print(f"   Result: {result}")

    # Path traversal attempts
    print("\n2. Path traversal attempts:")
    traversal_payloads = [
        "../test_file.txt",
        "../../test_file.txt",
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
    ]

    for i, payload in enumerate(traversal_payloads, 1):
        print(f"\n   Attack {i}: {payload}")
        result = simulator.vulnerable_read_file(payload)
        print(f"   Result: {result[:100]}...")

    # Clean up
    os.remove("test_file.txt")


def demonstrate_command_injection():
    """Demonstrate command injection attacks."""
    print("\n" + "=" * 60)
    print("COMMAND INJECTION DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    print("\n1. Normal command execution:")
    result = simulator.vulnerable_execute_command("echo 'Hello World'")
    print(f"   Result: {result}")

    # Command injection attempts
    print("\n2. Command injection attempts:")
    injection_payloads = [
        "whoami",
        "id",
        "ls -la",
        "dir",
        "echo 'command injection test'",
    ]

    for i, payload in enumerate(injection_payloads, 1):
        print(f"\n   Attack {i}: {payload}")
        result = simulator.vulnerable_execute_command(payload)
        print(f"   Result: {result}")


def demonstrate_ssrf():
    """Demonstrate SSRF attacks."""
    print("\n" + "=" * 60)
    print("SSRF (SERVER-SIDE REQUEST FORGERY) DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    print("\n1. SSRF attack attempts:")
    ssrf_payloads = [
        "http://localhost:22",
        "http://127.0.0.1:80",
        "http://httpbin.org/get",
        "file:///etc/passwd",
    ]

    for i, payload in enumerate(ssrf_payloads, 1):
        print(f"\n   Attack {i}: {payload}")
        result = simulator.vulnerable_make_request(payload)
        print(f"   Result: {result}")


def demonstrate_env_exposure():
    """Demonstrate environment variable exposure."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLE EXPOSURE DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    print("\n1. Environment variable exposure:")
    env_vars = ["PATH", "USER", "HOME", "SECRET_KEY", "API_KEY", "DATABASE_URL"]

    for var in env_vars:
        result = simulator.get_env_variable(var)
        print(f"   {var}: {result}")


def demonstrate_crypto_weaknesses():
    """Demonstrate cryptographic weaknesses."""
    print("\n" + "=" * 60)
    print("CRYPTOGRAPHIC WEAKNESSES DEMONSTRATION")
    print("=" * 60)

    simulator = VulnerableMCPSimulator()

    print("\n1. Weak cryptographic algorithms:")
    test_data = "sensitive_data_123"
    weak_algos = ["md5", "sha1", "sha224"]

    for algo in weak_algos:
        result = simulator.weak_generate_hash(test_data, algo)
        print(f"   {algo.upper()}: {result}")


def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("MCP VULNERABILITY SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows various security vulnerabilities")
    print("that could be present in an MCP server implementation.")
    print("=" * 60)

    try:
        demonstrate_sql_injection()
        demonstrate_file_traversal()
        demonstrate_command_injection()
        demonstrate_ssrf()
        demonstrate_env_exposure()
        demonstrate_crypto_weaknesses()

        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("This demonstration showed various security vulnerabilities:")
        print("• SQL Injection - Direct string concatenation in SQL queries")
        print("• Path Traversal - Unvalidated file path access")
        print("• Command Injection - Unsafe command execution")
        print("• SSRF - Server-side request forgery")
        print("• Environment Exposure - Sensitive environment variable access")
        print("• Crypto Weaknesses - Use of weak cryptographic algorithms")
        print("\nIn a real MCP server, these vulnerabilities could lead to:")
        print("• Data breaches and unauthorized access")
        print("• System compromise and remote code execution")
        print("• Network reconnaissance and internal system access")
        print("• Credential theft and privilege escalation")

    except Exception as e:
        print(f"Error during demonstration: {e}")
        return 1

    finally:
        # Clean up
        if os.path.exists("demo_vulnerable_mcp.db"):
            os.remove("demo_vulnerable_mcp.db")

    return 0


if __name__ == "__main__":
    sys.exit(main())
