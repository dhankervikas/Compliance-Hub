from app.database import SessionLocal
from app.models.tenant_framework import TenantFramework
from app.models.tenant import Tenant

db = SessionLocal()
tenant = db.query(Tenant).filter(Tenant.slug == "testtest").first()
if not tenant:
    print("Tenant testtest not found")
    exit(1)

print(f"Cleaning up frameworks for tenant: {tenant.name} ({tenant.internal_tenant_id})")
deleted = db.query(TenantFramework).filter(TenantFramework.tenant_id == tenant.internal_tenant_id).delete()
db.commit()
print(f"Deleted {deleted} framework links.")
db.close()
