from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.services.ai_service import generate_business_text
import time

def regenerate_all():
    db = SessionLocal()
    print("--- REGENERATING ALL ISO 27001 TITLES & DESCRIPTIONS (OPENAI) ---")
    
    # 1. Get ISO Framework ID
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("ISO Framework not found.")
        return
        
    fw_id = fw.id
    
    # 2. Get All Controls
    controls = db.query(Control).filter(Control.framework_id == fw_id).all()
    print(f"Found {len(controls)} ISO Controls. Starting AI Stream...")
    
    for i, c in enumerate(controls):
        print(f"[{i+1}/{len(controls)}] Processing {c.control_id}...")
        
        # Use existing title/desc as input "Standard Text"
        # We assume standard text is currently in description or title.
        # Ideally, we'd have the *original* standard text. 
        # But if the current title is "Policy", sending "Policy" to AI might confusing it.
        # Let's hope the ID "4.1" + Text is enough Context.
        
        input_text = c.description or c.title
        
        result = generate_business_text(c.control_id, input_text)
        
        new_title = result.get("business_title")
        new_desc = result.get("business_description")
        
        if new_title and new_desc:
            print(f"   -> NEW TITLE: {new_title}")
            # print(f"   -> NEW DESC:  {new_desc}")
            c.title = new_title
            c.description = new_desc
            # Update actionable_title if it existed (it doesn't, but concept exists)
            # The API falls back to title, so just updating title is enough.
            
            db.commit() # Commit each one to be safe/incremental
            time.sleep(0.5) # Avoid Rate Limit
        else:
            print("   -> FAILED TO GENERATE.")
            
    db.close()
    print("--- REGENERATION COMPLETE ---")

if __name__ == "__main__":
    regenerate_all()
