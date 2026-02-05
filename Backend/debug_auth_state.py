
from app.database import SessionLocal
from app.models.control import Control
from app.models.tenant import Tenant
from app.models.user import User
from sqlalchemy import text

def debug_auth():
    db = SessionLocal()
    try:
        print("--- TENANTS ---")
        tenants = db.query(Tenant).all()
        for t in tenants:
            print(f"ID: {t.id} | Slug: {t.slug} | Name: {t.name} | InternalID: {t.internal_tenant_id} | Active: {t.is_active}")
            
        print("\n--- USERS ---")
        users = db.query(User).all()
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Tenant: {u.tenant_id} | Role: {u.role} | IsActive: {u.is_active}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_auth()
