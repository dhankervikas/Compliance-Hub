from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.services.ai_service import generate_business_text
import time

def apply_vanta_rewrite():
    db = SessionLocal()
    print("--- STARTING VANTA-STYLE DATA FLUSH & REWRITE ---")
    
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw: return
    fw_id = fw.id
    
    # 1. HARDCODED OVERRIDES (User Specific)
    overrides = {
        "4.1": ("Determine external and internal issues", "Determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its information security management system."),
        "4.2": ("Determine interested parties and requirements", "Determine interested parties relevant to the ISMS and relevance of their requirements to information security."),
        "4.3": ("Determine the scope of the ISMS", "Determine the boundaries and applicability of the information security management system to establish its scope."),
        "5.2": ("Information security policy", "Establish, maintain, and communicate an information security policy that is appropriate to the purpose of the organization.")
    }
    
    print("Applying User Overrides...")
    for cid, (title, desc) in overrides.items():
        c = db.query(Control).filter(Control.control_id == cid, Control.framework_id == fw_id).first()
        if c:
            c.title = title
            c.description = desc
            # FLUSH AI DATA
            c.ai_explanation = None
            c.ai_requirements_json = None
            print(f"   -> Fixed {cid}: {title}")
    db.commit()
    
    # 2. BULK REWRITE (AI) FOR REST OF ISO
    print("Starting AI Bulk Rewrite for Remaining Controls...")
    controls = db.query(Control).filter(Control.framework_id == fw_id).all()
    
    for i, c in enumerate(controls):
        if c.control_id in overrides: continue # Skip overrides
        
        print(f"[{i+1}/{len(controls)}] Processing {c.control_id}...")
        
        # Flush first
        c.ai_explanation = None 
        c.ai_requirements_json = None
        
        # Generate Fresh
        input_text = c.description or c.title
        result = generate_business_text(c.control_id, input_text)
        
        new_title = result.get("business_title")
        new_desc = result.get("business_description")
        
        if new_title and new_desc:
            c.title = new_title
            c.description = new_desc
            print(f"   -> Rewrote: {new_title}")
            db.commit()
            time.sleep(0.5)
        else:
            print("   -> Failed to rewrite.")
            
    print("--- VANTA REWRITE COMPLETE ---")
    db.close()

if __name__ == "__main__":
    apply_vanta_rewrite()
