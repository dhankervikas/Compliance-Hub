
from app.database import SessionLocal
from app.models import User
from app.utils.security import get_password_hash

def reset_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print(f"[FOUND] User: {user.username}")
            new_hash = get_password_hash("password")
            user.hashed_password = new_hash
            db.commit()
            print("[SUCCESS] Password reset to 'password'")
        else:
            print("[MISSING] Admin user not found.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
