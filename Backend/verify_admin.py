from app.database import SessionLocal
from app.models.user import User
from app.utils.security import verify_password, get_password_hash

def verify_admin():
    db = SessionLocal()
    try:
        print("Checking for admin user...")
        user = db.query(User).filter(User.username == "admin").first()
        
        if not user:
            print("[X] Admin user NOT found!")
            print("Creating admin user now...")
            admin_user = User(
                email="admin@assurisk.ai",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin user created with password 'admin123'")
        else:
            print(f"[OK] Admin user found: {user.username} (Active: {user.is_active})")
            
            # Verify password
            if verify_password("admin123", user.hashed_password):
                print("[OK] Password 'admin123' is CORRECT")
            else:
                print("[X] Password 'admin123' is INCORRECT")
                print("Resetting password to 'admin123'...")
                user.hashed_password = get_password_hash("admin123")
                db.commit()
                print("[OK] Password reset to 'admin123'")
                
    except Exception as e:
        print(f"[ERROR] Error verifying admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_admin()
