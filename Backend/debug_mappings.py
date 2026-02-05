from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.person import Person

db = SessionLocal()
try:
    fw = db.query(Framework).filter(Framework.code.like('%ISO%')).first()
    if not fw:
        print("No ISO Framework found")
    else:
        print(f"Framework: {fw.id} {fw.code}")
        count = db.query(Control).filter(Control.framework_id == fw.id).count()
        mapped = db.query(Control).filter(Control.framework_id == fw.id, Control.process_name != None).count()
        print(f"Control Count: {count}")
        print(f"Mapped Controls: {mapped}")
        
        if mapped == 0 and count > 0:
            print("Attempting to auto-map orphans...")
            controls = db.query(Control).filter(Control.framework_id == fw.id).all()
            for c in controls:
                c.process_name = "Information Security"
                c.sub_process_name = "Governance"
            db.commit()
            print(f"Mapped {len(controls)} controls to 'Information Security' > 'Governance'")
finally:
    db.close()
