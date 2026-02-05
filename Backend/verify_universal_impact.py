import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.compliance_result import ComplianceResult
from app.models.control import Control
from app.services.compliance_evaluator import ComplianceEvaluator

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_impact():
    print("[-] Verifying Logic Engine Impact...")
    
    # 1. Pick a Target Intent
    # "Access Control Policy" -> INT-ACCESS-CONTROL-POLICY
    # Mapped to A.5.15, A.5.16 etc. in ISO
    target_intent_id = "INT-ACCESS-CONTROL-POLICY"
    
    intent = db.query(UniversalIntent).filter(UniversalIntent.intent_id == target_intent_id).first()
    if not intent:
        print(f"[FAIL] Intent {target_intent_id} not found.")
        return
        
    print(f"    [+] Found Intent: {intent.intent_id} (Status: {intent.status})")
    
    # 2. Simulate Completion
    print("    [+] Simulating Policy Creation / Completion...")
    intent.status = IntentStatus.COMPLETED
    db.commit()
    
    # 3. Trigger Calculation (Sync)
    print("    [+] Triggering Deduplication Engine...")
    ComplianceEvaluator.calculate_intent_impact_sync(intent.id)
    
    # 4. Verify Downstream Impact
    # Check for ISO A.5.15 (Access Control)
    target_control_ref = "A.5.15"
    print(f"    [?] Checking if Control {target_control_ref} is Satisfied...")
    
    control = db.query(Control).filter(Control.control_id == "ISO_A.5.15").first()
    if not control:
         # Fallback search
         control = db.query(Control).filter(Control.control_id.like(f"%{target_control_ref}")).first()
         
    if control:
        result = db.query(ComplianceResult).filter(
            ComplianceResult.control_id == control.id,
            ComplianceResult.tenant_id == "default_tenant"
        ).first()
        
        if result and result.status == "PASS":
            print(f"    [PASS] Control {control.control_id} is now PASS. (Evidence: {result.evidence_metadata})")
        else:
            print(f"    [FAIL] Control {control.control_id} status is {result.status if result else 'None'}")
    else:
        print(f"    [FAIL] Control {target_control_ref} not found in DB.")

if __name__ == "__main__":
    try:
        verify_impact()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
