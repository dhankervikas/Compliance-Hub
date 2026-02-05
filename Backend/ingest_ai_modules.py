import pandas as pd
import os
from app.database import SessionLocal, engine, Base
from app.models.requirement import RequirementMaster, RequirementStatus
from sqlalchemy import text

# Ensure tables exist
Base.metadata.create_all(bind=engine)

ASSET_DIR = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Backend\Assets\AI Framework Modules"

def ingest_modules():
    db = SessionLocal()
    try:
        print("Starting Data Ingestion...")
        
        # 1. Clear existing data (User requested "Delete AI framework related data")
        # We will clear RequirementMaster/Status to ensure fresh ingestion
        print("Clearing old requirement data...")
        db.execute(text("DELETE FROM requirement_status"))
        db.execute(text("DELETE FROM requirement_master"))
        db.commit()

        files = [f for f in os.listdir(ASSET_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]
        
        total_ingested = 0

        for f in files:
            path = os.path.join(ASSET_DIR, f)
            print(f"Processing: {f}")
            
            try:
                df = pd.read_excel(path)
                # Normalize columns: strip spaces, lower case for matching
                df.columns = [c.strip() for c in df.columns]
                
                # Expected columns: 'Domain Name', 'Control ID', 'Control Title', 'Requirements (Shall)'
                # Map to model
                for _, row in df.iterrows():
                    # Handle potential missing values or NaNs
                    if pd.isna(row.get('Requirements (Shall)')):
                        continue

                    dom = str(row.get('Domain Name', '')).strip()
                    cid = str(row.get('Control ID', '')).strip()
                    title = str(row.get('Control Title', '')).strip()
                    req_text = str(row.get('Requirements (Shall)', '')).strip()
                    
                    # Basic Target Control Logic (if present or derived)
                    # For now, we store Control ID as target if not specified
                    target = cid 

                    new_req = RequirementMaster(
                        domain=dom,
                        control_id=cid,
                        control_title=title,
                        requirement_text=req_text,
                        target_control=target,
                        module_source=f # Filename as module source
                    )
                    db.add(new_req)
                    total_ingested += 1
                
                db.commit()
                print(f"  -> Ingested rows from {f}")

            except Exception as e:
                print(f"  !! Error ingesting {f}: {e}")
                db.rollback()

        # Init RequirementStatus for all new requirements (default GAP)
        print("Initializing Status entries...")
        reqs = db.query(RequirementMaster).all()
        for r in reqs:
            status = RequirementStatus(requirement_id=r.id, status="GAP")
            db.add(status)
        db.commit()

        print(f"Ingestion Complete. Total Requirements: {total_ingested}")

    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_modules()
