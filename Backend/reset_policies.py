from app.database import SessionLocal
from app.models.policy import Policy
import datetime

# Define the Base Templates (from seed_policies.py) to restore "Template" state
TEMPLATES = {
    "Information Security Policy": """# Information Security Policy

## 1. Objective
To protect the organization's information assets from all threats, whether internal or external, deliberate or accidental.

## 2. Scope
This policy applies to all employees, contractors, and third parties who have access to information systems.

## 3. Policy Statements
- Information will be protected against unauthorized access.
- Confidentiality of information will be assured.
- Integrity of information will be maintained.
- Availability of information for business processes will be maintained.
""",
    "Access Control Policy": """# Access Control Policy

## 1. Purpose
To limit access to information and information processing facilities to authorized users.

## 2. User Access Management
- Formal user registration and de-registration process.
- Management of privileged access rights.
- Management of secret authentication information of users.

## 3. System Access Control
- Secure log-on procedures.
- Password management system.
- Use of privileged utility programs.
""",
    "Supplier Relationships Policy": """# Supplier Relationships Policy

## 1. Purpose
To ensure protection of the organization's assets that are accessible by suppliers.

## 2. Information Security in Supplier Relationships
- Information security policy for supplier relationships.
- Addressing security within supplier agreements.
- Information and communication technology supply chain.
""",
    "Mobile Device Policy": """# Mobile Device Policy

## 1. Mobile Device Management
- Registration of mobile devices.
- Physical protection.
- Access control.

## 2. Teleworking
- Security of teleworking site.
- Protection of information accessed remotely.
""",
    "Cryptography Policy": """# Cryptography Policy

## 1. Purpose
To ensure proper and effective use of cryptography to protect the confidentiality, authenticity and/or integrity of information.

## 2. Policy
- Use of encryption for sensitive data at rest and in transit.
- Key management lifecycle (generation, storage, destruction).
""",
    "Clear Desk and Clear Screen Policy": """# Clear Desk and Clear Screen Policy

## 1. Policy
- Papers and portable storage media must be locked away when not in use.
- Computer screens must be locked when unattended.
- Sensitive information must not be left on printers or fax machines.
"""
}

def reset_policies():
    db = SessionLocal()
    policies = db.query(Policy).all()
    
    print(f"Checking {len(policies)} Policies for Reset...")
    
    for p in policies:
        # Reset Status
        p.status = "Draft"
        p.version = "1.0 (Draft)"
        p.updated_at = datetime.datetime.utcnow()
        
        # Reset Content to Template if available
        if p.name in TEMPLATES:
            p.content = TEMPLATES[p.name]
            print(f" [RESET] {p.name} -> Reverted to Template & Draft")
        else:
            # If it's a custom policy, just mark as draft but keep content? 
            # User said "Reset all... to fresh", perhaps wipe content too?
            # Let's keep content for unknown ones but mark draft.
            print(f" [DRAFT] {p.name} -> Set to Draft (Custom Policy)")
            
    db.commit()
    db.close()
    print("All policies have been reset to Fresh Drafts with Templates.")

if __name__ == "__main__":
    reset_policies()
