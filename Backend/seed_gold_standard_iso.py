from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.policy import Policy
import json
import datetime

def seed_gold_standard():
    db = SessionLocal()
    print("Seeding ISO 27001:2022 Gold Standard Library...")

    # 1. Define The 15 High-Level Policies (Annex A Mappings)
    # Format: Title, Description, Controls
    annex_a_policies = [
        {
            "name": "Access Control Policy",
            "controls": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"],
            "description": "Governs the granting, review, and revocation of access rights to information assets."
        },
        {
            "name": "Asset Management Policy",
            "controls": ["A.5.9", "A.5.10", "A.5.11", "A.7.10"],
            "description": "Rules for inventorying, classifying, and handling information assets."
        },
        {
            "name": "Physical & Environmental Security Policy",
            "controls": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.7.7", "A.7.8", "A.7.9", "A.7.10", "A.7.11", "A.7.12", "A.7.13", "A.7.14"],
            "description": "Protects physical perimeters, offices, and equipment."
        },
        {
            "name": "Human Resources Security Policy",
            "controls": ["A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5", "A.6.6"],
            "description": "Security roles and responsibilities for employees during onboarding, employment, and termination."
        },
        {
            "name": "Secure Development Policy (SDLC)",
            "controls": ["A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29", "A.8.30", "A.8.31"],
            "description": "Ensures security is built into the software development lifecycle."
        },
        {
            "name": "Supplier & Vendor Security Policy",
            "controls": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
            "description": "Manages risks related to third-party suppliers and cloud providers."
        },
        {
            "name": "Incident Management Procedure",
            "controls": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28"],
            "description": "Procedures for detecting, reporting, and responding to information security incidents."
        },
        {
            "name": "Business Continuity & Disaster Recovery Plan",
            "controls": ["A.5.29", "A.5.30", "A.8.14"],
            "description": "Ensures the organization can recover from disruptive incidents."
        },
        {
            "name": "Mobile Device & Remote Working Policy",
            "controls": ["A.6.7", "A.8.1"],
            "description": "Secures teleworking and the use of mobile devices."
        },
        {
            "name": "Cryptography & Key Management Policy",
            "controls": ["A.8.24"],
            "description": "Standards for the use of encryption and management of cryptographic keys."
        },
        {
            "name": "Operations Security Policy",
            "controls": ["A.8.15", "A.8.16", "A.8.17", "A.8.19"],
            "description": "Ensures correct and secure operations of information processing facilities."
        },
        {
            "name": "Vulnerability & Patch Management Policy",
            "controls": ["A.8.8"],
            "description": "Timely detection and remediation of technical vulnerabilities."
        },
        {
            "name": "Backup & Retention Policy",
            "controls": ["A.8.10", "A.8.13"],
            "description": "Requirements for data backup frequency, testing, and retention."
        },
        {
            "name": "Network Security Policy",
            "controls": ["A.8.20", "A.8.21", "A.8.22"],
            "description": "Security of network infrastructure and data in transit."
        },
        {
            "name": "Data Protection & Privacy Policy",
            "controls": ["A.5.34", "A.8.11", "A.8.12"],
            "description": "Protection of PII and measures against data leakage."
        }
    ]

    # 2. Core ISMS Documents (Clauses 4-10)
    isms_docs = [
        {"name": "ISMS Scope Statement", "desc": "Clause 4.3"},
        {"name": "Information Security Policy (Leadership)", "desc": "Clause 5.2"},
        {"name": "ISMS Roles & Responsibilities", "desc": "Clause 5.3"},
        {"name": "Risk Assessment Methodology", "desc": "Clause 6.1"},
        {"name": "Risk Treatment Plan", "desc": "Clause 6.1.3"},
        {"name": "Competence & Training Policy", "desc": "Clause 7.2"},
        {"name": "Communication Plan", "desc": "Clause 7.4"},
        {"name": "Internal Audit Program", "desc": "Clause 9.2"},
        {"name": "Management Review Minutes Template", "desc": "Clause 9.3"},
        {"name": "Corrective Action Log", "desc": "Clause 10.2"},
    ]

    # Standard Markdown Template with Placeholders
    def generate_content(title):
        return f"""# {title}

**Version:** 1.0 (Template)
**Date:** {datetime.date.today()}
**Owner:** {{policy_owner}}

---

## 1. Purpose
The purpose of this {title} is to ensure {{company_name}} protects its information assets and meets the requirements of ISO/IEC 27001:2022.

## 2. Scope
This document applies to all employees, contractors, and third parties of {{company_name}} who access our systems, including systems hosted on {{cloud_provider}} and authenticated via {{identity_provider}}.

## 3. Policy Statements

### 3.1 General Requirements
{{company_name}} shall implement measures to... (Content specific to {title} goes here).

### 3.2 Specific Controls
- Control 1: ...
- Control 2: ...

## 4. Roles & Responsibilities
- **CISO**: Responsible for maintaining this policy.
- **Employees**: Responsible for adhering to this policy.

## 5. Compliance Mapping
| Clause/Control | Requirement |
| :--- | :--- |
| ISO 27001 | Mapped to relevant clauses |

"""

    count = 0
    
    # Process Annex A Policies
    for p_data in annex_a_policies:
        # Append (Template) to ensure uniqueness vs existing user policies
        template_name = f"{p_data['name']} (Template)"
        
        # Check if exists as template
        existing = db.query(Policy).filter(Policy.name == template_name).first()
        
        if not existing:
            new_p = Policy(
                name=template_name,
                description=p_data["description"],
                content=generate_content(p_data["name"]), # Title inside content doesn't need suffix necessarily, but fine
                version="1.0",
                status="Template",
                is_template=True,
                linked_frameworks="ISO 27001:2022",
                mapped_controls=json.dumps(p_data["controls"])
            )
            db.add(new_p)
            count += 1
        else:
            # Update mapping if exists
            existing.mapped_controls = json.dumps(p_data["controls"])
            existing.is_template = True # Ensure flag is set
            db.add(existing)

    # Process ISMS Docs
    for doc in isms_docs:
        template_name = f"{doc['name']} (Template)"
        existing = db.query(Policy).filter(Policy.name == template_name).first()
        if not existing:
            new_p = Policy(
                name=template_name,
                description=doc["desc"],
                content=generate_content(doc["name"]),
                version="1.0",
                status="Template",
                is_template=True,
                linked_frameworks="ISO 27001:2022",
                mapped_controls="[]"
            )
            db.add(new_p)
            count += 1

    db.commit()
    print(f"Seeded {count} new Gold Standard Templates.")
    db.close()

if __name__ == "__main__":
    seed_gold_standard()
