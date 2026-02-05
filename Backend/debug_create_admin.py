
from app.database import SessionLocal
from app.models import User
# Simplified hashing if security module fails, but try import first
try:
    from app.utils.security import get_password_hash
except ImportError:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def get_password_hash(password):
        return pwd_context.hash(password)

def fix_login():
    db = SessionLocal()
    pwd = get_password_hash("password")
    target_tenant_id = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" # TestTest UUID
    
    # 1. Reset Default Admin
    u1 = db.query(User).filter(User.username == "admin", User.tenant_id == "default_tenant").first()
    if u1:
        u1.hashed_password = pwd
        print("Reset admin (default_tenant)")
    else:
        print("Warning: default_tenant admin not found")

    # 2. Check/Create TestTest Admin
    # Check by tenant_id
    u2 = db.query(User).filter(User.username == "admin", User.tenant_id == target_tenant_id).first()
    
    if u2:
        u2.hashed_password = pwd
        print(f"Reset admin ({target_tenant_id})")
    else:
        # Create
        print(f"Creating admin for {target_tenant_id}")
        new_user = User(
            username="admin",
            email="admin@testtest.com",
            hashed_password=pwd,
            # Use UUID as tenant_id
            tenant_id=target_tenant_id,
            role="admin",
            full_name="TestTest Admin",
            is_active=True,
            is_superuser=True,
            allowed_frameworks="ALL"
        )
        db.add(new_user)

    db.commit()
    db.close()
    print("Login Fix Complete. Creds: admin / password")

if __name__ == "__main__":
    fix_login()
