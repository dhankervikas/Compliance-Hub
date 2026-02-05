from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import io
import json

from app.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.schemas.person import Person as PersonSchema
from app.services.privilege_service import PrivilegeService
from app.models.person import Person

router = APIRouter()

@router.post("/import", response_model=Dict[str, int])
async def import_people(
    file: UploadFile = File(None),
    json_data: List[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Import people from CSV or JSON.
    """
    data = []
    
    if json_data:
        data = json_data
    elif file:
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
            # Normalize keys to lower case
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            data = df.to_dict(orient='records')
        elif file.filename.endswith('.json'):
            data = json.loads(content)
        else:
             raise HTTPException(status_code=400, detail="Invalid file format. Use CSV or JSON.")
    
    if not data:
         raise HTTPException(status_code=400, detail="No data provided")

    return PrivilegeService.import_people(db, current_user.tenant_id, data)

@router.get("/", response_model=List[PersonSchema])
def read_people(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Person).filter(
        Person.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()

@router.get("/risks", response_model=List[Dict[str, Any]])
def get_identity_risks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns a list of 'Zombie Accounts' (Inactive Person -> Active User).
    """
    return PrivilegeService.detect_zombie_accounts(db, current_user.tenant_id)
