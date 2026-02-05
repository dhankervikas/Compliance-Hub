
import requests
import json

API_URL = "http://localhost:8000/settings"
# Assuming we have a valid token or can mock auth. 
# For this test, I'll assume I can hit it if I disable auth or if I use a known token.
# But getting a token is hard.
# So instead I will write a script that imports the app logic directly to test the backend function.

from app.database import SessionLocal
from app.api.settings import update_settings, get_settings
from app.schemas.compliance_profile import SettingsUpdate
from app.models.user import User

def test_scope_update():
    db = SessionLocal()
    try:
        # Mock user
        user = User(id=1, email="test@example.com", tenant_id="default_tenant")
        
        # 1. Simulate Framework Wizard Save (updates soc2_selected_principles)
        payload_wizard = SettingsUpdate(
            section="scope",
            content={
                "soc2_selected_principles": ["Security", "Availability"],
                "soc2_exclusions": {"Privacy": "Not applicable"}
            }
        )
        print("--- Saving Wizard Data ---")
        res1 = update_settings(section_key="scope", payload=payload_wizard, db=db, current_user=user)
        print("Result 1:", json.dumps(res1.content, default=str))

        # 2. Simulate Settings Form Save (updates scope_statement)
        # CRITICAL: Does it merge or overwrite?
        # The form sends:
        payload_form = SettingsUpdate(
            section="scope",
            content={
                "scope_statement": "My ISMS Scope",
                "locations": ["NY", "SF"],
                "frameworks": ["SOC 2"]
            }
        )
        print("\n--- Saving Form Data (Simulating Overwrite?) ---")
        # In the actual API, the Update logic REPLACES content with payload.content
        # Let's see what happens.
        res2 = update_settings(section_key="scope", payload=payload_form, db=db, current_user=user)
        print("Result 2:", json.dumps(res2.content, default=str))
        
        # Check if SOC 2 data persists
        if "soc2_selected_principles" not in res2.content:
            print("\n[FAILURE] SOC 2 Data LOST after Form Save!")
        else:
            print("\n[SUCCESS] SOC 2 Data Persisted.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup test data?
        # db.query(ComplianceSettings).filter(ComplianceSettings.section_key == "scope", ComplianceSettings.tenant_id == "default_tenant").delete()
        # db.commit()
        db.close()

if __name__ == "__main__":
    test_scope_update()
