from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user
from app.config import settings
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
from app.database import get_db
from app.models import Assessment

router = APIRouter()

# Configure OpenAI - Fixed legacy reference
api_key = settings.OPENAI_API_KEY
print(f"DEBUG: Loading OPENAI_API_KEY from settings. Value: {api_key[:5] if api_key else 'None'}...")


class AssessmentResponse(BaseModel):
    id: int
    control_id: int
    compliance_score: Optional[int]
    gaps: Optional[str]
    recommendations: Optional[str]
    assessed_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/analyze/{control_id}", response_model=AssessmentResponse)
def analyze_control(control_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Trigger Real AI analysis for a control using Gemini.
    """
    from app.services.ai_service import analyze_control_logic
    # Pass current_user implicit or explicit? 
    # analyze_control_logic likely needs to write to DB. 
    # It needs tenant_id. I probably need to update that function.
    assessment = analyze_control_logic(control_id, db, current_user.tenant_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Control not found or analysis failed")
    return assessment

@router.get("/control/{control_id}", response_model=List[AssessmentResponse])
def get_control_assessments(control_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get all assessments for a specific control.
    """
    # Verify control ownership
    # We can just filter assessments by tenant_id as well
    assessments = db.query(Assessment).filter(Assessment.control_id == control_id, Assessment.tenant_id == current_user.tenant_id).order_by(Assessment.assessed_at.desc()).all()
    return assessments
