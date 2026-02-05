import sys
import os
from sqlalchemy import text
from app.database import SessionLocal
from app.models.user import User

sys.path.append(os.getcwd())

def inspect_admin():
    db = SessionLocal()
    try:
        print("--- Inspecting Admin User ---")
        # Raw SQL to bypass any RLS that might be active on session (though new session shouldn't have any)
        result = db.execute(text("SELECT id, username, tenant_id, role, is_superuser FROM users WHERE username = 'admin'"))
        admin = result.fetchone()
        
        if admin:
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Tenant ID: {admin.tenant_id}")
            print(f"Role: {admin.role}")
            print(f"Superuser: {admin.is_superuser}")
        else:
            print("ERROR: Admin user not found!")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect_admin()
