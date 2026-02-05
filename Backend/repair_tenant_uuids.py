
from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import text

def fix_uuids():
    db = SessionLocal()
    try:
        print("Fetching Default Tenant UUID...")
        tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
        if not tenant:
            print("Error: Default Tenant not found!")
            return
        
        uuid = tenant.internal_tenant_id
        slug = tenant.slug
        print(f"Target UUID: {uuid}")
        print(f"Current Slug: {slug}")

        # Update Controls
        # Set tenant_id = UUID where tenant_id = SLUG
        print("Updating Controls...")
        c_stmt = text("UPDATE controls SET tenant_id = :uuid WHERE tenant_id = :slug")
        res = db.execute(c_stmt, {"uuid": uuid, "slug": slug})
        print(f"Controls Updated: {res.rowcount}")

        # Update Frameworks
        print("Updating Frameworks...")
        f_stmt = text("UPDATE frameworks SET tenant_id = :uuid WHERE tenant_id = :slug")
        res_f = db.execute(f_stmt, {"uuid": uuid, "slug": slug})
        print(f"Frameworks Updated: {res_f.rowcount}")

        db.commit()
        print("Commit Successful.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_uuids()
