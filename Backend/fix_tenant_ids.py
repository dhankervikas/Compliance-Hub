from app.database import SessionLocal
from app.models.control import Control
from app.models.user import User
from app.models.tenant import Tenant
import sqlalchemy

def fix_tenants():
    db = SessionLocal()
    print("--- FIXING TENANT IDS ---")
    
    # 1. Get Default Tenant
    dt = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    if not dt:
        print("Creating Default Tenant...")
        dt = Tenant(name="Default Organization", slug="default_tenant", internal_tenant_id="default-uuid-fixed", is_active=True)
        db.add(dt)
        db.commit()
        db.refresh(dt)
        
    print(f"Target Tenant UUID: {dt.internal_tenant_id}")
    
    # 2. Update Admin User
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        if admin.tenant_id != "default_tenant":
            admin.tenant_id = "default_tenant"
            db.commit()
            print("Admin user updated to 'default_tenant'")
    
    # 3. Update Controls
    # We update ALL controls to be visible to default tenant for now (Dev Mode)
    # Or just ISO 27001
    count = db.query(Control).count()
    print(f"Updating {count} controls to Tenant UUID: {dt.internal_tenant_id}")
    
    db.execute(
        sqlalchemy.text("UPDATE controls SET tenant_id = :tid"),
        {"tid": dt.internal_tenant_id}
    )
    db.commit()
    
    print("Fix Complete.")
    db.close()

if __name__ == "__main__":
    fix_tenants()
