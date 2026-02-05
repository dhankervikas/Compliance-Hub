
import requests
import json
from app.database import SessionLocal
from app.api.settings import update_settings
from app.schemas.compliance_profile import SettingsUpdate
from app.models.user import User

def reproduce_error():
    db = SessionLocal()
    try:
        # Mock the user "admin" from tenant "testtest"
        # We know this user exists from previous step
        user = db.query(User).filter(User.username == "admin", User.tenant_id == "testtest").first()
        if not user:
            print("User admin@testtest not found!")
            return

        print(f"Testing as User: {user.username} (Tenant: {user.tenant_id})")

        # Simulate payload from FrameworkSetupWizard.js
        # It sends section="scope" and content dict
        payload_data = {
            "section": "scope",
            "content": {
                "soc2_selected_principles": ["Security", "Availability", "Confidentiality"],
                "soc2_exclusions": {}
            }
        }
        
        payload = SettingsUpdate(**payload_data)
        
        print("Attempting update_settings...")
        try:
            response = update_settings(
                section_key="scope",
                payload=payload,
                db=db,
                current_user=user
            )
            print("Success!")
            print(json.dumps(response.content, default=str))
        except Exception as e:
            print(f"CAUGHT EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    reproduce_error()
