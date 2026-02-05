
from fastapi import Request, HTTPException, status
from app.utils.security import decode_access_token
import logging

logger = logging.getLogger("uvicorn")

async def verify_tenant(request: Request):
    # Skip public checks (handled by global dep)
    EXCLUDED_PATHS = [
        "/docs", 
        "/openapi.json", 
        "/health",
        "/api/v1/health/security-integrity", # Specific Public Endpoint
        "/health-api",
        "/api/public/integrity",
        "/api/v1/auth/login", 
        "/api/v1/auth/register",
        "/static",
        "/"
    ]
    
    try:
        # DEBUG LOGGING
        print(f"DEBUG: verify_tenant called. Method={request.method}, Path={request.url.path}")
        
        if request.method == "OPTIONS":
            print("DEBUG: IS OPTIONS -> Returning immediately")
            return
            
        path = request.url.path
        if path == "/" or any(path.startswith(p) for p in EXCLUDED_PATHS):
            return

        # Extract Token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
             # logger.warning(f"[TenantDependency] Missing Auth Header: {path}")
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="GHOST DEPS: Missing or invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        
        if not payload:
             # logger.warning(f"[TenantDependency] Invalid Token: {path}")
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        tenant_id = payload.get("tenant_id")
        username = payload.get("sub")
        
        # --- MASQUERADING LOGIC ---
        # Allow Super Admin to masquerade as another tenant
        target_tenant_id = request.headers.get("X-Target-Tenant-ID")
        
        # Check if user is Super Admin (simple check for now, can be role-based later)
        # Assuming 'admin' username is the Super Admin
        if username == "admin" and target_tenant_id:
             # logger.info(f"[TenantDependency] SuperAdmin masquerading as {target_tenant_id}")
             tenant_id = target_tenant_id
        
        if not tenant_id:
             # logger.warning(f"[TenantDependency] Missing Tenant ID: {payload}")
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing tenant context",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Set tenant in request state provided by Starlette
        request.state.tenant_id = tenant_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TenantDependency] UNEXPECTED ERROR: {e}")
        # raise HTTPException(status_code=500, detail="Internal Server Error during Tenant Verification")
        raise
        
# --- ENTITLEMENT GUARDS ---

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant_feature import TenantFeature
from app.models.tenant_framework import TenantFramework

class FeatureGuard:
    """
    Dependency to enforce Tenant Feature entitlements.
    Usage: @router.get("/...", dependencies=[Depends(FeatureGuard("aws_scanner"))])
    """
    def __init__(self, feature_key: str):
        self.feature_key = feature_key

    def __call__(self, request: Request, db: Session = Depends(get_db)):
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
             # Should have been caught by verify_tenant, but strict check
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant context missing for entitlement check")
        
        # Check DB for active feature
        # Note: We rely on internal_tenant_id usually, but verify_tenant sets 'slug' or 'id'?
        # Let's verify what verify_tenant sets. 
        # It decodes token -> payload.get("tenant_id") which is usually the SLUG in our system (e.g. "testtest").
        # However, the tables (TenantFeature) use `internal_tenant_id` (UUID) or `slug`?
        # Let's check TenantFeature model again. It uses ForeignKey("tenants.internal_tenant_id").
        # So we need to resolve Slug -> Internal ID first? Or does token have internal ID?
        # Token usually has 'sub' (username) and 'tenant_id' (slug).
        
        # OPTIMIZATION: We should probably store internal_id in token or resolve it once in verify_tenant.
        # For now, let's resolve it here via a join or look up.
        from app.models.tenant import Tenant
        
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
        if not tenant:
             raise HTTPException(status_code=401, detail="Invalid Tenant Context")
             
        feature = db.query(TenantFeature).filter(
            TenantFeature.tenant_id == tenant.internal_tenant_id,
            TenantFeature.feature_key == self.feature_key,
            TenantFeature.is_active == True
        ).first()
        
        if not feature:
            # logger.warning(f"Access Denied: Tenant '{tenant_id}' missing feature '{self.feature_key}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Feature '{self.feature_key}' is not enabled for your plan."
            )

class FrameworkGuard:
    """
    Dependency to enforce Tenant Framework entitlements.
    Usage: @router.get("/iso42001/...", dependencies=[Depends(FrameworkGuard("ISO27001"))])
    """
    def __init__(self, framework_code: str):
        self.framework_code = framework_code

    def __call__(self, request: Request, db: Session = Depends(get_db)):
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant context missing")
        
        from app.models.tenant import Tenant
        from app.models.framework import Framework
        
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
        if not tenant:
             raise HTTPException(status_code=401, detail="Invalid Tenant Context")
             
        # Check if framework specific code is active
        # Join TenantFramework -> Framework
        link = db.query(TenantFramework).join(Framework).filter(
            TenantFramework.tenant_id == tenant.internal_tenant_id,
            Framework.code == self.framework_code,
            TenantFramework.is_active == True
        ).first()
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Framework '{self.framework_code}' is not active for your tenant."
            )
class AuditorPermissionGuard:
    """
    Dependency to enforce Role-Based Access Control (RBAC) for Auditors.
    - BLOCKS: PUT, POST, DELETE, PATCH on protected resources.
    - ALLOWS: GET requests.
    - EXEMPTION: Specific paths (e.g., /api/v1/auditor/assessments).
    """
    def __call__(self, request: Request, db: Session = Depends(get_db)):
        # 1. Identify User Role
        # We need the user object. 
        # Ideally, we should have a `get_current_user` dep, but here we can look it up.
        tenant_id_slug = getattr(request.state, "tenant_id", None)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return # Should be accepted by verify_tenant already, or rejected.

        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if not payload:
            return

        username = payload.get("sub")
        
        from app.models.user import User
        from app.models.tenant import Tenant
        
        # Resolve Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_id_slug).first()
        if not tenant:
            return 
            
        # Resolve User
        user = db.query(User).filter(
            User.email == username, 
            User.tenant_id == tenant.internal_tenant_id
        ).first()

        if not user:
            return

        # 2. Check Allowed Methods
        if user.role == "AUDITOR":
            # ALLOW: GET (Read Only)
            if request.method == "GET":
                return
            
            # ALLOW: Specific Write Endpoints (Auditor Portal)
            allowed_write_paths = [
                "/api/v1/auditor/assessments",
                "/api/v1/auditor/integrity-check",
                "/api/v1/auth/logout" # Important
            ]
            
            # Check if current path matches exemption
            if request.url.path in allowed_write_paths:
                return
            
            # BLOCK EVERYTHING ELSE
            logger.warning(f"[RBAC] Blocked AUDITOR write attempt to {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Auditors have Read-Only access to this resource."
            )
            
# Instantiate for global use if needed, or use Depends(AuditorPermissionGuard())
verify_auditor_permissions = AuditorPermissionGuard()
