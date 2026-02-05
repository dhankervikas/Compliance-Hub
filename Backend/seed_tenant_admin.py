
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def seed_tenant_admin():
    db = SessionLocal()
    try:
        tenant_id = "testtest"
        username = "admin"
        password = "admin123"
        email = "admin@testtest.local" # Use a dummy email to avoid conflict with system admin
        
        # Check if user exists in this tenant
        user = db.query(User).filter(
            User.username == username,
            User.tenant_id == tenant_id
        ).first()
        
        if user:
            print(f"Updating existing user '{username}' in tenant '{tenant_id}'...")
            user.hashed_password = get_password_hash(password)
            user.email = email
            user.is_active = True
            user.role = "admin"
        else:
            print(f"Creating new user '{username}' in tenant '{tenant_id}'...")
            user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                tenant_id=tenant_id,
                full_name="Test Tenant Admin",
                role="admin",
                is_active=True
            )
            db.add(user)
            
        db.commit()
        print("User seeded successfully.")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Tenant: {tenant_id}")
            
    except Exception as e:
        print(f"Error seeding user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_tenant_admin()
