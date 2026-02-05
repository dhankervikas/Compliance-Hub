from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class TenantBase(BaseModel):
    name: str
    slug: str
    admin_email: str
    
    # Security & Context
    encryption_tier: str = "standard" # standard, advanced
    data_residency: str = "us-east-1"
    
    # ISO 42001 Context
    aims_scope: Optional[str] = None
    security_leader_role: Optional[str] = None
    existing_policies: bool = False
    
    # Framework Provisioning
    framework_ids: List[int] = [] # IDs of frameworks to enable (e.g. 1=ISO27001, 2=SOC2)

class TenantCreate(TenantBase):
    pass

class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    internal_tenant_id: str
    login_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True
