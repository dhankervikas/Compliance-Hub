from app.database import SessionLocal
from app.models import User
from app.utils.security import verify_password, get_password_hash

db = SessionLocal()

username = "admin"
password = "admin123"

print(f"--- DEBUGGING LOGIN FOR {username} ---")

# 1. Fetch User
user = db.query(User).filter(User.username == username).first()

if not user:
    print("[FAIL] User not found in DB!")
else:
    print(f"[OK] User found: ID={user.id}, Tenant={user.tenant_id}")
    
    # 2. Verify Password
    is_valid = verify_password(password, user.hashed_password)
    if is_valid:
        print("[OK] Password 'admin123' works!")
    else:
        print("[FAIL] Password 'admin123' FAILED.")
        print("Resetting password to 'admin123' now...")
        user.hashed_password = get_password_hash(password)
        db.commit()
        print("[OK] Password RESET complete.")
        
    # 3. Check Active Status
    print(f"Active: {user.is_active}")
    if not user.is_active:
        print("[FAIL] User is INACTIVE. Setting to Active...")
        user.is_active = True
        db.commit()

db.close()
