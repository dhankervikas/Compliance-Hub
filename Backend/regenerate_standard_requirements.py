from app.database import SessionLocal
from app.models.control import Control
from app.services.ai_service import suggest_evidence
from sqlalchemy import or_

def regenerate_stale_content():
    db = SessionLocal()
    print("--- REGENERATING CONTENT FOR 'STANDARD REQUIREMENT' CONTROLS ---")
    
    # Logic: Find controls where ai_explanation matches the placeholder "Standard Requirement"
    # Or just target Clause 4-10 specifically if we know they are bad.
    # The user said: "where the ai_explanation contains the string 'Standard Requirement'."
    
    # We'll check both ai_explanation and plain description just in case it's stored there temporarily
    targets = db.query(Control).filter(
        or_(
            Control.ai_explanation.like("%Standard Requirement%"),
            Control.description == "ISO 27001 Standard Requirement" 
        )
    ).all()
    
    total = len(targets)
    print(f"Found {total} controls with generic/stale content.")
    
    if total == 0:
        # Fallback: The user specifically mentioned 4.1, 4.2 etc might be bad.
        # Let's force check Clause 4.1
        print("Checking Clause 4.1 specifically...")
        c41 = db.query(Control).filter(Control.control_id == "4.1").first()
        if c41:
            print(f"4.1 Explanation: {c41.ai_explanation}")
            targets.append(c41)

    print(f"Starting regeneration for {len(targets)} controls...")
    
    success_count = 0
    for c in targets:
        print(f"[{success_count+1}/{len(targets)}] Regenerating {c.control_id}: {c.title}")
        try:
            # Passing regenerate=True forces the AI service to call the API again with the NEW prompt
            result = suggest_evidence(
                title=c.title,
                description=c.description or c.title,
                category=c.category,
                control_id=c.control_id,
                db=db,
                regenerate=True
            )
            val = result.get('explanation', 'N/A')
            print(f"   -> Done. New Goal: {val[:60]}...")
            success_count += 1
        except Exception as e:
            print(f"   -> FAILED: {e}")

    print(f"--- REGENERATION COMPLETE. {success_count} Updated. ---")
    db.close()

if __name__ == "__main__":
    regenerate_stale_content()
