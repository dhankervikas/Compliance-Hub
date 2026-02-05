
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User

# Setup Path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def list_users():
    print("[-] Listing All Users in DB...")
    
    # We need to bypass RLS to see all users if RLS is enabled on connection, 
    # but here we are using a fresh connection which might defaults to default_tenant or no filter depending on implementation.
    # The 'auth.py' uses 'SET app.current_tenant', so raw connection is likely RLS-free or default.
    # Let's try raw SQL to be sure or just query User model.
    
    users = db.query(User).all()
    for u in users:
        print(f"User: {u.username} | Email: {u.email} | Tenant: {u.tenant_id} | Role: {u.role}")

    print("\n[-] Checking specifically for 'admin' in 'testtest'...")
    specific = db.query(User).filter(User.username == "admin", User.tenant_id == "testtest").first()
    if specific:
        print(f"[FOUND] admin user exists for testtest: {specific}")
    else:
        print("[MISSING] admin user DOES NOT exist for tenant 'testtest'")

if __name__ == "__main__":
    list_users()
