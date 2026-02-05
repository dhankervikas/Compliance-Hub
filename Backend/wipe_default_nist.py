
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework

def wipe_default_nist():
    db = SessionLocal()
    print("--- WIPING DEFAULT TENANT NIST CONTROLS ---")
    
    # 1. Resolve Framework
    fw = db.query(Framework).filter(Framework.code == "NIST-CSF").first()
    if not fw:
        fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
        
    if not fw:
        print("Framework NIST CSF 2.0 not found.")
        return
        
    print(f"Target Framework: {fw.name} (ID: {fw.id})")
    
    # 2. Delete controls for 'default_tenant'
    deleted = db.query(Control).filter(
        Control.framework_id == fw.id,
        Control.tenant_id == "default_tenant"
    ).delete()
    
    print(f"Deleted {deleted} controls from 'default_tenant'.")
    db.commit()
    db.close()

if __name__ == "__main__":
    wipe_default_nist()
