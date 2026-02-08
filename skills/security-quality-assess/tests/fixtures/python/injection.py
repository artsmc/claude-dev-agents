"""Test fixture: Python injection vulnerabilities.

THIS FILE CONTAINS INTENTIONALLY VULNERABLE CODE FOR TESTING PURPOSES.
All code patterns are designed to validate the InjectionAnalyzer detection
capabilities.

Expected detections by InjectionAnalyzer:
  - sql-injection (HIGH, line ~22) - string concatenation
  - sql-injection (HIGH, line ~27) - f-string interpolation
  - sql-injection (HIGH, line ~32) - .format() usage
  - command-injection (CRITICAL, line ~42) - os.system
  - command-injection (CRITICAL, line ~47) - subprocess shell=True
  - command-injection (MEDIUM, line ~52) - subprocess without shell
  - code-injection (HIGH, line ~58) - eval
  - code-injection (HIGH, line ~62) - exec
  - code-injection (HIGH, line ~69) - pickle.loads

Total expected findings: 9
"""

import os
import subprocess
import pickle


# --- SQL Injection ---

# VULN: SQL injection via string concatenation
def get_user_concat(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

# VULN: SQL injection via f-string interpolation
def get_user_fstring(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

# VULN: SQL injection via .format()
def get_user_format(user_id):
    query = "SELECT * FROM users WHERE id = {}".format(user_id)
    return query

# Safe: Parameterized query (should NOT be flagged)
def get_user_safe(cursor, user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# --- Command Injection ---

# VULN: os.system (always dangerous)
def run_command_os(filename):
    os.system("cat " + filename)

# VULN: subprocess with shell=True
def run_command_shell(cmd):
    result = subprocess.call(cmd, shell=True)
    return result

# VULN: subprocess without shell=True (lower severity)
def run_command_no_shell(cmd):
    result = subprocess.run(cmd)
    return result


# --- Code Injection ---

# VULN: eval() usage
def calculate(expression):
    return eval(expression)

# VULN: exec() usage
def run_code(code_string):
    exec(code_string)


# --- Unsafe Deserialization ---

# VULN: pickle.loads (arbitrary code execution risk)
def load_data(serialized_data):
    return pickle.loads(serialized_data)


# Safe: json.loads is safe (should NOT be flagged)
import json

def load_json(data):
    return json.loads(data)
