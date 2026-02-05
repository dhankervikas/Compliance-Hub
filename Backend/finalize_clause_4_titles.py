from app.database import SessionLocal
from app.models.control import Control

def finalize_titles():
    db = SessionLocal()
    print("--- FINALIZING CLAUSE 4 TITLES ---")
    
    updates = {
        "4.1": ("Determine External and Internal Issues", "Determine Context & Stakeholders"),
        "4.2": ("Identify Interested Parties and Requirements", "Identify Interested Parties"),
        "4.3": ("Determine the Scope of the ISMS", "Define Scope of ISMS"),
        "4.4": ("Establish and Maintain ISMS Processes", "Maintain ISMS Processes")
    }
    
    for cid, (title, desc) in updates.items():
        c = db.query(Control).filter(Control.control_id == cid).first()
        if c:
            c.title = title
            c.description = desc
            print(f"Updated {cid}: {title}")
            
    db.commit()
    db.close()

if __name__ == "__main__":
    finalize_titles()
