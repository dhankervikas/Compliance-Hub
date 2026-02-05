from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PersonBase(BaseModel):
    email: str
    full_name: str
    employment_status: str = "Active"
    job_title: Optional[str] = None
    department: Optional[str] = None
    source: Optional[str] = "manual_import"
    external_id: Optional[str] = None
    tenant_id: Optional[str] = "default"

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    employment_status: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class Person(PersonBase):
    id: str
    last_synced_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
