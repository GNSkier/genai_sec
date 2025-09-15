#!/usr/bin/env python3
"""
Simple test script to verify the MCP vulnerability demonstration system.
This script performs basic functionality tests without running full attacks.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import mcp
        from mcp.server.fastmcp import FastMCP
        import sqlite3
        import requests
        import psutil

        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_payload_database():
    """Test the attack payload database."""
    print("Testing payload database...")
    try:
        from attack_payloads import ATTACK_PAYLOADS, get_payloads_by_category

        categories = list(ATTACK_PAYLOADS.keys())
        print(f"✓ Found {len(categories)} payload categories: {categories}")

        # Test getting payloads
        sql_payloads = get_payloads_by_category("sql_injection")
        print(f"✓ SQL injection payloads: {len(sql_payloads)}")

        return True
    except Exception as e:
        print(f"✗ Payload database error: {e}")
        return False


def test_stdio_server_syntax():
    """Test that the STDIO server has valid syntax."""
    print("Testing STDIO server syntax...")
    try:
        with open("vuln_mcp_stdio.py", "r") as f:
            code = f.read()
        compile(code, "vuln_mcp_stdio.py", "exec")
        print("✓ STDIO server syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ STDIO server syntax error: {e}")
        return False


def test_sse_server_syntax():
    """Test that the SSE server has valid syntax."""
    print("Testing SSE server syntax...")
    try:
        with open("vuln_mcp_sse.py", "r") as f:
            code = f.read()
        compile(code, "vuln_mcp_sse.py", "exec")
        print("✓ SSE server syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ SSE server syntax error: {e}")
        return False


def test_attack_client_syntax():
    """Test that the attack client has valid syntax."""
    print("Testing attack client syntax...")
    try:
        with open("comprehensive_attack_client.py", "r") as f:
            code = f.read()
        compile(code, "comprehensive_attack_client.py", "exec")
        print("✓ Attack client syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Attack client syntax error: {e}")
        return False


def test_requirements_file():
    """Test that requirements.txt exists and has content."""
    print("Testing requirements file...")
    try:
        if not os.path.exists("requirements.txt"):
            print("✗ requirements.txt not found")
            return False

        with open("requirements.txt", "r") as f:
            content = f.read().strip()

        if not content:
            print("✗ requirements.txt is empty")
            return False

        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("#")
        ]
        print(f"✓ Found {len(lines)} dependencies in requirements.txt")
        return True
    except Exception as e:
        print(f"✗ Requirements file error: {e}")
        return False


def test_database_creation():
    """Test that the database can be created."""
    print("Testing database creation...")
    try:
        import sqlite3

        conn = sqlite3.connect("test_vulnerable_mcp.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            "INSERT INTO test_records (name, address) VALUES ('test', 'test')"
        )
        conn.commit()
        cursor.execute("SELECT * FROM test_records")
        rows = cursor.fetchall()
        conn.close()

        # Clean up
        os.remove("test_vulnerable_mcp.db")

        print("✓ Database creation and operations work")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("Testing file structure...")
    required_files = [
        "vuln_mcp_stdio.py",
        "vuln_mcp_sse.py",
        "comprehensive_attack_client.py",
        "attack_payloads.py",
        "requirements.txt",
        "README.md",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False

    print("✓ All required files exist")
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("MCP Vulnerability System Implementation Test")
    print("=" * 50)

    tests = [
        test_file_structure,
        test_imports,
        test_payload_database,
        test_stdio_server_syntax,
        test_sse_server_syntax,
        test_attack_client_syntax,
        test_requirements_file,
        test_database_creation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed! The implementation is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run STDIO server: python vuln_mcp_stdio.py")
        print(
            "3. Run attack client: python comprehensive_attack_client.py vuln_mcp_stdio.py"
        )
    else:
        print("✗ Some tests failed. Please fix the issues before proceeding.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
