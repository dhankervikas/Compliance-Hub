from app.database import SessionLocal
from app.models.control import Control

def swap_data():
    db = SessionLocal()
    print("--- SWAPPING TITLE/DESCRIPTION FOR CLAUSE 4 ---")
    
    # Map: ID -> (Title=Intent, Desc=StandardName)
    updates = {
        "4.1": ("Determine internal and external issues relevant to the ISMS", "Determine Context & Stakeholders"),
        "4.2": ("Identify interested parties and their requirements relevant to information security", "Identify Interested Parties"),
        "4.3": ("Define and document the scope of the ISMS", "Define Scope of ISMS"),
        "4.4": ("Establish, implement, maintain, and continually improve the ISMS", "Maintain ISMS Processes"),
        
        # Clause 5
        "5.1": ("Demonstrate leadership and commitment with respect to the ISMS", "Leadership & Commitment"),
        "5.2": ("Establish the information security policy", "Information Security Policy"),
        "5.3": ("Ensure responsibilities and authorities are assigned and communicated", "Roles, Responsibilities & Authorities"),
        
        # Clause 6
        "6.1": ("Address risks and opportunities", "Actions to Address Risks"),
        "6.2": ("Establish information security objectives and plans to achieve them", "Information Security Objectives"),
        "6.3": ("Plan changes to the ISMS", "Planning of Changes"),  
        
        # Clause 7
        "7.1": ("Provide resources needed for the ISMS", "Resources"),
        "7.2": ("Ensure competence of persons doing work under control", "Competence"),
        "7.3": ("Ensure awareness of information security policy", "Awareness"),
        "7.4": ("Determine internal and external communications", "Communication"),
        "7.5": ("Create, update and control documented information", "Documented Information"),
        
        # Clause 8
        "8.1": ("Plan, implement and control processes needed", "Operational Planning & Control"),
        "8.2": ("Perform information security risk assessments", "Information Security Risk Assessment"),
        "8.3": ("Implement the information security risk treatment plan", "Information Security Risk Treatment"),
        
        # Clause 9
        "9.1": ("Monitor, measure, analyze and evaluate the ISMS", "Monitoring, Measurement, Analysis & Evaluation"),
        "9.2": ("Conduct internal audits at planned intervals", "Internal Audit"),
        "9.3": ("Review the ISMS at planned intervals", "Management Review"),
        
        # Clause 10
        "10.1": ("React to nonconformities and take action", "Nonconformity & Corrective Action"),
        "10.2": ("Continually improve the suitability, adequacy and effectiveness of the ISMS", "Continual Improvement"),
    }
    
    for cid, (new_title, new_desc) in updates.items():
        c = db.query(Control).filter(Control.control_id == cid).first()
        if c:
            print(f"Updating {cid}...")
            c.title = new_title
            c.description = new_desc
            # Ensure actionable_title (if API logic uses it logic side, though DB doesn't have col)
            # The API uses c.title if no match in ACTIONABLE_TITLES.
            # And I verified 4.1 etc are NOT in ACTIONABLE_TITLES list.
        else:
            print(f"Control {cid} NOT FOUND.")
            
    db.commit()
    print("--- SWAP COMPLETE ---")
    db.close()

if __name__ == "__main__":
    swap_data()
