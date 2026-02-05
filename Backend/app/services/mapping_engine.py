from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.requirement import RequirementMaster, RequirementStatus
from app.models.policy import Policy
from sqlalchemy import or_
import datetime

class MappingEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_global_scan(self):
        print("Starting Global Mapping Scan...")
        
        # 1. Fetch all requirements (Status entries)
        req_statuses = self.db.query(RequirementStatus).all()
        
        # 2. Fetch all Policies
        policies = self.db.query(Policy).all()
        
        updated_count = 0
        
        for status_entry in req_statuses:
            req = status_entry.requirement
            
            # Reset status first (Conservative approach)
            # status_entry.status = "GAP" 
            # status_entry.mapped_policy_id = None
            # status_entry.mapped_section = None
            
            mapped = False
            
            # 3. Simple Keyword Matching / Heuristic
            # Logic: If Policy Content contains the "Control ID" or key phrases from Requirement
            # Improvement: Use vector embeddings in future (pgvector/Pinecone)
            
            keywords = [req.control_id, req.control_title]
            
            # Clean keywords
            keywords = [k for k in keywords if k and len(k) > 3]

            for policy in policies:
                content = (policy.content or "").lower()
                name = (policy.name or "").lower()
                
                # Check for direct ID match (Strong signal)
                if req.control_id.lower() in content:
                    self._map_requirement(status_entry, policy, "Content Match (ID)")
                    mapped = True
                    break
                
                # Check for Title match in Policy Name (Strong signal)
                if req.control_title.lower() in name:
                     self._map_requirement(status_entry, policy, "Policy Name Match")
                     mapped = True
                     break
                     
                # Check for "Mapped Controls" metadata in Policy (if user manually linked)
                # Assumes policy.mapped_controls is JSON list of IDs
                if policy.mapped_controls and req.control_id in policy.mapped_controls:
                     self._map_requirement(status_entry, policy, "Explicit Metadata Link")
                     mapped = True
                     break

            if mapped:
                updated_count += 1
        
        self.db.commit()
        print(f"Mapping Complete. Updated {updated_count} requirements to MET.")

    def _map_requirement(self, status_entry, policy, reason):
        status_entry.status = "MET"
        status_entry.mapped_policy_id = policy.id
        status_entry.mapped_section = f"Mapped via {reason}"
        status_entry.last_verified = datetime.datetime.utcnow()
        status_entry.verification_metadata = {
            "mapped_by": "Global Scanner",
            "reason": reason,
            "policy_version": policy.version
        }

if __name__ == "__main__":
    db = SessionLocal()
    engine = MappingEngine(db)
    engine.run_global_scan()
    db.close()
