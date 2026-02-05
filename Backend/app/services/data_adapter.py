
import os
import json
from enum import Enum
from typing import List, Dict, Optional
from app.database import SessionLocal
from app.models.evidence import Evidence
from app.models.control import Control

class AuditMode(str, Enum):
    SIMULATION = "SIMULATION"
    AWS_LIVE = "AWS_LIVE"
    HYBRID = "HYBRID"

class DataSourceAdapter:
    def __init__(self):
        # self.mode = os.getenv("AUDIT_MODE", AuditMode.SIMULATION)
        self.mode = AuditMode.HYBRID
        self.mock_file = "data/mock_evidence_store.json"
        print(f"[DEBUG] DataSourceAdapter initialized. Mode: {self.mode}")

    def get_all_evidence(self, db: SessionLocal) -> List[Dict]:
        """
        Fetch all evidence based on current audit mode.
        """
        print(f"[DEBUG] get_all_evidence called. Mode: {self.mode}")
        if self.mode == AuditMode.SIMULATION:
            return self._load_mock_data(db)
        else:
            # Fallback to DB if live or hybrid
            return self._load_from_db(db)

    def get_evidence_by_id(self, db: SessionLocal, evidence_id: str) -> Optional[Dict]:
        all_data = self.get_all_evidence(db)
        for item in all_data:
            if item.get("id") == evidence_id:
                return item
        return None

    def update_evidence_status(self, evidence_id: str, status: str, comment: str = None) -> bool:
        """
        Updates evidence status. Persists to JSON in SIMULATION mode.
        """
        if self.mode == AuditMode.SIMULATION:
            return self._update_mock_data(evidence_id, status, comment)
        else:
            # Update DB logic here
            return False

    def _load_mock_data(self, db: SessionLocal) -> List[Dict]:
        if not os.path.exists(self.mock_file):
            return []
            
        # 1. Load Mock Evidence
        with open(self.mock_file, "r") as f:
            data = json.load(f)
            # Filter logic could go here if the mock file has mixed tenants
            evidence_list = data.get("current_evidence", [])
            print(f"[DEBUG] Loaded {len(evidence_list)} items from mock file.")

        # 2. Fetch Live SOA Status from DB
        # db passed in argument
        soa_map = {}
        try:
            from app.models.control import Control
            # This query uses the passed DB session which should have RLS or be filtered
            controls = db.query(Control).all()
            
            # Map control_id -> SOA Details
            soa_map = {c.control_id: {
                "is_applicable": c.is_applicable,
                "justification": c.justification,
                "reason": c.justification_reason
            } for c in controls}
        except Exception as e:
            print(f"Warning: Failed to sync with DB: {e}")
            # No db.close() here, managed by caller

        # 3. Evidence Inheritance Logic (Intent-Based for NIST)
        inheritance_map = {} 
        try:
            from app.models.control_mapping import ControlMapping
            from app.models.control import Control
            
            # Use Control Mapping (Global? or Tenant?)
            # Assuming ControlMapping is consistent or tenant-scoped
            all_mappings = db.query(ControlMapping).all()
            
            # Re-query controls list if needed or reuse
            # Using query again to be safe with session state?
            all_controls_list = db.query(Control).all()
            id_to_code = {c.id: c.control_id for c in all_controls_list}
            
            code_to_details = {c.control_id: {"title": c.title, "description": c.description} for c in all_controls_list}

            for m in all_mappings:
                if m.source_control_id in id_to_code and m.target_control_id in id_to_code:
                    source_code = id_to_code[m.source_control_id]
                    target_code = id_to_code[m.target_control_id]
                    
                    if source_code not in inheritance_map:
                        inheritance_map[source_code] = []
                    inheritance_map[source_code].append(target_code)
        except Exception as e:
            print(f"Warning: Failed to fetch mappings: {e}")

        # 4. Construct Final List (Same logic)
        expanded_evidence = []
        for item in evidence_list:
            cid = item.get("control_id")
            
            # A. Original Item (Apply SOA)
            if cid in soa_map:
                soa_data = soa_map[cid]
                item["is_applicable"] = soa_data["is_applicable"]
                item["justification"] = soa_data["justification"]
                item["justification_reason"] = soa_data["reason"]
                
                if soa_data["is_applicable"] is False:
                     item["status"] = "NOT_APPLICABLE"
                     
            expanded_evidence.append(item)
            
            # B. Inherited Item (Virtual)
            if cid in inheritance_map:
                targets = inheritance_map[cid]
                for target_code in targets:
                    virtual_item = item.copy()
                    virtual_item["control_id"] = target_code
                    virtual_item["original_control_id"] = cid 
                    virtual_item["id"] = f"{item['id']}_INHERITED_{target_code}"
                    virtual_item["source_control"] = cid 
                    
                    if target_code in code_to_details:
                        virtual_item["control_name"] = code_to_details[target_code]["title"]
                        virtual_item["control_description"] = code_to_details[target_code]["description"]

                    if target_code in soa_map:
                         soa_data = soa_map[target_code]
                         virtual_item["is_applicable"] = soa_data["is_applicable"]
                         virtual_item["justification"] = soa_data["justification"]
                         virtual_item["justification_reason"] = soa_data["reason"]
                         
                         if soa_data["is_applicable"] is False:
                             virtual_item["status"] = "NOT_APPLICABLE"
                    
                    expanded_evidence.append(virtual_item)

        # 5. Backfill logic (Same)
        existing_ids = set(e.get("control_id") for e in expanded_evidence)
        import re
        
        # Safe access to code_to_details if step 3 failed? 
        if 'code_to_details' not in locals():
            code_to_details = {}

        for cid, details in code_to_details.items():
            is_iso = re.match(r'^(\d|A\.)', cid)
            
            if not is_iso:
                if cid not in existing_ids:
                    soa_data = soa_map.get(cid, {"is_applicable": True, "justification": None, "reason": None})
                    status = "PENDING"
                    if soa_data["is_applicable"] is False:
                        status = "NOT_APPLICABLE"

                    expanded_evidence.append({
                        "id": f"PLACEHOLDER_{cid}",
                        "control_id": cid,
                        "control_name": details["title"],
                        "control_description": details["description"],
                        "status": status, 
                        "last_updated": "2026-01-01",
                        "auditor_comment": "No automated evidence linked. Manual review required.",
                        "is_applicable": soa_data["is_applicable"],
                        "justification": soa_data["justification"],
                        "justification_reason": soa_data["reason"],
                        "evidence_files": []
                    })

        print(f"[DEBUG] Returning {len(expanded_evidence)} expanded items.")
        return expanded_evidence

    def _update_mock_data(self, evidence_id: str, status: str, comment: str) -> bool:
        # No DB change needed for mock update
        return super()._update_mock_data(evidence_id, status, comment) if hasattr(super(), '_update_mock_data') else self.base_update_mock(evidence_id, status, comment)
        
    def base_update_mock(self, evidence_id: str, status: str, comment: str) -> bool:
         if not os.path.exists(self.mock_file):
            return False
            
         with open(self.mock_file, "r") as f:
            data = json.load(f)
         # ... existing update logic ...
         items = data.get("current_evidence", [])
         updated = False
         real_id = evidence_id.split("_INHERITED_")[0]
         for item in items:
            if item.get("id") == real_id:
                item["status"] = status
                if comment: item["auditor_comment"] = comment
                item["updated_at"] = "NOW"
                updated = True
                break
         if updated:
            with open(self.mock_file, "w") as f:
                json.dump(data, f, indent=2)
         return updated

    def _load_from_db(self, db: SessionLocal) -> List[Dict]:
        """
        Load controls/evidence directly from valid DB based on Audit Mode.
        """
        items = []
        try:
            # We fetch ALL controls. In real multi-tenant, filter by user's tenant.
            # Assuming 'testtest' or similar is the active context.
            controls = db.query(Control).all()
            
            for c in controls:
                # Strip suffix for frontend display (e.g. A.5.1#uuid -> A.5.1)
                display_id = c.control_id.split('#')[0]
                
                # Map Enum status to string
                status_str = c.status.value if hasattr(c.status, 'value') else str(c.status)
                
                # Derive process/badges
                badges = [c.category] if c.category else []
                
                items.append({
                    "id": str(c.id), # Use internal ID for React keys
                    "control_id": display_id,
                    "control_name": c.title,
                    "control_description": c.description,
                    "status": status_str.upper() if status_str else "NOT_STARTED",
                    "badges": badges,
                    "process": c.category,
                    "domain": c.domain,
                    "evidence_files": [], # Populated if we query Evidence table
                    "auditor_comment": "",
                    "updated_at": str(c.updated_at) if c.updated_at else ""
                })
        except Exception as e:
            print(f"Error loading from DB: {e}")
            return []
            
        return items
