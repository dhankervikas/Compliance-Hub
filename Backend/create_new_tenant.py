import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings

# Setup DB connection
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tenant_user(username, email, password, tenant_id, full_name=None):
    db = SessionLocal()
    
    # Check existing
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        print(f"Error: User with username '{username}' or email '{email}' already exists.")
        db.close()
        return

    print(f"Creating user '{username}' for Tenant '{tenant_id}'...")
    
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        tenant_id=tenant_id,
        full_name=full_name or username,
        is_active=True,
        role="admin" # First user of a tenant is usually admin of that tenant
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"SUCCESS: User {new_user.username} created (ID: {new_user.id}, Tenant: {new_user.tenant_id})")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new tenant user.")
    parser.add_argument("username", help="Username")
    parser.add_argument("email", help="Email address")
    parser.add_argument("password", help="Password")
    parser.add_argument("tenant_id", help="Tenant ID (e.g., 'acme_corp')")
    parser.add_argument("--name", help="Full Name", default=None)

    # Allow interactive if no args?
    if len(sys.argv) == 1:
        print(" Interactive Mode: Create New Tenant User")
        u = input("Username: ")
        e = input("Email: ")
        p = input("Password: ")
        t = input("Tenant ID: ")
        n = input("Full Name [Optional]: ")
        create_tenant_user(u, e, p, t, n)
    else:
        args = parser.parse_args()
        create_tenant_user(args.username, args.email, args.password, args.tenant_id, args.name)
