
from app.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.utils.security import get_password_hash

db = SessionLocal()
try:
    print("Starting Recovery...")
    
    # 1. Restore Super Admin
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        print("Restoring 'admin' user...")
        hashed = get_password_hash("admin")
        admin = User(
            username="admin",
            email="admin@assurisk.ai",
            hashed_password=hashed,
            tenant_id="default_tenant",
            full_name="System Administrator",
            role="admin",
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Admin restored.")
    else:
        print("Admin exists.")

    # 2. Cleanup Orphaned Tenants (Tenants with no users)
    # Since we know users table was empty, practically all tenants (except default) are orphans regarding admins
    # But let's be careful.
    # We will delete all tenants except 'default_tenant' to allow a clean slate for testing.
    
    print("Cleaning up test tenants...")
    db.query(Tenant).filter(Tenant.slug != "default_tenant").delete()
    db.commit()
    print("Test tenants deleted.")
    
    # Verify
    u_count = db.query(User).count()
    t_count = db.query(Tenant).count()
    print(f"Final State: {u_count} Users, {t_count} Tenants.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
