from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
import sqlalchemy
import re

def fix_iso_mapping_v2():
    db = SessionLocal()
    print("--- FIXING ISO 27001 MAPPING V2 (VERBATIM + INTENT SUMMARIES) ---")
    
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("ISO27001 framework not found.")
        return
        
    fw_id = fw.id

    # 1. FIXED REFERENCE OVERWRITE (Verbatim "Truth" for 4.1-5.2)
    # Directive 1
    verbatim_overrides = {
        "4.1": (
            "Understanding the organization and its context", 
            "The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its information security management system."
        ),
        "4.2": (
            "Understanding the needs and expectations of interested parties", 
            "The organization shall determine interested parties that are relevant to the ISMS and the requirements of these interested parties relevant to information security."
        ),
        "4.3": (
            "Determining the scope of the information security management system",
            "The organization shall determine the boundaries and applicability of the ISMS to establish its scope, considering the issues in 4.1 and requirements in 4.2."
        ),
        "5.2": (
            "Information security policy", 
            "Top management shall establish an information security policy that is appropriate to the purpose of the organization and includes a commitment to satisfy applicable requirements."
        )
    }

    # 2. INTENT SUMMARIES (Directive 4)
    # High-fidelity summaries for 6.x+
    intent_summaries = {
        "6.1.1": (
            "General Risk Actions",
            "Establish a systematic planning process to identify risks and opportunities that ensure the ISMS can achieve its intended outcomes and prevent undesired effects."
        ),
        "6.1.2": (
            "Risk Assessment",
            "Define and apply a repeatable information security risk assessment process that establishes criteria for identifying, analyzing, and evaluating risks to the confidentiality, integrity, and availability of information."
        ),
        "6.1.3": (
            "Risk Treatment",
            "Define a process to select appropriate risk treatment options and determine all controls necessary to implement the chosen treatment, documenting these in a Statement of Applicability."
        ),
        "6.2": (
            "Security Objectives",
            "Establish measurable information security objectives at relevant functions and levels that are consistent with the security policy and aligned with business risks."
        )
    }
    
    # Merge for processing
    all_overrides = {**verbatim_overrides, **intent_summaries}

    # Process Overrides
    print("Applying Fixed Overrides...")
    for cid, (title, desc) in all_overrides.items():
        sql = sqlalchemy.text("UPDATE controls SET title=:title, description=:desc, updated_at=CURRENT_TIMESTAMP WHERE control_id=:cid AND framework_id=:fw_id")
        result = db.execute(sql, {"title": title, "desc": desc, "cid": cid, "fw_id": fw_id})
        print(f" -> Set {cid}: '{title}'")

    # 3. GLOBAL CLEANUP (Clauses 4-10)
    # Strip ID from Title if present (e.g. "9.1 Monitoring" -> "Monitoring")
    # Only applies if NOT in overrides (overrides are already clean)
    print("Applying Global Title Cleanup (Stripping IDs)...")
    
    controls = db.query(Control).filter(Control.framework_id == fw_id).all()
    
    # Regex to match starting ID like "6.1.2 " or "A.5.1 "
    id_pattern = re.compile(r'^([A-Z0-9\.]+)\s+(.*)')

    count = 0
    for c in controls:
        if c.control_id in all_overrides:
            continue
            
        # Check if title starts with the ID
        match = id_pattern.match(c.title)
        if match:
             # If the extracted ID matches the control_id (loosely), strip it
             # OR just strip any leading ID-like string
             clean_title = match.group(2)
             
             # Safety check: Don't accidentally strip real words. 
             # IDs usually contain numbers or dots.
             prefix = match.group(1)
             if any(char.isdigit() for char in prefix) or '.' in prefix:
                 c.title = clean_title
                 count += 1
                 # print(f"    Cleaned {c.control_id}: '{match.group(0)}' -> '{clean_title}'")
    
    if count > 0:
        db.commit()
        print(f" -> Cleaned {count} titles.")
    else:
        print(" -> No additional titles needed cleaning.")

    db.commit()
    print("--- ISO 27001 MAPPING V2 COMPLETE ---")
    db.close()

if __name__ == "__main__":
    fix_iso_mapping_v2()
