
from app.database import SessionLocal
from app.api.settings import get_settings
from app.models.user import User

def debug_get_settings():
    db = SessionLocal()
    try:
        # User: admin (from testtest)
        user = db.query(User).filter(User.username == "admin", User.tenant_id == "testtest").first()
        if not user:
            print("User admin@testtest not found!")
            return

        print(f"Testing GET settings/org_profile as User: {user.username} (Tenant: {user.tenant_id})")

        try:
            response = get_settings(
                section_key="org_profile",
                db=db,
                current_user=user
            )
            print("Success!")
            print(f"Content: {response.content}")
        except Exception as e:
            print(f"CAUGHT EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    debug_get_settings()
