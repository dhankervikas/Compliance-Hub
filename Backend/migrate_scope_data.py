from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.settings import ComplianceSettings
from app.models.scope_justification import ScopeJustification
from app.models.tenant import Tenant
import json

def migrate_scope_data():
    db = SessionLocal()
    try:
        # 1. Get all ComplianceSettings for 'scope'
        settings_list = db.query(ComplianceSettings).filter(ComplianceSettings.section_key == "scope").all()
        
        migrated_count = 0
        
        for settings in settings_list:
            content = settings.content
            tenant_id_key = settings.tenant_id
            
            # Resolve Tenant UUID if needed (though settings usually store the internal ID or slug depending on impl)
            # Assuming settings.tenant_id IS the UUID or at least the consistent FK.
            # But let's verify if tenant exists to be safe
            
            if not content:
                continue
                
            soc2_exclusions = content.get("soc2_exclusions", {})
            
            if not soc2_exclusions:
                continue
                
            print(f"Migrating {len(soc2_exclusions)} exclusions for tenant {tenant_id_key}...")
            
            for criteria_id, justification in soc2_exclusions.items():
                # Check if already exists
                exists = db.query(ScopeJustification).filter(
                    ScopeJustification.tenant_id == tenant_id_key,
                    ScopeJustification.standard_type == "SOC2",
                    ScopeJustification.criteria_id == criteria_id
                ).first()
                
                if not exists:
                    new_record = ScopeJustification(
                        tenant_id=tenant_id_key,
                        standard_type="SOC2",
                        criteria_id=criteria_id,
                        reason_code="NOT_APPLICABLE", # Defaulting to N/A as per old logic
                        justification_text=justification
                    )
                    db.add(new_record)
                    migrated_count += 1
            
        db.commit()
        print(f"Migration Complete. {migrated_count} records created.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist first
    from app.models.scope_justification import ScopeJustification
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    
    migrate_scope_data()
