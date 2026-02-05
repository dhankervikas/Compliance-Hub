"""
Seed script to populate ALL SOC 2 Trust Services Criteria
Domains: Security (CC), Availability (A), Confidentiality (C), Processing Integrity (PI), Privacy (P)

Usage:
    python seed_soc2_full.py
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.framework import Framework
from app.models.control import Control, ControlStatus

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def create_framework(db: Session):
    existing = db.query(Framework).filter(Framework.code == "SOC2_2017").first()
    if existing:
        print(f"Framework already exists: {existing.name} (ID: {existing.id})")
        return existing
    
    framework = Framework(
        name="SOC 2 - Trust Services Criteria (2017)",
        code="SOC2_2017",
        description="AICPA Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy",
        version="2017"
    )
    db.add(framework)
    db.commit()
    db.refresh(framework)
    print(f"Created framework: {framework.name} (ID: {framework.id})")
    return framework

def create_controls(db: Session, framework_id: int):
    # This list allows us to add Non-CC controls easily
    controls_data = [
        # --- AVAILABILITY (A) ---
        {
            "control_id": "A1.1",
            "title": "Availability Capacity Management",
            "description": "The entity limits availability of information and systems to authorized people.",
            "category": "Availability",
            "priority": "medium"
        },
        {
            "control_id": "A1.2",
            "title": "Environmental Protections",
            "description": "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections, software, data back-up processes, and recovery infrastructure to meet its objectives.",
            "category": "Availability",
            "priority": "high"
        },
        {
            "control_id": "A1.3",
            "title": "Backups and Recovery",
            "description": "The entity tests recovery plan procedures to support the recovery of the system.",
            "category": "Availability",
            "priority": "high"
        },

        # --- CONFIDENTIALITY (C) ---
        {
            "control_id": "C1.1",
            "title": "Confidentiality of Information",
            "description": "The entity identifies and maintains confidential information to meet the entity's objectives related to confidentiality.",
            "category": "Confidentiality",
            "priority": "high"
        },
        {
            "control_id": "C1.2",
            "title": "Disposal of Confidential Information",
            "description": "The entity disposes of confidential information to meet the entity's objectives related to confidentiality.",
            "category": "Confidentiality",
            "priority": "high"
        },

        # --- PROCESSING INTEGRITY (PI) ---
        {
            "control_id": "PI1.1",
            "title": "Processing Integrity",
            "description": "The entity obtains or generates, uses, and communicates relevant, quality information regarding the objectives related to processing, including definitions of data processed and product and service specifications, to support the use of relevant, quality information.",
            "category": "Processing Integrity",
            "priority": "medium"
        },
        {
            "control_id": "PI1.2",
            "title": "Completeness, Accuracy, Timeliness",
            "description": "The entity implements policies and procedures over system inputs, including controls over completeness and accuracy, to result in products, services, and reporting to meet the entity’s objectives.",
            "category": "Processing Integrity",
            "priority": "medium"
        },

        # --- PRIVACY (P) ---
        {
            "control_id": "P1.0",
            "title": "Notice and Communication of Objectives",
            "description": "The entity provides notice to privacy principals about its privacy practices to meet the entity’s objectives related to privacy. The entity communicates its objectives related to privacy to authorized people.",
            "category": "Privacy",
            "priority": "high"
        },
        {
            "control_id": "P2.0",
            "title": "Choice and Consent",
            "description": "The entity communicates choices available regarding the collection, use, retention, disclosure, and disposal of personal information to the privacy principals. The entity obtains the consent of privacy principals.",
            "category": "Privacy",
            "priority": "high"
        },
        {
            "control_id": "P3.0",
            "title": "Collection",
            "description": "The entity collects personal information to meet its objectives related to privacy.",
            "category": "Privacy",
            "priority": "medium"
        },
        {
            "control_id": "P4.0",
            "title": "Use, Retention, and Disposal",
            "description": "The entity limits the use, retention, and disposal of personal information to meet its objectives related to privacy.",
            "category": "Privacy",
            "priority": "high"
        },
        {
            "control_id": "P5.0",
            "title": "Access",
            "description": "The entity provides privacy principals with access to their personal information for review and correction to meet its objectives related to privacy.",
            "category": "Privacy",
            "priority": "medium"
        },
        {
            "control_id": "P6.0",
            "title": "Disclosure and Notification",
            "description": "The entity discloses personal information to third parties with the explicit consent of privacy principals. The entity notifies privacy principals of breaches.",
            "category": "Privacy",
            "priority": "high"
        },
        {
            "control_id": "P7.0",
            "title": "Quality",
            "description": "The entity collects and maintains accurate, up-to-date, complete, and relevant personal information to meet its objectives related to privacy.",
            "category": "Privacy",
            "priority": "medium"
        },
        {
            "control_id": "P8.0",
            "title": "Monitoring and Enforcement",
            "description": "The entity monitors compliance to meet its objectives related to privacy, including procedures to address privacy related inquiries, complaints, and disputes.",
            "category": "Privacy",
            "priority": "high"
        }
    ]

    count = 0
    skipped = 0
    for data in controls_data:
        existing = db.query(Control).filter(
            Control.control_id == data["control_id"], 
            Control.framework_id == framework_id
        ).first()
        
        if existing:
            print(f"Skipping existing: {data['control_id']}")
            skipped += 1
            continue
            
        control = Control(
            framework_id=framework_id,
            status=ControlStatus.NOT_STARTED,
            **data
        )
        db.add(control)
        count += 1
        print(f"Created: {data['control_id']}")

    db.commit()
    print(f"Finished. Created {count}, Skipped {skipped}.")

def main():
    db = get_db()
    try:
        print("Seeding SOC 2 (Full Scope)...")
        framework = create_framework(db)
        create_controls(db, framework.id)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
