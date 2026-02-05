
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.tenant import Tenant

def fix_nist_badges():
    db = SessionLocal()
    print("--- FIXING NIST BADGES ---")
    
    # 1. Resolve Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == "testtest").first()
    if not tenant:
        print("Tenant not found")
        return
    
    targets = [
        {"title": "Incident Recovery Improvement", "new_category": "Operational"},
        {"title": "Incident Recovery Plan Execution", "new_category": "Operational"}
    ]
    
    updated_count = 0
    
    for t in targets:
        # Find control by title and tenant
        controls = db.query(Control).filter(
            Control.tenant_id == tenant.internal_tenant_id, 
            Control.title == t["title"]
        ).all()
        
        for c in controls:
            print(f"Updating '{c.title}' (ID: {c.id}) -> Category: {t['new_category']}")
            c.category = t["new_category"]
            updated_count += 1
            
    db.commit()
    print(f"Updated {updated_count} controls.")
    db.close()

if __name__ == "__main__":
    fix_nist_badges()
