from app.database import SessionLocal, engine, Base
from app.models.policy import Policy
from app.services.ai_service import generate_premium_policy
import time
import datetime

# List of policies required by ISO 27001:2022 [Updated with ISO 27001:2022 Control IDs]
# Source: Annex A 5.1, 5.15, 5.24, 6.6, 6.7, 7.5, 8.1, 8.4, 8.7, 8.10, 8.13, 8.24, 8.25
POLICIES_TO_SEED = [
    {
        "name": "Change Management Policy",
        "control": "A.8.32 Change management",
        "description": "Changes to information processing facilities and information systems shall be subject to change management procedures."
    },
    {
        "name": "Information Security Policy",
        "control": "A.5.1 Policies for information security",
        "description": "Information security policies and topic-specific policies shall be defined, approved and communicated."
    },
    {
        "name": "Access Control Policy",
        "control": "A.5.15 Access control",
        "description": "Rules to control physical and logical access to information and information processing facilities shall be defined and implemented."
    },
    {
        "name": "Acceptable Use Policy (AUP)",
        "control": "A.5.10 Acceptable use of information and other associated assets",
        "description": "Rules for proper use of company assets, detailing expected behavior and prohibited activities."
    },
    {
        "name": "Supplier Security Policy",
        "control": "A.5.19 Information security in supplier relationships",
        "description": "Requirements for mitigating risks associated with suppliers' access to the organization's assets."
    },
    {
        "name": "Remote Working Policy",
        "control": "A.6.7 Remote working",
        "description": "Security measures for protecting information accessed, processed, or stored at teleworking sites."
    },
    {
        "name": "Incident Management Policy",
        "control": "A.5.24 Information security incident management planning and preparation",
        "description": "Procedures for reporting, assessing, responding to, and learning from information security incidents."
    },
    {
        "name": "Business Continuity Policy",
        "control": "A.5.29 Information security during disruption",
        "description": "Framework for maintaining information security continuity during adverse situations or crises."
    },
    {
        "name": "Cryptography Policy",
        "control": "A.8.24 Use of cryptography",
        "description": "Rules for the effective use of cryptographic controls (encryption) to protect confidentiality and integrity."
    },
    {
        "name": "Secure Development Policy",
        "control": "A.8.25 Secure development life cycle",
        "description": "Rules for secure software development and system engineering, including security checkpoints."
    },
    {
        "name": "Data Retention & Disposal Policy",
        "control": "A.8.10 Information deletion",
        "description": "Guidelines for data retention periods and secure disposal of media and information."
    },
    {
        "name": "Human Resource Security Policy",
        "control": "A.6.1 Screening",
        "description": "Security requirements for employees during onboarding, employment, and offboarding."
    },
    {
        "name": "Asset Management Policy",
        "control": "A.5.9 Inventory of information and other associated assets",
        "description": "Rules for identifying, classifying, and managing information assets throughout their lifecycle."
    },
    {
        "name": "Physical Security Policy",
        "control": "A.7.1 Physical security perimeters",
        "description": "Measures to prevent unauthorized physical access, damage, and interference to the organization's premises."
    }
]

COMPANY_PROFILE = {
    "Industry": "B2B SaaS (FinTech)",
    "Cloud Provider": "AWS (Amazon Web Services)",
    "Identity Provider": "Okta",
    "Source Control": "GitHub",
    "Work Model": "Remote-First",
    "Communication": "Slack",
    "Device Management": "Kandji (macOS) / Intune (Windows)"
}

def seed_enhanced_policies():
    print("----------------------------------------------------------------")
    print(" STARTING PREMIUM POLICY GENERATION (Powered by Gemini 2.0)")
    print("----------------------------------------------------------------")
    
    db = SessionLocal()
    
    count = 0
    total = len(POLICIES_TO_SEED)

    for p in POLICIES_TO_SEED:
        count += 1
        name = p["name"]
        print(f"[{count}/{total}] Processing: {name}")
        
        # Check if exists to avoid unnecessary API costs/time, OR overwrite if draft
        existing = db.query(Policy).filter(Policy.name == name).first()
        
        if existing and existing.status == "Approved":
            print(f"   -> Skipped (Already Approved)")
            continue

        print(f"   -> Generating Content with AI Engine...")
        try:
            # Retry Logic for Rate Limits
            max_retries = 3
            entry_content = ""
            
            for attempt in range(max_retries):
                try:
                    # Call AI Service - NEW ENGINE
                    entry_content = generate_premium_policy(
                        control_title=p["control"], 
                        policy_name=name,
                        company_profile=COMPANY_PROFILE,
                        control_description=p["description"]
                    )
                    
                    if "Error" in entry_content and len(entry_content) < 500:
                         raise Exception(entry_content) # Trigger retry if AI returned error string
                         
                    break # Success
                except Exception as e:
                    print(f"   -> Attempt {attempt+1} failed ({e}). Retrying in 20s...")
                    time.sleep(20)
            
            # Fallback if AI completely fails
            if not entry_content or "Error" in entry_content:
                print(f"   -> AI Service Exhausted. Using Premium Template Fallback.")
                entry_content = f"""
| Document Control | |
| :--- | :--- |
| **Classification** | Internal Use Only |
| **Owner** | Compliance Officer |
| **Approver** | CTO / CISO |
| **Version** | 1.0 (Draft) |
| **Last Updated** | {datetime.datetime.utcnow().strftime('%Y-%m-%d')} |

---

# {name}

## 1. Purpose
The purpose of this {name} is to establish the requirements for {p['description'].lower()} This ensures compliance with {p['control']} of ISO 27001:2022.

## 2. Scope
This policy applies to all employees, contractors, and third-party users who have access to {COMPANY_PROFILE['Industry']} systems and data.
Specific systems in scope include: **{COMPANY_PROFILE['Cloud Provider']}** and **{COMPANY_PROFILE['Identity Provider']}** environments.

## 3. Policy Statements

### 3.1 General Requirements
The organization shall enforce strict controls regarding {name}.
*   All changes must be authorized.
*   Risk assessments must be performed.
*   Logs must be maintained.

*(Note: This is a robust template placeholder generated because the AI service is momentarily unavailable. Please click 'Auto-Fill' or 'Regenerate' later to get full custom details.)*

## 4. Roles & Responsibilities
| Role | Responsibility |
| :--- | :--- |
| **CISO** | Accountable for policy enforcement. |
| **System Owners** | Responsible for implementation. |
| **Users** | Responsible for adherence. |

## 5. Compliance Mapping
| Reference | Requirement |
| :--- | :--- |
| **{p['control']}** | {p['description']} |
"""

            # Brief pause to respect potential rate limits
            time.sleep(5)
            
            if existing:
                print(f"   -> Updating existing draft.")
                existing.content = entry_content
                existing.description = p["description"]
                existing.updated_at = datetime.datetime.utcnow()
                existing.version = "2.0-AI" 
                existing.status = "Review" 
            else:
                print(f"   -> Creating new policy.")
                new_policy = Policy(
                    name=name,
                    description=p["description"],
                    content=entry_content,
                    status="Review",
                    owner="Compliance Officer",
                    version="2.0-AI",
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )
                db.add(new_policy)
            
            db.commit()
            print("   -> Success.")
            
        except Exception as e:
            print(f"   -> CRITICAL ERROR: {e}")
            db.rollback()

    db.close()
    print("----------------------------------------------------------------")
    print(" POLICY GENERATION COMPLETE")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    seed_enhanced_policies()
