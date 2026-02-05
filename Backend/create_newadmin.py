from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        username = "newadmin"
        password = "admin123"
        email = "newadmin@assurisk.ai"
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"Creating user {username}...")
            u = User(
                email=email,
                username=username,
                full_name="New Admin",
                hashed_password=get_password_hash(password),
                role="admin",
                allowed_frameworks="ALL",
                is_active=True
            )
            db.add(u)
            print(f"User created: {username} / {password}")
        else:
            print(f"User {username} already exists. Resetting password...")
            user.hashed_password = get_password_hash(password)
            user.role = "admin"
            print(f"Password reset to: {password}")

        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
