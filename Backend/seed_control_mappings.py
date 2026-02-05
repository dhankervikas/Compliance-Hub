"""
Seed control mappings between ISO 27001 and SOC 2
This allows one control implementation to satisfy multiple frameworks
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Control
from add_control_mappings import ControlMapping

# ISO 27001 → SOC 2 Mappings
# Format: {ISO_control_id: [SOC2_control_ids]}
CONTROL_MAPPINGS = {
    # ISMS Clauses → SOC 2 Common Criteria
    "4.1": ["CC3.1"],  # Context → Objectives
    "4.2": ["CC3.1"],  # Interested parties → Objectives
    "4.3": ["CC3.1"],  # Scope → Objectives
    "5.1": ["CC1.1", "CC1.2"],  # Leadership → Control Environment
    "5.2": ["CC1.1", "CC2.2"],  # Policy → Control Environment & Communication
    "5.3": ["CC1.3", "CC1.5"],  # Roles & Responsibilities → Structure & Accountability
    "6.1.1": ["CC3.1"],  # General risk → Objectives
    "6.1.2": ["CC3.2"],  # Risk assessment → Identifies and Analyzes Risk
    "6.1.3": ["CC3.2"],  # Risk treatment → Risk Management
    "7.2": ["CC1.4"],  # Competence → Commitment to Competence
    "7.3": ["CC1.4"],  # Awareness → Competence
    "7.4": ["CC2.2", "CC2.3"],  # Communication → Internal & External Communication
    "7.5.1": ["CC2.1"],  # Documented information → Uses Relevant Information
    "8.2": ["CC3.2"],  # Risk assessment (operation) → Risk Assessment
    "9.1": ["CC4.1"],  # Monitoring → Ongoing Evaluations
    "9.2": ["CC4.1"],  # Internal audit → Evaluations
    "9.3": ["CC4.1", "CC4.2"],  # Management review → Evaluations & Communication
    "10.1": ["CC4.2"],  # Continual improvement → Communicates Deficiencies
    "10.2": ["CC4.2", "CC9.2"],  # Nonconformity → Deficiencies & Incident Response
    
    # Annex A Controls → SOC 2
    "A.5.1": ["CC1.1", "CC2.2"],  # Policies → Control Environment & Communication
    "A.5.2": ["CC1.3", "CC1.5"],  # Roles & Responsibilities → Structure & Accountability
    "A.5.3": ["CC1.3"],  # Segregation of duties → Structure
    "A.5.7": ["CC9.2"],  # Threat intelligence → Incident Response
    "A.5.8": ["CC5.1"],  # Information security in project management → Control Activities
    "A.5.10": ["CC6.8"],  # Acceptable use → Data Classification
    "A.5.14": ["CC6.8"],  # Information transfer → Data Protection
    "A.5.15": ["CC6.1"],  # Access control → Logical Access
    "A.5.16": ["CC6.7"],  # Identity management → Access Management
    "A.5.17": ["CC2.1"],  # Authentication information → Information Security
    "A.5.18": ["CC6.2", "CC6.3"],  # Access rights → Access Management
    "A.5.23": ["CC6.8"],  # Information security for cloud services → Data Classification
    "A.5.24": ["CC9.2"],  # Incident management → Incident Response
    "A.5.25": ["CC9.2"],  # Assessment of information security events → Incident Response
    "A.5.26": ["CC9.2"],  # Response to information security incidents → Incident Response
    "A.5.28": ["CC6.8"],  # Collection of evidence → Data Management
    "A.5.30": ["CC7.4"],  # ICT readiness for business continuity → Backup & Recovery
    
    "A.6.1": ["CC1.4"],  # Screening → Competence
    "A.6.2": ["CC1.4"],  # Terms and conditions of employment → Competence
    "A.6.3": ["CC1.4"],  # Information security awareness → Awareness
    "A.6.4": ["CC1.5"],  # Disciplinary process → Accountability
    "A.6.5": ["CC1.5"],  # Responsibilities after termination → Accountability
    "A.6.6": ["CC6.8"],  # Confidentiality agreements → Data Protection
    "A.6.7": ["CC6.6"],  # Remote working → Remote Access
    "A.6.8": ["CC9.2"],  # Information security event reporting → Incident Response
    
    "A.7.1": ["CC6.4"],  # Physical security perimeters → Physical Access
    "A.7.2": ["CC6.4"],  # Physical entry → Physical Access
    "A.7.3": ["CC6.4"],  # Securing offices → Physical Access
    "A.7.4": ["CC7.2"],  # Physical security monitoring → System Monitoring
    "A.7.7": ["CC6.4"],  # Clear desk and clear screen → Physical Security
    "A.7.8": ["CC6.4"],  # Equipment siting and protection → Physical Protection
    "A.7.9": ["CC6.4"],  # Security of assets off-premises → Asset Protection
    "A.7.10": ["CC7.3"],  # Storage media → System Maintenance
    "A.7.11": ["CC5.2"],  # Supporting utilities → Technology Controls
    "A.7.12": ["CC5.2"],  # Cabling security → Infrastructure Security
    "A.7.13": ["CC7.3"],  # Equipment maintenance → System Maintenance
    "A.7.14": ["CC7.3"],  # Secure disposal → Data Destruction
    
    "A.8.1": ["CC6.1", "CC6.8"],  # User endpoint devices → Logical Access & Classification
    "A.8.2": ["CC6.7"],  # Privileged access rights → Privileged Access
    "A.8.3": ["CC6.3"],  # Information access restriction → Access Control
    "A.8.4": ["CC6.1"],  # Access to source code → Code Access
    "A.8.5": ["CC6.2"],  # Secure authentication → Authentication
    "A.8.6": ["CC5.2"],  # Capacity management → Technology Management
    "A.8.7": ["CC7.5"],  # Protection against malware → Malware Protection
    "A.8.8": ["CC5.2"],  # Management of technical vulnerabilities → Vulnerability Management
    "A.8.9": ["CC5.2"],  # Configuration management → System Configuration
    "A.8.10": ["CC6.8"],  # Information deletion → Data Deletion
    "A.8.11": ["CC6.8"],  # Data masking → Data Protection
    "A.8.12": ["CC6.8"],  # Data leakage prevention → Data Loss Prevention
    "A.8.13": ["CC7.4"],  # Information backup → Backup & Recovery
    "A.8.14": ["CC5.2"],  # Redundancy of information processing facilities → High Availability
    "A.8.15": ["CC7.2"],  # Logging → Monitoring
    "A.8.16": ["CC7.2"],  # Monitoring activities → System Monitoring
    "A.8.17": ["CC7.2"],  # Clock synchronization → Time Synchronization
    "A.8.18": ["CC6.7"],  # Use of privileged utility programs → Privileged Access
    "A.8.19": ["CC7.1", "CC8.1"],  # Installation of software → Change Management
    "A.8.20": ["CC5.2"],  # Networks security → Network Security
    "A.8.21": ["CC5.2"],  # Security of network services → Network Services
    "A.8.22": ["CC5.2"],  # Segregation of networks → Network Segmentation
    "A.8.23": ["CC5.2"],  # Web filtering → Web Security
    "A.8.24": ["CC6.1"],  # Use of cryptography → Encryption
    "A.8.25": ["CC7.1"],  # Secure development life cycle → SDLC
    "A.8.26": ["CC7.1"],  # Application security requirements → Security Requirements
    "A.8.27": ["CC5.2"],  # Secure system architecture → Architecture
    "A.8.28": ["CC7.1"],  # Secure coding → Code Security
    "A.8.29": ["CC7.1"],  # Security testing in development → Security Testing
    "A.8.30": ["CC7.1"],  # Outsourced development → Third-party Development
    "A.8.31": ["CC7.1"],  # Separation of development, test and production → Environment Separation
    "A.8.32": ["CC7.1", "CC8.1"],  # Change management → Change Management
    "A.8.33": ["CC7.1"],  # Test information → Test Data
    "A.8.34": ["CC7.2"],  # Protection of information systems during audit testing → Audit Protection
}

def seed_mappings():
    """Create mappings between ISO 27001 and SOC 2 controls"""
    db: Session = SessionLocal()
    
    try:
        print("Starting control mappings seed...")
        print("=" * 60)
        
        # Get all controls
        all_controls = db.query(Control).all()
        control_lookup = {c.control_id: c.id for c in all_controls}
        
        mappings_created = 0
        mappings_skipped = 0
        
        for iso_control_id, soc2_control_ids in CONTROL_MAPPINGS.items():
            # Find ISO control
            if iso_control_id not in control_lookup:
                print(f"✗ ISO control {iso_control_id} not found")
                continue
            
            iso_db_id = control_lookup[iso_control_id]
            
            for soc2_control_id in soc2_control_ids:
                # Find SOC 2 control
                if soc2_control_id not in control_lookup:
                    print(f"✗ SOC 2 control {soc2_control_id} not found")
                    continue
                
                soc2_db_id = control_lookup[soc2_control_id]
                
                # Check if mapping already exists
                existing = db.query(ControlMapping).filter(
                    ControlMapping.source_control_id == iso_db_id,
                    ControlMapping.target_control_id == soc2_db_id
                ).first()
                
                if existing:
                    mappings_skipped += 1
                    continue
                
                # Create mapping (bidirectional)
                # ISO → SOC2
                mapping1 = ControlMapping(
                    source_control_id=iso_db_id,
                    target_control_id=soc2_db_id,
                    mapping_type="equivalent",
                    notes=f"{iso_control_id} satisfies {soc2_control_id}"
                )
                db.add(mapping1)
                
                # SOC2 → ISO (reverse mapping)
                mapping2 = ControlMapping(
                    source_control_id=soc2_db_id,
                    target_control_id=iso_db_id,
                    mapping_type="equivalent",
                    notes=f"{soc2_control_id} satisfied by {iso_control_id}"
                )
                db.add(mapping2)
                
                mappings_created += 2
                
                if mappings_created % 20 == 0:
                    print(f"  Created {mappings_created // 2} bidirectional mappings...")
        
        db.commit()
        
        print("-" * 60)
        print(f"✓ Successfully created {mappings_created // 2} control mappings!")
        print(f"  (Total mapping records: {mappings_created} - bidirectional)")
        if mappings_skipped > 0:
            print(f"  Skipped {mappings_skipped} existing mappings")
        
        print("\nBenefits:")
        print("- Implement one ISO 27001 control → automatically counts for SOC 2")
        print("- Avoid duplicate compliance work")
        print("- See cross-framework coverage instantly")
        
        print("\n" + "=" * 60)
        print("Control mappings seeding complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_mappings()