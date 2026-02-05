"""
Map ISO 27001 Controls to Business Processes (Domains)
Based on user feedback:
- Governance
- HR security
- Asset Management
- Access Management
- Physical Security
- Operations
- Configuration Management
- Cryptography
- Logging and Monitoring
- Clock Synchronization
- Vulnerability Management
- Capacity Management
- Backup Management
- Network Security
- SDLC
- Supplier Management
- Incident & Resilience
- Threat Intelligence
- Legal & Compliance
- Risk Management
- Performance Evaluation and Improvement
"""

from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import or_

def map_domains():
    db = SessionLocal()
    try:
        # Get ISO Framework
        fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
        if not fw:
            print("ISO 27001 Framework not found!")
            return
            
        controls = db.query(Control).filter(Control.framework_id == fw.id).all()
        print(f"Mapping domains for {len(controls)} controls...")
        
        mapping_updates = 0
        
        for c in controls:
            cid = c.control_id
            title = c.title.lower()
            domain = "Governance" # Default fallback
            
            # --- CLAUSES ---
            if cid.startswith("4.") or cid.startswith("5."):
                domain = "Governance"
            elif cid.startswith("6.") or cid in ["8.2", "8.3"]:
                domain = "Risk Management"
            elif cid.startswith("7."):
                if "competence" in title or "awareness" in title:
                    domain = "HR Security" 
                else: 
                    domain = "Governance" # Resources / Docs
            elif cid.startswith("8.") and cid not in ["8.2", "8.3"]:
                domain = "Operations"
            elif cid.startswith("9."):
                domain = "Performance Evaluation"
            elif cid.startswith("10."):
                domain = "Improvement"
            
            # --- ANNEX A ---
            
            # Threat Intelligence
            if cid == "A.5.7": domain = "Threat Intelligence"
            
            # Identity & Access (A.5.15-18, A.8.2-5) - Prioritize Access Management
            elif cid in ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"]:
                domain = "Access Management"
            
            # Supplier (A.5.19-23)
            elif cid in ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"]:
                domain = "Supplier Management"
                
            # Incident & Resilience (A.5.24-30) - Resilience often includes BCP (A.5.29-30)
            elif cid.startswith("A.5.2") and int(cid.split('.')[2]) >= 24: # A.5.24 - A.5.30
                domain = "Incident & Resilience"
                
            # Legal (A.5.31-36)
            elif cid in ["A.5.31", "A.5.32", "A.5.33", "A.5.34", "A.5.35", "A.5.36", "A.5.37"]:
                 domain = "Legal & Compliance"
            
            # HR Security (A.6)
            elif cid.startswith("A.6."):
                domain = "HR Security"

            # Asset Management (A.5.9-14, A.5.33?, A.8.1?)
            elif cid in ["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13", "A.5.14", "A.8.1", "A.7.10"]:
                domain = "Asset Management"
            
            # Physical (A.7) - Excluding A.7.10 (Assets), A.7.8 (Equip?)
            elif cid.startswith("A.7."):
                domain = "Physical Security"
                
            # Vulnerability (A.8.8)
            elif cid == "A.8.8": domain = "Vulnerability Management"
            
            # Configuration (A.8.9)
            elif cid == "A.8.9": domain = "Configuration Management"
            
            # Backup (A.8.13)
            elif cid == "A.8.13": domain = "Backup Management"
            
            # Logging (A.8.15, A.8.16)
            elif cid in ["A.8.15", "A.8.16"]: domain = "Logging and Monitoring"
            
            # Clock Sync (A.8.17)
            elif cid == "A.8.17": domain = "Clock Synchronization"
            
            # Malware (A.8.7)
            elif cid == "A.8.7": domain = "Operations" # Or specific? User didn't list Malware separatly, "Operations" covers it.
            
            # Network (A.8.20, A.8.21, A.8.22, A.8.23?)
            elif cid in ["A.8.20", "A.8.21", "A.8.22", "A.8.23"]:
                domain = "Network Security"
                
            # Crypto (A.8.24)
            elif cid == "A.8.24": domain = "Cryptography"
            
            # Capacity (A.8.6)
            elif cid == "A.8.6": domain = "Capacity Management"
            
            # SDLC (A.8.25-34)
            elif cid.startswith("A.8.2") and int(cid.split('.')[2]) >= 25: # A.8.25+
                domain = "SDLC"
            elif cid.startswith("A.8.3"): # A.8.30+
                domain = "SDLC"

            # Governance (A.5.1-6, A.5.8) - Remaining A.5
            elif cid.startswith("A.5.") and c.domain == "Governance": # If failed other checks
                 pass
            
            c.domain = domain
            mapping_updates += 1
            
        db.commit()
        print(f"Updated {mapping_updates} controls with Business Process domains.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    map_domains()
