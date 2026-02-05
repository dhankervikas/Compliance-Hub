from app.database import SessionLocal
from app.models.control import Control
from app.services.ai_service import suggest_evidence
import sys

def regenerate_iso():
    db = SessionLocal()
    print("--- REGENERATING ISO 27001 CONTENT (ANTIGRAVITY STANDARD) ---")
    
    # Dynamic Framework Lookup
    # We need the ID for ISO27001
    from app.models.framework import Framework
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("ERROR: Could not find ISO27001 Framework!")
        return

    fw_id = fw.id
    print(f"Detected ISO27001 Framework ID: {fw_id}")

    # Select a subset of controls to update immediately (Annex A)
    # We focus on 5.x, 6.x, 7.x, 8.x
    controls = db.query(Control).filter(
        Control.framework_id == fw_id,
        Control.control_id.in_([
            "A.5.1", "A.5.9", "A.5.15", # Organizational
            "A.6.1", "A.6.3",           # People
            "A.7.2", "A.7.8",           # Physical
            "A.8.1", "A.8.10", "A.8.20" # Technological
        ])
    ).all()
    
    total = len(controls)
    print(f"Targeting {total} Key Controls for High-Quality Regeneration...")
    
    for i, c in enumerate(controls):
        print(f"[{i+1}/{total}] Regenerating {c.control_id}: {c.title}...")
        try:
            # Force Regenerate = True
            result = suggest_evidence(
                title=c.title,
                description=c.description or c.title,
                category=c.category,
                control_id=c.control_id,
                db=db,
                regenerate=True
            )
            print(f"   -> Success. Explanation: {result.get('explanation')[:50]}...")
        except Exception as e:
            print(f"   -> FAILED: {e}")
            
    db.close()
    print("--- REGENERATION COMPLETE ---")

if __name__ == "__main__":
    regenerate_iso()
