
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.tenant import Tenant

def check_duplicates():
    db = SessionLocal()
    print("--- Checking NIST Duplicates ---")
    
    # 1. Get Framework
    fw = db.query(Framework).filter(Framework.code == "NIST-CSF").first() # ID 5 usually
    if not fw:
        fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
    
    if not fw:
        print("NIST Framework not found.")
        return
        
    print(f"Framework: {fw.name} (ID: {fw.id})")
    
    # 2. Get Test Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == "testtest").first()
    tenant_uuid = tenant.internal_tenant_id if tenant else "unknown"
    print(f"Tenant UUID: {tenant_uuid}")
    
    # 3. Query All Controls for this framework (No tenant filter initially to see all)
    controls = db.query(Control).filter(Control.framework_id == fw.id).all()
    print(f"Total Controls in DB for Framework: {len(controls)}")
    
    # Group by Clean ID (stripping tenant suffix)
    by_id = {}
    for c in controls:
        # Expected ID format: "CODE#TENANT_PREFIX"
        clean = c.control_id.split('#')[0]
        if clean not in by_id:
            by_id[clean] = []
        by_id[clean].append(c)
        
    # Print Duplicates
    print("\n--- DETECTED DUPLICATES ---")
    count = 0
    for cid, list_c in by_id.items():
        if len(list_c) > 1:
            print(f"\nControl ID: {cid}")
            for c in list_c:
                print(f" - DB_ID: {c.id} | Tenant: {c.tenant_id} | Cat: {c.category} | Title: {c.title}")
            count += 1
            if count > 10:
                print("... (more duplicates exist)")
                break
                
    if count == 0:
        print("No duplicates found by ID.")

    db.close()

if __name__ == "__main__":
    check_duplicates()
