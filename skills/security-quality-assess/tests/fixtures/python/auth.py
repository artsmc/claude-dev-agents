"""Test fixture: Python authentication vulnerabilities.

THIS FILE CONTAINS INTENTIONALLY VULNERABLE CODE FOR TESTING PURPOSES.
All code patterns are designed to validate the AuthAnalyzer detection
capabilities.

Expected detections by AuthAnalyzer:
  - hardcoded-password (CRITICAL, line ~21) - password variable
  - hardcoded-password (CRITICAL, line ~24) - secret_key variable
  - weak-jwt-secret (HIGH, line ~33) - short JWT signing secret
  - weak-jwt-secret (HIGH, line ~37) - JWT_SECRET assignment
  - insecure-session-cookie (MEDIUM, line ~46) - secure=False
  - insecure-session-cookie (MEDIUM, line ~47) - httpOnly=False
  - missing-authentication (HIGH, line ~59) - route without @login_required

Total expected findings: 7
"""

from flask import Flask, session, jsonify

app = Flask(__name__)

# VULN: Hardcoded password in variable assignment
password = "SuperSecretP@ss123!"

# VULN: Hardcoded secret_key
secret_key = "my_application_secret_key_2024"

# Safe: Password from environment (should NOT be flagged)
import os
safe_password = os.environ.get("DB_PASSWORD", "changeme")


# --- Weak JWT Configuration ---

import jwt

# VULN: JWT signed with short secret (< 32 characters)
def create_token_weak(payload):
    return jwt.encode(payload, "short_secret", algorithm="HS256")

# VULN: JWT secret assigned as short string variable
jwt_secret = "weak_key_123"

# Safe: JWT with long secret (should NOT be flagged)
def create_token_safe(payload):
    return jwt.encode(payload, "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8", algorithm="HS256")


# --- Insecure Session Configuration ---

# VULN: Session cookie without secure flag
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = False

# Safe: Proper session configuration
# app.config["SESSION_COOKIE_SECURE"] = True
# app.config["SESSION_COOKIE_HTTPONLY"] = True


# --- Missing Authentication ---

# Safe: Public route (login page, should NOT be flagged)
@app.route("/login")
def login():
    return "Login page"

# VULN: Route handler without authentication decorator
@app.route("/api/users")
def get_users():
    return jsonify({"users": []})

# Safe: Route handler WITH authentication decorator
def login_required(f):
    pass

@app.route("/api/admin")
@login_required
def admin_panel():
    return jsonify({"admin": True})
