import os
import sqlite3
import sys
import asyncio
import subprocess
import requests
import hashlib
import random
import string
import socket
import psutil
import json
from pathlib import Path

# Windows event loop fix for asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from mcp.server.fastmcp import FastMCP
from sse_starlette.sse import EventSourceResponse

# Import the sanitizer agent
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.sanitizer_agent import SanitizerAgent

# Database setup
DB_NAME = "vulnerable_mcp_sse.db"


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


app = FastAPI()
mcp = FastMCP("Vulnerable SSE MCP Server")

print("[SERVER] Module loaded")


# Attack endpoint for direct exploitation
@app.post("/attack")
async def attack_endpoint(request: Request):
    """Direct attack endpoint for various vulnerability demonstrations."""
    data = await request.json()
    attack_type = data.get("attack_type")

    # Always reset database for consistent testing
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS records")
        cursor.execute(
            """
            CREATE TABLE records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                credit_card TEXT
            )
        """
        )
        conn.commit()
    except Exception as e:
        return JSONResponse(
            {"error": f"Table recreate error: {e}"}, status_code=500
        )
    conn.close()

    if attack_type == "sqli":
        # SQL Injection attack
        payload = data.get(
            "payload",
            {
                "name": "attacker', '123 exploit st'); DROP TABLE records;--",
                "address": "hacked",
            },
        )
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.executescript(
                f"INSERT INTO records (name, address) VALUES ('{payload['name']}', '{payload['address']}')"
            )
            conn.commit()
            # Try to query the table after attack
            try:
                cursor.execute("SELECT * FROM records")
                rows = cursor.fetchall()
                result = {"sqli": "failed", "rows": rows}
            except Exception as e:
                result = {"sqli": "success", "error": str(e)}
            conn.close()
        except Exception as e:
            result = {"sqli": "success", "error": str(e)}
        return JSONResponse(result)

    elif attack_type == "env":
        var_name = data.get("var_name", "SECRET_KEY")
        value = os.environ.get(var_name, "Not found")
        return JSONResponse({"env_var": var_name, "value": value})

    elif attack_type == "file_read":
        file_path = data.get("file_path", "/etc/passwd")
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return JSONResponse(
                {"file_path": file_path, "content": content[:1000]}
            )
        except Exception as e:
            return JSONResponse({"file_path": file_path, "error": str(e)})

    elif attack_type == "command":
        command = data.get("command", "whoami")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )
            return JSONResponse(
                {
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
        except Exception as e:
            return JSONResponse({"command": command, "error": str(e)})

    elif attack_type == "ssrf":
        url = data.get("url", "http://localhost:22")
        try:
            response = requests.get(url, timeout=5)
            return JSONResponse(
                {
                    "url": url,
                    "status_code": response.status_code,
                    "content": response.text[:500],
                }
            )
        except Exception as e:
            return JSONResponse({"url": url, "error": str(e)})

    else:
        return JSONResponse({"error": "Unknown attack_type"}, status_code=400)


# SSE test endpoints
@app.get("/ping")
def ping():
    print("[SERVER] /ping endpoint called")
    return {"pong": True}


@app.get("/sse-test/")
async def sse_test():
    print("[SERVER] /sse-test/ endpoint entered")

    async def event_gen():
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
            message = {
                "mcp_event": "update",
                "count": i,
                "timestamp": asyncio.get_event_loop().time(),
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[SERVER] /sse-test/ yielding message {i}")

    return EventSourceResponse(event_gen())


@app.get("/sse-test2/")
async def sse_test2():
    print("[SERVER] /sse-test2/ endpoint entered")

    async def event_gen():
        print("[SERVER] /sse-test2/ generator created")
        i = 0
        while True:
            await asyncio.sleep(1)
            msg = f"data: starlette test message {i}\n\n"
            print(f"[SERVER] /sse-test2/ yielding: {msg.strip()}")
            yield msg.encode()
            i += 1

    return StreamingResponse(event_gen(), media_type="text/event-stream")


# Mount the SSE server
from mcp.server.sse import create_sse_server

app.mount("/sse", create_sse_server(mcp))


@app.on_event("startup")
def on_startup():
    setup_database()


@app.get("/")
def read_root():
    return {
        "message": "Vulnerable MCP SSE Server",
        "endpoints": {
            "attack": "/attack",
            "ping": "/ping",
            "sse_test": "/sse-test/",
            "sse_test2": "/sse-test2/",
            "mcp_sse": "/sse",
        },
        "attack_types": ["sqli", "env", "file_read", "command", "ssrf"],
    }


# All the same vulnerable tools as STDIO server
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
    try:
        cursor.execute(
            f"INSERT INTO records (name, address, email, phone, credit_card) VALUES ('{name}', '{address}', '{email}', '{phone}', '{credit_card}')"
        )
        conn.commit()
        result = f"Record inserted: {name}, {address}, {email}, {phone}, {credit_card}"
    except Exception as e:
        result = f"SQL ERROR: {e}"
    conn.close()
    return result


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


@mcp.tool()
def get_env_variable(var_name: str) -> str:
    """Retrieve the value of an environment variable."""
    return os.getenv(var_name, "Variable not found")


@mcp.tool()
def list_all_env_vars() -> str:
    """List all environment variables (exposes sensitive information)."""
    return json.dumps(dict(os.environ), indent=2)


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
def generate_hash(data: str, algorithm: str = "md5") -> str:
    """Generate hash using weak algorithms."""
    try:
        hasher = getattr(hashlib, algorithm)()
        hasher.update(data.encode())
        return hasher.hexdigest()
    except Exception as e:
        return f"Error generating hash: {e}"


@mcp.tool()
def get_system_info() -> str:
    """Get detailed system information."""
    try:
        info = {
            "platform": os.name,
            "current_user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "current_directory": os.getcwd(),
            "python_version": sys.version,
            "environment_variables": dict(os.environ),
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting system info: {e}"


# PII Sanitization Tools
@mcp.tool()
def detect_pii(text: str) -> str:
    """Detect PII in the given text using enhanced detection methods."""
    try:
        agent = SanitizerAgent()
        detection_summary = agent.detect_pii(text)
        return json.dumps(detection_summary, indent=2)
    except Exception as e:
        return f"Error detecting PII: {e}"


@mcp.tool()
def sanitize_text(text: str, redaction_type: str = "generic") -> str:
    """Sanitize text by redacting detected PII. Options: generic, mask, remove."""
    try:
        agent = SanitizerAgent()
        result = agent.sanitize_text(text, redaction_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sanitizing text: {e}"


@mcp.tool()
def get_sanitization_report(text: str) -> str:
    """Get a detailed report of what PII would be detected and sanitized."""
    try:
        agent = SanitizerAgent()
        report = agent.get_sanitization_report(text)
        return json.dumps(report, indent=2)
    except Exception as e:
        return f"Error generating sanitization report: {e}"


@mcp.tool()
def sanitize_file(file_path: str, redaction_type: str = "generic") -> str:
    """Sanitize a file by redacting detected PII. Returns sanitized content."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        agent = SanitizerAgent()
        result = agent.sanitize_text(content, redaction_type)

        # Write sanitized content to a new file
        sanitized_path = file_path + ".sanitized"
        with open(sanitized_path, "w", encoding="utf-8") as f:
            f.write(result["sanitized_text"])

        return json.dumps(
            {
                "original_file": file_path,
                "sanitized_file": sanitized_path,
                "pii_detected": result["pii_detected"],
                "detection_summary": result["detection_summary"],
            },
            indent=2,
        )
    except Exception as e:
        return f"Error sanitizing file: {e}"


if __name__ == "__main__":
    setup_database()
    print("[SERVER] Starting FastAPI app on port 9000...")
    print("Available endpoints:")
    print("- POST /attack - Direct attack endpoint")
    print("- GET /ping - Health check")
    print("- GET /sse-test/ - SSE test endpoint")
    print("- GET /sse-test2/ - Alternative SSE test")
    print("- GET /sse - MCP SSE endpoint")
    print("Attack types: sqli, env, file_read, command, ssrf")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
