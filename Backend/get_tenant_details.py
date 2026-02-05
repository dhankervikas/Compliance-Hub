
from app.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()
tenants = db.query(Tenant).all()

print(f"{'Name':<20} | {'ID':<5} | {'Internal ID (UUID)'}")
print("-" * 60)
for t in tenants:
    print(f"{t.name:<20} | {t.id:<5} | {t.internal_tenant_id}")
