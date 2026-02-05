
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.tenant import Tenant
from data.nist_csf_2_0 import NIST_CSF_DATA
import sys

def fix_nist_data():
    db = SessionLocal()
    tenant_slug = "testtest"
    
    print(f"--- FIXING NIST DATA for tenant: {tenant_slug} ---")
    
    # 1. Resolve Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        print("Tenant not found")
        return
    tenant_uuid = tenant.internal_tenant_id
    print(f"Tenant UUID: {tenant_uuid}")

    # 2. Resolve NIST Framework (TARGETING ID 5 / Code NIST-CSF)
    fw = db.query(Framework).filter(Framework.code == "NIST-CSF").first()
    if not fw:
        # Fallback to search by Name if Code differs
        fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
        
    if not fw:
        print("NIST Framework not found.")
        return
        
    print(f"Target Framework: ID={fw.id}, Code={fw.code}, Name={fw.name}")

    # 3. WIPE ALL CONTROLS for this Framework + Tenant
    print(f"Wiping existing controls for Framework {fw.id}...")
    deleted = db.query(Control).filter(
        Control.framework_id == fw.id,
        Control.tenant_id == tenant_uuid
    ).delete()
    db.commit()
    print(f"Deleted {deleted} controls.")
    
    # 4. RE-SEED 134 Items
    print("Re-seeding 134 NIST Controls...")
    count = 0
    for func in NIST_CSF_DATA:
        # 1. Function
        f_uid = f"{func['function_code']}#{tenant_uuid[:8]}"
        db.add(Control(
            tenant_id=tenant_uuid, framework_id=fw.id,
            control_id=f_uid, title=func["function"], 
            description=func.get("description", func["function"]),
            category="Function", domain=func["function"]
        ))
        count += 1
        
        for cat in func["categories"]:
            # 2. Category
            c_uid = f"{cat['code']}#{tenant_uuid[:8]}"
            db.add(Control(
                tenant_id=tenant_uuid, framework_id=fw.id,
                control_id=c_uid, title=cat["category"],
                description=cat.get("description", cat["category"]),
                category="Category", domain=func["function"]
            ))
            count += 1
            
            for sub in cat["subcategories"]:
                # 3. Subcategory
                s_uid = f"{sub['code']}#{tenant_uuid[:8]}"
                db.add(Control(
                    tenant_id=tenant_uuid, framework_id=fw.id,
                    control_id=s_uid, title=sub["title"],
                    description=sub.get("description", sub["title"]),
                    category=cat["category"], domain=func["function"]
                ))
                count += 1
                
    db.commit()
    print(f"Successfully inserted {count} controls.")
    db.close()

if __name__ == "__main__":
    fix_nist_data()
