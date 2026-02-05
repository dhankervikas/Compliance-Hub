
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User
from app.utils.security import get_password_hash

# Setup Path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def fix_admin_user():
    print("[-] Fixing admin user for 'testtest'...")
    
    user = db.query(User).filter(User.username == "admin", User.tenant_id == "testtest").first()
    
    if not user:
        print("[ERROR] User not found!")
        return

    # Fix Email
    if not user.email:
        print("[-] Setting missing email to 'admin@testtest.com'")
        user.email = "admin@testtest.com"
        
    # Reset Password to 'admin'
    print("[-] Resetting password to 'admin'")
    user.hashed_password = get_password_hash("admin")
    
    db.commit()
    print("[SUCCESS] User updated. You should be able to login with 'admin' / 'admin'.")

if __name__ == "__main__":
    fix_admin_user()
