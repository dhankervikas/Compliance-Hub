import os
import glob
import mammoth
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.master_template import MasterTemplate

# Path to the immutable templates
TEMPLATE_DIR = os.path.join(os.getcwd(), "src", "assets", "templates", "master")

def extract_control_id(filename):
    """
    Tries to extract 'A.5.15' or similar from filename.
    Example: 'ISO27001_A.5.15_Access_Control.docx' -> 'A.5.15'
    """
    # Simple heuristic: split by underscore, look for pattern "A.X.X" or "CCX.X"
    parts = filename.split('_')
    for i, p in enumerate(parts):
        # A.X.X or CCX.X
        if ('A.' in p or 'CC' in p) and any(c.isdigit() for c in p):
            return p
        # Clause X.X (e.g., Clause_4.1)
        if p.lower() == "clause" and i + 1 < len(parts):
            val = parts[i+1]
            if any(c.isdigit() for c in val):
                return val
    return None

def seed_templates():
    print(f"Scanning for templates in: {TEMPLATE_DIR}")
    docx_files = glob.glob(os.path.join(TEMPLATE_DIR, "*.docx"))
    
    if not docx_files:
        print("[WARNING] No .docx files found in template directory.")
        return

    db: Session = SessionLocal()
    count = 0 
    
    for file_path in docx_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        try:
            with open(file_path, "rb") as docx_file:
                # Convert to HTML (mammoth default)
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value
                messages = result.messages
                
                # Check messages for warnings
                for msg in messages:
                    print(f"  - Mammoth Warning: {msg}")

                # Find existing or create new
                existing = db.query(MasterTemplate).filter(MasterTemplate.original_filename == filename).first()
                if existing:
                    print(f"  - Updating existing template: {filename}")
                    existing.content = html_content
                    existing.title = filename.replace(".docx", "").replace("_"," ")
                    # existing.control_id = extract_control_id(filename) # Optional: update control ID logic
                else:
                    print(f"  - Creating new template: {filename}")
                    new_template = MasterTemplate(
                        title=filename.replace(".docx", "").replace("_"," "),
                        content=html_content,
                        original_filename=filename,
                        control_id=extract_control_id(filename),
                        is_immutable=True
                    )
                    db.add(new_template)
                
                count += 1

        except Exception as e:
            print(f"  [ERROR] Failed to process {filename}: {e}")
    
    db.commit()
    print(f"Seed Complete. Processed {count} templates.")

if __name__ == "__main__":
    seed_templates()
