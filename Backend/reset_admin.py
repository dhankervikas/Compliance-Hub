
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        # Find admin in default_tenant
        # We need a way to distinguish if username is duplicate.
        # SQLite doesn't strictly enforce schema tenant separation unless we filter.
        
        users = db.query(User).filter(User.username == "admin").all()
        target_user = None
        for u in users:
            if u.tenant_id == "default_tenant":
                target_user = u
                break
        
        if target_user:
            print(f"Found admin user in {target_user.tenant_id}. Resetting password to 'admin'...")
            target_user.hashed_password = get_password_hash("admin")
            db.commit()
            print("Password reset successful.")
        else:
            print("Admin user in default_tenant NOT FOUND. Creating one...")
            target_user = User(
                username="admin",
                email="admin@system.local",
                hashed_password=get_password_hash("admin"),
                tenant_id="default_tenant",
                full_name="System Administrator",
                role="admin",
                is_active=True,
                is_superuser=True
            )
            db.add(target_user)
            db.commit()
            print("Admin user created.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
