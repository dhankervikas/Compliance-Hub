
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.tenant import Tenant
import sys
import os

# Import Data Sources
from data.nist_csf_2_0 import NIST_CSF_DATA
from seed_iso42001_unified import ISO_42001_CONTROLS

def seed_full_tenant_data(tenant_slug="testtest"):
    db = SessionLocal()
    try:
        print(f"--- FULL SEEDING FOR TENANT: {tenant_slug} ---")
        
        # 1. Resolve Tenant ID
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not tenant:
            print(f"ERROR: Tenant '{tenant_slug}' not found!")
            return
        
        tenant_uuid = tenant.internal_tenant_id
        print(f"Target Tenant UUID: {tenant_uuid}")

        # --- SEED ISO 42001 (70 Items) ---
        # Import Business Mapping
        from data.iso42001_business_mapping import ISO_42001_BUSINESS_MAP

        iso_fw = db.query(Framework).filter(Framework.code == "ISO42001").first()
        if not iso_fw:
            print("Creating ISO 42001 Framework...")
            iso_fw = Framework(name="ISO 42001:2023", code="ISO42001", description="AI Management System")
            db.add(iso_fw)
            db.commit()
            db.refresh(iso_fw)
        
        print(f"Seeding ISO 42001 (Ref ID: {iso_fw.id})...")
        
        # Wipe Existing
        deleted = db.query(Control).filter(
            Control.framework_id == iso_fw.id,
            Control.tenant_id == tenant_uuid
        ).delete()
        print(f" - Deleted {deleted} existing ISO controls.")
        
        # Insert Full Set
        count = 0
        for item in ISO_42001_CONTROLS:
            # UNIQUE ID FIX: Append Tenant UUID to Control ID
            # Structure: {ORIGINAL_ID}#{TENANT_UUID_PREFIX}
            unique_control_id = f"{item['control_id']}#{tenant_uuid[:8]}"
            
            # LOOKUP BUSINESS DOMAIN
            # Use original ID to look up domain mapping
            b_domain = ISO_42001_BUSINESS_MAP.get(item['control_id'], "AI Ethics & Governance")

            c = Control(
                tenant_id=tenant_uuid,
                framework_id=iso_fw.id,
                control_id=unique_control_id, # Tenant Scoped ID
                title=item["title"],
                description=item["description"],
                category=item["category"],
                status="not_started",
                domain=b_domain # USE MAPPED BUSINESS DOMAIN
            )
            db.add(c)
            count += 1
        print(f" - Inserted {count} ISO 42001 Controls.")


        # --- SEED NIST CSF 2.0 (134 Items) ---
        # Try finding by code first, then name
        nist_fw = db.query(Framework).filter(Framework.code == "NIST_CSF_2.0").first()
        if not nist_fw:
             nist_fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
             
        if not nist_fw:
             print("Creating NIST CSF 2.0 Framework...")
             nist_fw = Framework(name="NIST CSF 2.0", code="NIST_CSF_2.0", description="NIST CSF 2.0")
             db.add(nist_fw)
             db.commit()
             db.refresh(nist_fw)
        
        print(f"Seeding NIST CSF 2.0 (Ref ID: {nist_fw.id})...")

        # Wipe Existing
        deleted = db.query(Control).filter(
            Control.framework_id == nist_fw.id,
            Control.tenant_id == tenant_uuid
        ).delete()
        print(f" - Deleted {deleted} existing NIST controls.")

        # Insert Full Set (Recursive parsing of NIST Data Structure)
        nist_count = 0
        
        for func in NIST_CSF_DATA:
            # 1. Function
            f_code = func.get("function_code")
            f_uid = f"{f_code}#{tenant_uuid[:8]}"
            
            db.add(Control(
                tenant_id=tenant_uuid, framework_id=nist_fw.id,
                control_id=f_uid, title=func["function"], 
                description=func.get("description", func["function"]),
                category="Function", domain=func["function"]
            ))
            nist_count += 1
            
            for cat in func["categories"]:
                # 2. Category
                c_code = cat.get("code")
                c_uid = f"{c_code}#{tenant_uuid[:8]}"
                
                db.add(Control(
                    tenant_id=tenant_uuid, framework_id=nist_fw.id,
                    control_id=c_uid, title=cat["category"],
                    description=cat.get("description", cat["category"]), # Fallback desc
                    category="Category", domain=func["function"]
                ))
                nist_count += 1
                
                for sub in cat["subcategories"]:
                    # 3. Subcategory (The actual controls usually)
                    s_code = sub.get("code")
                    s_uid = f"{s_code}#{tenant_uuid[:8]}"
                    
                    db.add(Control(
                        tenant_id=tenant_uuid, framework_id=nist_fw.id,
                        control_id=s_uid, title=sub["title"],
                        description=sub.get("description", sub["title"]),
                        category=cat["category"], domain=func["function"]
                    ))
                    nist_count += 1
        
        print(f" - Inserted {nist_count} NIST CSF 2.0 Controls.")
        
        db.commit()
        print("\nSUCCESS: Database successfully seeded.")

    except Exception as e:
        print(f"ERROR Seeding Data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_full_tenant_data()
