"""
Policy Intents Mapping
======================
Maps each policy to its specific compliance requirements from ISO 27001:2022 
and SOC 2 standards. These intents are the exact requirements that MUST appear 
in the generated policy content to be audit-ready.
"""

from typing import Dict, List

# This is the master mapping of policies to their required controls
POLICY_CONTROL_MAP = {
    # Context & Scope Documents (Mandatory for ISO 27001 Clause 4)
    "ISMS Scope": ["ISO_4.1", "ISO_4.3"],
    "Context of the Organization": ["ISO_4.1", "ISO_4.2"],
    "Interested Parties": ["ISO_4.2", "A.5.5", "A.5.6"],
    
    # Leadership Documents (ISO Clause 5)
    "Information Security Policy": ["ISO_5.2", "A.5.1", "CC1.1", "CC1.2"],
    "Management Commitment Statement": ["ISO_5.1", "CC1.1"],
    "ISMS Roles and Responsibilities": ["ISO_5.3", "A.5.2", "A.5.3", "A.5.4", "CC1.3"],
    
    # Planning Documents (ISO Clause 6)
    "Risk Assessment Methodology": ["ISO_6.1.2", "A.5.7", "CC3.2"],
    "Risk Treatment Plan": ["ISO_6.1.3", "A.5.7"],
    "Statement of Applicability (SoA)": ["ISO_6.1.3", "A.5.1"],
    "Information Security Objectives": ["ISO_6.2"],
    
    # Support Documents (ISO Clause 7)
    "Competence and Awareness Policy": ["ISO_7.2", "ISO_7.3", "A.6.3"],
    "Information Security Training Program": ["A.6.3", "CC1.4"],
    "Document Control Procedure": ["ISO_7.5", "A.5.33", "A.5.37"],
    
    # Operational Policies (ISO Clause 8 & Annex A)
    "Access Control Policy": ["A.5.15", "A.5.16", "A.5.18", "A.8.2", "A.8.3", "CC6.1", "CC6.2"],
    "Acceptable Use Policy": ["A.5.10", "A.5.29", "CC1.4"],
    "Asset Management Policy": ["A.5.9", "A.5.10", "A.5.11", "A.5.14", "CC6.5"],
    "Backup and Recovery Policy": ["A.8.13", "A.8.14", "CC3.1"],
    "Business Continuity Policy": ["A.5.29", "A.5.30", "CC3.1"],
    "Change Management Policy": ["A.8.32", "CC8.1"],
    "Cryptography Policy": ["A.8.24", "CC6.1"],
    "Data Classification Policy": ["A.5.12", "A.5.13", "CC6.5"],
    "Data Protection and Privacy Policy": [
        "A.5.34", "A.8.11", "CC6.5",
        "P1.1", "P1.2", "P2.1", "P2.2", "P3.1", "P3.2", "P3.3", "P4.1", "P4.2", "P4.3",
        "P5.1", "P5.2", "P6.1", "P6.2", "P6.3", "P6.4", "P7.1", "P8.1", "P8.2", "P8.3"
    ],
    "Incident Response Policy": ["A.5.24", "A.5.25", "A.5.26", "CC7.3"],
    "Mobile Device Policy": ["A.6.7", "A.8.3", "CC6.3"],
    "Network Security Policy": ["A.8.20", "A.8.21", "A.8.22", "CC6.6"],
    "Password Policy": ["A.5.17", "A.8.5", "CC6.1"],
    "Physical Security Policy": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "CC6.4"],
    "Remote Access Policy": ["A.6.7", "A.8.3", "CC6.7"],
    "Secure Development Policy": ["A.8.25", "A.8.26", "A.8.27", "A.8.28", "CC8.1"],
    "Third-Party Security Policy": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "CC9.1"],
    "Vulnerability Management Policy": ["A.8.8", "CC7.1"],
    
    # Additional ISO 27001 A.5 Controls
    "Security in Project Management": ["A.5.8"],
    "Information Security in Supplier Relationships": ["A.5.19", "A.5.20"],
    "Supplier Security Agreements": ["A.5.21", "CC9.1"],
    "ICT Supply Chain Management": ["A.5.22", "CC9.1"],
    "Monitoring and Review of Supplier Services": ["A.5.23"],
    "Information Transfer": ["A.5.14"],
    "Incident Management": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "CC7.3"],
    "Evidence Collection": ["A.5.28"],
    "Legal and Compliance Requirements": ["A.5.31", "A.5.32"],
    "Independent Review": ["A.5.35", "A.5.36"],
    
    # Additional ISO 27001 A.6 Controls
    "Screening": ["A.6.1"],
    "Terms and Conditions of Employment": ["A.6.2"],
    "Disciplinary Process": ["A.6.4"],
    "Responsibilities After Termination": ["A.6.5"],
    "Confidentiality Agreements": ["A.6.6"],
    "Teleworking": ["A.6.7"],
    "Information Security Event Reporting": ["A.6.8"],
    
    # Additional ISO 27001 A.7 Controls
    "Physical Entry Controls": ["A.7.2"],
    "Securing Offices and Facilities": ["A.7.3"],
    "Working in Secure Areas": ["A.7.4"],
    "Desk and Screen Policy": ["A.7.7"],
    "Equipment Siting and Protection": ["A.7.8"],
    "Security of Assets Off-Premises": ["A.7.9"],
    "Storage Media": ["A.7.10"],
    "Supporting Utilities": ["A.7.11"],
    "Cabling Security": ["A.7.12"],
    "Equipment Maintenance": ["A.7.13"],
    "Secure Disposal": ["A.7.14"],
    
    # Additional ISO 27001 A.8 Controls
    "User Endpoint Devices": ["A.8.1"],
    "Privileged Access Rights": ["A.8.2"],
    "Information Access Restriction": ["A.8.3"],
    "Access to Source Code": ["A.8.4"],
    "Secure Authentication": ["A.8.5"],
    "Capacity Management": ["A.8.6"],
    "Protection Against Malware": ["A.8.7", "CC7.2"],
    "Configuration Management": ["A.8.9", "CC8.1"],
    "Information Deletion": ["A.8.10"],
    "Data Masking": ["A.8.11"],
    "Data Leakage Prevention": ["A.8.12"],
    "Logging and Monitoring": ["A.8.15", "A.8.16", "CC7.2"],
    "Clock Synchronization": ["A.8.17"],
    "Use of Privileged Utility Programs": ["A.8.18"],
    "Software Installation": ["A.8.19"],
    "Networks Segregation": ["A.8.22"],
    "Web Filtering": ["A.8.23"],
    "Testing": ["A.8.29"],
    "Outsourced Development": ["A.8.30"],
    "Separation of Environments": ["A.8.31"]
}


# Intent definitions: What MUST be included in each policy
POLICY_INTENTS = {
    "ISMS Scope": {
        "description": "Defines the boundaries of the ISMS",
        "mandatory_elements": [
            "MUST reference Clause 4.1 (Understanding the organization and its context)",
            "MUST reference Clause 4.3 (Determining the scope of the ISMS)",
            "SHALL define physical locations, organizational units, and/or business functions included",
            "SHALL specify information assets, systems, and processes in scope",
            "SHALL identify external and internal interfaces and dependencies",
            "SHALL list any exclusions with justification (if applicable)",
            "MUST align with business objectives and risk appetite",
            "SHALL be approved by top management",
            "MUST be documented, maintained, and available to interested parties"
        ],
        "section_specific_requirements": {
            "purpose": "Link to ISO 27001:2022 Clause 4.3 requirement",
            "scope": "Define exact boundaries (geographic, organizational, technical)",
            "policy_statements": "Include mandatory ISMS scope elements per ISO",
            "review_maintenance": "Annual review or when significant changes occur"
        },
        "audit_evidence_needed": [
            "Document showing defined ISMS boundaries",
            "Approval by top management",
            "Justification for any exclusions",
            "Mapping to organizational structure"
        ]
    },
    
    "Context of the Organization": {
        "description": "Documents understanding of organizational context per Clause 4.1 and 4.2",
        "mandatory_elements": [
            "MUST address Clause 4.1 (external and internal issues)",
            "MUST address Clause 4.2 (interested parties and their requirements)",
            "SHALL identify external factors: legal, regulatory, technological, competitive",
            "SHALL identify internal factors: culture, capabilities, objectives, obligations",
            "SHALL list interested parties (customers, regulators, partners, employees)",
            "SHALL define requirements of each interested party relevant to ISMS",
            "MUST document how context influences ISMS scope and objectives",
            "SHALL be reviewed regularly and updated when context changes"
        ],
        "section_specific_requirements": {
            "purpose": "Explain Clause 4.1 and 4.2 compliance",
            "scope": "Cover all relevant internal/external factors",
            "procedures": "Process for regular context review",
            "review_maintenance": "Minimum annual review, or when triggered by changes"
        },
        "audit_evidence_needed": [
            "List of external issues affecting ISMS",
            "List of internal issues affecting ISMS",
            "Interested parties register with requirements",
            "Evidence of periodic context reviews"
        ]
    },
    
    "Information Security Policy": {
        "description": "Top-level policy as required by ISO 5.2 and A.5.1",
        "mandatory_elements": [
            "MUST satisfy ISO Clause 5.2 (Information Security Policy)",
            "MUST satisfy Annex A.5.1 (Policies for information security)",
            "SHALL be approved by top management",
            "SHALL be appropriate to the purpose of the organization",
            "SHALL include information security objectives or framework for setting them",
            "SHALL include commitment to satisfy applicable requirements",
            "SHALL include commitment to continual improvement",
            "SHALL be available to interested parties as appropriate",
            "SHALL be communicated within organization and to relevant external parties",
            "MUST align with SOC 2 CC1.1 and CC1.2 (control environment)"
        ],
        "section_specific_requirements": {
            "purpose": "State high-level information security commitment",
            "scope": "Apply to entire ISMS scope",
            "policy_statements": "Include objectives, commitments, and principles",
            "roles_responsibilities": "Define ownership at board/executive level",
            "review_maintenance": "Annual review by top management"
        },
        "audit_evidence_needed": [
            "Top management approval signature",
            "Communication records (all-hands, intranet, onboarding)",
            "Linkage to other policies in hierarchy",
            "Annual review meeting minutes"
        ]
    },
    
    "Access Control Policy": {
        "description": "Comprehensive access control covering A.5.15, A.5.16, A.5.18, A.8.2, A.8.3",
        "mandatory_elements": [
            "MUST address A.5.15 (Access control)",
            "MUST address A.5.16 (Identity management)",
            "MUST address A.5.18 (Access rights)",
            "MUST address A.8.2 (Privileged access rights)",
            "MUST address A.8.3 (Information access restriction)",
            "SHALL implement principle of least privilege",
            "SHALL define user access provisioning process",
            "SHALL define access review process (minimum annually)",
            "SHALL address privileged account management",
            "SHALL address role-based access control (RBAC) or equivalent",
            "SHALL cover access for employees, contractors, and third parties",
            "MUST align with SOC 2 CC6.1 and CC6.2"
        ],
        "section_specific_requirements": {
            "purpose": "Enforce confidentiality, integrity, availability through access controls",
            "scope": "All systems, applications, and data",
            "policy_statements": [
                "Default deny posture",
                "Least privilege enforcement",
                "Segregation of duties for critical functions",
                "Privileged access monitoring",
                "Regular access reviews (quarterly or annually)"
            ],
            "procedures": [
                "Onboarding: request, approval, provisioning",
                "Changes: re-approval for elevated access",
                "Offboarding: immediate revocation",
                "Emergency access: logging and time-limited"
            ],
            "compliance_monitoring": "Automated access reviews, audit logs, quarterly reports"
        },
        "audit_evidence_needed": [
            "Access request and approval records",
            "Evidence of quarterly/annual access reviews",
            "Privileged account inventory",
            "Access revocation logs for terminated users",
            "Role-permission matrices"
        ]
    },
    
    "Incident Response Policy": {
        "description": "Incident management per A.5.24, A.5.25, A.5.26",
        "mandatory_elements": [
            "MUST address A.5.24 (Information security incident management planning)",
            "MUST address A.5.25 (Assessment and decision on information security events)",
            "MUST address A.5.26 (Response to information security incidents)",
            "SHALL define incident categories and severity levels",
            "SHALL establish incident response team (IRT) roles",
            "SHALL define detection, reporting, assessment, response, recovery phases",
            "SHALL include communication plan (internal and external)",
            "SHALL address evidence preservation and forensics",
            "SHALL require post-incident review and lessons learned",
            "MUST align with SOC 2 CC7.3"
        ],
        "section_specific_requirements": {
            "purpose": "Minimize impact of security incidents",
            "scope": "All information security events and incidents",
            "policy_statements": [
                "Mandatory reporting of suspected incidents within 2 hours",
                "Incident classification within 4 hours",
                "Escalation to senior management for high/critical incidents",
                "No retaliation for good-faith reporting"
            ],
            "procedures": [
                "Detection: automated alerts + user reporting",
                "Containment: isolate affected systems",
                "Eradication: remove threat, patch vulnerabilities",
                "Recovery: restore services, verify integrity",
                "Post-incident: root cause analysis, lessons learned"
            ],
            "roles_responsibilities": [
                "Incident Response Manager: overall coordination",
                "Security Analyst: technical investigation",
                "Legal/Compliance: regulatory notifications",
                "Communications: stakeholder updates"
            ]
        },
        "audit_evidence_needed": [
            "Incident response plan document",
            "Evidence of IRT training and drills",
            "Incident tickets/logs showing response times",
            "Post-incident reports",
            "Communication templates"
        ]
    },
    
    "Backup and Recovery Policy": {
        "description": "Backup procedures per A.8.13 and business continuity A.8.14",
        "mandatory_elements": [
            "MUST address A.8.13 (Information backup)",
            "MUST address A.8.14 (Redundancy of information processing facilities)",
            "SHALL define backup frequency for each data classification",
            "SHALL specify retention periods",
            "SHALL require regular backup testing (minimum quarterly)",
            "SHALL define recovery time objective (RTO) and recovery point objective (RPO)",
            "SHALL address offsite/cloud backup storage",
            "SHALL include backup encryption requirements",
            "MUST align with SOC 2 CC3.1"
        ],
        "section_specific_requirements": {
            "purpose": "Ensure data availability and business continuity",
            "scope": "All critical systems and data",
            "policy_statements": [
                "Daily incremental backups for production systems",
                "Weekly full backups",
                "Backup data encrypted at rest and in transit",
                "Offsite backup copies stored in geographically separate location",
                "Quarterly restore testing",
                "RTO < 4 hours, RPO < 24 hours for critical systems"
            ],
            "procedures": [
                "Automated backup jobs with success/failure monitoring",
                "Backup verification (integrity checks)",
                "Restore testing procedure",
                "Backup rotation and retention per data classification",
                "Incident-triggered additional backups"
            ]
        },
        "audit_evidence_needed": [
            "Backup logs showing frequency and success rates",
            "Restore test results",
            "Offsite storage agreements",
            "Encryption certificates",
            "RTO/RPO achievement reports"
        ]
    },
    
    "Risk Assessment Methodology": {
        "description": "Risk assessment process per ISO 6.1.2 and A.5.7",
        "mandatory_elements": [
            "MUST satisfy ISO Clause 6.1.2 (Information security risk assessment)",
            "MUST address A.5.7 (Threat intelligence)",
            "SHALL define criteria for risk acceptance",
            "SHALL establish process for identifying risks to confidentiality, integrity, availability",
            "SHALL define risk analysis methodology (qualitative/quantitative)",
            "SHALL specify risk assessment frequency (minimum annually)",
            "SHALL identify risk owners",
            "SHALL integrate threat intelligence",
            "MUST align with SOC 2 CC3.2"
        ],
        "section_specific_requirements": {
            "purpose": "Systematic identification and assessment of information security risks",
            "scope": "All assets, threats, and vulnerabilities within ISMS scope",
            "policy_statements": [
                "Risk assessments conducted annually and after major changes",
                "Use industry-standard risk methodology (e.g., NIST, ISO 31000)",
                "Risk scoring: Likelihood x Impact on 5-point scale",
                "Risks rated High or Critical require treatment plans within 30 days"
            ],
            "procedures": [
                "Asset identification and valuation",
                "Threat and vulnerability identification",
                "Likelihood and impact assessment",
                "Risk calculation and prioritization",
                "Documentation in risk register"
            ],
            "roles_responsibilities": [
                "CISO: Overall risk assessment oversight",
                "Asset Owners: Identify and value assets",
                "Risk Assessors: Conduct assessments",
                "Executive Committee: Approve risk acceptance"
            ]
        },
        "audit_evidence_needed": [
            "Risk assessment methodology document",
            "Completed risk register",
            "Risk acceptance approvals for accepted risks",
            "Evidence of annual risk assessment",
            "Threat intelligence sources"
        ]
    },
    
    "Third-Party Security Policy": {
        "description": "Supplier security per A.5.19, A.5.20, A.5.21, A.5.22",
        "mandatory_elements": [
            "MUST address A.5.19 (Information security in supplier relationships)",
            "MUST address A.5.20 (Addressing information security within supplier agreements)",
            "MUST address A.5.21 (Managing information security in the ICT supply chain)",
            "MUST address A.5.22 (Monitoring, review and change management of supplier services)",
            "SHALL require vendor risk assessments before engagement",
            "SHALL mandate security requirements in contracts",
            "SHALL define ongoing vendor monitoring process",
            "SHALL address data protection and confidentiality",
            "SHALL cover incident notification requirements",
            "SHALL include right to audit clauses",
            "MUST align with SOC 2 CC9.1"
        ],
        "section_specific_requirements": {
            "purpose": "Manage information security risks from third parties",
            "scope": "All vendors with access to systems, data, or facilities",
            "policy_statements": [
                "Vendor security assessment required before contract",
                "High-risk vendors: detailed security questionnaire + SOC 2 report",
                "Medium-risk vendors: security attestation",
                "Annual vendor security reviews",
                "Vendor incident notification within 24 hours",
                "Contractual right to audit"
            ],
            "procedures": [
                "Pre-engagement: risk categorization, security assessment",
                "Contract phase: security exhibit, SLA terms, liability clauses",
                "Ongoing: periodic reviews, performance monitoring",
                "Offboarding: data return/destruction, access revocation"
            ]
        },
        "audit_evidence_needed": [
            "Vendor inventory with risk ratings",
            "Vendor security assessments",
            "Contracts with security provisions",
            "Annual vendor review records",
            "SOC 2 reports from critical vendors"
        ]
    },
    
    "Vulnerability Management Policy": {
        "description": "Technical vulnerability management per A.8.8",
        "mandatory_elements": [
            "MUST address A.8.8 (Management of technical vulnerabilities)",
            "SHALL define vulnerability scanning frequency (minimum monthly)",
            "SHALL require patch management within defined timeframes",
            "SHALL prioritize vulnerabilities based on CVSS or similar scoring",
            "SHALL address zero-day and critical vulnerability response",
            "SHALL cover both internal and external vulnerabilities",
            "SHALL require vulnerability disclosure coordination",
            "MUST align with SOC 2 CC7.1"
        ],
        "section_specific_requirements": {
            "purpose": "Identify and remediate security vulnerabilities before exploitation",
            "scope": "All systems, applications, and network devices",
            "policy_statements": [
                "Weekly authenticated vulnerability scans for internal systems",
                "Monthly external vulnerability scans by third party",
                "Critical vulnerabilities (CVSS 9.0+): 7-day remediation SLA",
                "High vulnerabilities (CVSS 7.0-8.9): 30-day remediation SLA",
                "Medium/Low: 90-day remediation SLA",
                "Emergency patching process for zero-day threats"
            ],
            "procedures": [
                "Automated scanning with credentialed access",
                "Vulnerability validation and false positive filtering",
                "Risk-based prioritization",
                "Patch testing in non-production environment",
                "Deployment to production with change control",
                "Verification scanning post-remediation"
            ]
        },
        "audit_evidence_needed": [
            "Vulnerability scan reports",
            "Patch deployment records",
            "Remediation SLA compliance metrics",
            "Exception approvals for delayed patching",
            "Vulnerability tracking database"
        ]
    },
    
    "Cryptography Policy": {
        "description": "Cryptographic controls per A.8.24",
        "mandatory_elements": [
            "MUST address A.8.24 (Use of cryptography)",
            "SHALL define approved cryptographic algorithms and key lengths",
            "SHALL specify encryption requirements for data at rest and in transit",
            "SHALL address key lifecycle management (generation, distribution, storage, rotation, destruction)",
            "SHALL prohibit weak or deprecated algorithms (MD5, SHA-1, DES, RC4)",
            "SHALL require use of industry-standard protocols (TLS 1.2+, SSH v2)",
            "MUST align with SOC 2 CC6.1"
        ],
        "section_specific_requirements": {
            "purpose": "Protect confidentiality and integrity through cryptography",
            "scope": "All sensitive data and communications",
            "policy_statements": [
                "Approved algorithms: AES-256, RSA 2048+, ECDSA P-256+",
                "All data at rest: encrypted with AES-256 or equivalent",
                "All data in transit: encrypted with TLS 1.2+ or IPSec",
                "Encryption keys managed via Hardware Security Module (HSM) or AWS KMS",
                "Key rotation: annually for data encryption keys, every 2 years for certificate keys",
                "Deprecated: MD5, SHA-1, DES, 3DES, RC4, SSL, TLS 1.0/1.1"
            ],
            "procedures": [
                "Key generation using FIPS 140-2 validated modules",
                "Key storage: HSM or encrypted key vault",
                "Key access: limited to authorized crypto officers",
                "Key destruction: secure deletion meeting NIST SP 800-88 standards"
            ]
        },
        "audit_evidence_needed": [
            "Cryptographic standards document",
            "Certificate inventory",
            "Key management procedures",
            "HSM configuration",
            "Evidence of deprecated algorithm removal"
        ]
    }
}

# Add remaining policy intents (abbreviated for space - expand as needed)
POLICY_INTENTS.update({
    "Password Policy": {
        "description": "Authentication security per A.5.17 and A.8.5",
        "mandatory_elements": [
            "MUST address A.5.17 (Authentication information)",
            "MUST address A.8.5 (Secure authentication)",
            "SHALL require minimum 12-character passwords for standard accounts",
            "SHALL require multi-factor authentication (MFA) for privileged and remote access",
            "SHALL prohibit password reuse (last 24 passwords)",
            "SHALL enforce password expiration (maximum 90 days)",
            "SHALL require immediate password change upon suspected compromise",
            "MUST align with SOC 2 CC6.1"
        ]
    },
    
    "Data Classification Policy": {
        "description": "Information classification per A.5.12 and A.5.13",
        "mandatory_elements": [
            "MUST address A.5.12 (Classification of information)",
            "MUST address A.5.13 (Labelling of information)",
            "SHALL define classification levels (e.g., Public, Internal, Confidential, Restricted)",
            "SHALL specify handling requirements for each classification level",
            "SHALL require data owners to classify information assets",
            "SHALL include data labeling requirements",
            "MUST align with SOC 2 CC6.5"
        ]
    },
    
    "Change Management Policy": {
        "description": "Change control per A.8.32",
        "mandatory_elements": [
            "MUST address A.8.32 (Change management)",
            "SHALL require formal change request and approval process",
            "SHALL mandate testing before production deployment",
            "SHALL include rollback procedures",
            "SHALL require documentation of all changes",
            "SHALL define emergency change process",
            "MUST align with SOC 2 CC8.1"
        ]
    },
    
    "Network Security Policy": {
        "description": "Network controls per A.8.20, A.8.21, A.8.22",
        "mandatory_elements": [
            "MUST address A.8.20 (Networks security)",
            "MUST address A.8.21 (Security of network services)",
            "MUST address A.8.22 (Segregation of networks)",
            "SHALL require network segmentation (production, development, DMZ)",
            "SHALL mandate firewall rules and ACLs",
            "SHALL require IDS/IPS deployment",
            "SHALL enforce secure network protocols",
            "MUST align with SOC 2 CC6.6"
        ]
    },
    
    "Mobile Device Policy": {
        "description": "Mobile and remote working per A.6.7 and A.8.3",
        "mandatory_elements": [
            "MUST address A.6.7 (Remote working)",
            "MUST address A.8.3 (Information access restriction)",
            "SHALL require device encryption",
            "SHALL mandate mobile device management (MDM) enrollment",
            "SHALL enforce remote wipe capability",
            "SHALL require device passcode/biometric",
            "SHALL prohibit jailbroken/rooted devices",
            "MUST align with SOC 2 CC6.3"
        ]
    }
})


def get_policy_intents(policy_name: str) -> Dict:
    """
    Retrieves the intent requirements for a specific policy
    
    Args:
        policy_name: Name of the policy (must match POLICY_CONTROL_MAP key)
        
    Returns:
        Dictionary containing intent requirements, or empty dict if not found
    """
    return POLICY_INTENTS.get(policy_name, {})


def get_mapped_controls(policy_name: str) -> List[str]:
    """
    Retrieves the ISO/SOC 2 controls mapped to a specific policy
    
    Args:
        policy_name: Name of the policy
        
    Returns:
        List of control identifiers
    """
    return POLICY_CONTROL_MAP.get(policy_name, [])


def validate_policy_coverage(policy_name: str, policy_content: str) -> Dict:
    """
    Validates whether policy content addresses all required intents
    
    Args:
        policy_name: Name of the policy
        policy_content: The generated policy text
        
    Returns:
        Dictionary with coverage analysis
    """
    intents = get_policy_intents(policy_name)
    if not intents:
        return {"error": f"No intents defined for policy: {policy_name}"}
    
    mandatory_elements = intents.get("mandatory_elements", [])
    content_lower = policy_content.lower()
    
    covered = []
    missing = []
    
    for element in mandatory_elements:
        # Extract key terms from the intent
        key_terms = []
        if "MUST address" in element:
            # Extract control reference (e.g., "A.5.15")
            import re
            control_ref = re.search(r'[A-Z]\.\d+\.\d+', element)
            if control_ref:
                key_terms.append(control_ref.group())
        
        # Check for SHALL/MUST requirements
        if "SHALL" in element or "MUST" in element:
            # Extract the requirement phrase
            requirement = element.split("SHALL ")[-1].split("MUST ")[-1].lower()
            # Simple keyword check
            if any(word in content_lower for word in requirement.split()[:3]):
                covered.append(element)
            else:
                missing.append(element)
        else:
            # For descriptive elements, just mark as needing review
            covered.append(element)
    
    coverage_pct = (len(covered) / len(mandatory_elements) * 100) if mandatory_elements else 0
    
    return {
        "policy_name": policy_name,
        "coverage_percentage": round(coverage_pct, 2),
        "covered_elements": covered,
        "missing_elements": missing,
        "audit_ready": len(missing) == 0 and coverage_pct >= 90
    }
