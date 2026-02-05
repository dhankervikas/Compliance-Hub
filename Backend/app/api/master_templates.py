from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.master_template import MasterTemplate

router = APIRouter()

# --- Schemas ---
class MasterTemplateResponse(BaseModel):
    id: int
    title: str
    control_id: Optional[str]
    content: str
    original_filename: str
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# --- Endpoints ---
@router.get("/", response_model=List[MasterTemplateResponse])
def get_master_templates(db: Session = Depends(get_db)):
    """
    Fetch all immutable master templates.
    """
    return db.query(MasterTemplate).all()

@router.get("/{template_id}", response_model=MasterTemplateResponse)
def get_master_template(template_id: int, db: Session = Depends(get_db)):
    """
    Fetch a specific master template content.
    """
    template = db.query(MasterTemplate).filter(MasterTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Master Template not found")
    return template
