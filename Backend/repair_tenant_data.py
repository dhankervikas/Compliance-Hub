
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.tenant import Tenant
from sqlalchemy import text

def repair_tenant_ids():
    db = SessionLocal()
    try:
        print("Repairing Tenant IDs...")
        
        # 1. Update Controls
        result = db.execute(text("UPDATE controls SET tenant_id = 'default_tenant' WHERE tenant_id != 'default_tenant'"))
        print(f"Updated {result.rowcount} controls to 'default_tenant'.")
        
        # 2. Update Frameworks
        result_fw = db.execute(text("UPDATE frameworks SET tenant_id = 'default_tenant' WHERE tenant_id != 'default_tenant'"))
        print(f"Updated {result_fw.rowcount} frameworks to 'default_tenant'.")
        
        # 3. Ensure Tenant Exists
        tenant = db.query(Tenant).filter(Tenant.slug == 'default_tenant').first()
        if not tenant:
            print("Creating default_tenant record...")
            start_tenant = Tenant(
                slug="default_tenant",
                name="Default Organization",
                internal_tenant_id="default_tenant",
                tier="enterprise"
            )
            db.add(start_tenant)
        
        db.commit()
        print("Repair Complete. Consignment confirmed.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    repair_tenant_ids()
