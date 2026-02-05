
from app.database import SessionLocal
from app.models.user import User
from app.api.users import read_users
from fastapi import HTTPException

# Mock Dependency
def get_mock_admin():
    db = SessionLocal()
    # Get the testtest admin
    user = db.query(User).filter(User.username == "admin", User.tenant_id == "testtest").first()
    db.close()
    if not user:
        raise Exception("Test User not found")
    return user

def reproduce_users():
    db = SessionLocal()
    admin = get_mock_admin()
    print(f"Acting as: {admin.username} ({admin.email}) Role: {admin.role}")
    
    try:
        users = read_users(skip=0, limit=100, db=db, admin=admin)
        print(f"Found {len(users)} users.")
        for u in users:
            print(f" - {u.username} (Tenant: {u.tenant_id})")
    except Exception as e:
        print(f"Error calling read_users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reproduce_users()
