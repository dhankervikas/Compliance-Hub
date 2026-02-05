from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel
from typing import List, Optional
from app.services.ai_service import suggest_evidence, analyze_gap 

router = APIRouter()

class EvidenceSuggestionRequest(BaseModel):
    title: str
    description: str
    category: str
    control_id: Optional[str] = None # Changed to str to support "A.8.12"
    regenerate: Optional[bool] = False # Force regeneration

class JustificationRequest(BaseModel):
    control_id: str
    title: str
    category: str
    scope_description: Optional[str] = "Standard ISO 27001 Scope"

# ...

@router.post("/suggest-evidence")
def suggest_evidence_endpoint(req: EvidenceSuggestionRequest, db: Session = Depends(get_db)):
    return suggest_evidence(req.title, req.description, req.category, req.control_id, db, req.regenerate)

class GapAnalysisRequest(BaseModel):
    control_title: str
    requirements: List[dict] # [{name, type}]
    uploaded_files: List[str] # List of filenames

class ArtifactGenerationRequest(BaseModel):
    control_title: str
    artifact_name: str
    context: str

class DocumentReviewRequest(BaseModel):
    control_id: int
    evidence_id: int

@router.post("/gap-analysis")
def gap_analysis_endpoint(req: GapAnalysisRequest):
    return analyze_gap(req.control_title, req.requirements, req.uploaded_files)

@router.post("/generate-artifact")
def generate_artifact_endpoint(req: ArtifactGenerationRequest):
    from app.services.ai_service import generate_artifact_content
    content = generate_artifact_content(req.control_title, req.artifact_name, req.context)
    return {"content": content}

@router.post("/review-document")
def review_document_endpoint(req: DocumentReviewRequest, db: Session = Depends(get_db)):
    from app.services.ai_service import review_document
    return review_document(req.control_id, req.evidence_id, db)

@router.post("/suggest-justification")
def suggest_justification_endpoint(req: JustificationRequest):
    from app.services.ai_service import suggest_justification
    return suggest_justification(req.title, req.control_id, req.category, req.scope_description)

class PolicyRequest(BaseModel):
    title: str
    description: str

@router.post("/generate-policy")
def generate_policy_endpoint(req: PolicyRequest):
    from app.services.ai_policy_service import PolicyGenerationService
    service = PolicyGenerationService()
    # Use the comprehensive generation
    result = service.generate_policy(policy_name=req.title, company_name="AssuRisk") 
    # Note: result contains { content, metadata, etc. }
    # We return just content to match frontend expectation for now, or full object?
    # Frontend expects "response.data.choices[0].message.content" in the old code.
    # The new frontend service will need to adapt to return result.content.
    return {"content": result["content"]}
