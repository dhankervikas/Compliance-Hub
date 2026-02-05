
from app.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

def move_admin_legacy():
    db = SessionLocal()
    try:
        print("Moving admin_legacy (ID 2) to default_tenant...")
        user = db.query(User).filter(User.id == 2).first()
        if not user:
            print("User ID 2 not found.")
            return

        print(f"User: {user.username}, Current Tenant: {user.tenant_id}")
        
        target_tenant = "default_tenant"
        user.tenant_id = target_tenant
        
        db.commit()
        print(f"Success. Moved {user.username} to {target_tenant}.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    move_admin_legacy()
