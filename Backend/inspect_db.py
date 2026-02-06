from app.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.utils.security import verify_password, get_password_hash

db = SessionLocal()

print("--- USERS ---")
users = db.query(User).all()
for u in users:
    print(f"User: {u.username}, Email: {u.email}, Tenant: {u.tenant_id}, Active: {u.is_active}")
    if u.username == "admin":
        is_valid = verify_password("admin123", u.hashed_password)
        print(f"   Password 'admin123' valid? {is_valid}")

print("\n--- TENANTS ---")
tenants = db.query(Tenant).all()
for t in tenants:
    print(f"Tenant: {t.name} ({t.slug}) - ID: {t.id} / {t.internal_tenant_id}")

db.close()
