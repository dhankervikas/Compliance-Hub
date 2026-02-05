### PRIVACY & DATA PROTECTION RULES

- **PII Detection:** Every upload must be scanned for GDPR-regulated data.
- **Masking Requirement:** Technical evidence (screenshots) must have non-essential PII masked.
- **Prohibited Data:** Never allow the storage of clear-text passwords, full credit card numbers, or health records (HIPAA).
- **Security Measure:** Use SHA-256 hashing if the user needs to provide a unique identifier without revealing the actual PII.

### ZERO-KNOWLEDGE EVIDENCE RULES

- **Storage Policy:** Metadata is the record; the file is the ghost.
- **Verification:** Always generate a SHA-256 hash. If the client changes 1 character in their local file, the hash will break, ensuring integrity.
- **Privacy:** Never display full-text confidential docs in the Business View; use 'Evidence Context' snippets only.
