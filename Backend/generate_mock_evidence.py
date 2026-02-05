
import json
import random
import os
from datetime import datetime, timedelta

OUTPUT_FILE = "data/mock_evidence_store.json"
os.makedirs("data", exist_ok=True)

# 22 DETAILED PROCESSES (Aligned with FrameworkDetail.js Custom Restructure)
PROCESS_GOV = "Governance & Policy"
PROCESS_HR = "HR Security"
PROCESS_ASSET = "Asset Management"
PROCESS_IAM = "Access Control (IAM)"
PROCESS_PHYSICAL = "Physical Security"
PROCESS_OPS = "Operations (General)"
PROCESS_CONFIG = "Configuration Management"
PROCESS_CRYPTO = "Cryptography"
PROCESS_LOGGING = "Logging & Monitoring"
PROCESS_CLOCK = "Clock Synchronization"
PROCESS_VULN = "Vulnerability Management"
PROCESS_CAPACITY = "Capacity Management"
PROCESS_BACKUP = "Backup Management"
PROCESS_NETWORK = "Network Security"
PROCESS_SDLC = "SDLC (Development)"
PROCESS_SUPPLIER = "Supplier Mgmt"
PROCESS_INCIDENT = "Incident & Resilience"
PROCESS_THREAT = "Threat Intel"
PROCESS_LEGAL = "Legal & Compliance"
PROCESS_RISK = "Risk Management"
PROCESS_PERF = "Performance Evaluation"
PROCESS_IMPROVE = "Improvement"

# COMPLIANCE INTENT (Mock Mapping)
DEFAULT_INTENT = {"id": "INT-GEN", "name": "General Compliance", "badges": ["ISO-27001"]}
COMPLIANCE_INTENTS = {
    "A.5.15": {"id": "INT-IAM-01", "name": "Access Control Policy", "badges": ["SOC2-CC6.1", "ISO-A.5.15"]},
    "A.8.28": {"id": "INT-SDLC-04", "name": "Secure Coding Standards", "badges": ["SOC2-CC7.1", "ISO-A.8.28"]},
    "A.8.24": {"id": "INT-ENC-01", "name": "Encryption at Rest", "badges": ["HIPAA-164.312", "ISO-A.8.24"]},
    "9.2.1": {"id": "INT-AUDIT-01", "name": "Internal Audit Program", "badges": ["ISO-9.2", "SOC2-CC1.2"]}
}

# EXACT 123 ITEMS (30 Clauses + 93 Annex A Controls)
ISO_STRUCTURE = [
    # CLAUSE 4: Context (4)
    {"id": "4.1", "name": "Understanding the organization", "description": "Determine external and internal issues.", "type": "CLAUSE", "domain": "Context", "process": PROCESS_GOV},
    {"id": "4.2", "name": "Understanding needs of stakeholders", "description": "Determine interested parties and requirements.", "type": "CLAUSE", "domain": "Context", "process": PROCESS_GOV},
    {"id": "4.3", "name": "Scope of the ISMS", "description": "Determine the boundaries and applicability.", "type": "CLAUSE", "domain": "Context", "process": PROCESS_GOV},
    {"id": "4.4", "name": "ISMS", "description": "Establish, implement, maintain and continually improve the ISMS.", "type": "CLAUSE", "domain": "Context", "process": PROCESS_GOV},

    # CLAUSE 5: Leadership (3)
    {"id": "5.1", "name": "Leadership and commitment", "description": "Top management commitment.", "type": "CLAUSE", "domain": "Leadership", "process": PROCESS_GOV},
    {"id": "5.2", "name": "Policy", "description": "Establish information security policy.", "type": "CLAUSE", "domain": "Leadership", "process": PROCESS_GOV},
    {"id": "5.3", "name": "Organizational roles", "description": "Assign responsibilities and authorities.", "type": "CLAUSE", "domain": "Leadership", "process": PROCESS_GOV},

    # CLAUSE 6: Planning (5)
    {"id": "6.1.1", "name": "General planning", "description": "Plan actions to address risks and opportunities.", "type": "CLAUSE", "domain": "Planning", "process": PROCESS_RISK},
    {"id": "6.1.2", "name": "Information security risk assessment", "description": "Define and apply a risk assessment process.", "type": "CLAUSE", "domain": "Planning", "process": PROCESS_RISK},
    {"id": "6.1.3", "name": "Information security risk treatment", "description": "Define and apply a risk treatment process.", "type": "CLAUSE", "domain": "Planning", "process": PROCESS_RISK},
    {"id": "6.2", "name": "Information security objectives", "description": "Establish objectives and plans to achieve them.", "type": "CLAUSE", "domain": "Planning", "process": PROCESS_RISK},
    {"id": "6.3", "name": "Planning of changes", "description": "Changes to the ISMS shall be carried out in a planned manner.", "type": "CLAUSE", "domain": "Planning", "process": PROCESS_RISK},

    # CLAUSE 7: Support (7)
    {"id": "7.1", "name": "Resources", "description": "Determine and provide resources.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_GOV},
    {"id": "7.2", "name": "Competence", "description": "Ensure necessary competence of persons.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_HR},
    {"id": "7.3", "name": "Awareness", "description": "Persons doing work shall be aware of policy.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_HR},
    {"id": "7.4", "name": "Communication", "description": "Determine internal and external communications.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_GOV},
    {"id": "7.5.1", "name": "General Documented Info", "description": "ISMS shall include documented information.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_GOV},
    {"id": "7.5.2", "name": "Creating and updating", "description": "Appropriate identification and format.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_GOV},
    {"id": "7.5.3", "name": "Control of documented info", "description": "Protected and available.", "type": "CLAUSE", "domain": "Support", "process": PROCESS_GOV},

    # CLAUSE 8: Operation (3)
    {"id": "8.1", "name": "Operational planning and control", "description": "Plan, implement and control processes.", "type": "CLAUSE", "domain": "Operation", "process": PROCESS_RISK},
    {"id": "8.2", "name": "Information security risk assessment", "description": "Perform risk assessments at planned intervals.", "type": "CLAUSE", "domain": "Operation", "process": PROCESS_RISK},
    {"id": "8.3", "name": "Information security risk treatment", "description": "Implement risk treatment plan.", "type": "CLAUSE", "domain": "Operation", "process": PROCESS_RISK},

    # CLAUSE 9: Performance Evaluation (6)
    {"id": "9.1", "name": "Monitoring, measurement, analysis", "description": "Evaluate the information security performance.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},
    {"id": "9.2.1", "name": "General Internal Audit", "description": "Conduct internal audits at planned intervals.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},
    {"id": "9.2.2", "name": "Internal Audit Programme", "description": "Plan, establish, implement audit programme.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},
    {"id": "9.3.1", "name": "General Management Review", "description": "Top management shall review ISMS.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},
    {"id": "9.3.2", "name": "Management Review Inputs", "description": "Include status of actions, changes, and feedback.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},
    {"id": "9.3.3", "name": "Management Review Results", "description": "Decisions related to improvement opportunities.", "type": "CLAUSE", "domain": "Performance", "process": PROCESS_PERF},

    # CLAUSE 10: Improvement (2)
    {"id": "10.1", "name": "Continual improvement", "description": "Continually improve suitability, adequacy, effectiveness.", "type": "CLAUSE", "domain": "Improvement", "process": PROCESS_IMPROVE},
    {"id": "10.2", "name": "Nonconformity and corrective action", "description": "React to nonconformity and take action.", "type": "CLAUSE", "domain": "Improvement", "process": PROCESS_IMPROVE},

    # ANNEX A.5: Organizational (37)
    {"id": "A.5.1", "name": "Policies for information security", "description": "Policies for information security.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.2", "name": "Information security roles", "description": "Information security roles and responsibilities.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.3", "name": "Segregation of duties", "description": "Segregation of duties.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.4", "name": "Management responsibilities", "description": "Management responsibilities.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.5", "name": "Contact with authorities", "description": "Contact with authorities.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.6", "name": "Contact with special interest groups", "description": "Contact with special interest groups.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.7", "name": "Threat intelligence", "description": "Threat intelligence.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_THREAT},
    {"id": "A.5.8", "name": "Information security in project management", "description": "Information security in project management.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_GOV},
    {"id": "A.5.9", "name": "Inventory of information and other associated assets", "description": "Inventory of information and other associated assets.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.10", "name": "Acceptable use of information and other associated assets", "description": "Acceptable use of information and other associated assets.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.11", "name": "Return of assets", "description": "Return of assets.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.12", "name": "Classification of information", "description": "Classification of information.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.13", "name": "Labelling of information", "description": "Labelling of information.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.14", "name": "Information transfer", "description": "Information transfer.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_NETWORK},
    {"id": "A.5.15", "name": "Access control", "description": "Access control.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_IAM},
    {"id": "A.5.16", "name": "Identity management", "description": "Identity management.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_IAM},
    {"id": "A.5.17", "name": "Authentication information", "description": "Authentication information.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_IAM},
    {"id": "A.5.18", "name": "Access rights", "description": "Access rights.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_IAM},
    {"id": "A.5.19", "name": "Information security in supplier relationships", "description": "Information security in supplier relationships.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_SUPPLIER},
    {"id": "A.5.20", "name": "Addressing information security within supplier agreements", "description": "Addressing information security within supplier agreements.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_SUPPLIER},
    {"id": "A.5.21", "name": "Managing information security in the ICT supply chain", "description": "Managing information security in the ICT supply chain.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_SUPPLIER},
    {"id": "A.5.22", "name": "Monitoring, review and change management of supplier services", "description": "Monitoring, review and change management of supplier services.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_SUPPLIER},
    {"id": "A.5.23", "name": "Information security for use of cloud services", "description": "Information security for use of cloud services.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_SUPPLIER},
    {"id": "A.5.24", "name": "Information security incident management planning and preparation", "description": "Information security incident management planning and preparation.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.25", "name": "Assessment and decision on information security events", "description": "Assessment and decision on information security events.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.26", "name": "Response to information security incidents", "description": "Response to information security incidents.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.27", "name": "Learning from information security incidents", "description": "Learning from information security incidents.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.28", "name": "Collection of evidence", "description": "Collection of evidence.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.29", "name": "Information security during disruption", "description": "Information security during disruption.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.30", "name": "ICT readiness for business continuity", "description": "ICT readiness for business continuity.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_INCIDENT},
    {"id": "A.5.31", "name": "Legal, statutory, regulatory and contractual requirements", "description": "Legal, statutory, regulatory and contractual requirements.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_LEGAL},
    {"id": "A.5.32", "name": "Intellectual property rights", "description": "Intellectual property rights.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_LEGAL},
    {"id": "A.5.33", "name": "Protection of records", "description": "Protection of records.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_ASSET},
    {"id": "A.5.34", "name": "Privacy and protection of PII", "description": "Privacy and protection of PII.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_LEGAL},
    {"id": "A.5.35", "name": "Independent review of information security", "description": "Independent review of information security.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_PERF},
    {"id": "A.5.36", "name": "Compliance with policies, rules and standards", "description": "Compliance with policies, rules and standards.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_LEGAL},
    {"id": "A.5.37", "name": "Documented operating procedures", "description": "Documented operating procedures.", "type": "CONTROL", "domain": "Organizational", "process": PROCESS_OPS},

    # ANNEX A.6: People (8)
    {"id": "A.6.1", "name": "Screening", "description": "Screening.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.2", "name": "Terms and conditions of employment", "description": "Terms and conditions of employment.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.3", "name": "Information security awareness, education and training", "description": "Information security awareness, education and training.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.4", "name": "Disciplinary process", "description": "Disciplinary process.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.5", "name": "Responsibilities after termination or change of employment", "description": "Responsibilities after termination or change of employment.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.6", "name": "Confidentiality or non-disclosure agreements", "description": "Confidentiality or non-disclosure agreements.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.7", "name": "Remote working", "description": "Remote working.", "type": "CONTROL", "domain": "People", "process": PROCESS_HR},
    {"id": "A.6.8", "name": "Information security event reporting", "description": "Information security event reporting.", "type": "CONTROL", "domain": "People", "process": PROCESS_INCIDENT},

    # ANNEX A.7: Physical (14)
    {"id": "A.7.1", "name": "Physical security perimeters", "description": "Physical security perimeters.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.2", "name": "Physical entry", "description": "Physical entry.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.3", "name": "Securing offices, rooms and facilities", "description": "Securing offices, rooms and facilities.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.4", "name": "Physical security monitoring", "description": "Physical security monitoring.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.5", "name": "Protecting against physical and environmental threats", "description": "Protecting against physical and environmental threats.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.6", "name": "Working in secure areas", "description": "Working in secure areas.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.7", "name": "Clear desk and clear screen", "description": "Clear desk and clear screen.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_ASSET},
    {"id": "A.7.8", "name": "Equipment siting and protection", "description": "Equipment siting and protection.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.9", "name": "Security of assets off-premises", "description": "Security of assets off-premises.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.10", "name": "Storage media", "description": "Storage media.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_ASSET},
    {"id": "A.7.11", "name": "Supporting utilities", "description": "Supporting utilities.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.12", "name": "Cabling security", "description": "Cabling security.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_NETWORK},
    {"id": "A.7.13", "name": "Equipment maintenance", "description": "Equipment maintenance.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_PHYSICAL},
    {"id": "A.7.14", "name": "Secure disposal or re-use of equipment", "description": "Secure disposal or re-use of equipment.", "type": "CONTROL", "domain": "Physical", "process": PROCESS_ASSET},

    # ANNEX A.8: Technological (34)
    {"id": "A.8.1", "name": "User endpoint devices", "description": "User endpoint devices.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_ASSET},
    {"id": "A.8.2", "name": "Privileged access rights", "description": "Privileged access rights.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_IAM},
    {"id": "A.8.3", "name": "Information access restriction", "description": "Information access restriction.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_IAM},
    {"id": "A.8.4", "name": "Access to source code", "description": "Access to source code.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.5", "name": "Secure authentication", "description": "Secure authentication.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_IAM},
    {"id": "A.8.6", "name": "Capacity management", "description": "Capacity management.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_CAPACITY},
    {"id": "A.8.7", "name": "Protection against malware", "description": "Protection against malware.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_OPS},
    {"id": "A.8.8", "name": "Management of technical vulnerabilities", "description": "Management of technical vulnerabilities.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_VULN},
    {"id": "A.8.9", "name": "Configuration management", "description": "Configuration management.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_CONFIG},
    {"id": "A.8.10", "name": "Information deletion", "description": "Information deletion.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_ASSET},
    {"id": "A.8.11", "name": "Data masking", "description": "Data masking.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_ASSET},
    {"id": "A.8.12", "name": "Data leakage prevention", "description": "Data leakage prevention.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_OPS},
    {"id": "A.8.13", "name": "Information backup", "description": "Information backup.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_BACKUP},
    {"id": "A.8.14", "name": "Redundancy of information processing facilities", "description": "Redundancy of information processing facilities.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_OPS},
    {"id": "A.8.15", "name": "Logging", "description": "Logging.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_LOGGING},
    {"id": "A.8.16", "name": "Monitoring activities", "description": "Monitoring activities.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_LOGGING},
    {"id": "A.8.17", "name": "Clock synchronization", "description": "Clock synchronization.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_CLOCK},
    {"id": "A.8.18", "name": "Use of privileged utility programs", "description": "Use of privileged utility programs.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_OPS},
    {"id": "A.8.19", "name": "Installation of software on operational systems", "description": "Installation of software on operational systems.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_OPS},
    {"id": "A.8.20", "name": "Networks security", "description": "Networks security.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_NETWORK},
    {"id": "A.8.21", "name": "Security of network services", "description": "Security of network services.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_NETWORK},
    {"id": "A.8.22", "name": "Segregation of networks", "description": "Segregation of networks.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_NETWORK},
    {"id": "A.8.23", "name": "Web filtering", "description": "Web filtering.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_NETWORK},
    {"id": "A.8.24", "name": "Use of cryptography", "description": "Use of cryptography.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_CRYPTO},
    {"id": "A.8.25", "name": "Secure development lifecycle", "description": "Secure development lifecycle.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.26", "name": "Application security requirements", "description": "Application security requirements.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.27", "name": "Secure system architecture and engineering principles", "description": "Secure system architecture and engineering principles.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.28", "name": "Secure coding", "description": "Secure coding.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.29", "name": "Security testing in development and acceptance", "description": "Security testing in development and acceptance.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.30", "name": "Outsourced development", "description": "Outsourced development.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.31", "name": "Separation of development, test and production environments", "description": "Separation of development, test and production environments.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.32", "name": "Change management", "description": "Change management.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.33", "name": "Test information", "description": "Test information.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC},
    {"id": "A.8.34", "name": "Protection of information systems during audit testing", "description": "Protection of information systems during audit testing.", "type": "CONTROL", "domain": "Technological", "process": PROCESS_SDLC}
]

# Updated Status Distribution
STATUSES = [
    "VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED", # 50% Clean
    "PENDING", "PENDING", "PENDING", # 30% Pending
    "MAJOR_NC", # 1 Critical Issue
    "MINOR_NC", "MINOR_NC", # 2 Minor Issues
    "OBSERVATION", "OBSERVATION", # 2 Observations
    "OFI", # 1 Opportunity for Improvement
    "NEEDS_CLARIFICATION"
]

RESOURCES = ["AWS-Config-Prod", "Emp-Handbook-v2", "PenTest-Report-2025", "Access-Review-Q4", "Risk-Register-XLS"]

def generate_evidence():
    evidence_list = []
    trends = []
    
    count = 0
    
    for item in ISO_STRUCTURE:
        status = random.choice(STATUSES)
        resource = random.choice(RESOURCES)
        
        # SOA LOGIC: Deterministic Exclusion (A.8.28, A.8.30 are Not Applicable)
        is_applicable = True
        if item["id"] in ["A.8.28", "A.8.30"]:
            is_applicable = False
            status = "NOT_APPLICABLE"

        payload = {}

        # SPECIAL LOGIC: A.8.24 CRYPTOGRAPHY (Encryption Matrix)
        if item["id"] == "A.8.24" and is_applicable:
            vol_type = random.choice(["EBS", "RDS", "S3"])
            is_encrypted = random.choice([True, True, False]) # Bias towards encrypted
            algo = "AES-256" if is_encrypted else "None"
            payload = {
                "resource_type": vol_type,
                "volume_id": f"vol-{random.randint(10000,99999)}",
                "encryption_status": "ENCRYPTED" if is_encrypted else "UNENCRYPTED",
                "algorithm": algo,
                "check": "passed" if is_encrypted else "failed"
            }
            if not is_encrypted: status = "MAJOR_NC" # Critical failure

        # SPECIAL LOGIC: A.8.28 SECURE CODING (GitHub Metrics)
        elif item["id"] == "A.8.28" and is_applicable:
            repo_name = f"repo-{random.choice(['backend', 'frontend', 'infra'])}-{random.randint(1,5)}"
            bp_enabled = random.choice([True, True, False])
            payload = {
                "repository": repo_name,
                "branch_protection": "ENABLED" if bp_enabled else "DISABLED",
                "pr_reviews_required": 2 if bp_enabled else 0,
                "dismiss_stale_reviews": bp_enabled,
                "check": "passed" if bp_enabled else "failed"
            }
            if not bp_enabled: status = "MINOR_NC"

        # STANDARD LOGIC
        else:
            if status in ["MAJOR_NC", "MINOR_NC"]:
                payload = {"error": "Non-Conformity Detected", "details": "Control implementation does not meet policy requirements."}
            elif status == "VERIFIED":
                payload = {"check": "passed", "verified_by": "System"}
            else:
                payload = {"uploaded_by": "user", "file_type": "pdf"}

        # Look up Intent
        intent_data = COMPLIANCE_INTENTS.get(item["id"], DEFAULT_INTENT)

        evidence_item = {
            "id": f"EV-{2000 + count}",
            "control_id": item["id"],
            "control_name": item["name"],
            "control_description": item["description"], 
            "domain": item["domain"], 
            "type": item["type"],     
            "process": item["process"],
            "is_applicable": is_applicable,
            "intent": {
                "id": intent_data["id"],
                "name": intent_data["name"]
            },
            "badges": intent_data["badges"],
            "resource_name": f"{resource}-{random.randint(100,999)}",
            "status": status,
            "submitted_at": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
            "auditor_comment": "Please clarify." if status == "NEEDS_CLARIFICATION" else None,
            "raw_payload": payload
        }
        evidence_list.append(evidence_item)
        count += 1

    # 2. Generate Historical Data
    base_score = 30
    for i in range(12):
        month_name = (datetime.now() - timedelta(days=30 * (11-i))).strftime("%b")
        base_score += random.randint(2, 5)
        if base_score > 98: base_score = 98
        trends.append({"month": month_name, "score": base_score})

    return {
        "current_evidence": evidence_list,
        "historical_trends": trends,
        "generated_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    data = generate_evidence()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data['current_evidence'])} ISO 27001:2022 mock evidence items + Trends in {OUTPUT_FILE}")
