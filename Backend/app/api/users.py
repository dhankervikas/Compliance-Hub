from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.framework import Framework
from app.models.user import User
from app.models.tenant import Tenant
from app.models.framework import Framework
from app.models.tenant_framework import TenantFramework
from app.models.tenant_feature import TenantFeature
from app.schemas.user import User as UserSchema, UserUpdate, UserCreate
from app.api.auth import get_current_user
from app.utils.security import get_password_hash
from app.config import settings

from sqlalchemy import func
from pydantic import BaseModel

router = APIRouter()

class TenantCreate(BaseModel):
    org_name: str
    admin_username: str
    admin_email: str
    password: str
    
    # Optional Fields from Wizard
    slug: str = None
    framework_ids: List[int] = []
    encryption_tier: str = "standard"
    data_residency: str = "us-east-1"
    aims_scope: str = None
    security_leader_role: str = None
    existing_policies: bool = False

class TenantResponse(BaseModel):
    tenant_id: str
    name: str # New field
    user_count: int
    is_active: bool # New field

# Dependency to restrict to Admin
def get_current_admin(current_user: User = Depends(get_current_user)):
    # Simple check. In real app, check current_user.role == 'admin' or is_superuser
    if current_user.role != 'admin' and not current_user.is_superuser:
         raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/tenants", response_model=List[TenantResponse])
def list_tenants(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """List all unique tenants and their user counts"""
    # Join User aggregation with Tenant table
    # We want: Tenant info + count of users
    
    # 1. Get counts
    user_counts = db.query(User.tenant_id, func.count(User.id)).group_by(User.tenant_id).all()
    count_map = {r[0]: r[1] for r in user_counts}
    
    # 2. Get Tenants
    tenants = db.query(Tenant).all()
    
    results = []
    for t in tenants:
        results.append({
            "tenant_id": t.slug,
            "name": t.name,
            "is_active": t.is_active,
            "user_count": count_map.get(t.slug, 0)
        })
        
    return results

@router.post("/tenants", status_code=status.HTTP_201_CREATED)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Create a new tenant (and its first admin user)"""
    
    # 1. Generate Tenant ID slug
    import re
    slug = re.sub(r'[^a-z0-9]', '_', tenant.org_name.lower())
    
    # 2. Check overlap (Tenant Slug only)
    # We rely on DB UniqueConstraint(username, tenant_id) for user uniqueness.
    # However, if we want to be nice, we can check basic tenant existence first.
    
    # Use provided slug or generate one
    final_slug = tenant.slug if tenant.slug else slug
    
    if db.query(Tenant).filter(Tenant.slug == final_slug).first():
          raise HTTPException(status_code=400, detail="Tenant/Slug already exists")
        
    # 3. Create Tenant Record
    import secrets
    
    tenant_metadata = {
        "encryption_tier": tenant.encryption_tier,
        "data_residency": tenant.data_residency,
        "aims_scope": tenant.aims_scope,
        "security_leader_role": tenant.security_leader_role,
        "existing_policies": tenant.existing_policies
    }
    
    new_tenant = Tenant(
        name=tenant.org_name,
        slug=final_slug,
        encryption_key=secrets.token_hex(32),
        is_active=True,
        metadata_json=tenant_metadata
    )
    db.add(new_tenant)
    db.flush() 
    
    # 3.5 Link Frameworks
    # Now link frameworks
    for fid in tenant.framework_ids:
        tf = TenantFramework(
            tenant_id=new_tenant.internal_tenant_id,
            framework_id=fid,
            is_active=True
        )
        db.add(tf)
    
    if tenant.framework_ids:
        db.commit()

    # 4. Create User
    hashed = get_password_hash(tenant.password)
    new_user = User(
        username=tenant.admin_username, # Use original username (e.g. 'admin')
        email=tenant.admin_email,
        hashed_password=hashed,
        tenant_id=new_tenant.slug, # Associated with this tenant
        full_name=tenant.org_name + " Admin",
        role="admin",
        is_active=True
    )
    
    # Note: DB constraint (username, tenant_id) will catch duplicates for this tenant.
    # Email is still globally unique in model (unless we fixed that too). 
    # If users reuse email across tenants, we might get an error.
    # Ideally, we should remove checking overlap logic for username/email globally.
         
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        # Clean up tenant if user creation fails? Ideally yes.
        # But for now let's just raise
        raise HTTPException(status_code=400, detail=f"Failed to create admin user: {str(e)}")
        
    # Generate Login URL based on dynamic config
    login_url = f"{settings.BASE_URL}/t/{new_tenant.slug}/login"
        
    return {
        "message": "Tenant created", 
        "tenant_id": new_tenant.slug, 
        "username": new_user.username,
        "name": new_tenant.name,
        "internal_tenant_id": new_tenant.internal_tenant_id,
        "login_url": login_url
    }


class TenantStatusUpdate(BaseModel):
    is_active: bool

@router.patch("/tenants/{tenant_id}/status")
def update_tenant_status(
    tenant_id: str, 
    status_update: TenantStatusUpdate,
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    """Activate or Deactivate a Tenant"""
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    tenant.is_active = status_update.is_active
    db.commit()
    
    action = "activated" if status_update.is_active else "deactivated"
    return {"message": f"Tenant {tenant.name} has been {action}", "is_active": tenant.is_active}

class TenantFrameworkStatus(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool

class TenantFrameworkUpdate(BaseModel):
    framework_ids: List[int]

@router.get("/tenants/{tenant_id}/frameworks", response_model=List[TenantFrameworkStatus])
def list_tenant_frameworks(
    tenant_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    """List all frameworks and their status for a specific Tenant"""
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    # Get all frameworks (Catalog)
    all_frameworks = db.query(Framework).all()
    
    # Get active links for this tenant
    active_links = db.query(TenantFramework).filter(
        TenantFramework.tenant_id == tenant.internal_tenant_id,
        TenantFramework.is_active == True
    ).all()
    
    active_ids = {link.framework_id for link in active_links}
    
    results = []
    for fw in all_frameworks:
        results.append({
            "id": fw.id,
            "name": fw.name,
            "code": fw.code,
            "is_active": fw.id in active_ids
        })
        
    return results

@router.put("/tenants/{tenant_id}/frameworks")
def update_tenant_frameworks(
    tenant_id: str, 
    update: TenantFrameworkUpdate, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    """Update active frameworks for a Tenant"""
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    # Get current links
    existing_links = db.query(TenantFramework).filter(
        TenantFramework.tenant_id == tenant.internal_tenant_id
    ).all()
    
    existing_map = {link.framework_id: link for link in existing_links}
    
    target_ids = set(update.framework_ids)
    
    # Process updates
    # 1. Enable or Create
    for fid in target_ids:
        if fid in existing_map:
            existing_map[fid].is_active = True
        else:
            # Create new link
            new_link = TenantFramework(
                tenant_id=tenant.internal_tenant_id,
                framework_id=fid,
                is_active=True
            )
            db.add(new_link)
            
    # 2. Disable missing
    for fid, link in existing_map.items():
        if fid not in target_ids:
            link.is_active = False
            
    db.commit()
    
    return {"message": "Tenant frameworks updated", "active_frameworks": list(target_ids)}

# --- ENTITLEMENTS API (Combined) ---

class EntitlementStatus(BaseModel):
    frameworks: List[dict] # {id, name, code, is_active}
    features: List[dict] # {key, is_active}
    account_status: str # 'active', 'deactivated'

class EntitlementUpdate(BaseModel):
    framework_ids: List[int]
    active_features: List[str]
    account_status: str # 'active', 'deactivated'

def _get_entitlements_logic(db: Session, tenant_slug: str):
    print(f"DEBUG: _get_entitlements_logic called for slug='{tenant_slug}' (Type: {type(tenant_slug)})")
    
    # DEBUG: List all tenants to see what DB sees
    all_ts = db.query(Tenant).all()
    print(f"DEBUG: Visible Tenants in DB Session: {[t.slug for t in all_ts]}")

    # Updated Logic: Check Slug, Internal ID (UUID), or PK ID
    tenant = db.query(Tenant).filter(
        (Tenant.slug == tenant_slug) | 
        (Tenant.internal_tenant_id == tenant_slug)
    ).first()
    
    if not tenant:
        print(f"DEBUG: Tenant '{tenant_slug}' NOT FOUND in DB query.")
        # Try manual match (fallback loop usually not needed if filter works)
        for t in all_ts:
             if t.slug == tenant_slug or t.internal_tenant_id == tenant_slug:
                 print("DEBUG: Found via manual loop!")
                 tenant = t
                 break
                 
    if not tenant:
        visible_slugs = [t.slug for t in all_ts]
        debug_msg = f"Tenant '{tenant_slug}' NOT FOUND. Visible: {visible_slugs}"
        print(f"DEBUG: {debug_msg}")
        return None # Return None to let caller raise 404
        
    # 1. Frameworks
    all_frameworks = db.query(Framework).all()
    active_links = db.query(TenantFramework).filter(
        TenantFramework.tenant_id == tenant.internal_tenant_id,
        TenantFramework.is_active == True
    ).all()
    active_fw_ids = {link.framework_id for link in active_links}
    
    fw_list = []
    for fw in all_frameworks:
        fw_list.append({
            "id": fw.id,
            "name": fw.name,
            "code": fw.code,
            "is_active": fw.id in active_fw_ids
        })
        
    # 2. Features
    AVAILABLE_FEATURES = ["aws_scanner", "github_scanner", "custom_reports", "sso_integration"]
    
    current_features = db.query(TenantFeature).filter(
        TenantFeature.tenant_id == tenant.internal_tenant_id,
        TenantFeature.is_active == True
    ).all()
    active_usage_keys = {f.feature_key for f in current_features}
    
    feat_list = []
    for key in AVAILABLE_FEATURES:
        feat_list.append({
            "key": key,
            "is_active": key in active_usage_keys
        })
        
    # 3. Account Status
    status = "active" if tenant.is_active else "deactivated"
    
    return {
        "frameworks": fw_list,
        "features": feat_list,
        "account_status": status
    }

@router.get("/tenants/{tenant_id}/entitlements", response_model=EntitlementStatus)
def get_tenant_entitlements(
    tenant_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    """Get full entitlement status for a tenant (Admin Only)"""
    result = _get_entitlements_logic(db, tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result

@router.get("/me/entitlements", response_model=EntitlementStatus)
def get_my_entitlements(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get entitlement status for the current user's tenant"""
    result = _get_entitlements_logic(db, current_user.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant context not found")
    return result

@router.put("/tenants/{tenant_id}/entitlements")
def update_tenant_entitlements(
    tenant_id: str, 
    update: EntitlementUpdate, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    """Update all entitlements for a tenant"""
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    # 1. Update Account Status
    is_active_target = (update.account_status == 'active')
    if tenant.is_active != is_active_target:
        tenant.is_active = is_active_target
        # Log this action?
        
    # 2. Update Frameworks
    existing_fw_links = db.query(TenantFramework).filter(
        TenantFramework.tenant_id == tenant.internal_tenant_id
    ).all()
    fw_map = {link.framework_id: link for link in existing_fw_links}
    target_fw_ids = set(update.framework_ids)
    
    for fid in target_fw_ids:
        if fid in fw_map:
            fw_map[fid].is_active = True
        else:
            new_link = TenantFramework(
                tenant_id=tenant.internal_tenant_id,
                framework_id=fid,
                is_active=True
            )
            db.add(new_link)
            
    for fid, link in fw_map.items():
        if fid not in target_fw_ids:
            link.is_active = False
            
    # 3. Update Features
    existing_feats = db.query(TenantFeature).filter(
        TenantFeature.tenant_id == tenant.internal_tenant_id
    ).all()
    feat_map = {f.feature_key: f for f in existing_feats}
    target_feats = set(update.active_features)
    
    for key in target_feats:
        if key in feat_map:
            feat_map[key].is_active = True
        else:
            new_feat = TenantFeature(
                tenant_id=tenant.internal_tenant_id,
                feature_key=key,
                is_active=True
            )
            db.add(new_feat)
            
    for key, feat in feat_map.items():
        if key not in target_feats:
            feat.is_active = False
            
    db.commit()
    
    return {"message": "Entitlements updated successfully"}

@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    # Enforce Tenant Isolation
    if admin.is_superuser:
        # Superusers can see all users (or we could add a tenant_id query param to filter)
        users = db.query(User).offset(skip).limit(limit).all()
    else:
        # Tenant Admins can only see users in their tenant
        users = db.query(User).filter(User.tenant_id == admin.tenant_id).offset(skip).limit(limit).all()
    return users

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data['password'])
        del update_data['password']
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(db_user)
    db.commit()
    return None
