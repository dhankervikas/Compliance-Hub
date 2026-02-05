
import sys
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.tenant import Tenant
import uuid

# Import Data Sources
# Note: Adjust imports based on running from Backend/ directory
try:
    from app.utils.iso_data import ISO_CONTROLS_DATA
    from seed_soc2 import SOC2_COMMON_CRITERIA
    from data.nist_csf_2_0 import NIST_CSF_DATA
    from seed_iso42001_unified import ISO_42001_CONTROLS
    from data.iso42001_business_mapping import ISO_42001_BUSINESS_MAP
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running from the Backend/ directory.")
    sys.exit(1)

def seed_auditor_complete(tenant_slug="testtest"):
    db = SessionLocal()
    try:
        print(f"--- COMPLETE AUDITOR DATA SEEDING FOR: {tenant_slug} ---")
        
        # 1. Resolve Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not tenant:
            print(f"Tenant '{tenant_slug}' not found! Using hardcoded fallback if needed.")
            # Fallback for dev env if slug doesn't match but we know the UUID
            # or try to find a default
            tenant = db.query(Tenant).first()
            if not tenant:
                print("No tenants found in DB. Aborting.")
                return
            print(f"Reflected to available tenant: {tenant.slug} ({tenant.internal_tenant_id})")
        
        tenant_uuid = tenant.internal_tenant_id
        print(f"Target Tenant UUID: {tenant_uuid}")

        # --- HELPER: Get or Create Framework ---
        def get_fw(code, name, desc):
            fw = db.query(Framework).filter(Framework.code == code).first()
            if not fw:
                # Try by name
                fw = db.query(Framework).filter(Framework.name == name).first()
            
            if not fw:
                print(f"Creating Framework: {name}...")
                fw = Framework(name=name, code=code, description=desc)
                db.add(fw)
                db.commit()
                db.refresh(fw)
            else:
                 # Update code if needed (e.g. NIST_CSF -> NIST_CSF_2.0)
                 if fw.code != code:
                     print(f"Updating Framework Code: {fw.code} -> {code}")
                     fw.code = code
                     db.commit()
                     db.refresh(fw)

            return fw

        # --- HELPER: Process Mapping ---
        PROCESS_MAP = {
            "Governance": "Governance & Policy",
            "Performance Evaluation": "Audit & Assurance",
            "Improvement": "Audit & Assurance",
            "Control Environment": "Governance & Policy",
            "Communication and Information": "Governance & Policy",
            "Risk Assessment": "Risk Management",
            "Monitoring Activities": "Logging & Monitoring",
            "Control Activities": "Operations (General)",
            "Logical and Physical Access": "Access Control (IAM)",
            "System Operations": "Operations (General)",
            "Change Management": "Configuration Management",
            "Risk Mitigation": "Risk Management",
            "Function": "Governance & Policy", # NIST Functions
            "Category": "Governance & Policy" # NIST Categories
        }
        
        def normalize_category(cat):
            return PROCESS_MAP.get(cat, cat)
            
        # --- 2. SEED ISO 27001 ---
        iso_fw = get_fw("ISO27001", "ISO 27001:2022", "Information Security Management System")
        print(f"Seeding ISO 27001 (Ref ID: {iso_fw.id})...")
        
        # Wipe
        # Wipe ALL controls for tenant to prevent framework ID mismatches (ghost data)
        print("Wiping ALL controls for tenant to ensure clean slate...")
        db.query(Control).filter(Control.tenant_id == tenant_uuid).delete()
        db.commit()
        
        iso_count = 0
        for item in ISO_CONTROLS_DATA:
            # ONLY Annex A for Auditor Portal visuals usually, but let's do all
            # But Filter: Dashboard expects 'A.' usually
             if not (item["control_id"].startswith("A.") or item["control_id"].strip()[0].isdigit()):
                 continue

             unique_id = f"{item['control_id']}#{tenant_uuid[:8]}"
             c = Control(
                 tenant_id=tenant_uuid,
                 framework_id=iso_fw.id,
                 control_id=unique_id, 
                 title=item["title"],
                 description=item["description"],
                 category=normalize_category(item.get("category", "Uncategorized")),
                 domain=item.get("domain", "General"),
                 status="not_started",
                 priority=item.get("priority", "medium"),
                 classification=item.get("classification", "MANUAL")
             )
             db.add(c)
             iso_count += 1
        print(f" - Inserted {iso_count} ISO 27001 Controls.")


        # --- 3. SEED SOC 2 ---
        soc_fw = get_fw("SOC2", "SOC 2 (2017)", "Trust Service Criteria")
        print(f"Seeding SOC 2 (Ref ID: {soc_fw.id})...")
        
        db.query(Control).filter(Control.framework_id == soc_fw.id, Control.tenant_id == tenant_uuid).delete()
        
        soc_count = 0
        for item in SOC2_COMMON_CRITERIA:
            unique_id = f"{item['control_id']}#{tenant_uuid[:8]}"
            c = Control(
                tenant_id=tenant_uuid,
                framework_id=soc_fw.id,
                control_id=unique_id,
                title=item["title"],
                description=item["description"],
                category=normalize_category(item["category"]), # Important for Process View
                domain=item.get("category", "General"), # Use Category as Domain if missing
                status="not_started",
                priority=item.get("priority", "high"),
                classification="MANUAL" # Default
            )
            db.add(c)
            soc_count += 1
        print(f" - Inserted {soc_count} SOC 2 Controls.")


        # --- 4. SEED NIST CSF 2.0 ---
        nist_fw = get_fw("NIST_CSF_2.0", "NIST CSF 2.0", "Cybersecurity Framework")
        print(f"Seeding NIST CSF 2.0 (Ref ID: {nist_fw.id})...")

        db.query(Control).filter(Control.framework_id == nist_fw.id, Control.tenant_id == tenant_uuid).delete()
        
        nist_count = 0
        for func in NIST_CSF_DATA:
            # Function (GV, ID, etc.) can be a "Control" or just grouping. 
            # Frontend regex allows: GV|ID|PR|DE|RS|RC
            
            # 1. Function Level
            # db.add(Control(tenant_id=tenant_uuid, framework_id=nist_fw.id, control_id=func["function_code"], ...))
            # Usually we only want the leaf nodes for evidence, but header nodes for display.
            # I will include all levels like seed_tenant_full_data did.
            
            # NOTE: seed_tenant_full_data used suffix `#{tenant_uuid[:8]}`. 
            # I will avoid that for now to match Frontend Regex `^GV...`. 
            # `GV...#uuid` DOES match `^GV`, so that was safe.
            # But simple `GV` is cleaner if table allows. I'll stick to simple IDs.
            
            # Function
            f_uid = f"{func['function_code']}#{tenant_uuid[:8]}"
            db.add(Control(
                tenant_id=tenant_uuid, framework_id=nist_fw.id,
                control_id=f_uid, title=func["function"],
                description=func.get("description", func["function"]),
                category=normalize_category("Function"), domain=func["function"], status="not_started"
            ))
            nist_count += 1
            
            for cat in func["categories"]:
                # Category
                c_uid = f"{cat['code']}#{tenant_uuid[:8]}"
                db.add(Control(
                    tenant_id=tenant_uuid, framework_id=nist_fw.id,
                    control_id=c_uid, title=cat["category"],
                    description=cat.get("description", cat["category"]),
                    category=normalize_category("Category"), domain=func["function"], status="not_started"
                ))
                nist_count += 1
                
                for sub in cat["subcategories"]:
                    # Subcategory (The actual actionable control)
                    s_uid = f"{sub['code']}#{tenant_uuid[:8]}"
                    db.add(Control(
                        tenant_id=tenant_uuid, framework_id=nist_fw.id,
                        control_id=s_uid, title=sub["title"],
                        description=sub.get("description", sub["title"]),
                        category=normalize_category(cat["category"]), # This maps to Process often
                        domain=func["function"],
                        status="not_started"
                    ))
                    nist_count += 1
        
        print(f" - Inserted {nist_count} NIST CSF 2.0 Controls.")


        # --- 5. SEED ISO 42001 ---
        ai_fw = get_fw("ISO42001", "ISO 42001:2023", "AI Management System")
        print(f"Seeding ISO 42001 (Ref ID: {ai_fw.id})...")
        
        db.query(Control).filter(Control.framework_id == ai_fw.id, Control.tenant_id == tenant_uuid).delete()
        
        ai_count = 0
        for item in ISO_42001_CONTROLS:
             b_domain = ISO_42001_BUSINESS_MAP.get(item['control_id'], "AI Ethics & Governance")
             unique_id = f"{item['control_id']}#{tenant_uuid[:8]}"
             c = Control(
                 tenant_id=tenant_uuid,
                 framework_id=ai_fw.id,
                 control_id=unique_id,
                 title=item["title"],
                 description=item["description"],
                 category=normalize_category(item["category"]),
                 domain=b_domain,
                 status="not_started"
             )
             db.add(c)
             ai_count += 1
        print(f" - Inserted {ai_count} ISO 42001 Controls.")

        db.commit()
        print("\nSUCCESS: Database successfully seeded for Listener.")
        
    except Exception as e:
        print(f"ERROR Seeding Data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_auditor_complete()
