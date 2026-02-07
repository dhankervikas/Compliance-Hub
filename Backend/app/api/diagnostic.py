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

@router.get("/env-check")
def check_env_vars():
    """
    Diagnostic: Check if critical environment variables are loaded.
    Returns MASKED values for security.
    """
    import os
    
    # List of keys to check
    keys = ["OPENAI_API_KEY", "DATABASE_URL", "SECRET_KEY"]
    results = {}
    
    for k in keys:
        val = os.getenv(k)
        if not val:
            results[k] = "MISSING"
        else:
            # Mask the value (show first 4 chars only)
            masked = f"{val[:4]}...{val[-2:]}" if len(val) > 6 else "***"
            results[k] = f"PRESENT ({masked})"
            
    return {
        "status": "diagnostic",
        "env_vars": results,
        "note": "If OPENAI_API_KEY is MISSING, the app cannot connect to AI."
    }
