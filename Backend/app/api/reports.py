from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User
from report_generator import ComplianceReporter
from app.services.multi_framework_report import MultiFrameworkReportService
import os

router = APIRouter(
    tags=["reports"]
)

@router.get("/unified-controls-evidence")
def get_unified_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates the "Unified Controls Evidence Report".
    Shows how Universal Intents satisfy multiple standards.
    """
    try:
        # Pass the tenant_id from the current_user context
        tenant_id = current_user.tenant_id if hasattr(current_user, 'tenant_id') else "default_tenant"
        
        report_data = MultiFrameworkReportService.generate_unified_report(db, tenant_id)
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
def get_dashboard_metrics():
    reporter = ComplianceReporter()
    try:
        return reporter.get_aggregated_metrics()
    finally:
        reporter.close()

@router.post("/auditor-pack")
def generate_auditor_pack():
    reporter = ComplianceReporter()
    try:
        path, filename = reporter.generate_auditor_pack()
        if os.path.exists(path):
            return FileResponse(path, filename=filename, media_type='application/zip')
        else:
            raise HTTPException(status_code=500, detail="Failed to generate report")
    finally:
        reporter.close()

@router.get("/ai-mapping")
def get_ai_mapping():
    """
    Returns the generated AI -> ISO 42001 Mapping as JSON for UI display.
    """
    import pandas as pd
    try:
        # Path to the static report generated earlier
        report_path = os.path.join(os.getcwd(), "app", "static", "reports", "AI_ISO_42001_Mapping_Report.xlsx")
        
        if not os.path.exists(report_path):
            return {"error": "Report not generated yet", "data": []}
            
        df = pd.read_excel(report_path)
        # Convert NaN to empty string for JSON safety
        df = df.fillna("")
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        print(f"Error reading mapping report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
