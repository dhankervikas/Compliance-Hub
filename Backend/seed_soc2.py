"""
Seed SOC 2 Trust Service Criteria (TSC) 2017
Focuses on Common Criteria (CC) which are mandatory for all SOC 2 audits
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Framework, Control

# SOC 2 Framework
SOC2_FRAMEWORK = {
    "name": "SOC 2 (2017)",
    "code": "SOC2",
    "description": "Trust Service Criteria for Security, Availability, and Confidentiality",
    "version": "2017"
}

# SOC 2 Common Criteria (CC) - Mandatory for all SOC 2 audits
SOC2_COMMON_CRITERIA = [
    # CC1: Control Environment
    {
        "control_id": "CC1.1",
        "title": "COSO Principle 1: Demonstrates Commitment to Integrity and Ethical Values",
        "description": "The entity demonstrates a commitment to integrity and ethical values.",
        "category": "Control Environment",
        "priority": "high"
    },
    {
        "control_id": "CC1.2",
        "title": "COSO Principle 2: Exercises Oversight Responsibility",
        "description": "The board of directors demonstrates independence from management and exercises oversight of the development and performance of internal control.",
        "category": "Control Environment",
        "priority": "high"
    },
    {
        "control_id": "CC1.3",
        "title": "COSO Principle 3: Establishes Structure, Authority, and Responsibility",
        "description": "Management establishes, with board oversight, structures, reporting lines, and appropriate authorities and responsibilities in the pursuit of objectives.",
        "category": "Control Environment",
        "priority": "high"
    },
    {
        "control_id": "CC1.4",
        "title": "COSO Principle 4: Demonstrates Commitment to Competence",
        "description": "The entity demonstrates a commitment to attract, develop, and retain competent individuals in alignment with objectives.",
        "category": "Control Environment",
        "priority": "high"
    },
    {
        "control_id": "CC1.5",
        "title": "COSO Principle 5: Enforces Accountability",
        "description": "The entity holds individuals accountable for their internal control responsibilities in the pursuit of objectives.",
        "category": "Control Environment",
        "priority": "high"
    },
    
    # CC2: Communication and Information
    {
        "control_id": "CC2.1",
        "title": "COSO Principle 13: Uses Relevant Information",
        "description": "The entity obtains or generates and uses relevant, quality information to support the functioning of internal control.",
        "category": "Communication and Information",
        "priority": "high"
    },
    {
        "control_id": "CC2.2",
        "title": "COSO Principle 14: Communicates Internally",
        "description": "The entity internally communicates information, including objectives and responsibilities for internal control, necessary to support the functioning of internal control.",
        "category": "Communication and Information",
        "priority": "high"
    },
    {
        "control_id": "CC2.3",
        "title": "COSO Principle 15: Communicates Externally",
        "description": "The entity communicates with external parties regarding matters affecting the functioning of internal control.",
        "category": "Communication and Information",
        "priority": "high"
    },
    
    # CC3: Risk Assessment
    {
        "control_id": "CC3.1",
        "title": "COSO Principle 6: Specifies Suitable Objectives",
        "description": "The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks relating to objectives.",
        "category": "Risk Assessment",
        "priority": "high"
    },
    {
        "control_id": "CC3.2",
        "title": "COSO Principle 7: Identifies and Analyzes Risk",
        "description": "The entity identifies risks to the achievement of its objectives across the entity and analyzes risks as a basis for determining how the risks should be managed.",
        "category": "Risk Assessment",
        "priority": "high"
    },
    {
        "control_id": "CC3.3",
        "title": "COSO Principle 8: Assesses Fraud Risk",
        "description": "The entity considers the potential for fraud in assessing risks to the achievement of objectives.",
        "category": "Risk Assessment",
        "priority": "high"
    },
    {
        "control_id": "CC3.4",
        "title": "COSO Principle 9: Identifies and Analyzes Significant Change",
        "description": "The entity identifies and assesses changes that could significantly impact the system of internal control.",
        "category": "Risk Assessment",
        "priority": "high"
    },
    
    # CC4: Monitoring Activities
    {
        "control_id": "CC4.1",
        "title": "COSO Principle 16: Conducts Ongoing and/or Separate Evaluations",
        "description": "The entity selects, develops, and performs ongoing and/or separate evaluations to ascertain whether the components of internal control are present and functioning.",
        "category": "Monitoring Activities",
        "priority": "high"
    },
    {
        "control_id": "CC4.2",
        "title": "COSO Principle 17: Evaluates and Communicates Deficiencies",
        "description": "The entity evaluates and communicates internal control deficiencies in a timely manner to those parties responsible for taking corrective action.",
        "category": "Monitoring Activities",
        "priority": "high"
    },
    
    # CC5: Control Activities
    {
        "control_id": "CC5.1",
        "title": "COSO Principle 10: Selects and Develops Control Activities",
        "description": "The entity selects and develops control activities that contribute to the mitigation of risks to the achievement of objectives to acceptable levels.",
        "category": "Control Activities",
        "priority": "high"
    },
    {
        "control_id": "CC5.2",
        "title": "COSO Principle 11: Selects and Develops General Controls over Technology",
        "description": "The entity selects and develops general control activities over technology to support the achievement of objectives.",
        "category": "Control Activities",
        "priority": "high"
    },
    {
        "control_id": "CC5.3",
        "title": "COSO Principle 12: Deploys Control Activities",
        "description": "The entity deploys control activities through policies that establish what is expected and procedures that put policies into action.",
        "category": "Control Activities",
        "priority": "high"
    },
    
    # CC6: Logical and Physical Access Controls
    {
        "control_id": "CC6.1",
        "title": "Logical and Physical Access Controls",
        "description": "The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.2",
        "title": "Authentication and Access",
        "description": "Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.3",
        "title": "Access Removal",
        "description": "The entity removes access to systems and data in a timely manner when access is no longer needed.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.4",
        "title": "Physical Access",
        "description": "The entity restricts physical access to facilities and protected information assets to authorized personnel.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.5",
        "title": "Access Monitoring",
        "description": "The entity monitors and reviews access to systems and data.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.6",
        "title": "Remote Access",
        "description": "The entity implements controls to protect against unauthorized access through remote connections.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.7",
        "title": "Privileged Access",
        "description": "The entity restricts the use of privileged access and elevated system access.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    {
        "control_id": "CC6.8",
        "title": "Data Classification",
        "description": "The entity identifies and classifies data based on criticality and sensitivity.",
        "category": "Logical and Physical Access",
        "priority": "high"
    },
    
    # CC7: System Operations
    {
        "control_id": "CC7.1",
        "title": "System Operations - Change Management",
        "description": "The entity uses a change management process to deploy changes to infrastructure and software.",
        "category": "System Operations",
        "priority": "high"
    },
    {
        "control_id": "CC7.2",
        "title": "System Monitoring",
        "description": "The entity monitors system components and the operation of those components for anomalies.",
        "category": "System Operations",
        "priority": "high"
    },
    {
        "control_id": "CC7.3",
        "title": "System Maintenance",
        "description": "The entity implements security patch management processes and system maintenance activities.",
        "category": "System Operations",
        "priority": "high"
    },
    {
        "control_id": "CC7.4",
        "title": "Data Backup and Recovery",
        "description": "The entity implements backup and recovery procedures for data and systems.",
        "category": "System Operations",
        "priority": "high"
    },
    {
        "control_id": "CC7.5",
        "title": "Malware Protection",
        "description": "The entity implements measures to prevent malicious software from affecting system operations.",
        "category": "System Operations",
        "priority": "high"
    },
    
    # CC8: Change Management
    {
        "control_id": "CC8.1",
        "title": "Change Management Process",
        "description": "The entity authorizes, designs, develops, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures.",
        "category": "Change Management",
        "priority": "high"
    },
    
    # CC9: Risk Mitigation
    {
        "control_id": "CC9.1",
        "title": "Vendor Management",
        "description": "The entity identifies, selects, and manages vendors and business partners with access to systems and data.",
        "category": "Risk Mitigation",
        "priority": "high"
    },
    {
        "control_id": "CC9.2",
        "title": "Incident Response",
        "description": "The entity identifies, reports, and responds to security incidents in a timely manner.",
        "category": "Risk Mitigation",
        "priority": "high"
    },
]

def seed_soc2():
    """Seed SOC 2 Common Criteria"""
    db: Session = SessionLocal()
    
    try:
        print("Starting SOC 2 seeding...")
        print("=" * 60)
        
        # Check if SOC 2 framework already exists
        existing = db.query(Framework).filter(Framework.code == "SOC2").first()
        if existing:
            print("✗ SOC 2 framework already exists!")
            print(f"  Framework ID: {existing.id}")
            return
        
        # Create SOC 2 framework
        framework = Framework(**SOC2_FRAMEWORK)
        db.add(framework)
        db.commit()
        db.refresh(framework)
        
        print(f"✓ Created framework: {framework.name}")
        print(f"  Framework ID: {framework.id}")
        print(f"  Code: {framework.code}")
        print("-" * 60)
        
        # Add controls
        controls_added = 0
        for control_data in SOC2_COMMON_CRITERIA:
            control = Control(
                framework_id=framework.id,
                **control_data
            )
            db.add(control)
            controls_added += 1
            
            if controls_added % 5 == 0:
                print(f"  Added {controls_added} controls...")
        
        db.commit()
        
        print("-" * 60)
        print(f"✓ Successfully added {controls_added} SOC 2 Common Criteria!")
        print("\nCategories added:")
        categories = {}
        for ctrl in SOC2_COMMON_CRITERIA:
            cat = ctrl['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"  - {cat}: {count} controls")
        
        print("\n" + "=" * 60)
        print("SOC 2 seeding complete!")
        print(f"Total controls in database: {db.query(Control).count()}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_soc2()