from app.database import SessionLocal, engine, Base
from app.models.policy import Policy
import datetime

# Ensure tables exist (will create if missing, but won't migrate existing columns in SQLite easily without Alembic)
# valid for dev if we don't mind potential schema mismatch errors if not recreated.
# Base.metadata.create_all(bind=engine) 

def seed_policies():
    db = SessionLocal()
    
    # ISO 27001:2022 Mandatory Documents check
    policies = [
        {
            "name": "Information Security Policy",
            "description": "High-level policy defining the organization's information security objectives and commitment.",
            "content": """# Information Security Policy

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
            "status": "Approved",
            "owner": "CISO",
            "version": "1.0"
        },
        {
            "name": "Access Control Policy",
            "description": "Policy governing access to information and information processing facilities.",
            "content": """# Access Control Policy

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
            "status": "Review",
            "owner": "IT Manager",
            "version": "0.9"
        },
        {
            "name": "Supplier Relationships Policy",
            "description": "Policy for ensuring security in supplier relationships.",
            "content": """# Supplier Relationships Policy

## 1. Purpose
To ensure protection of the organization's assets that are accessible by suppliers.

## 2. Information Security in Supplier Relationships
- Information security policy for supplier relationships.
- Addressing security within supplier agreements.
- Information and communication technology supply chain.
""",
            "status": "Draft",
            "owner": "Legal",
            "version": "0.1"
        },
        {
            "name": "Mobile Device Policy",
            "description": "Policy for the use of mobile devices and teleworking.",
            "content": """# Mobile Device Policy

## 1. Mobile Device Management
- Registration of mobile devices.
- Physical protection.
- Access control.

## 2. Teleworking
- Security of teleworking site.
- Protection of information accessed remotely.
""",
            "status": "Approved",
            "owner": "IT Ops",
            "version": "2.1"
        },
        {
            "name": "Cryptography Policy",
            "description": "Policy on the use of cryptographic controls.",
            "content": """# Cryptography Policy

## 1. Purpose
To ensure proper and effective use of cryptography to protect the confidentiality, authenticity and/or integrity of information.

## 2. Policy
- Use of encryption for sensitive data at rest and in transit.
- Key management lifecycle (generation, storage, destruction).
""",
            "status": "Approved",
            "owner": "Security Engineering",
            "version": "1.0"
        },
        {
            "name": "Clear Desk and Clear Screen Policy",
            "description": "Policy requirments for leaving workstations unattended.",
            "content": """# Clear Desk and Clear Screen Policy

## 1. Policy
- Papers and portable storage media must be locked away when not in use.
- Computer screens must be locked when unattended.
- Sensitive information must not be left on printers or fax machines.
""",
            "status": "Approved",
            "owner": "HR",
            "version": "1.0"
        },
        {
            "name": "Privacy Policy",
            "description": "Policy governing the collection, use, and disposal of personal information (PII).",
            "content": "# Privacy Policy\n\n## Purpose\nTo ensure compliance with privacy laws and SOC 2 Privacy criteria.\n\n## Policy\n- Notice to subjects.\n- Choice and consent.\n- Collection only for specified purposes.",
            "status": "Draft",
            "owner": "Legal",
            "version": "1.0",
            "linked_frameworks": "SOC 2 (Privacy), GDPR"
        },
        {
            "name": "Disaster Recovery Policy",
            "description": "Procedures for restoring IT infrastructure after a disruption.",
            "content": "# Disaster Recovery Policy\n\n## Objective\nTo minimize downtime and data loss in the event of a disaster.\n\n## Scope\nCritical systems including ERP and CRM.",
            "status": "Approved",
            "owner": "IT Ops",
            "version": "1.2",
            "linked_frameworks": "SOC 2 (Availability), ISO 27001"
        }
    ]

    print(f"Seeding {len(policies)} Policies...")
    
    for p_data in policies:
        # Check if exists
        exists = db.query(Policy).filter(Policy.name == p_data["name"]).first()
        if not exists:
            policy = Policy(
                name=p_data["name"],
                description=p_data["description"],
                content=p_data["content"],
                status=p_data.get("status", "Draft"),
                owner=p_data.get("owner", "Compliance"),
                version=p_data.get("version", "1.0"),
                linked_frameworks=p_data.get("linked_frameworks", "ISO 27001, SOC 2"),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(policy)
            print(f"Created: {p_data['name']}")
        else:
            # Update linked_frameworks for existing
            exists.linked_frameworks = p_data.get("linked_frameworks", "ISO 27001, SOC 2")
            db.add(exists)
            print(f"Updated: {p_data['name']}")
    
    db.commit()
    db.close()
    print("Policy Seeding Complete.")

if __name__ == "__main__":
    seed_policies()
