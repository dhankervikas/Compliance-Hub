from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.utils.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    token_tenant_id: str = payload.get("tenant_id")
    mode: str = payload.get("mode", "standard")
    
    # --- MASQUERADING LOGIC (HEADER BASED) ---
    # Prioritize the header if present and user is admin
    target_tenant_id = request.headers.get("X-Target-Tenant-ID")
    effective_tenant_id = token_tenant_id
    
    print(f"DEBUG: Auth Header Check. User={username}, MsgHeader={target_tenant_id}, TokenTenant={token_tenant_id}")

    if username == "admin" and target_tenant_id:
        effective_tenant_id = target_tenant_id
        print(f"DEBUG: Masquerading as {effective_tenant_id} (Admin Override)")
    
    # ... (RLS Logic)

    
    # Fetch User
    # Note: We must join with Tenant if we want to be strict, but username is unique per tenant
    # However, the Token contains the specific tenant_id claim.
    # For now, simplistic fetch by username (assuming unique globally or filtered later)
    # Actually, we should filter by the token's tenant_id if we want to be safe, 
    # BUT admin might be masquerading.
    
    # Original Logic:
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception

    # CRITICAL FIX: Ensure user object reflects the Tenant Context (Real or Masqueraded)
    if user:
        if effective_tenant_id != user.tenant_id:
            # Detach user from session to prevent this temporary change from being committed to DB
            db.expunge(user)
            user.tenant_id = effective_tenant_id
            
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token, supporting Tenant Context via Header"""
    
    # 1. Determine Target Tenant
    target_tenant_id = request.headers.get("X-Target-Tenant-ID")
    
    # 2. Query User with Tenant Context
    query = db.query(User).filter(User.username == form_data.username)
    
    if target_tenant_id:
        # Resolve Slug/ID to UUID
        tenant_obj = db.query(Tenant).filter(
            (Tenant.slug == target_tenant_id) | (Tenant.internal_tenant_id == target_tenant_id) | (Tenant.id == target_tenant_id)
        ).first()
        
        if not tenant_obj:
             # If tenant validation fails, generic error
             pass # continue to user query which will fail safely
        else:
             target_uuid = tenant_obj.internal_tenant_id
             # Verify Tenant Active Status
             if not tenant_obj.is_active:
                  raise HTTPException(status_code=403, detail="Workspace is deactivated. Contact Support.")
             
             # Filter User by Resulting UUID
             query = query.filter(User.tenant_id == target_uuid)
             
    else:
        # Fallback: If no header, assume default_tenant OR handle ambiguity.
        # For now, let's prefer 'default_tenant' logic if we want to restrict generic logins
        # or just let it match parameters.
        # Ideally, we should require context for non-unique usernames.
        # But for 'admin' (super admin), they are in 'default_tenant'.
        query = query.filter(User.tenant_id == "default_tenant")

    user = query.first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Improved error message for debugging (though purely generic for security)
        # We'll just say Invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password, or invalid workspace context",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Double check tenant status if we found the user (redundant if we checked via header, but good for safety)
    if user.tenant_id != "default_tenant":
        tenant = db.query(Tenant).filter(Tenant.slug == user.tenant_id).first()
        if tenant and not tenant.is_active:
            raise HTTPException(status_code=403, detail="Workspace is deactivated. Contact Support.")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "tenant_id": user.tenant_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



from fastapi import Response

@router.options("/me")
async def options_me():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

# --- IMPERSONATION ENDPOINT ---
from pydantic import BaseModel
class ImpersonateRequest(BaseModel):
    tenant_id: str

@router.post("/impersonate", response_model=Token)
def impersonate(
    request: ImpersonateRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Super Admin only: Generate a token scoped to a specific tenant.
    """
    if current_user.role != 'admin' and not current_user.is_superuser:
         raise HTTPException(status_code=403, detail="Only admins can impersonate")
         
    # Verify target tenant exists (by checking if any user belongs to it)
    # Since we don't have a distinct Tenant table yet, we check User table usage
    exists = db.query(User).filter(User.tenant_id == request.tenant_id).first()
    if not exists:
         raise HTTPException(status_code=404, detail="Target tenant not found")
         
    # Check Tenant Status
    target_tenant = db.query(Tenant).filter(Tenant.slug == request.tenant_id).first()
    if target_tenant and not target_tenant.is_active:
         raise HTTPException(status_code=403, detail="Cannot impersonate: Workspace is deactivated.")
         
    # Generate Token scoped to target tenant
    # Note: 'sub' remains the admin's username, but 'tenant_id' is swapped.
    # This allows auditing who performed the action (admin).
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "tenant_id": request.tenant_id, "mode": "impersonation"}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}