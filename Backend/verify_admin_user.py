
from app.database import SessionLocal
from app.models import User

def check_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print(f"[FOUND] User: {user.username}, Email: {user.email}, Active: {user.is_active}, Tenant: {user.tenant_id}")
        else:
            print("[MISSING] Admin user not found.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()
