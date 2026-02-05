from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.framework import Framework
from app.models.control import Control

router = APIRouter()

@router.get("/db-stats")
def get_db_stats(db: Session = Depends(get_db)):
    frameworks = db.query(Framework).all()
    stats = []
    total_controls = 0
    
    for fw in frameworks:
        count = db.query(Control).filter(Control.framework_id == fw.id).count()
        total_controls += count
        stats.append({
            "id": fw.id,
            "code": fw.code,
            "name": fw.name,
            "control_count": count
        })
        
    return {
        "total_controls": total_controls,
        "frameworks": stats,
        "message": "Please share this JSON with the support team."
    }
