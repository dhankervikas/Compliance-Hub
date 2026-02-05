from app.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.models.tenant_framework import TenantFramework

db = SessionLocal()

print("--- USERS ---")
users = db.query(User).filter(User.username.in_(['admin', 'testtest', 'admin@assurisk.ai'])).all()
for u in users:
    print(f"User: {u.username}, TenantID: {u.tenant_id}, Role: {u.role}")

print("\n--- TENANTS ---")
tenants = db.query(Tenant).all()
for t in tenants:
    print(f"Tenant: {t.name}, Slug: {t.slug}, InternalID: {t.internal_tenant_id}, Active: {t.is_active}")

print("\n--- TENANT FRAMEWORKS ---")
links = db.query(TenantFramework).all()
for l in links:
    print(f"Link: Tenant={l.tenant_id}, FW={l.framework_id}, Active={l.is_active}")

db.close()
