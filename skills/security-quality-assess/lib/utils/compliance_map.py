"""CWE to STIG V-number and NIST 800-53 control mapping.

Enables automatic compliance tagging of security findings.
Based on DISA Application Security and Development STIG V6R1.
"""

# CWE -> (STIG V-numbers, NIST 800-53 controls)
CWE_COMPLIANCE_MAP: dict[str, dict] = {
    "CWE-20": {"stig_ids": ["V-222606", "V-222612"], "nist_controls": ["SI-10"], "stig_title": "Input Validation"},
    "CWE-22": {"stig_ids": ["V-222606"], "nist_controls": ["SI-10"], "stig_title": "Path Traversal"},
    "CWE-78": {"stig_ids": ["V-222604"], "nist_controls": ["SI-10"], "stig_title": "Command Injection"},
    "CWE-79": {"stig_ids": ["V-222602"], "nist_controls": ["SI-10"], "stig_title": "Cross-Site Scripting"},
    "CWE-89": {"stig_ids": ["V-222608"], "nist_controls": ["SI-10"], "stig_title": "SQL Injection"},
    "CWE-94": {"stig_ids": ["V-222604", "V-222612"], "nist_controls": ["SI-10"], "stig_title": "Code Injection"},
    "CWE-209": {"stig_ids": ["V-222610", "V-222611"], "nist_controls": ["SI-11"], "stig_title": "Error Information Exposure"},
    "CWE-250": {"stig_ids": ["V-222430"], "nist_controls": ["AC-6"], "stig_title": "Execution with Unnecessary Privileges"},
    "CWE-256": {"stig_ids": ["V-222542"], "nist_controls": ["IA-5"], "stig_title": "Plaintext Password Storage"},
    "CWE-269": {"stig_ids": ["V-222429"], "nist_controls": ["AC-6"], "stig_title": "Improper Privilege Management"},
    "CWE-287": {"stig_ids": ["V-222522", "V-222642"], "nist_controls": ["IA-2", "IA-5"], "stig_title": "Improper Authentication"},
    "CWE-306": {"stig_ids": ["V-222522", "V-222425"], "nist_controls": ["IA-2", "AC-3"], "stig_title": "Missing Authentication"},
    "CWE-307": {"stig_ids": ["V-222432"], "nist_controls": ["AC-7"], "stig_title": "Brute Force"},
    "CWE-311": {"stig_ids": ["V-222588", "V-222589"], "nist_controls": ["SC-28"], "stig_title": "Missing Encryption"},
    "CWE-319": {"stig_ids": ["V-222543", "V-222596"], "nist_controls": ["SC-8", "SC-13"], "stig_title": "Cleartext Transmission"},
    "CWE-326": {"stig_ids": ["V-222570", "V-222571"], "nist_controls": ["SC-13"], "stig_title": "Inadequate Encryption Strength"},
    "CWE-327": {"stig_ids": ["V-222570", "V-222571", "V-222572", "V-222573"], "nist_controls": ["SC-13"], "stig_title": "Use of Broken Crypto Algorithm"},
    "CWE-352": {"stig_ids": ["V-222603"], "nist_controls": ["SI-10"], "stig_title": "Cross-Site Request Forgery"},
    "CWE-502": {"stig_ids": ["V-222612", "V-222645"], "nist_controls": ["SI-10"], "stig_title": "Insecure Deserialization"},
    "CWE-532": {"stig_ids": ["V-222444"], "nist_controls": ["AU-3", "AU-12"], "stig_title": "Sensitive Data in Logs"},
    "CWE-611": {"stig_ids": ["V-222607"], "nist_controls": ["SI-10"], "stig_title": "XXE"},
    "CWE-613": {"stig_ids": ["V-222387", "V-222388"], "nist_controls": ["AC-12"], "stig_title": "Session Expiration"},
    "CWE-614": {"stig_ids": ["V-222391"], "nist_controls": ["SC-8"], "stig_title": "Insecure Session Cookie"},
    "CWE-732": {"stig_ids": ["V-222430"], "nist_controls": ["AC-6"], "stig_title": "Incorrect Permission Assignment"},
    "CWE-778": {"stig_ids": ["V-222462", "V-222463"], "nist_controls": ["AU-12"], "stig_title": "Insufficient Logging"},
    "CWE-798": {"stig_ids": ["V-222642"], "nist_controls": ["IA-5"], "stig_title": "Hardcoded Credentials"},
    "CWE-918": {"stig_ids": ["V-222606"], "nist_controls": ["SI-10"], "stig_title": "Server-Side Request Forgery"},
    "CWE-943": {"stig_ids": ["V-222608"], "nist_controls": ["SI-10"], "stig_title": "NoSQL Injection"},
    "CWE-1321": {"stig_ids": ["V-222612"], "nist_controls": ["SI-10"], "stig_title": "Prototype Pollution"},
}


def get_compliance_info(cwe_id: str) -> dict:
    """Look up STIG and NIST mappings for a CWE ID.

    Args:
        cwe_id: CWE identifier (e.g., "CWE-89")

    Returns:
        Dict with stig_ids, nist_controls, and stig_title.
        Returns empty lists if CWE not mapped.
    """
    return CWE_COMPLIANCE_MAP.get(cwe_id, {"stig_ids": [], "nist_controls": [], "stig_title": ""})
