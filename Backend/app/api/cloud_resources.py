from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.auth import get_current_user
from app.models.cloud_resource import CloudResource
from app.models.user import User

router = APIRouter()

@router.get("/{id}")
def get_resource(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch a specific cloud resource by ID.
    Enforces strict tenant isolation: 
    Users can only access resources where resource.tenant_id matches their own.
    """
    
    # 1. Fetch
    resource = db.query(CloudResource).filter(CloudResource.id == id).first()
    
    # 2. Check Existence
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # 3. Enforce Isolation (Application Layer)
    # Even if RLS fails (SQLite), this blocks access.
    if resource.tenant_id != current_user.tenant_id:
        # Standard security practice: Return 404 to avoid leaking existence
        raise HTTPException(status_code=404, detail="Resource not found")
        
    return resource
