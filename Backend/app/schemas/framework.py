from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class FrameworkBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    version: Optional[str] = None


class FrameworkCreate(FrameworkBase):
    pass


class FrameworkUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None


class Framework(FrameworkBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class FrameworkWithStats(Framework):
    total_controls: int
    implemented_controls: int
    in_progress_controls: int
    not_started_controls: int
    completion_percentage: float