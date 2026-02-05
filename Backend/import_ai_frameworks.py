
import pandas as pd
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.framework import Framework
from app.models.control import Control

# Config
FRAMEWORK_NAME = "AI Frameworks"
FRAMEWORK_CODE = "AI_FRAMEWORK"
FRAMEWORK_DESC = "Unified AI Management, Governance, Privacy, and CyberSecurity Framework."

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES = {
    "AI Management": os.path.join(BASE_DIR, "data", "AI_Management_Module.xlsx"),
    "AI Governance": os.path.join(BASE_DIR, "data", "AI_Governance_Module.xlsx"),
    "AI Privacy": os.path.join(BASE_DIR, "data", "AI_Privacy_Module.xlsx"),
    "AI CyberSecurity": os.path.join(BASE_DIR, "data", "AI_CyberSecurity_Module.xlsx")
}

def import_ai_frameworks():
    db = SessionLocal()
    try:
        # 1. Create or Get Framework
        fw = db.query(Framework).filter(Framework.code == FRAMEWORK_CODE).first()
        if not fw:
            print(f"Creating Framework: {FRAMEWORK_NAME}")
            fw = Framework(
                name=FRAMEWORK_NAME, 
                code=FRAMEWORK_CODE, 
                description=FRAMEWORK_DESC,
                version="1.0"
            )
            db.add(fw)
            db.commit()
            db.refresh(fw)
        else:
            print(f"Framework {FRAMEWORK_NAME} already exists.")

        # 2. Process Files
        for module_name, file_path in FILES.items():
            if not os.path.exists(file_path):
                print(f"Skipping missing file: {file_path}")
                print(f"  -> Absolute path checked: {os.path.abspath(file_path)}")
                continue
                
            print(f"Processing Module: {module_name} from {file_path}...")
            
            try:
                df = pd.read_excel(file_path, sheet_name="Scoring Matrix")
                
                # Normalize Columns
                # Expected aliases
                def get_val(row, aliases, default=''):
                    for alias in aliases:
                        if alias in row and not pd.isna(row[alias]):
                            return row[alias]
                    return default

                # Define Prefixes
                PREFIX_MAP = {
                    "AI Management": "M",
                    "AI Governance": "G",
                    "AI Privacy": "P",
                    "AI CyberSecurity": "C"
                }
                
                count = 0
                for index, row in df.iterrows():
                    raw_cid = str(get_val(row, ['Clause / Control No.', 'Clause No.', 'Control ID', 'Control_ID'])).strip()
                    if not raw_cid or raw_cid == 'nan' or raw_cid == '':
                        continue
                        
                    # Generate Unique AI ID
                    prefix = PREFIX_MAP.get(module_name, "X")
                    cid = f"AI-{prefix}-{raw_cid}"
                        
                    # Title & Desc
                    title = get_val(row, ['Control Description', 'Clause Description', 'Title'], 'Untitled Control')
                    desc = get_val(row, ['Requirements (Shall)', 'Requirements Summary', 'Description', 'Governance & Risk Requirements'], '')
                    domain = get_val(row, ['Domain Name', 'Domain'], module_name) # Default to Module Name if missing
                    procedure = get_val(row, ['Testing Procedure', 'Test Procedure', 'Procedures'], '')
                    
                    # Check if exists (Using Unique AI ID)
                    existing = db.query(Control).filter(Control.control_id == cid).first()
                    
                    if existing:
                        # Update fields
                        existing.title = title
                        existing.description = desc
                        existing.domain = domain
                        existing.category = module_name
                        existing.framework_id = fw.id
                        existing.implementation_notes = procedure
                    else:
                        new_ctrl = Control(
                            control_id=cid,
                            title=title,
                            description=desc,
                            framework_id=fw.id,
                            domain=domain,
                            category=module_name, 
                            implementation_notes=procedure,
                            status="not_started"
                        )
                        db.add(new_ctrl)
                    
                    count += 1
                
                db.commit()
                print(f"  -> Imported {count} controls for {module_name}")
                
            except Exception as e:
                print(f"  -> Error processing {module_name}: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    import_ai_frameworks()
