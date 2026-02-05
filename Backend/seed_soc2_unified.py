"""
Unified SOC 2 (2017 TSC) Seed Script
====================================
1. Creates 'SOC 2 - Trust Services Criteria (2017)' Framework.
2. Seeds controls for all 5 Trust Principles:
   - Security (CC) - Mandated Common Criteria
   - Availability (A)
   - Confidentiality (C)
   - Processing Integrity (PI)
   - Privacy (P)
3. Performs Intelligent Cross-Mapping to ISO 27001 controls using shared Policy Intents.
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.framework import Framework
from app.models.control import Control, ControlStatus
from app.models.control_mapping import ControlMapping
from app.services.policy_intents import POLICY_CONTROL_MAP

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------
# FRAMEWORK DEFINITION
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# FRAMEWORK DEFINITION
# ------------------------------------------------------------------
FRAMEWORK_DATA = {
    "name": "SOC 2 Type II",
    "code": "SOC2",  # TARGETING EXISTING ID 2
    "description": "AICPA Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy",
    "version": "2017"
}

# ------------------------------------------------------------------
# CONTROL DATA (Combined CC + A/C/PI/P)
# ------------------------------------------------------------------
CONTROLS_DATA = [
    # --- SECURITY (COMMON CRITERIA) ---
    {"control_id": "CC1.1", "title": "CC1.1 - Integrity & Ethics", "description": "The entity demonstrates a commitment to integrity and ethical values.", "category": "Security", "priority": "high"},
    {"control_id": "CC1.2", "title": "CC1.2 - Board Oversight", "description": "The board demonstrates independence and exercises oversight of internal control.", "category": "Security", "priority": "high"},
    {"control_id": "CC1.3", "title": "CC1.3 - Structure & Authority", "description": "Management establishes structures, reporting lines, and authorities.", "category": "Security", "priority": "high"},
    {"control_id": "CC1.4", "title": "CC1.4 - Competence", "description": "The entity demonstrates a commitment to attract, develop, and retain competent individuals.", "category": "Security", "priority": "high"},
    {"control_id": "CC1.5", "title": "CC1.5 - Accountability", "description": "The entity holds individuals accountable for internal control responsibilities.", "category": "Security", "priority": "high"},

    {"control_id": "CC2.1", "title": "CC2.1 - Quality Information", "description": "The entity uses relevant, quality information to support internal control.", "category": "Security", "priority": "high"},
    {"control_id": "CC2.2", "title": "CC2.2 - Internal Communication", "description": "The entity communicates information internally (objectives/responsibilities).", "category": "Security", "priority": "high"},
    {"control_id": "CC2.3", "title": "CC2.3 - External Communication", "description": "The entity communicates with external parties regarding internal control matters.", "category": "Security", "priority": "high"},

    {"control_id": "CC3.1", "title": "CC3.1 - Specific Objectives", "description": "The entity specifies objectives with clarity to enable risk identification.", "category": "Security", "priority": "high"},
    {"control_id": "CC3.2", "title": "CC3.2 - Risk Identification", "description": "The entity identifies and analyzes risks to the achievement of objectives.", "category": "Security", "priority": "high"},
    {"control_id": "CC3.3", "title": "CC3.3 - Fraud Risk", "description": "The entity considers the potential for fraud in assessing risks.", "category": "Security", "priority": "high"},
    {"control_id": "CC3.4", "title": "CC3.4 - Change Management (Risk)", "description": "The entity assesses changes that could impact the system of internal control.", "category": "Security", "priority": "high"},

    {"control_id": "CC4.1", "title": "CC4.1 - Ongoing Evaluations", "description": "The entity performs ongoing evaluations of internal control (Monitoring).", "category": "Security", "priority": "high"},
    {"control_id": "CC4.2", "title": "CC4.2 - Deficiency Reporting", "description": "The entity communicates deficiencies timely to those responsible.", "category": "Security", "priority": "high"},

    {"control_id": "CC5.1", "title": "CC5.1 - Risk Mitigation", "description": "The entity selects control activities that mitigate risks to acceptable levels.", "category": "Security", "priority": "high"},
    {"control_id": "CC5.2", "title": "CC5.2 - Tech Controls", "description": "The entity selects general control activities over technology.", "category": "Security", "priority": "high"},
    {"control_id": "CC5.3", "title": "CC5.3 - Policies", "description": "The entity deploys control activities through policies and procedures.", "category": "Security", "priority": "high"},

    {"control_id": "CC6.1", "title": "CC6.1 - Logical Access", "description": "The entity implements logical access security software, infrastructure, and architectures.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.2", "title": "CC6.2 - User Registration", "description": "Prior to issuing system credentials, the entity registers and authorizes new users.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.3", "title": "CC6.3 - Access Modifications", "description": "The entity authorizes and modifies access to protected information assets.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.4", "title": "CC6.4 - Physical Access", "description": "The entity restricts physical access to facilities and protected information assets.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.5", "title": "CC6.5 - Disposal of Credentials", "description": "The entity discontinues logical and physical access when no longer needed.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.6", "title": "CC6.6 - External Access", "description": "The entity implements controls to protect against unauthorized external access.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.7", "title": "CC6.7 - Transmission Security", "description": "The entity restricts the transmission of protected information over networks.", "category": "Security", "priority": "high"},
    {"control_id": "CC6.8", "title": "CC6.8 - Malware Protection", "description": "The entity implements controls to prevent, detect, and act upon malicious software.", "category": "Security", "priority": "high"},

    {"control_id": "CC7.1", "title": "CC7.1 - Configuration Monitoring", "description": "The entity monitors system configuration for compliance with baselines.", "category": "Security", "priority": "high"},
    {"control_id": "CC7.2", "title": "CC7.2 - Vulnerability Management", "description": "The entity monitors for vulnerabilities and remediates them.", "category": "Security", "priority": "high"},
    {"control_id": "CC7.3", "title": "CC7.3 - Incident Detection", "description": "The entity evaluates security events to determine if they are incidents.", "category": "Security", "priority": "high"},
    {"control_id": "CC7.4", "title": "CC7.4 - Incident Response", "description": "The entity responds to identified security incidents.", "category": "Security", "priority": "high"},
    {"control_id": "CC7.5", "title": "CC7.5 - Disaster Recovery", "description": "The entity implements distinct procedures to restore operations after a disruption.", "category": "Security", "priority": "high"},

    {"control_id": "CC8.1", "title": "CC8.1 - Change Management", "description": "The entity authorizes, designs, develops, tests, approves, and implements changes.", "category": "Security", "priority": "high"},

    {"control_id": "CC9.1", "title": "CC9.1 - Vendor Management", "description": "The entity identifies, selects, and manages risks associated with vendors.", "category": "Security", "priority": "high"},
    {"control_id": "CC9.2", "title": "CC9.2 - Insider Threat", "description": "The entity assesses and manages risks associated with vendors and business partners.", "category": "Security", "priority": "high"},

    # --- AVAILABILITY (A) ---
    {"control_id": "A1.1", "title": "A1.1 - Capacity Management", "description": "The entity maintains, monitors, and evaluates current processing capacity.", "category": "Availability", "priority": "medium"},
    {"control_id": "A1.2", "title": "A1.2 - Environmental Controls", "description": "The entity authorizes, designs, develops, implements, operates, approves, and monitors environmental protections.", "category": "Availability", "priority": "high"},
    {"control_id": "A1.3", "title": "A1.3 - Data Backup & Recovery", "description": "The entity tests recovery plan procedures to support the recovery of the system.", "category": "Availability", "priority": "high"},

    # --- CONFIDENTIALITY (C) ---
    {"control_id": "C1.1", "title": "C1.1 - Confidentiality", "description": "The entity identifies and maintains confidential information to meet objectives.", "category": "Confidentiality", "priority": "high"},
    {"control_id": "C1.2", "title": "C1.2 - Disposal", "description": "The entity disposes of confidential information to meet objectives.", "category": "Confidentiality", "priority": "high"},

    # --- PROCESSING INTEGRITY (PI) ---
    {"control_id": "PI1.1", "title": "PI1.1 - Processing Objective", "description": "The entity obtains or generates, uses, and communicates relevant quality information regarding processing.", "category": "Processing Integrity", "priority": "medium"},
    {"control_id": "PI1.2", "title": "PI1.2 - System Inputs", "description": "The entity implements policies and procedures over system inputs (completeness/accuracy).", "category": "Processing Integrity", "priority": "medium"},
    {"control_id": "PI1.3", "title": "PI1.3 - Data Processing", "description": "The entity implements policies and procedures over system processing to meet objectives.", "category": "Processing Integrity", "priority": "medium"},
    {"control_id": "PI1.4", "title": "PI1.4 - Data Storage", "description": "The entity implements policies and procedures to direct data storage and maintenance.", "category": "Processing Integrity", "priority": "medium"},
    {"control_id": "PI1.5", "title": "PI1.5 - System Outputs", "description": "The entity implements policies and procedures over system outputs.", "category": "Processing Integrity", "priority": "medium"},

    # --- PRIVACY (P) [EXPANDED] ---
    {"control_id": "P1.1", "title": "P1.1 - Privacy Notice", "description": "The entity provides notice to privacy principals about its privacy practices.", "category": "Privacy", "priority": "high"},
    {"control_id": "P1.2", "title": "P1.2 - Methods of Notice", "description": "The entity communicates changes to its privacy practices to privacy principals.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P2.1", "title": "P2.1 - Choice and Consent", "description": "The entity communicates choices regarding personal information and obtains consent.", "category": "Privacy", "priority": "high"},
    {"control_id": "P2.2", "title": "P2.2 - Withdrawal of Consent", "description": "The entity allows privacy principals to withdraw their consent.", "category": "Privacy", "priority": "high"},
    {"control_id": "P3.1", "title": "P3.1 - Collection", "description": "The entity collects personal information only as necessary to meet objectives.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P3.2", "title": "P3.2 - Sources of Data", "description": "The entity collects data from reliable sources.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P3.3", "title": "P3.3 - Sensitive Info", "description": "The entity collects sensitive personal information only when necessary.", "category": "Privacy", "priority": "high"},
    {"control_id": "P4.1", "title": "P4.1 - Use of Information", "description": "The entity uses personal information only for the specific purposes for which it was collected.", "category": "Privacy", "priority": "high"},
    {"control_id": "P4.2", "title": "P4.2 - Retention", "description": "The entity retains personal information only as long as necessary.", "category": "Privacy", "priority": "high"},
    {"control_id": "P4.3", "title": "P4.3 - Disposal", "description": "The entity securely disposes of personal information when no longer needed.", "category": "Privacy", "priority": "high"},
    {"control_id": "P5.1", "title": "P5.1 - Access", "description": "The entity provides individuals with access to their personal information for review/correction.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P5.2", "title": "P5.2 - Denial of Access", "description": "The entity communicates reasons for denial of access requests.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P6.1", "title": "P6.1 - Disclosure to 3rd Parties", "description": "The entity discloses information only to authorized third parties.", "category": "Privacy", "priority": "high"},
    {"control_id": "P6.2", "title": "P6.2 - 3rd Party Compliance", "description": "The entity ensures third parties protect personal information.", "category": "Privacy", "priority": "high"},
    {"control_id": "P6.3", "title": "P6.3 - Data Breaches", "description": "The entity notifies affected parties of unauthorized disclosure (breaches).", "category": "Privacy", "priority": "high"},
    {"control_id": "P6.4", "title": "P6.4 - Disclosure Records", "description": "The entity maintains a record of disclosures of personal information.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P7.1", "title": "P7.1 - Quality", "description": "The entity maintains accurate, complete, and relevant personal information.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P8.1", "title": "P8.1 - Monitoring", "description": "The entity monitors compliance with privacy policies.", "category": "Privacy", "priority": "high"},
    {"control_id": "P8.2", "title": "P8.2 - Inquiries & Complaints", "description": "The entity addresses inquiries, complaints, and disputes regarding privacy.", "category": "Privacy", "priority": "medium"},
    {"control_id": "P8.3", "title": "P8.3 - Enforcement", "description": "The entity enforces privacy policies and procedures.", "category": "Privacy", "priority": "high"},
]

def map_controls_by_policy(db: Session, soc2_fw_id: int):
    """
    Intelligent Cross-Mapping:
    Uses the POLICY_CONTROL_MAP to find which ISO controls appear alongside SOC 2 controls.
    Creates a 'ControlMapping' record for each relationship.
    """
    print("\\n[Mapping Logic] Analyzing Policy Intents for Cross-Mapping...")
    
    # Pre-fetch all controls for fast lookup
    all_controls = db.query(Control).all()
    control_map = {c.control_id: c for c in all_controls}
    
    mappings_created = 0
    
    # Iterate through each Policy's defined controls
    for policy, matched_controls in POLICY_CONTROL_MAP.items():
        # Separate ISO and SOC2 controls listed for this policy
        iso_ids = [cid for cid in matched_controls if cid.startswith("A.") or cid.startswith("ISO")]
        soc2_ids = [cid for cid in matched_controls if cid.startswith("CC") or cid.startswith("A") or cid.startswith("P") or cid.startswith("C")]
        
        # Valid SOC2 IDs in our current seed (e.g. A1.1 might clash with ISO A.5, but our ISO is A.5.x)
        soc2_ids = [cid for cid in soc2_ids if not cid.startswith("A.") and not cid.startswith("ISO")]

        if not iso_ids or not soc2_ids:
            continue
            
        # Create Many-to-Many mappings for this Cluster
        for iso_id in iso_ids:
            for soc2_id in soc2_ids:
                if iso_id in control_map and soc2_id in control_map:
                    iso_ctrl = control_map[iso_id]
                    soc2_ctrl = control_map[soc2_id]
                    
                    # Check if items belong to distinct frameworks (Sanity check)
                    if iso_ctrl.framework_id == soc2_ctrl.framework_id:
                        continue 
                        
                    # Check if mapping already exists
                    existing = db.query(ControlMapping).filter(
                        ControlMapping.source_control_id == iso_ctrl.id,
                        ControlMapping.target_control_id == soc2_ctrl.id
                    ).first()
                    
                    if not existing:
                        mapping = ControlMapping(
                            source_control_id=iso_ctrl.id,
                            target_control_id=soc2_ctrl.id,
                            mapping_type="intent_based",
                            notes=f"Linked via {policy}"
                        )
                        db.add(mapping)
                        mappings_created += 1
                        print(f"  + Mapped {iso_id} <-> {soc2_id} (via {policy})")
    
    db.commit()
    print(f"\\n[Mapping Logic] Created {mappings_created} new intent-based mappings.")


def seed_soc2_unified():
    db = SessionLocal()
    try:
        print("Starting Unified SOC 2 Seeding...")
        
        # 0. Cleanup Old Mess (if any)
        dup_fw = db.query(Framework).filter(Framework.code == "SOC2_2017").first()
        if dup_fw:
            print(f"Cleaning up duplicate framework: {dup_fw.name}")
            db.query(ControlMapping).filter((ControlMapping.source_control_id.in_(db.query(Control.id).filter(Control.framework_id == dup_fw.id))) | (ControlMapping.target_control_id.in_(db.query(Control.id).filter(Control.framework_id == dup_fw.id)))).delete(synchronize_session=False)
            db.query(Control).filter(Control.framework_id == dup_fw.id).delete()
            db.delete(dup_fw)
            db.commit()

        # 1. Create/Get Framework
        framework = db.query(Framework).filter(Framework.code == FRAMEWORK_DATA["code"]).first()
        if not framework:
            framework = Framework(**FRAMEWORK_DATA)
            db.add(framework)
            db.commit()
            db.refresh(framework)
            print(f"[OK] Created Framework: {framework.name}")
        else:
            print(f"[OK] Targeting existing Framework: {framework.name} (ID: {framework.id})")
            # Force cleanup of old 'legacy' controls so we have a clean slate of 64 correct ones
            print("  - Clearing existing controls to ensure clean state...")
            db.query(ControlMapping).filter((ControlMapping.source_control_id.in_(db.query(Control.id).filter(Control.framework_id == framework.id))) | (ControlMapping.target_control_id.in_(db.query(Control.id).filter(Control.framework_id == framework.id)))).delete(synchronize_session=False)
            db.query(Control).filter(Control.framework_id == framework.id).delete()
            db.commit()
            
        # 2. Seed Controls
        count = 0 
        for data in CONTROLS_DATA:
            existing = db.query(Control).filter(
                Control.control_id == data["control_id"],
                Control.framework_id == framework.id
            ).first()
            
            if not existing:
                control = Control(
                    framework_id=framework.id,
                    status=ControlStatus.NOT_STARTED,
                    **data
                )
                db.add(control)
                count += 1
            else:
                # Update category if needed (for older seeds)
                if existing.category != data["category"]:
                    existing.category = data["category"]
                    db.add(existing)

        # 2.5 Inject LINK_ID based on Policy Intents (For Evidence Sync)
        print("  - Injecting LINK_ID tags for Evidence Sync...")
        # Reverse map: Control ID -> Policy Name
        control_policy_map = {}
        for policy_name, controls in POLICY_CONTROL_MAP.items():
            normalized_key = policy_name.upper().replace(" ", "_").replace("&", "AND").replace("-", "_")
            for cid in controls:
                # We only take the first/primary policy for now to simplify testing
                if cid not in control_policy_map:
                    control_policy_map[cid] = normalized_key

        # Apply to DB controls
        controls_to_update = db.query(Control).filter(Control.framework_id == framework.id).all()
        link_count = 0
        for c in controls_to_update:
            if c.control_id in control_policy_map:
                link_key = control_policy_map[c.control_id]
                note = f"LINK_ID: {link_key}"
                
                # Update notes without overwriting existing unrelated notes
                if c.implementation_notes:
                    if "LINK_ID:" not in c.implementation_notes:
                        c.implementation_notes += f" | {note}"
                    # If it has one, leave it (or update? assumed clean seed)
                else:
                    c.implementation_notes = note
                
                db.add(c)
                link_count += 1
        
        print(f"  - Injected LINK_ID tags into {link_count} controls.")

        db.commit()
        print(f"[OK] Seeded/Updated {count} SOC 2 controls.")
        
        # 3. Intelligent Mapping
        map_controls_by_policy(db, framework.id)
        
        print("SOC 2 Unified Seeding Complete.")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_soc2_unified()
