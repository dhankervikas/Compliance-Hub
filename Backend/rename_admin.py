
from app.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

def rename_admin():
    db = SessionLocal()
    try:
        print("Renaming Duplicate Admin (ID 2)...")
        user = db.query(User).filter(User.id == 2).first()
        if not user:
            print("User ID 2 not found.")
            return

        print(f"Renaming {user.username} -> admin_legacy")
        user.username = "admin_legacy"
        # We also need to move it to default_tenant if we want to keep it valid?
        # Or just rename it so 'admin' resolves to ID 1.
        # Let's just rename it first.
        
        db.commit()
        print("Rename Successful.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rename_admin()
