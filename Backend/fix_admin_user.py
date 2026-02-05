
from app.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from sqlalchemy import text

def fix_admin_user():
    db = SessionLocal()
    try:
        print("Fixing Admin User ID 2...")
        # 1. Get User 2
        user = db.query(User).filter(User.id == 2).first()
        if not user:
            print("User ID 2 not found.")
            return

        # 2. Update to default_tenant
        # We need the Slug 'default_tenant' because User model likely uses tenant_id as string slug matching Tenant.slug
        # (Based on User: admin, Tenant: default_tenant output earlier)
        target_tenant = "default_tenant"
        
        print(f"Current User Tenant: {user.tenant_id}")
        user.tenant_id = target_tenant
        
        db.commit()
        print(f"Updated User ID 2 to tenant: {target_tenant}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_user()
