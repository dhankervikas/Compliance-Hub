from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def create_users():
    db = SessionLocal()
    try:
        # 1. Auditor
        auditor = db.query(User).filter(User.username == "auditor").first()
        if not auditor:
            print("Creating Auditor user...")
            u = User(
                email="auditor@assurisk.ai",
                username="auditor",
                full_name="Jane Auditor",
                hashed_password=get_password_hash("auditor123"),
                role="auditor",
                allowed_frameworks="ALL",
                is_active=True
            )
            db.add(u)
            print("Auditor created: auditor / auditor123")
        else:
            print("Auditor user already exists. Resetting password...")
            auditor.hashed_password = get_password_hash("auditor123")
            auditor.role = "auditor" # Ensure role is set
            print("Auditor password reset to: auditor123")

        # 2. Standard User
        user = db.query(User).filter(User.username == "user").first()
        if not user:
            print("Creating Standard User...")
            u = User(
                email="user@assurisk.ai",
                username="user",
                full_name="John User",
                hashed_password=get_password_hash("user123"),
                role="user",
                allowed_frameworks="ALL",
                is_active=True
            )
            db.add(u)
            print("Standard User created: user / user123")
        else:
            print("Standard User already exists.")

        db.commit()
        print("Success.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_users()
