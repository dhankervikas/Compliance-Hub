
from app.database import SessionLocal
from app.models import User, Tenant, Framework, TenantFramework

def inspect():
    db = SessionLocal()
    try:
        print("--- TENANTS ---")
        tenants = db.query(Tenant).all()
        for t in tenants:
            print(f"ID: {t.id} | Slug: {t.slug} | Name: {t.name} | UUID: {t.internal_tenant_id}")

        print("\n--- FRAMEWORKS ---")
        fws = db.query(Framework).all()
        for f in fws:
            print(f"ID: {f.id} | Code: {f.code} | TenantId: {f.tenant_id}")

        print("\n--- TENANT FRAMEWORKS ---")
        tfs = db.query(TenantFramework).all()
        for tf in tfs:
             print(f"Tenant: {tf.tenant_id} | Framework: {tf.framework_id} | Active: {tf.is_active}")

        print("\n--- USERS ---")
        users = db.query(User).all()
        for u in users:
            print(f"User: {u.username} | TenantID: {u.tenant_id} | Role: {u.role}")
    except Exception as e:
        print(e)
    finally:
        db.close()

if __name__ == "__main__":
    inspect()
