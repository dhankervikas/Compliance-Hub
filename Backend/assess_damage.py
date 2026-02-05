from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import func

def assess_damage():
    db = SessionLocal()
    try:
        # Get Framework IDs
        iso = db.query(Framework).filter(Framework.code == "ISO27001").first()
        soc2 = db.query(Framework).filter(Framework.code == "SOC2").first()
        ai = db.query(Framework).filter(Framework.code == "AI_FRAMEWORK").first()
        
        if not ai:
            print("AI Framework not found. No damage possible from AI import.")
            return

        print(f"IDs -> ISO: {iso.id if iso else 'N/A'}, SOC2: {soc2.id if soc2 else 'N/A'}, AI: {ai.id}")
        
        # 1. Check for ISO Hijack (Numeric IDs like 5.1, 6.1, A.5.1)
        # Note: ISO 27001:2022 uses '5.1', 'A.5.1' etc.
        # AI Framework likely uses 'A.1.1' etc. which might clash if not careful, 
        # but the specific issue is likely Clause IDs (4 - 10).
        
        print("\n--- ISO 27001 Hijack Check ---")
        # Check for numeric IDs (Clauses) under AI framework
        hijacked_clauses = []
        ai_controls = db.query(Control).filter(Control.framework_id == ai.id).all()
        
        for c in ai_controls:
            # Check for Clause IDs: "4.1", "5.1", ... "10.2"
            # And Annex A IDs if they clash: "A.5.1"
            
            # Simple heuristic: If it starts with 4-10 and has a dot, and is NOT typical AI ID
            if c.control_id[0].isdigit() and '.' in c.control_id:
                parts = c.control_id.split('.')
                if parts[0].isdigit() and 4 <= int(parts[0]) <= 10:
                     hijacked_clauses.append(c)
        
        print(f"Found {len(hijacked_clauses)} potential ISO Clause controls under AI Framework:")
        for c in hijacked_clauses[:5]:
            print(f" - {c.control_id}: {c.title}")
            
        # 2. Check for SOC 2 Hijack
        print("\n--- SOC 2 Hijack Check ---")
        # SOC 2 IDs usually look like CC1.1, A1.1, etc.
        # If AI framework imported something like "CC1.1", it would take it.
        hijacked_soc2 = []
        for c in ai_controls:
            if c.control_id.startswith("CC") or c.control_id.startswith("PI") or c.control_id.startswith("A1."):
                 hijacked_soc2.append(c)
                 
        print(f"Found {len(hijacked_soc2)} potential SOC 2 controls under AI Framework:")
        for c in hijacked_soc2[:5]:
             print(f" - {c.control_id}: {c.title}")

    finally:
        db.close()

if __name__ == "__main__":
    assess_damage()
