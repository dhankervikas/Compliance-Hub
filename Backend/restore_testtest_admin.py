from app.database import SessionLocal
from app.models import User
from app.utils.security import get_password_hash
import uuid

db = SessionLocal()

# TestTest Internal ID confirmed from previous step
TENANT_UUID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"
USERNAME = "admin"
PASSWORD = "admin123"

print(f"--- RESTORING ADMIN FOR TENANT {TENANT_UUID} ---")

# Check if exists (just in case)
existing = db.query(User).filter(User.username == USERNAME, User.tenant_id == TENANT_UUID).first()
if existing:
    print("User already exists!")
else:
    print("Creating user...")
    unique_email = f"admin_{str(uuid.uuid4())[:8]}@testtest.local"
    # Or check if we can reuse the email if we find the orphan
    print(f"Using email: {unique_email}")
    
    new_user = User(
        email=unique_email,
        username=USERNAME,
        full_name="TestTest Admin",
        hashed_password=get_password_hash(PASSWORD),
        tenant_id=TENANT_UUID,
        is_active=True,
        is_superuser=False, # Tenant admins are usually not superusers, but verified by role
        role="admin"
    )
    db.add(new_user)
    db.commit()
    print("SUCCESS: User restored.")

db.close()
