from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.control import Control
from app.models.person import Person
from sqlalchemy import func

db = SessionLocal()
print("--- TENANT DIAGNOSTIC ---")
tenants = db.query(Tenant).all()
for t in tenants:
    print(f"Tenant: Name='{t.name}', Slug='{t.slug}', UUID='{t.internal_tenant_id}'")

print("\n--- CONTROL TENANT COUNTS ---")
counts = db.query(Control.tenant_id, func.count(Control.id)).group_by(Control.tenant_id).all()
for tenant_id, count in counts:
    print(f"Tenant ID '{tenant_id}': {count} controls")

db.close()
