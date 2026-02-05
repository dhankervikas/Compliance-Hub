from sqlalchemy.orm import Session
from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.control import Control
from app.models.compliance_result import ComplianceResult

class MultiFrameworkReportService:
    """
    Generates the "Unified Controls Evidence Report".
    Pivots data by Universal Intent to show the "One-to-Many" benefits.
    """
    
    @staticmethod
    def generate_unified_report(db: Session, tenant_id: str):
        # 1. Fetch All Universal Intents
        intents = db.query(UniversalIntent).all()
        
        report_data = {
            "summary": {
                "total_intents": len(intents),
                "completed_intents": len([i for i in intents if i.status == IntentStatus.COMPLETED]),
                "standards_covered": set() # Will populate below
            },
            "intents": []
        }
        
        for intent in intents:
            # Get Crosswalks
            mappings = db.query(IntentFrameworkCrosswalk).filter(
                IntentFrameworkCrosswalk.intent_id == intent.id
            ).all()
            
            # Group by Framework
            impact_map = {}
            for m in mappings:
                if m.framework_id not in impact_map:
                    impact_map[m.framework_id] = []
                    report_data["summary"]["standards_covered"].add(m.framework_id)
                impact_map[m.framework_id].append(m.control_reference)
            
            # Format Intent Entry
            entry = {
                "intent_id": intent.intent_id,
                "description": intent.description,
                "category": intent.category,
                "status": intent.status.value,
                "impact": impact_map, # e.g. {"ISO_27001": ["A.5.15"], "SOC2": ["CC6.1"]}
                "impact_count": sum(len(v) for v in impact_map.values())
            }
            report_data["intents"].append(entry)
            
        # Convert set to list for JSON serialization
        report_data["summary"]["standards_covered"] = list(report_data["summary"]["standards_covered"])
            
        return report_data
