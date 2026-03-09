# Security Auditor — Compliance Module

Load this module when the task explicitly requires compliance framework assessment (FedRAMP, NIST 800-53, GDPR, HIPAA, PCI DSS, or Section 508).

---

## FedRAMP / NIST 800-53 Controls

This platform targets **FedRAMP Moderate** compliance. Key control families to verify:

### AC — Access Control

- **AC-2 Account Management:** All user accounts must be managed with formal provisioning/deprovisioning. Verify accounts are disabled promptly when users depart. Document account types (USER, ADMIN, CONTRACTOR).
- **AC-3 Access Enforcement:** RBAC enforced at every protected endpoint. No endpoint skips authorization check.
- **AC-6 Least Privilege:** Users and processes operate with minimum necessary permissions. Audit admin accounts regularly.
- **AC-17 Remote Access:** All remote access uses MFA and encrypted sessions.

### AU — Audit and Accountability

- **AU-2 Audit Events:** Log all authentication events (login, logout, failed attempts), role changes, privilege escalation, data access, and admin actions.
- **AU-3 Audit Record Content:** Each log entry must include: date/time, user ID, event type, outcome (success/failure), and source IP.
- **AU-9 Protection of Audit Information:** Logs must be write-protected. Separate log storage from application storage.
- **AU-11 Audit Record Retention:** Audit logs retained for **7 years** minimum. Verify log rotation policy does not purge before 7 years.

### IA — Identification and Authentication

- **IA-2 Identification and Authentication:** All users uniquely identified. MFA required for privileged access.
- **IA-5 Authenticator Management:** Password complexity rules enforced. Passwords hashed with bcrypt/argon2, minimum 12 rounds.
- **IA-8 Non-Organizational Users:** External users (contractors, API clients) use separate authentication flows.

### SC — System and Communications Protection

- **SC-8 Transmission Confidentiality:** TLS 1.2+ enforced on all endpoints. Verify HSTS header present.
- **SC-28 Protection of Information at Rest:** Sensitive data (PII, credentials) encrypted at rest. Key management via AWS Secrets Manager or equivalent.

### SI — System and Information Integrity

- **SI-3 Malicious Code Protection:** Dependency scanning in CI/CD. No high/critical CVEs in production.
- **SI-10 Information Input Validation:** All user input validated before processing.

---

## GDPR Compliance Checklist

Applicable when processing EU personal data:

- [ ] **Lawful basis documented:** Consent, contract, legitimate interest, or legal obligation established for each data type
- [ ] **Privacy notice present:** Users informed of data collection, purpose, retention period, and rights
- [ ] **Data minimization enforced:** Only collect PII necessary for stated purpose
- [ ] **Right to erasure implemented:** Users can request deletion of their data (and it actually deletes)
- [ ] **Data portability:** Users can export their data in machine-readable format
- [ ] **Breach notification process:** 72-hour notification to supervisory authority; procedures documented
- [ ] **DPA (Data Processing Agreement):** Signed with all third-party processors (AWS, analytics vendors, etc.)
- [ ] **Retention periods defined:** Each PII category has documented max retention period
- [ ] **Data transfers documented:** Cross-border transfers (to US) covered by SCCs or adequacy decision
- [ ] **No PII in logs:** Audit logs must not contain passwords, tokens, payment details, or identifying data

---

## HIPAA Compliance Checklist

Applicable when handling Protected Health Information (PHI):

- [ ] **BAA (Business Associate Agreement):** Signed with all vendors handling PHI
- [ ] **PHI encryption at rest:** AES-256 or equivalent for all stored PHI
- [ ] **PHI encryption in transit:** TLS 1.2+ for all PHI transmission
- [ ] **Access controls:** Only authorized workforce members access PHI
- [ ] **Audit logging for PHI access:** Every PHI access logged (who, what, when)
- [ ] **Automatic logoff:** Sessions expire after inactivity period
- [ ] **Unique user identification:** No shared accounts for PHI access
- [ ] **Emergency access procedure:** Documented break-glass procedure with logging
- [ ] **Backup and disaster recovery:** PHI backed up and recovery tested
- [ ] **Workstation security:** Access to PHI restricted to authorized workstations

---

## PCI DSS Compliance Checklist

Applicable when handling payment card data:

- [ ] **Cardholder data not stored** unless absolutely necessary (PAN, CVV, magnetic stripe)
- [ ] **PAN masked in display:** Show only last 4 digits when displaying card numbers
- [ ] **Encryption of cardholder data:** PAN encrypted at rest with strong cryptography
- [ ] **Key management:** Encryption keys stored separately from encrypted data; documented rotation schedule
- [ ] **Access restricted to cardholder data:** Need-to-know basis only
- [ ] **Secure coding practices:** All payment-related code reviewed against PCI DSS Requirement 6
- [ ] **Network segmentation:** Payment systems in isolated network segment
- [ ] **Penetration testing scheduled:** Annually and after significant changes
- [ ] **Vulnerability management:** Internal scans quarterly; external scans by ASV
- [ ] **Incident response plan:** Documented procedure for payment data breach

---

## Section 508 / WCAG 2.1 Level AA

Applicable to all web-based interfaces (FedRAMP requires Section 508 compliance):

### Perceivable

- [ ] All images have meaningful alt text (or empty alt="" for decorative)
- [ ] All form inputs have associated labels
- [ ] Color is not the only way information is conveyed
- [ ] Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- [ ] All video content has captions; audio content has transcripts
- [ ] Text can be resized to 200% without loss of content or function

### Operable

- [ ] All interactive elements keyboard accessible (no mouse-only interactions)
- [ ] Focus indicator visible on all focusable elements
- [ ] No content flashes more than 3 times per second
- [ ] Skip navigation link present for keyboard users
- [ ] Page titles are unique and descriptive

### Understandable

- [ ] Language of page set in HTML (`lang` attribute)
- [ ] Error messages identify the field and describe how to fix
- [ ] Labels and instructions provided for all form inputs
- [ ] Input purpose communicated (autocomplete attributes set)

### Robust

- [ ] Valid HTML (passes W3C validator)
- [ ] ARIA roles, states, and properties used correctly
- [ ] All dynamic content changes announced to screen readers (live regions)
- [ ] Custom components use appropriate ARIA patterns

### Compliance Verification Tools

```bash
# Automated accessibility scan
npx @axe-core/cli http://localhost:3500

# Lighthouse accessibility audit
npx lighthouse http://localhost:3500 --only-categories=accessibility

# Manual screen reader testing
# NVDA (Windows), VoiceOver (macOS/iOS), TalkBack (Android)
```

---

## 7-Year Audit Log Retention

**Requirement:** FedRAMP, HIPAA, and financial regulations require minimum 7-year audit log retention.

### Implementation Checklist

- [ ] Log rotation configured to archive rather than delete
- [ ] Archived logs stored in separate, immutable storage (S3 with Object Lock, or equivalent)
- [ ] Logs compressed after 90 days (cost optimization)
- [ ] Retrieval process documented and tested
- [ ] Log deletion requires dual authorization
- [ ] Retention policy enforced programmatically (not just policy documentation)

### Storage Pattern

```
Active logs (0-90 days): Application log service / database
Archived logs (90 days - 7 years): S3 with Object Lock (COMPLIANCE mode)
Log format: Structured JSON with timestamp, user ID, action, outcome, source IP
```

### What Must Be Retained

- All authentication events (login, logout, password reset, MFA, failures)
- All authorization decisions (access granted/denied)
- All privilege escalation events (role assignments, admin actions)
- All data access events for PII/PHI/PCI data
- All configuration changes
- All API access with user identity and endpoint

---

## Compliance Audit Report Template

When completing a compliance assessment, include:

```markdown
## Compliance Assessment: [Framework] — [Date]

### Coverage Summary
- Controls Reviewed: [N]
- Controls Passing: [N]
- Controls Failing: [N]
- Controls N/A: [N]

### Critical Gaps (immediate action required)
1. [Control ID]: [Gap description] — Remediation: [specific fix]

### High Gaps (fix within 30 days)
1. [Control ID]: [Gap description] — Remediation: [specific fix]

### Evidence Collected
- [Evidence artifact 1]: [location/link]
- [Evidence artifact 2]: [location/link]

### Next Assessment Date
[Date — typically annual for FedRAMP/HIPAA, quarterly for PCI DSS scans]
```
