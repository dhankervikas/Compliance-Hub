from sqlalchemy.orm import Session
from app.models.process import Process
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.control import Control
from app.models.framework import Framework

class ProcessService:
    @staticmethod
    def get_processes_with_controls(db: Session, framework_code: str):
        """
        Retrieves processes filtered by framework_code.
        Returns a list of processes with their specific Mapped Controls nested inside.
        Structure: Process -> [Controls]
        """
        # 1. Get Framework ID
        fw = db.query(Framework).filter(Framework.code == framework_code).first()
        if not fw:
            return []
            
        # 2. Get Processes for this Framework (Tagging/Filtering)
        # Logic: Matches Process.framework_code 
        processes = db.query(Process).filter(Process.framework_code == framework_code).all()
        
        result = []
        
        for proc in processes:
            proc_data = {
                "id": proc.id,
                "name": proc.name,
                "description": proc.description,
                "controls": []
            }
            
            # 3. Resolve Controls via Intent
            # Process.name (Category) -> UniversalIntent.category
            # UniversalIntent -> Crosswalk -> Control
            
            # Find ID range of intents for this process category
            # Note: This relies on the 'category' string matching. In a stricter schema, we'd use IDs.
            proc_name_clean = proc.name.strip()
            intents = db.query(UniversalIntent).filter(UniversalIntent.category == proc_name_clean).all()
            intent_ids = [i.id for i in intents]
            
            if intent_ids:
                # Find Crosswalk entries for this framework
                crosswalks = db.query(IntentFrameworkCrosswalk).filter(
                    IntentFrameworkCrosswalk.intent_id.in_(intent_ids),
                    IntentFrameworkCrosswalk.framework_id == framework_code
                ).all()
                
                control_refs = [cw.control_reference for cw in crosswalks]
                
                # Fetch actual Controls
                if control_refs:
                    controls = db.query(Control).filter(
                        Control.framework_id == fw.id,
                        Control.control_id.in_(control_refs)
                    ).all()
                    
                    for c in controls:
                        proc_data["controls"].append({
                            "id": c.id,
                            "control_id": c.control_id,
                            "title": c.title,
                            "description": c.description,
                            "status": c.status,
                            "framework_id": c.framework_id,
                            "assignee": {"name": c.owner_rel.name, "initials": c.owner_rel.initials} if c.owner_rel else None
                        })
            
            result.append(proc_data)
            
        return result
