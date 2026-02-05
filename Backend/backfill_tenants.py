from app.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
import uuid
import secrets

def backfill_tenants():
    db = SessionLocal()
    try:
        print("Starting Tenant Backfill...")
        
        # 1. Get all unique tenant_ids from Users
        # We exclude 'default_tenant' as that is the super-admin realm (unless we want to manage it too, but usually it's special)
        # Actually, let's include everything to be safe, but handle default specially if needed.
        
        tenant_ids = db.query(User.tenant_id).distinct().all()
        tenant_ids = [t[0] for t in tenant_ids if t[0]]
        
        print(f"Found distinct tenant_ids in User table: {tenant_ids}")
        
        created_count = 0
        existing_count = 0
        
        for t_id in tenant_ids:
            # Check if tenant exists
            tenant = db.query(Tenant).filter(Tenant.slug == t_id).first()
            
            if tenant:
                print(f"Tenant '{t_id}' already exists. Skipping.")
                existing_count += 1
                continue
            
            # Create Tenant
            print(f"Creating Tenant record for '{t_id}'...")
            
            # Try to find a user to get a better name?
            admin_user = db.query(User).filter(User.tenant_id == t_id).first()
            name = t_id.replace('_', ' ').title() if not admin_user else f"{t_id.replace('_', ' ').title()}"
            
            new_tenant = Tenant(
                name=name,
                slug=t_id,
                internal_tenant_id=str(uuid.uuid4()),
                encryption_key=secrets.token_hex(32), # Generate a key for backfilled tenants
                is_active=True # Default to active
            )
            
            db.add(new_tenant)
            created_count += 1
            
        db.commit()
        print(f"Backfill Complete. Created: {created_count}, Existing: {existing_count}")
        
    except Exception as e:
        print(f"Error during backfill: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_tenants()
