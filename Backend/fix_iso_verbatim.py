from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
import sqlalchemy

def fix_iso_27001_mapping():
    db = SessionLocal()
    print("--- FIXING ISO 27001 MAPPING TO VERBATIM STANDARD ---")
    
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("ISO27001 framework not found.")
        return
        
    fw_id = fw.id

    # Master Truth Dictionary
    # Title: Verbatim Standard Title
    # Description: Verbatim Standard Requirement (Shall statement)
    corrections = {
        "4.1": (
            "Understanding the organization and its context", 
            "The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its information security management system."
        ),
        "4.2": (
            "Understanding the needs and expectations of interested parties", 
            "The organization shall determine: a) interested parties that are relevant to the information security management system; b) the relevant requirements of these interested parties; c) which of these requirements will be addressed through the information security management system."
        ),
        "4.3": (
            "Determining the scope of the information security management system",
            "The organization shall determine the boundaries and applicability of the information security management system to establish its scope."
        ),
        "5.1": (
            "Leadership and commitment",
            "Top management shall demonstrate leadership and commitment with respect to the information security management system."
        ),
        "5.2": (
            "Information security policy", 
            "Top management shall establish, implement and maintain an information security policy that: a) is appropriate to the purpose of the organization; b) includes information security objectives or provides the framework for setting information security objectives; c) includes a commitment to satisfy applicable requirements related to information security; d) includes a commitment to continual improvement of the information security management system."
        ),
        "6.1.1": (
            "General",
            "When planning for the information security management system, the organization shall consider the issues referred to in 4.1 and the requirements referred to in 4.2 and determine the risks and opportunities that need to be addressed."
        )
    }

    for cid, (title, desc) in corrections.items():
        # Using bind parameters for safety, though these are hardcoded strings
        sql = sqlalchemy.text("UPDATE controls SET title=:title, description=:desc, updated_at=CURRENT_TIMESTAMP WHERE control_id=:cid AND framework_id=:fw_id")
        result = db.execute(sql, {"title": title, "desc": desc, "cid": cid, "fw_id": fw_id})
        print(f" -> Updated {cid}: '{title}'")
    
    db.commit()
    print("--- ISO 27001 MAPPING FIXED ---")
    db.close()

if __name__ == "__main__":
    fix_iso_27001_mapping()
