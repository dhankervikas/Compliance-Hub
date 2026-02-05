from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def reset_password():
    db = SessionLocal()
    try:
        username = "newadmin"
        new_password = "auditor123"
        
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User {username} found. Current Role: {user.role}")
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            print(f"Password successfully reset to: {new_password}")
        else:
            print(f"Error: User {username} not found in database.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
