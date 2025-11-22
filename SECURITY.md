# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of nadoo-plugin-sdk seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before we have released a fix
- Exploit the vulnerability beyond what is necessary to demonstrate it
- Distribute malicious plugins as proof of concept

### Please DO:

1. **Email us directly** at **security@nadoo.ai**
2. Include a detailed description of the vulnerability
3. Provide steps to reproduce the issue
4. Include any proof-of-concept code (if applicable)
5. Suggest a fix or mitigation (if you have one)

### What to Include in Your Report

A good security report should include:

- **Description**: What is the vulnerability?
- **Impact**: What can an attacker do with this vulnerability?
- **Affected Versions**: Which versions are affected?
- **Reproduction Steps**: How to reproduce the vulnerability?
- **Proof of Concept**: Code demonstrating the issue (optional but helpful)
- **Suggested Fix**: Your ideas for fixing it (optional)

Example:
```
Subject: [SECURITY] Potential code injection in plugin loader

Description:
Plugin loading mechanism may allow arbitrary code execution
if malicious plugin packages are installed.

Impact:
An attacker could execute malicious code by distributing
a crafted .nadoo-plugin file.

Affected Versions:
0.1.0 and earlier

Steps to Reproduce:
1. Create malicious plugin with __init__ code execution
2. Build as .nadoo-plugin
3. Install to workspace
4. Observe code execution on import

Suggested Fix:
Implement sandboxed loading with RestrictedPython or isolated processes.
```

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Updates**: Every 72 hours
- **Resolution Timeline**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

## Disclosure Policy

Once we have a fix ready:

1. We will notify you
2. We will coordinate disclosure timing with you
3. We will release a security advisory
4. We will credit you in the advisory (unless you prefer to remain anonymous)
5. We will release a patched version

---

## Security Best Practices for Plugin Developers

### 1. Input Validation

Always validate user inputs in your plugin tools:

```python
from nadoo_plugin import NadooPlugin, tool, parameter

class MyPlugin(NadooPlugin):
    @tool(name="process_data")
    @parameter("url", type="string", required=True)
    def process_data(self, url: str) -> dict:
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL scheme")

        # Validate URL length
        if len(url) > 2048:
            raise ValueError("URL too long")

        # Use whitelist of allowed domains (if applicable)
        allowed_domains = ["example.com", "api.example.com"]
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if domain not in allowed_domains:
            raise ValueError(f"Domain {domain} not allowed")

        # Process safely
        return {"url": url}
```

### 2. Avoid Code Injection

Never use `eval()`, `exec()`, or `__import__()` with user input:

```python
# ❌ DANGEROUS - Never do this
def bad_example(self, code: str) -> dict:
    result = eval(code)  # CODE INJECTION!
    return {"result": result}

# ✅ SAFE - Use safe alternatives
def good_example(self, expression: str) -> dict:
    # Use a safe expression evaluator
    import ast
    try:
        tree = ast.parse(expression, mode='eval')
        # Only allow simple expressions
        if not isinstance(tree.body, (ast.Constant, ast.BinOp, ast.UnaryOp)):
            raise ValueError("Complex expressions not allowed")
        result = eval(compile(tree, '<string>', 'eval'))
        return {"result": result}
    except SyntaxError:
        raise ValueError("Invalid expression")
```

### 3. Secure API Keys and Secrets

Never hardcode secrets in your plugin:

```python
import os

class MyPlugin(NadooPlugin):
    def on_initialize(self):
        # ✅ GOOD - Use environment variables
        self.api_key = self.require_env("MY_API_KEY")

        # ❌ BAD - Never hardcode
        # self.api_key = "sk-1234567890"  # DON'T DO THIS!

    @tool(name="call_api")
    def call_api(self, query: str) -> dict:
        # Use the API key from environment
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # ...
```

### 4. Sanitize File Paths

Prevent path traversal attacks:

```python
import os
from pathlib import Path

class MyPlugin(NadooPlugin):
    @tool(name="read_file")
    @parameter("filename", type="string", required=True)
    def read_file(self, filename: str) -> dict:
        # ❌ DANGEROUS - Path traversal vulnerability
        # content = open(filename).read()

        # ✅ SAFE - Validate and sanitize path
        base_dir = Path("/safe/plugin/directory")
        file_path = (base_dir / filename).resolve()

        # Ensure path is within base directory
        if not str(file_path).startswith(str(base_dir)):
            raise ValueError("Path traversal detected")

        # Check file exists and is a file
        if not file_path.is_file():
            raise FileNotFoundError("File not found")

        content = file_path.read_text()
        return {"content": content}
```

### 5. Rate Limiting

Implement rate limiting for expensive operations:

```python
from time import time
from collections import defaultdict

class MyPlugin(NadooPlugin):
    def on_initialize(self):
        self.rate_limit_cache = defaultdict(list)

    def check_rate_limit(self, user_id: str, limit: int = 10, window: int = 60):
        """Check if user has exceeded rate limit"""
        now = time()
        # Clean old requests
        self.rate_limit_cache[user_id] = [
            req_time for req_time in self.rate_limit_cache[user_id]
            if now - req_time < window
        ]

        # Check limit
        if len(self.rate_limit_cache[user_id]) >= limit:
            raise ValueError(f"Rate limit exceeded: {limit} requests per {window}s")

        # Record request
        self.rate_limit_cache[user_id].append(now)

    @tool(name="expensive_operation")
    def expensive_operation(self, data: str) -> dict:
        # Apply rate limiting
        user_id = self.context.user_id or "anonymous"
        self.check_rate_limit(user_id, limit=10, window=60)

        # Perform operation
        # ...
```

### 6. Safe External Requests

Validate and secure external HTTP requests:

```python
import httpx

class MyPlugin(NadooPlugin):
    @tool(name="fetch_url")
    @parameter("url", type="string", required=True)
    def fetch_url(self, url: str) -> dict:
        # Validate URL
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL scheme")

        # Prevent SSRF attacks
        from urllib.parse import urlparse
        parsed = urlparse(url)

        # Block private IPs
        blocked_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        if parsed.hostname in blocked_hosts:
            raise ValueError("Access to private IPs not allowed")

        # Use timeout
        try:
            response = httpx.get(
                url,
                timeout=10.0,  # 10 second timeout
                follow_redirects=False,  # Don't follow redirects
                headers={"User-Agent": "NadooPlugin/0.1.0"}
            )
            response.raise_for_status()
            return {"content": response.text}
        except httpx.TimeoutException:
            raise ValueError("Request timed out")
        except httpx.HTTPError as e:
            raise ValueError(f"HTTP error: {e}")
```

### 7. Logging Best Practices

Don't log sensitive information:

```python
class MyPlugin(NadooPlugin):
    @tool(name="process_user_data")
    @parameter("api_key", type="string", required=True)
    @parameter("user_email", type="string", required=True)
    def process_user_data(self, api_key: str, user_email: str) -> dict:
        # ❌ BAD - Logs sensitive data
        # self.context.log(f"Processing with key: {api_key}")
        # self.context.log(f"User email: {user_email}")

        # ✅ GOOD - Log without sensitive data
        self.context.log("Processing user data")
        self.context.log_debug(f"User email hash: {hash(user_email)}")

        # Process safely
        # ...
```

### 8. Error Handling

Don't expose internal details in error messages:

```python
class MyPlugin(NadooPlugin):
    @tool(name="connect_database")
    def connect_database(self, connection_string: str) -> dict:
        try:
            # Database connection
            conn = self._connect(connection_string)
            return {"status": "connected"}
        except Exception as e:
            # ❌ BAD - Exposes internal details
            # raise ValueError(f"Connection failed: {connection_string} - {e}")

            # ✅ GOOD - Generic error message
            self.context.log_error(f"Database connection failed: {type(e).__name__}")
            return {"error": "Database connection failed", "status": "error"}
```

---

## Security Checklist for Plugin Authors

Before publishing your plugin:

- [ ] All secrets are in environment variables, not hardcoded
- [ ] User inputs are validated and sanitized
- [ ] No use of `eval()`, `exec()`, or `__import__()` with user input
- [ ] File path operations are protected against traversal
- [ ] External requests validate URLs and use timeouts
- [ ] Rate limiting is implemented for expensive operations
- [ ] Error messages don't leak sensitive information
- [ ] Logging doesn't include secrets or PII
- [ ] Dependencies are up to date and audited
- [ ] Plugin has been tested with malicious inputs

## Security Checklist for Plugin Users

Before installing a plugin:

- [ ] Plugin is from a trusted source
- [ ] Plugin code has been reviewed (if possible)
- [ ] Plugin permissions are reasonable
- [ ] Plugin dependencies are trustworthy
- [ ] Plugin is actively maintained
- [ ] No known security vulnerabilities

## Known Security Considerations

### 1. Plugin Code Execution

Plugins execute Python code with access to system resources:

- **Risk**: Malicious plugins can execute arbitrary code
- **Mitigation**: Only install trusted plugins, review code, use sandboxed execution (future)

### 2. Dependency Vulnerabilities

Plugins may depend on vulnerable packages:

- **Risk**: Vulnerabilities in dependencies
- **Mitigation**: Regularly update dependencies, use `pip-audit` or similar tools

### 3. Data Access

Plugins can access workspace data:

- **Risk**: Unauthorized data access or exfiltration
- **Mitigation**: Review plugin permissions, implement audit logging (future)

## Contact

- **Security Email**: security@nadoo.ai
- **General Contact**: dev@nadoo.ai
- **GitHub**: https://github.com/nadoo-ai/nadoo-plugin-sdk/security/advisories

## Credits

We thank the security researchers who have responsibly disclosed vulnerabilities:

- (No vulnerabilities reported yet)

## Updates

This security policy may be updated from time to time. Please check back regularly.

**Last Updated**: 2025-11-22
