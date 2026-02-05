import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.scope_justification import ScopeJustification
from app.utils.security import create_access_token, get_password_hash
import uuid

# Setup Test Client
client = TestClient(app)

# Helper to create tokens (Copied from test_tenant_isolation to be standalone)
def create_test_token(username, tenant_id):
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

def test_scope_isolation_by_standard():
    print("\n--- Starting Scope By Standard Isolation Test ---")
    
    tenant_id = f"Tenant_Scope_{uuid.uuid4().hex[:8]}"
    username = f"scope_auditor_{uuid.uuid4().hex[:8]}"
    
    # 1. Setup Data
    db = SessionLocal()
    
    # Create ISO Record
    iso_scope = ScopeJustification(
        tenant_id=tenant_id,
        standard_type="ISO27001",
        criteria_id="A.5.1",
        reason_code="NOT_APPLICABLE",
        justification_text="ISO Only Reason"
    )
    
    # Create SOC2 Record
    soc_scope = ScopeJustification(
        tenant_id=tenant_id,
        standard_type="SOC2",
        criteria_id="CC1.1",
        reason_code="NOT_APPLICABLE",
        justification_text="SOC Only Reason"
    )
    
    db.add(iso_scope)
    db.add(soc_scope)
    db.commit()
    db.close()
    
    print(f"[Setup] Created ISO and SOC2 scope records for '{tenant_id}'")
    
    # 2. Get Token
    token = create_test_token(username, tenant_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test ISO Filter
    print("[Action] Fetching with standard_type='ISO27001'...")
    res_iso = client.get("/api/v1/scope/justifications?standard_type=ISO27001", headers=headers)
    assert res_iso.status_code == 200
    data_iso = res_iso.json()
    print(f"[Result] Got {len(data_iso)} records")
    
    assert len(data_iso) == 1
    assert data_iso[0]["standard_type"] == "ISO27001"
    assert data_iso[0]["criteria_id"] == "A.5.1"
    print("[PASS] ISO Filter strictly returned only ISO data.")

    # 4. Test SOC2 Filter
    print("[Action] Fetching with standard_type='SOC2'...")
    res_soc = client.get("/api/v1/scope/justifications?standard_type=SOC2", headers=headers)
    assert res_soc.status_code == 200
    data_soc = res_soc.json()
    print(f"[Result] Got {len(data_soc)} records")
    
    assert len(data_soc) == 1
    assert data_soc[0]["standard_type"] == "SOC2"
    assert data_soc[0]["criteria_id"] == "CC1.1"
    print("[PASS] SOC2 Filter strictly returned only SOC2 data.")
    
    # 5. Test Cross-Tenant Isolation (Extra Benefit)
    other_token = create_test_token("hacker", "Tenant_Other")
    res_other = client.get("/api/v1/scope/justifications", headers={"Authorization": f"Bearer {other_token}"})
    assert res_other.status_code == 200
    assert len(res_other.json()) == 0
    print("[PASS] Cross-Tenant Isolation verified (0 records for other tenant).")

if __name__ == "__main__":
    test_scope_isolation_by_standard()
