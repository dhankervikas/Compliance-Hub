from app.database import SessionLocal
from app.models.person import Person
from app.models.control import Control
from app.services.ai_service import suggest_evidence
import json

def diagnose():
    db = SessionLocal()
    print("--- DIAGNOSING A.8.12 ---")
    
    # Check DB State
    controls = db.query(Control).filter(Control.control_id.like("%A.8.12%")).all()
    print(f"Found {len(controls)} controls matching 'A.8.12'")
    
    for c in controls:
        print(f"\n[DB Control]: ID='{c.control_id}' | Title='{c.title}'")
        print(f"RAW JSON: {c.ai_requirements_json}")
        
    # Check Service Logic
    print("\n--- CHECKING SERVICE LOGIC ---")
    print("Calling suggest_evidence('Data leakage prevention', '', 'Operations', 'A.8.12', db=db, regenerate=False)...")
    result = suggest_evidence('Data leakage prevention', '', 'Operations', 'A.8.12', db=db, regenerate=False)
    print("RESULT (Use Persisted):")
    print(json.dumps(result, indent=2))
    
    print("\nCalling suggest_evidence(..., regenerate=True)...")
    # Mocking OpenAI call or just seeing if it bypasses DB
    # We won't actually call OpenAI here to avoid cost/time, but we can check if it returns 'Standard Policy'
    # Actually, suggest_evidence will call OpenAI. That's fine.
    
    db.close()

if __name__ == "__main__":
    diagnose()
