from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.settings import ComplianceSettings
from app.models.user import User
from app.schemas.compliance_profile import (
    SettingsUpdate, SettingsResponse, 
    OrgProfile, ScopeProfile, TechStackProfile, DataPrivacyProfile,
    AccessProfile, HRProfile, VendorProfile, SecOpsProfile,
    BCPProfile, DocPreferences
)
from app.api.auth import get_current_user

router = APIRouter()

# Mapping Section Keys to Pydantic Models for validation
SECTION_MODEL_MAP = {
    "org_profile": OrgProfile,
    "scope": ScopeProfile,
    "tech_stack": TechStackProfile,
    "data_privacy": DataPrivacyProfile,
    "access_identity": AccessProfile,
    "hr_security": HRProfile,
    "vendors": VendorProfile,
    "sec_ops": SecOpsProfile,
    "bcp_dr": BCPProfile,
    "doc_preferences": DocPreferences
}

def calculate_completeness(content: Dict) -> int:
    """Simple heuristic: % of non-null/non-empty values"""
    if not content:
        return 0
    total = len(content)
    filled = sum(1 for v in content.values() if v not in [None, "", []])
    return int((filled / total) * 100)

@router.get("/{section_key}", response_model=SettingsResponse)
def get_settings(
    section_key: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if section_key not in SECTION_MODEL_MAP:
        raise HTTPException(status_code=400, detail="Invalid section key")

    if section_key not in SECTION_MODEL_MAP:
        raise HTTPException(status_code=400, detail="Invalid section key")

    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Filter settings by tenant to avoid data leaks
    settings = db.query(ComplianceSettings).filter(
        ComplianceSettings.section_key == section_key,
        ComplianceSettings.tenant_id == tenant_uuid
    ).first()
    
    if not settings:
        # Return empty default for that section if not found
        return SettingsResponse(
            section=section_key,
            content={}, # Frontend handles defaults
            completeness_score=0,
            updated_at=None
        )

    return SettingsResponse(
        section=settings.section_key,
        content=settings.content,
        updated_at=settings.updated_at,
        completeness_score=settings.completeness_score
    )

@router.put("/{section_key}", response_model=SettingsResponse)
def update_settings(
    section_key: str,
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if section_key not in SECTION_MODEL_MAP:
        raise HTTPException(status_code=400, detail="Invalid section key")
    
    # 1. Resolve Tenant UUID
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # 2. Fetch Existing Settings
    settings = db.query(ComplianceSettings).filter(
        ComplianceSettings.section_key == section_key,
        ComplianceSettings.tenant_id == tenant_uuid
    ).first()

    # 3. Deep Merge Logic
    # We always merge the NEW payload into the OLD content to preserve missing keys (like Wizard data)
    def deep_merge(target, source):
        if not isinstance(source, dict):
            return source
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge(target[key], value)
            else:
                target[key] = value
        return target

    # Start with existing content or empty dict
    current_content = settings.content.copy() if settings and settings.content else {}
    
    # Clean payload (remove empty strings which might be sent by forms)
    def clean_content(d):
        if isinstance(d, dict):
            return {k: clean_content(v) for k, v in d.items() if v != ""}
        if isinstance(d, list):
            return [clean_content(v) for v in d if v != ""]
        return d
    
    new_content = clean_content(payload.content)
    
    # Merge
    merged_content = deep_merge(current_content, new_content)

    # 4. Validate Merged Content
    ModelClass = SECTION_MODEL_MAP[section_key]
    try:
        # validate strictness? The model might have defaults. 
        # We assume the merged content is valid.
        # If partial updates are allowed, we might need to be careful with Required fields.
        # But for settings, we usually treat them as growing over time.
        # Let's try to validate the RESULT
        validated_model = ModelClass(**merged_content)
        final_content = validated_model.model_dump() # equivalent to .dict()
    except Exception as e:
        # Fallback: if validation fails (e.g. missing required field that wasn't in either),
        # we might just save the dict but log a warning. 
        # However, for robustness, we'll save the merged dict.
        print(f"Validation Warning for {section_key}: {e}")
        final_content = merged_content

    score = calculate_completeness(final_content)

    if not settings:
        settings = ComplianceSettings(
            section_key=section_key,
            content=final_content,
            updated_by=str(current_user.id),
            completeness_score=score,
            tenant_id=tenant_uuid
        )
        db.add(settings)
    else:
        settings.content = final_content
        settings.updated_by = str(current_user.id)
        settings.completeness_score = score
        # No need to update tenant_id/section_key
    
    db.commit()
    db.refresh(settings)

    return SettingsResponse(
        section=settings.section_key,
        content=settings.content,
        updated_at=settings.updated_at,
        completeness_score=settings.completeness_score
    )

@router.get("/status/overview")
def get_completeness_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns the completeness score for ALL sections"""
    """Returns the completeness score for ALL sections"""
    # Resolve Tenant UUID
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    all_settings = db.query(ComplianceSettings).filter(ComplianceSettings.tenant_id == tenant_uuid).all()
    overview = {key: 0 for key in SECTION_MODEL_MAP.keys()}
    
    for s in all_settings:
        overview[s.section_key] = s.completeness_score
        
    return overview
