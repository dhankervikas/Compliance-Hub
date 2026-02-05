from app.database import SessionLocal
from app.models.control import Control
from app.models.user import User
from app.models.tenant import Tenant

def check_tenant():
    db = SessionLocal()
    print("--- CHECKING TENANT IDS ---")
    
    # User
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print(f"User 'admin': TenantID='{admin.tenant_id}'")
        
        # Resolve Tenant UUID Logic (mirrored from API)
        tenant = db.query(Tenant).filter(Tenant.slug == admin.tenant_id).first()
        resolved_uuid = tenant.internal_tenant_id if tenant else admin.tenant_id
        print(f"Resolved UUID for Admin: '{resolved_uuid}'")
    else:
        print("User 'admin' NOT FOUND")
        
    # Controls
    c = db.query(Control).filter(Control.control_id == "4.1").first()
    if c:
        print(f"Control 4.1 TenantID: '{c.tenant_id}'")
    
    # Default Tenant
    dt = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    if dt:
        print(f"Default Tenant Internal UUID: '{dt.internal_tenant_id}'")
    else:
        print("Default Tenant NOT FOUND in Tenant table")

    db.close()

if __name__ == "__main__":
    check_tenant()
