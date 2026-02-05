
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.process import Process, SubProcess
from sqlalchemy import func

def check_process_data():
    db = SessionLocal()
    try:
        frameworks = db.query(Framework).all()
        for fw in frameworks:
            print(f"\n--- Framework: {fw.name} ({fw.code}) ---")
            
            # Count controls with mapped processes
            # Join Control -> SubProcess -> Process
            controls_with_process = db.query(Control).join(Control.sub_processes).filter(
                Control.framework_id == fw.id
            ).distinct().count()
            
            total_controls = db.query(Control).filter(Control.framework_id == fw.id).count()
            
            print(f"Total Controls: {total_controls}")
            print(f"Controls with Process: {controls_with_process} ({(controls_with_process/total_controls*100) if total_controls else 0:.1f}%)")
            
            # List top processes by control count
            if controls_with_process > 0:
                top_processes = db.query(
                    Process.name, func.count(Control.id)
                ).join(SubProcess, Process.id == SubProcess.process_id)\
                 .join(Control, Control.sub_processes)\
                 .filter(Control.framework_id == fw.id)\
                 .group_by(Process.name)\
                 .order_by(func.count(Control.id).desc())\
                 .limit(10).all()
                
                print("Top Processes:")
                for p, c in top_processes:
                    print(f"  - {p}: {c}")
            else:
                print("  (No processes mapped)")

    finally:
        db.close()

if __name__ == "__main__":
    check_process_data()
