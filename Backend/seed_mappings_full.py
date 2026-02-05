from app.database import SessionLocal
from app.models.control import Control
from app.models.process import Process, SubProcess
from sqlalchemy import or_

def seed_full_mappings():
    db = SessionLocal()
    try:
        print("Starting Full Mapping Seed...")
        
        # 1. Get Framework 1 (ISO 27001)
        fw_id = 1
        
        # 2. Get All ISO 27001 Controls
        controls = db.query(Control).filter(Control.framework_id == fw_id).all()
        print(f"Found {len(controls)} ISO 27001 controls.")
        
        if not controls:
            print("No controls found! Aborting.")
            return

        # 3. Define Logic to Map Annex A sections to Processes
        # Process Mapping Rules (Heuristic)
        # A.5 -> Governance & Assets (Split)
        # A.6 -> Governance (Internal Org)
        # A.7 -> Physical
        # A.8 -> Security Operations & Engineering (New 2022 structure mixes them)
        # 5, 6, 7 (Clauses) -> Governance
        # 8 (Operation) -> Ops
        # 9, 10 -> Audit/Improvement
        
        # Helper to find subprocess by partial name
        def get_sp(name_part):
            return db.query(SubProcess).filter(SubProcess.name.ilike(f"%{name_part}%")).first()

        # Map targets
        target_map = {
            "5.": get_sp("Policy"), # 5. Leadership -> Policy & Standards
            "6.": get_sp("Risk Assessment"), # 6. Planning -> Risk
            "7.": get_sp("Competence"), # 7. Support -> Resource/Competence (Assume exists or fallback)
            "8.": get_sp("Operational"), # 8. Operation -> needed? Clause 8 is usually Ops
            "9.": get_sp("Audit"), # 9. Performance -> Internal Audit
            "10.": get_sp("Improvement"), # 10. Improvement -> Post-incident or Audit
            
            # Annex A (2022)
            "A.5.": get_sp("Policy"), # Organizational -> Governance/Policy
            "A.6.": get_sp("Human"), # People -> HR (if exists) or "Identity"
            "A.7.": get_sp("Physical"), # Physical -> Physical
            "A.8.": get_sp("Security Monitoring"), # Technological -> Ops
        }
        
        # Refine Targets if 2013 version (A.5-A.18)
        # But DB check showed A.7.8 (2022 uses A.5-A.8 domains).
        # A.7.8 in 2022 is "Equipment siting and protection" -> Physical
        
        # Let's use broader buckets ensuring EVERY control lands SOMEWHERE.
        
        sp_governance = get_sp("Policy") or get_sp("Governance")
        sp_risk = get_sp("Risk")
        sp_identity = get_sp("Access Management")
        sp_ops = get_sp("Security Monitoring") or get_sp("Vulnerability")
        sp_physical = get_sp("Physical")
        sp_dev = get_sp("Secure Development")
        sp_supplier = get_sp("Supplier")
        sp_incident = get_sp("Incident")
        
        count = 0
        for c in controls:
            cid = c.control_id
            target_sp = sp_governance # Default
            
            if cid.startswith("A.5"): target_sp = sp_governance # Organizational
            elif cid.startswith("A.6"): target_sp = sp_identity # People
            elif cid.startswith("A.7"): target_sp = sp_physical # Physical
            elif cid.startswith("A.8"): target_sp = sp_ops # Technological
            
            # Refine A.8 Technological (it's huge)
            if cid.startswith("A.8.25"): target_sp = sp_dev # SDLC
            if cid.startswith("A.8.30"): target_sp = sp_dev # Test data
            if cid.startswith("A.8.20"): target_sp = sp_ops # Networks
            if cid.startswith("A.8.24"): target_sp = sp_dev # Crypto
            
            # Clauses
            if cid.startswith("4."): target_sp = sp_governance
            if cid.startswith("5."): target_sp = sp_governance
            if cid.startswith("6."): target_sp = sp_risk
            if cid.startswith("7."): target_sp = sp_governance
            if cid.startswith("8."): target_sp = sp_ops
            if cid.startswith("9."): target_sp = get_sp("Audit")
            if cid.startswith("10."): target_sp = get_sp("Incident")

            if target_sp:
                if c not in target_sp.controls:
                    target_sp.controls.append(c)
                    count += 1
        
        db.commit()
        print(f"Successfully mapped {count} controls to processes.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_full_mappings()
