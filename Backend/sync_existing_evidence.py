from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.evidence import Evidence
from app.models.control import Control
import os
import re

def retroactive_sync():
    db = SessionLocal()
    try:
        print("Starting Retroactive Evidence Sync...")
        
        # 1. Fetch all evidence
        all_evidence = db.query(Evidence).all()
        print(f"Found {len(all_evidence)} total evidence items.")
        
        synced_count = 0
        
        for ev in all_evidence:
            # Get parent control
            control = db.query(Control).get(ev.control_id)
            if not control or not control.implementation_notes:
                continue
                
            # Check for LINK_ID
            match = re.search(r"LINK_ID:\s*([A-Za-z0-9_]+)", control.implementation_notes)
            if match:
                link_key = match.group(1)
                
                # Find peers
                linked_controls = db.query(Control).filter(
                    Control.implementation_notes.like(f"%LINK_ID: {link_key}%"),
                    Control.id != control.id
                ).all()
                
                for peer in linked_controls:
                    # Check if already exists in peer
                    exists = db.query(Evidence).filter(
                        Evidence.control_id == peer.id,
                        Evidence.file_path == ev.file_path # Same physical file
                    ).first()
                    
                    if not exists:
                        new_ev = Evidence(
                            filename=ev.filename,
                            file_path=ev.file_path,
                            file_size=ev.file_size,
                            file_type=ev.file_type,
                            title=ev.title,
                            description=f"Synced from Control {control.control_id} ({control.title})",
                            control_id=peer.id,
                            status=ev.status,
                            validation_source=ev.validation_source,
                            uploaded_by="retro_sync"
                        )
                        db.add(new_ev)
                        synced_count += 1
                        print(f"  + Synced '{ev.filename}' from {control.control_id} -> {peer.control_id}")
        
        db.commit()
        print(f"\n[Success] Retroactively synced {synced_count} evidence items.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    retroactive_sync()
