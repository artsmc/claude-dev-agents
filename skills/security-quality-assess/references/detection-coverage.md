# Detection Coverage

### OWASP Top 10 (2021)

✅ **A01 - Broken Access Control**
- Missing authentication decorators
- Unauthenticated route handlers

✅ **A02 - Cryptographic Failures**
- Hardcoded secrets (AWS keys, API tokens, passwords)
- Weak cryptography (MD5, SHA1, DES)
- High-entropy strings (potential secrets)

✅ **A03 - Injection**
- SQL injection (string concatenation in queries)
- Command injection (shell=True, os.system)
- Code injection (eval, exec, compile)
- XSS (innerHTML, dangerouslySetInnerHTML)

✅ **A04 - Insecure Design**
- PII exposure in logs
- Unencrypted sensitive data storage

✅ **A05 - Security Misconfiguration**
- Debug mode enabled in production
- Insecure CORS configurations
- Missing security headers

✅ **A06 - Vulnerable Components**
- Known CVEs from OSV database
- Outdated dependencies with security issues

✅ **A07 - Authentication Failures**
- Weak JWT secrets
- Insecure session cookies
- Hardcoded passwords
