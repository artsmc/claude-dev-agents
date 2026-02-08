"""Test fixture: Python secrets and weak cryptography.

THIS FILE CONTAINS INTENTIONALLY VULNERABLE CODE FOR TESTING PURPOSES.
All credentials are synthetic/fake and used solely to validate the
SecretsAnalyzer detection capabilities.

Expected detections by SecretsAnalyzer:
  - hardcoded-aws-key (CRITICAL, line ~14)
  - hardcoded-github-token (CRITICAL, line ~18)
  - hardcoded-api-key (HIGH, line ~22)
  - high-entropy-string (HIGH, line ~26)
  - weak-crypto-md5 (MEDIUM, line ~35)
  - weak-crypto-sha1 (MEDIUM, line ~39)

Total expected findings: 6
"""

# VULN: Hardcoded AWS access key (matches AKIA[0-9A-Z]{16})
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLEQ"

# VULN: Hardcoded GitHub personal access token (matches ghp_[a-zA-Z0-9]{36})
GITHUB_TOKEN = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789"

# VULN: Generic API key assignment (matches api_key = "...", 32+ chars)
api_key = "aB3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA"

# VULN: High-entropy string that should be detected (entropy > 4.5, len >= 20)
INTERNAL_TOKEN = "r8Kp2Lm4Qn6Sv8Uw0Yx3Ab5Cd7Ef9Gh"

# Safe: This should NOT be flagged (loaded from environment)
import os
SAFE_KEY = os.environ.get("API_KEY", "default")


# --- Weak Cryptography ---

import hashlib

# VULN: MD5 usage (weak hash algorithm)
def hash_password_md5(password):
    return hashlib.md5(password.encode()).hexdigest()

# VULN: SHA-1 usage (weak hash algorithm)
def hash_data_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()

# Safe: SHA-256 is acceptable
def hash_data_safe(data):
    return hashlib.sha256(data.encode()).hexdigest()


# --- Safe patterns that should NOT trigger ---

# Safe: URL (false positive filter should exclude)
DOCS_URL = "https://docs.example.com/api/v2/long/path/to/resource"

# Safe: File path
CONFIG_PATH = "/etc/myapp/configuration/secrets/vault.yml"

# Safe: UUID
REQUEST_ID = "550e8400-e29b-41d4-a716-446655440000"
