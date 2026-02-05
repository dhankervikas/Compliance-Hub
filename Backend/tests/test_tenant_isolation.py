import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.cloud_resource import CloudResource
from app.utils.security import create_access_token, get_password_hash
from app.api import auth

# Setup Test Client
client = TestClient(app)

# Helper to create tokens
def create_test_token(username, tenant_id):
    # We must ensure the user exists in DB for get_current_user dependency 
    # because verify_tenant checks token, but get_current_user checks DB.
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username, 
            email=f"{username}@test.com", 
            hashed_password=get_password_hash("pw"), 
            full_name=username,
            tenant_id=tenant_id,
            is_active=True
        )
        db.add(user)
        db.commit()
    db.close()
    
    return create_access_token(data={"sub": username, "tenant_id": tenant_id})

def test_tenant_isolation():
    print("\n--- Starting Tenant Isolation Test ---")
    
    # 1. Setup Data - Create Resource for Tenant BETA
    db = SessionLocal()
    
    # Create Beta Resource
    # Since we are adding to a persistent DB (SQLite dev), we should be careful or clean up.
    # For this test, we create a unique ID to avoid collision or rely on auto-increment.
    beta_resource = CloudResource(
        tenant_id="Tenant_Beta",
        provider="aws", 
        resource_type="s3_bucket", 
        resource_id="beta-secret-bucket-999",
        compliance_metadata="ENCRYPTED_SECRET_DATA"
    )
    db.add(beta_resource)
    db.commit()
    db.refresh(beta_resource)
    target_id = beta_resource.id
    
    print(f"[Setup] Created Resource ID {target_id} for 'Tenant_Beta'")
    db.close()
    
    # 2. Attack: Tenant ALPHA tries to access Beta Resource
    # Generate Token for Alpha
    token = create_test_token("alpha_user", "Tenant_Alpha")
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"[Action] Requesting Resource {target_id} as 'Tenant_Alpha'...")
    response = client.get(f"/api/v1/cloud-resources/{target_id}", headers=headers)
    
    print(f"[Result] Status Code: {response.status_code}")
    print(f"[Result] Body: {response.json()}")
    
    # 3. Assert
    # We expect 404 because our logic returns 404 if tenant mismatch to hide existence
    if response.status_code == 404:
        print("\n[PASS] Resource Not Found (correctly hidden).")
    elif response.status_code == 403:
        print("\n[PASS] Access Forbidden.")
    else:
        print(f"\n[FAIL] Expected 404/403, got {response.status_code}")
        pytest.fail(f"Security Breach! Status Code: {response.status_code}")

if __name__ == "__main__":
    # Allow running directly
    test_tenant_isolation()
