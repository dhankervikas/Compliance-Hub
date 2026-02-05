from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.mapping_engine import MappingEngine
from app.services.report_generator_v2 import ReportGeneratorV2
from app.models.requirement import RequirementMaster, RequirementStatus
import os

router = APIRouter(
    tags=["AI Compliance"]
)

@router.post("/scan")
def trigger_compliance_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    engine = MappingEngine(db)
    # Run in background to avoid timeout
    background_tasks.add_task(engine.run_global_scan)
    return {"message": "Compliance Scan initiated in background."}

@router.get("/stats")
def get_compliance_stats(db: Session = Depends(get_db)):
    # Calculate real-time stats (similar to report generator logic)
    query = db.query(RequirementMaster, RequirementStatus).\
        outerjoin(RequirementStatus, RequirementMaster.id == RequirementStatus.requirement_id).all()
        
    module_stats = {}
    
    for req, status in query:
        mod = req.module_source.replace(".xlsx", "").replace("_", " ") # Clean name
        st_val = status.status if status else "GAP"
        
        if mod not in module_stats:
            module_stats[mod] = {"total": 0, "met": 0}
        
        module_stats[mod]["total"] += 1
        if st_val == "MET":
            module_stats[mod]["met"] += 1
            
    # Format for frontend
    results = []
    for mod, stats in module_stats.items():
        score = (stats["met"] / stats["total"] * 100) if stats["total"] > 0 else 0
        results.append({
            "module": mod,
            "met": stats["met"],
            "total": stats["total"],
            "score": round(score, 1)
        })
        
    return results

@router.get("/report/pdf")
def download_pdf_report(db: Session = Depends(get_db)):
    gen = ReportGeneratorV2(db)
    output = gen.generate_compliance_report(workspace_id=1) # ID ignored for now
    
    path = output["pdf"]
    if os.path.exists(path):
        return FileResponse(path, filename="AI_Compliance_Report.pdf", media_type="application/pdf")
    return {"error": "Report generation failed"}
