from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models import Policy
from app.services import ai_service
from app.services.ai_policy_service import PolicyGenerationService

router = APIRouter()

# --- Schemas ---
class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    version: str = "1.0"
    status: str = "Draft"
    owner: str = "Compliance Team"

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    owner: Optional[str] = None
    name: Optional[str] = None

class PolicyResponse(PolicyBase):
    id: int
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    title: str
    context: str

# --- Endpoints ---

from app.api.auth import get_current_user

@router.get("/", response_model=List[PolicyResponse])
def get_policies(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id
    
    return db.query(Policy).filter(Policy.tenant_id == tenant_uuid).all()

@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    policy = db.query(Policy).filter(Policy.id == policy_id, Policy.tenant_id == current_user.tenant_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_policy = Policy(**policy.dict(), tenant_id=current_user.tenant_id)
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(policy_id: int, update_data: PolicyUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id, Policy.tenant_id == current_user.tenant_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Versioning Logic: If content changed, increment minor version contextually
    if update_data.content and update_data.content != db_policy.content:
        # If currently Approved, this edit makes it a "Draft" again with a version bump
        if db_policy.status == "Approved":
            db_policy.status = "Draft"
            try:
                # 1.0 -> 1.1, 1.1 -> 1.2
                v_parts = db_policy.version.split('.')
                db_policy.version = f"{v_parts[0]}.{int(v_parts[1]) + 1}"
            except:
                db_policy.version = "1.1" # Fallback
        
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(db_policy, field, value)
    
    db_policy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id, Policy.tenant_id == current_user.tenant_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(db_policy)
    db.commit()
    return None

@router.post("/{policy_id}/generate")
def generate_policy_content(policy_id: int, req: GenerateRequest, db: Session = Depends(get_db)):
    """
    Generate policy content using AI (OpenAI)
    """
    # 1. Fetch Policy Details
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    policy_name = policy.name if policy else "Policy Document"
    
    # 2. Fetch Organization Context
    from app.models.settings import ComplianceSettings
    org_settings = db.query(ComplianceSettings).filter(ComplianceSettings.section_key == "org_profile").first()
    org_data = org_settings.content if org_settings else {}
    company_name = org_data.get("legal_name", "AssuRisk")

    # 3. Call AI Policy Service
    service = PolicyGenerationService()
    result = service.generate_policy(policy_name=policy_name, company_name=company_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "AI Generation Failed"))

    return {"content": result.get("content")}

class RewriteRequest(BaseModel):
    text: str
    instruction: str = "simplify" # simplify, expand, formalize

@router.post("/{policy_id}/rewrite")
def rewrite_policy_section(policy_id: int, req: RewriteRequest, db: Session = Depends(get_db)):
    """
    Rewrites a specific text chunk using AI.
    """
    # Simple direct prompt
    try:
        content = ai_service.rewrite_text(req.text, req.instruction)
        return {"content": content}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.post("/{policy_id}/approve")
def approve_policy(policy_id: int, db: Session = Depends(get_db)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # 1. Update Policy Status
    db_policy.status = "Approved"
    db_policy.updated_at = datetime.utcnow()
    
    # 2. Generate PDF and get path
    from app.services.pdf_generator import create_signed_pdf
    # Get Approver from Policy metadata or default
    approver = "CISO (Admin)" 
    
    try:
        pdf_path = create_signed_pdf(
            policy_name=db_policy.name,
            content=db_policy.content,
            version=db_policy.version,
            approver=approver
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        pdf_path = None

    # 3. Create Document Record (Repository)
    # Import Document inside function to avoid circular imports if any
    from app.models.document import Document
    
    new_document = Document(
        policy_id=db_policy.id,
        content=db_policy.content,
        status="approved",
        version=db_policy.version,
        approved_by=approver,
        approved_date=datetime.utcnow(),
        pdf_path=pdf_path
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(db_policy)
    
    return {"status": "approved", "version": db_policy.version, "document_id": new_document.id, "pdf_path": pdf_path}

@router.post("/{policy_id}/request_approval")
def request_approval(policy_id: int, db: Session = Depends(get_db)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Update status to Pending Approval
    db_policy.status = "Pending Approval"
    db_policy.updated_at = datetime.utcnow()
    db.commit()

    # Mock Email Logic
    print(f"[MOCK EMAIL] Sending approval request for policy '{db_policy.name}' to admin@assurisk.com")
    
    return {"message": "Approval request sent", "status": "Pending Approval"}

    return {"message": "Approval request sent", "status": "Pending Approval"}

@router.post("/clone-master/{template_id}", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def clone_master_template(template_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Clones an Immutable Master Template into a User-Editable Draft Policy.
    Injects global variables (Company Name, etc.) into the content.
    """
    from app.models.master_template import MasterTemplate
    from app.models.settings import ComplianceSettings
    
    # 1. Fetch Master Template
    master = db.query(MasterTemplate).filter(MasterTemplate.id == template_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master Template not found")

    # 2. Fetch Context Variables (Company Name, etc)
    # Ideally reuse a service for this variable injection
    org_settings = db.query(ComplianceSettings).filter(ComplianceSettings.section_key == "org_profile").first()
    org_data = org_settings.content if org_settings else {}
    company_name = org_data.get("legal_name", "AssuRisk")
    
    # 3. Enhanced Variable Injection
    content = master.content
    
    # Standard Variables
    content = content.replace("{{company_name}}", company_name)
    content = content.replace("{{current_date}}", datetime.now().strftime("%B %d, %Y"))
    content = content.replace("{{year}}", str(datetime.now().year))
    
    # Context Variables (Mocked or from Settings)
    scope_text = org_data.get("scope_description", "All information systems, networks, and data.")
    content = content.replace("{{policy_scope}}", scope_text)
    
    # Regulations (Mocked for now, implies Settings expansion later)
    regulations = "ISO 27001:2022, SOC 2 Type II, GDPR, CCPA"
    content = content.replace("{{key_regulations}}", regulations)
    content = content.replace("{{mfa_tool}}", "Okta (Default)")
    
    # Author
    content = content.replace("{{author_name}}", "Compliance Officer")
    
    # 4. Create Policy Draft
    # Check if a policy with this name already exists? Maybe append (Copy) if so.
    
    
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    new_policy = Policy(
        name=master.title,
        description=f"Generated from Master Template: {master.original_filename}",
        content=content,
        version="0.1", # Initial Draft
        status="Draft",
        master_template_id=master.id,
        is_template=False, 
        linked_frameworks="ISO 27001", 
        mapped_controls=f'["{master.control_id}"]' if master.control_id else "[]",
        tenant_id=tenant_uuid
    )
    
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    
    return new_policy

@router.post("/{policy_id}/restore", response_model=PolicyResponse)
def restore_policy_from_master(policy_id: int, db: Session = Depends(get_db)):
    """
    Restores a policy to its Master Template content.
    """
    from app.models.master_template import MasterTemplate
    from app.models.settings import ComplianceSettings

    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    if not policy.master_template_id:
        raise HTTPException(status_code=400, detail="This policy is not linked to a Master Template")

    master = db.query(MasterTemplate).filter(MasterTemplate.id == policy.master_template_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Linked Master Template not found")

    # Re-inject variables
    org_settings = db.query(ComplianceSettings).filter(ComplianceSettings.section_key == "org_profile").first()
    org_data = org_settings.content if org_settings else {}
    company_name = org_data.get("legal_name", "AssuRisk")
    
    content = master.content
    content = content.replace("{{company_name}}", company_name)
    content = content.replace("{{mfa_tool}}", "Okta (Default)") 

    policy.content = content
    policy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(policy)
    
    return policy
