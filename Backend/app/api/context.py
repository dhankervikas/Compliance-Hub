from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.context import ContextIssue, InterestedParty, ScopeDocument

router = APIRouter(tags=["Context (Clause 4)"])

# --- Pydantic Models ---
class IssueCreate(BaseModel):
    name: str
    category: str
    pestle_category: str
    description: Optional[str] = None
    impact: str
    treatment: str

class IssueResponse(IssueCreate):
    id: int
    class Config:
        from_attributes = True

class PartyCreate(BaseModel):
    stakeholder: str
    needs: str
    requirements: str
    compliance_mapping: Optional[str] = None

class PartyResponse(PartyCreate):
    id: int
    class Config:
        from_attributes = True

class ScopeUpdate(BaseModel):
    content: str
    boundaries_physical: Optional[str] = None
    boundaries_logical: Optional[str] = None
    dependencies_json: Optional[str] = None

class ScopeResponse(ScopeUpdate):
    id: int
    class Config:
        from_attributes = True

# --- Endpoints ---

# 4.1 Issues
@router.get("/issues", response_model=List[IssueResponse])
def get_issues(db: Session = Depends(get_db)):
    return db.query(ContextIssue).all()

@router.post("/issues", response_model=IssueResponse)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    db_issue = ContextIssue(**issue.model_dump())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.delete("/issues/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(ContextIssue).filter(ContextIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.delete(issue)
    db.commit()
    return {"status": "deleted"}

# 4.2 Interested Parties
@router.get("/interested-parties", response_model=List[PartyResponse])
def get_parties(db: Session = Depends(get_db)):
    return db.query(InterestedParty).all()

@router.post("/interested-parties", response_model=PartyResponse)
def create_party(party: PartyCreate, db: Session = Depends(get_db)):
    db_party = InterestedParty(**party.model_dump())
    db.add(db_party)
    db.commit()
    db.refresh(db_party)
    return db_party

@router.delete("/interested-parties/{party_id}")
def delete_party(party_id: int, db: Session = Depends(get_db)):
    party = db.query(InterestedParty).filter(InterestedParty.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    db.delete(party)
    db.commit()
    return {"status": "deleted"}

# 4.3 Scope
@router.get("/scope", response_model=ScopeResponse)
def get_scope(db: Session = Depends(get_db)):
    scope = db.query(ScopeDocument).first()
    if not scope:
        # Create default if missing
        scope = ScopeDocument(
            content="# ISMS Scope\n\nThe scope of the ISMS includes...",
            boundaries_physical="Headquarters (San Francisco)",
            boundaries_logical="AWS US-East-1 Production Environment",
            dependencies_json="[]"
        )
        db.add(scope)
        db.commit()
        db.refresh(scope)
    return scope

@router.put("/scope", response_model=ScopeResponse)
def update_scope(data: ScopeUpdate, db: Session = Depends(get_db)):
    scope = db.query(ScopeDocument).first()
    if not scope:
        scope = ScopeDocument()
        db.add(scope)
    
    scope.content = data.content
    scope.boundaries_physical = data.boundaries_physical
    scope.boundaries_logical = data.boundaries_logical
    scope.dependencies_json = data.dependencies_json
    
    db.commit()
    db.refresh(scope)
    return scope
