from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Control
from app.services.ai_service import suggest_evidence
import json

def debug_force_regen():
    db: Session = SessionLocal()
    try:
        # 1. Find the control "Annex A.5 & A.8" or similar
        # User said "Annex A.5 & A.8: Network Services, Segregation, and Transfer"
        # Search by title likeness
        control = db.query(Control).filter(Control.title.ilike("%Network Services%")).first()
        
        if not control:
            print("Control not found via title search.")
            # Try finding A.8.12 just to be sure
            control = db.query(Control).filter(Control.control_id == "A.8.12").first()
            if control:
                print(f"Fallback to A.8.12: {control.title}")
            else:
                print("No suitable control found.")
                return

        print(f"Found Control: {control.control_id} - {control.title}")
        print(f"Current Data (Preview): {str(control.ai_requirements_json)[:100]}")

        # 2. Force Regeneration
        print("\n--- Triggering AI Regeneration (OpenAI) ---")
        result = suggest_evidence(
            title=control.title,
            description=control.description,
            category="Organization of Information Security",
            control_id=control.control_id, # String ID
            db=db,
            regenerate=True
        )

        print("\n--- AI Result ---")
        print(json.dumps(result, indent=2))
        
        # 3. Check if it saved
        db.refresh(control)
        print(f"\nSaved Data (Preview): {str(control.ai_requirements_json)[:100]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_force_regen()
