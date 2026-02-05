"""
Seed NIST CSF 2.0 Framework and Intent-Based Mappings
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Framework, Control, ControlMapping
from data.nist_csf_2_0 import NIST_CSF_DATA

# --- INTENT-BASED MAPPING DICTIONARY ---
# Format: "NIST_CODE": ["ISO_CODE", "SOC2_CODE"]
# Logic: These mappings represent shared compliance INTENT.
# Example: NIST GV.OC-01 (Mission) == ISO 4.1 (Context)
NIST_INTENT_MAP = {
    # GOVERN
    "GV.OC-01": ["4.1"],         # Organizational Context -> Context of Org
    "GV.OC-02": ["4.2"],         # External Dependencies -> Interested Parties
    "GV.OC-03": ["4.2", "4.3"],  # Legal Req -> Scope & Interested Parties
    "GV.RM-01": ["6.1.1"],       # Risk Strategy -> General Risk
    "GV.RM-02": ["5.1", "6.1.1"],# Risk Tolerance -> Leadership & Risk

    # IDENTIFY
    "ID.AM-01": ["A.8.1", "A.5.9"], # Hardware -> User Endpoints & Inventory
    "ID.AM-02": ["A.5.9", "A.5.10"],# Software -> Inventory & Acceptable Use
    "ID.AM-05": ["A.5.12"],         # Prioritization -> Classification
    "ID.RA-01": ["A.8.8", "6.1.2"], # Vuln ID -> Tech Vuln Mgmt & Risk Assessment
    "ID.RA-02": ["A.5.7"],          # Threat Intel -> Threat Intelligence
    "ID.RA-03": ["6.1.2"],          # Risk Determination -> Risk Assessment

    # PROTECT
    "PR.AA-01": ["A.5.16"],         # Identity -> Identity Mgmt
    "PR.AA-02": ["A.5.15", "A.9.1"],# Access -> Access Control
    "PR.AA-03": ["A.6.7"],          # Remote Access -> Remote Working
    "PR.DS-01": ["A.8.24", "CC6.1"],# Data At Rest -> Encryption
    "PR.DS-02": ["A.5.14", "CC6.7"],# Data In Transit -> Info Transfer

    # DETECT
    "DE.CM-01": ["A.8.16"],         # Network Monitoring -> Monitoring Activities
    "DE.CM-02": ["A.7.4"],          # Physical Monitoring -> Physical Monitoring
    "DE.AE-01": ["A.8.15", "A.8.16"], # Baseline/Event -> Logging & Monitoring

    # RESPOND
    "RS.MA-01": ["A.5.24", "CC7.3"],# Incident Plan -> Incident Mgmt
    "RS.MA-02": ["A.6.8"],          # Reporting -> Reporting Events

    # RECOVER
    "RC.RP-01": ["A.5.29", "A.5.30"] # Recovery -> Business Continuity
}

def seed_nist():
    db: Session = SessionLocal()
    try:
        print("SEEDING NIST CSF 2.0...")
        
        # 1. Create Framework
        fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
        if not fw:
            fw = Framework(
                name="NIST CSF 2.0",
                code="NIST_CSF_2.0",
                description="National Institute of Standards and Technology Cybersecurity Framework 2.0",
                version="2.0"
            )
            db.add(fw)
            db.commit()
            db.refresh(fw)
            print(" - Created Framework: NIST CSF 2.0")
        else:
            print(" - Framework NIST CSF 2.0 already exists")

        # 1.5 CLEAR EXISTING CONTROLS (To prevent duplicates/orphans)
        # This ensures exactly 134 items (State Enforcement)
        existing_count = db.query(Control).filter(Control.framework_id == fw.id).delete()
        db.commit()
        print(f" - Cleared {existing_count} existing controls to ensure clean state.")

        # 2. Create Controls (Functions + Categories + Subcategories)
        count = 0
        for func in NIST_CSF_DATA:
            # A. Insert FUNCTION as a Control (e.g. "GV")
            f_code = func.get("function_code", func["function"][:2])
            
            # Use Title as Description if Desc is empty (Fixes UI Blankness)
            f_desc = func.get("description", "")
            if not f_desc: f_desc = func["function"]

            f_ctrl = Control(
                control_id=f_code,
                title=func["function"],
                description=f_desc,
                framework_id=fw.id,
                category="Function", 
                domain=func["function"],
                is_applicable=True,
                priority="high"
            )
            db.add(f_ctrl)
            count += 1

            for cat in func["categories"]:
                # B. Insert CATEGORY as a Control (e.g. "GV.OC")
                c_code = cat["code"]
                
                # Fix Blank Controls: Use Title if Description is missing
                c_desc = "" # Data often has no desc
                if not c_desc: c_desc = cat["category"]

                c_ctrl = Control(
                    control_id=c_code,
                    title=cat["category"],
                    description=c_desc,
                    framework_id=fw.id,
                    category=cat["category"],
                    domain=func["function"],
                    is_applicable=True,
                    priority="high"
                )
                db.add(c_ctrl)
                count += 1

                for sub in cat["subcategories"]:
                    # C. Insert SUBCATEGORY (Leaf)
                    # Desc usually exists, but fallback just in case
                    s_desc = sub["description"]
                    if not s_desc: s_desc = sub["title"]

                    control = Control(
                        control_id=sub["code"],
                        title=sub["title"],
                        description=s_desc,
                        framework_id=fw.id,
                        category=cat["category"],
                        domain=func["function"],
                        is_applicable=True,
                        priority="high"
                    )
                    db.add(control)
                    count += 1
        
        db.commit()
        print(f" - Seeded {count} NIST Controls.")

        # 3. Create Intent-Based Mappings
        print("Creating Intent-Based Mappings...")
        mapping_count = 0
        
        # Pre-fetch lookup
        all_controls = db.query(Control).all()
        control_map = {c.control_id: c.id for c in all_controls}

        for nist_code, mapped_codes in NIST_INTENT_MAP.items():
            if nist_code not in control_map:
                print(f" - Skipping {nist_code} (Not found in DB)")
                continue
            
            nist_db_id = control_map[nist_code]

            for target_code in mapped_codes:
                if target_code not in control_map:
                    # Might be missing if SOC2/ISO not fully seeded, skip silent
                    continue
                
                target_db_id = control_map[target_code]

                # Check Existing
                exists = db.query(ControlMapping).filter(
                    ControlMapping.source_control_id == nist_db_id,
                    ControlMapping.target_control_id == target_db_id
                ).first()

                if not exists:
                    # NIST -> Target
                    m1 = ControlMapping(
                        source_control_id=nist_db_id,
                        target_control_id=target_db_id,
                        mapping_type="equivalent", # Intent-based equivalence
                        notes="Intent-Based Mapping (NIST CSF 2.0)"
                    )
                    db.add(m1)
                    
                    # Target -> NIST
                    m2 = ControlMapping(
                        source_control_id=target_db_id,
                        target_control_id=nist_db_id,
                        mapping_type="equivalent",
                        notes="Intent-Based Mapping (NIST CSF 2.0)"
                    )
                    db.add(m2)
                    mapping_count += 2
        
        db.commit()
        print(f" - Created {mapping_count} Intent-Based Mappings.")

    except Exception as e:
        print(f" - Error seeding NIST: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_nist()
