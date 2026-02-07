"""
Master Policy Templates Library
===============================
This file contains the "Legal Bones" and structural skeletons for the Compliance Compiler.
The AI's job is to weave the Tenant Profile into these templates, NOT to write them from scratch.

Each template contains:
1. ISO/SOC2 Mapping placeholders
2. "SHALL/MUST" (RFC 2119) language
3. Placeholders for "Audit Artifacts"
"""

MASTER_POLICY_TEMPLATES = {
    "default": """
# {{POLICY_NAME}}

| Document Control | |
| :--- | :--- |
| **Version** | 1.0 (Audit-Ready) |
| **Owner** | {{POLICY_OWNER}} |
| **Approver** | {{POLICY_APPROVER}} |
| **Effective Date** | {{CURRENT_DATE}} |
| **Classification** | Internal |

## 1. Purpose and Strategic Alignment
The {{COMPANY_NAME}} Information Security Management System (ISMS) mandates this policy to ensure {{POLICY_GOAL}}. This policy aligns with ISO 27001:2022 Clause {{ISO_CLAUSE}} and SOC 2 {{SOC2_CRITERIA}}.

## 2. Scope and Applicability
This policy applies to all {{COMPANY_NAME}} information assets, employees, and contractors.
**Technical Scope:** All assets within {{CLOUD_STACK}} accounts defined in the Asset Inventory.

## 3. Policy Statements

### 3.1 Core Mandate
The organization SHALL establish a framework for {{POLICY_TOPIC}} that ensures confidentiality, integrity, and availability.

### 3.2 Specific Technical Requirements
(Compiling... Injecting specific requirements based on {{INDUSTRY}} and {{TECH_STACK}}...)

## 4. Compliance and Monitoring
| Requirement | Audit Artifact (Evidence) | Frequency |
| :--- | :--- | :--- |
| Policy Review | Management Review Meeting Minutes | Annual |
| Operational Check | {{EVIDENCE_TYPE}} | {{FREQUENCY}} |

## 5. Enforcement
Violations of this policy MUST be reported to the CISO. Disciplinary action SHALL follow the HR Disciplinary Policy.

## 6. Multi-Standard Cross-Walk
| ISO 27001:2022 | SOC 2 (TSC) | NIST 800-53 | Requirement Summary |
| :--- | :--- | :--- | :--- |
| {{ISO_REF}} | {{SOC2_REF}} | {{NIST_REF}} | {{REQ_SUMMARY}} |
""",

    "Access Control Policy": """
# Access Control Policy

| Document Control | |
| :--- | :--- |
| **Version** | 1.0 (Audit-Ready) |
| **Owner** | {{POLICY_OWNER}} |
| **Approver** | {{POLICY_APPROVER}} |
| **Effective Date** | {{CURRENT_DATE}} |

## 1. Purpose
To limit access to information and information processing facilities used by {{COMPANY_NAME}}. This aligns with ISO 27001:2022 A.5.15 and SOC 2 CC6.1.

## 2. Policy Statements

### 2.1 Principle of Least Privilege
Access to {{CLOUD_STACK}} resources SHALL be restricted to the minimum necessary privileges required to perform job functions.
*   **Implementation**: Role-Based Access Control (RBAC) MUST be utilized in {{IDENTITY_PROVIDER}}.

### 2.2 User Registration and De-registration
A formal user registration and de-registration process MUST be implemented to enable assignment of access rights.
*   **Audit Artifact**: Ticket/Log of access provisioning and de-provisioning from {{HR_SYSTEM}} to {{IDENTITY_PROVIDER}}.

### 2.3 Password Management
Allocations of secret authentication information MUST be controlled through a formal management process.
*   **Requirement**: Passwords SHALL meet complexity requirements (Min 12 chars, alphanumeric).
*   **MFA**: Multi-Factor Authentication (MFA) SHALL be enforced for all users in {{IDENTITY_PROVIDER}}.

### 2.4 Review of User Access Rights
Asset owners SHALL review users' access rights at regular intervals.
*   **Frequency**: {{ACCESS_REVIEW_FREQUENCY}} (Default: Quarterly).
*   **Audit Artifact**: Access Review Report signed by asset owners.

## 3. Compliance Mapping
| Requirement | ISO 27001:2022 | SOC 2 | NIST 800-53 | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| Access Policy | A.5.15 | CC6.1 | AC-1 | This Document |
| User Provisioning | A.5.16 | CC6.2 | AC-2 | JIRA Tickets / IdP Logs |
| Privileged Access | A.8.2 | CC6.3 | AC-6 | IAM Role Usage Logs |
""",

    "Information Security Policy": """
# Information Security Policy (ISMS)

| Document Control | |
| :--- | :--- |
| **Version** | 1.0 (Context-Aware) |
| **Owner** | CISO |
| **Effective Date** | {{CURRENT_DATE}} |

## 1. Context of the Organization (ISO 4.1)
The organization SHALL determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcomes of its information security management system.

### 1.1 PESTEL Analysis (Auto-Generated for {{INDUSTRY}})
*   **Political**: {{PESTEL_POLITICAL}}
*   **Economic**: {{PESTEL_ECONOMIC}}
*   **Social**: {{PESTEL_SOCIAL}}
*   **Technological**: {{PESTEL_TECHNOLOGICAL}}
*   **Environmental**: {{PESTEL_ENVIRONMENTAL}} (Climate Change Amendment 2024 included)
*   **Legal**: {{PESTEL_LEGAL}}

## 2. Interested Parties (ISO 4.2)
The organization SHALL determine interested parties and their requirements.
*   **Regulators**: {{REGULATORS}}
*   **Customers**: SLA and Data Protection requirements.

## 3. Scope of the ISMS (ISO 4.3)
The scope includes all information assets, processes, and people involved in the delivery of {{COMPANY_SERVICE}}.
*   **Technical Boundary**: {{CLOUD_STACK}} Production Environment.
*   **Exclusions**: {{EXCLUSIONS}} (Must be justified).

## 4. Leadership and Commitment
Top management SHALL demonstrate leadership and commitment with respect to the information security management system.

## 5. Compliance Mapping
| Requirement | ISO 27001:2022 | Statutory Law | Evidence |
| :--- | :--- | :--- | :--- |
| Context | 4.1 | - | PESTEL Analysis Doc |
| Stakeholders | 4.2 | GDPR/CCPA | Stakeholder Matrix |
| Scope | 4.3 | - | Scope Document |
"""
}

def get_master_template(policy_name: str) -> str:
    """Retrieves the best-fit master template or the default."""
    return MASTER_POLICY_TEMPLATES.get(policy_name, MASTER_POLICY_TEMPLATES["default"])
