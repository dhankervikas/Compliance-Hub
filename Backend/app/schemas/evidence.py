from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EvidenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None


class EvidenceCreate(BaseModel):
    control_id: int
    filename: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_by: Optional[str] = None
    collection_date: Optional[datetime] = None


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    collection_date: Optional[datetime] = None


class Evidence(EvidenceBase):
    id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    control_id: int
    uploaded_by: Optional[str] = None
    collection_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True