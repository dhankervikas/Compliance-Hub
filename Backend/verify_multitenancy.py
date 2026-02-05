import requests
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.framework import Framework
from app.utils.security import get_password_hash, create_access_token
from datetime import timedelta

# Setup DB connection directly for setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_URL = "http://localhost:8000/api/v1"

def setup_users():
    db = SessionLocal()
    
    # 1. Ensure Admin (Default Tenant)
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        print("Admin user not found. Please run the server once to seed it.")
        sys.exit(1)
    
    # 2. Create/Get Tenant User (Test Tenant)
    tenant_user = db.query(User).filter(User.username == "tenant_user").first()
    if not tenant_user:
        tenant_user = User(
            email="tenant@test.com",
            username="tenant_user",
            full_name="Tenant User",
            hashed_password=get_password_hash("test1234"),
            tenant_id="test_tenant_A", # EXPLICIT DIFFERENT TENANT
            is_active=True
        )
        db.add(tenant_user)
        db.commit()
        db.refresh(tenant_user)
        print("Created 'tenant_user' in 'test_tenant_A'")
    else:
        # Ensure tenant_id is correct (in case checking old user)
        if tenant_user.tenant_id != "test_tenant_A":
            tenant_user.tenant_id = "test_tenant_A"
            db.commit()
            print("Updated 'tenant_user' to 'test_tenant_A'")

    db.close()
    return admin, tenant_user

def get_token(username, tenant_id):
    # Retrieve user to get role/id if needed, but we essentially duplicate login logic
    # Actually, simpler to just spoof the token using the secret from config?
    # Or call the login endpoint?
    # Calling login endpoint works if password is known.
    
    if username == "admin":
        password = "admin123"
    else:
        password = "test1234"
        
    resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Login failed for {username}: {resp.text}")
        sys.exit(1)
    
    # Check if the token claims have the correct tenant_id
    # We can decode or trust.
    # The API /auth/login uses user.tenant_id from DB.
    return resp.json()["access_token"]

def verify_isolation():
    print("\n--- VERIFYING MULTITENANCY ---")
    
    # 1. Setup
    setup_users()
    
    # 2. Get Tokens
    admin_token = get_token("admin", "default_tenant")
    tenant_token = get_token("tenant_user", "test_tenant_A")
    
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_tenant = {"Authorization": f"Bearer {tenant_token}"}
    
    # 3. Create Admin Framework
    print("\n[ADMIN] Creating 'Admin Secret Framework'...")
    fw_data = {
        "name": "Admin Secret Framework",
        "code": "ADMIN_SEC_001",
        "description": "Only for default tenant",
        "version": "1.0"
    }
    # Check if exists first to avoid error
    check = requests.get(f"{API_URL}/frameworks/", headers=headers_admin)
    existing = [f for f in check.json() if f["code"] == "ADMIN_SEC_001"]
    if not existing:
        resp = requests.post(f"{API_URL}/frameworks/", json=fw_data, headers=headers_admin)
        if resp.status_code != 201:
            print(f"Failed to create admin framework: {resp.text}")
    else:
        print("Admin framework already exists.")

    # 4. Create Tenant Framework
    print("\n[TENANT] Creating 'Tenant Secret Framework'...")
    fw_data_t = {
        "name": "Tenant Secret Framework V2",
        "code": "TENANT_SEC_NEW",
        "description": "Only for test tenant",
        "version": "1.0"
    }
    check_t = requests.get(f"{API_URL}/frameworks/", headers=headers_tenant)
    existing_t = [f for f in check_t.json() if f["code"] == "TENANT_SEC_NEW"]
    if not existing_t:
        resp = requests.post(f"{API_URL}/frameworks/", json=fw_data_t, headers=headers_tenant)
        if resp.status_code != 201:
            print(f"Failed to create tenant framework: {resp.text}")
    else:
         print("Tenant framework already exists.")

    # 5. Verify Visibility FROM ADMIN
    print("\n[CHECK] Admin Visibility:")
    resp_a = requests.get(f"{API_URL}/frameworks/", headers=headers_admin)
    fws_a = resp_a.json()
    codes_a = [f["code"] for f in fws_a]
    print(f"Admin sees: {codes_a}")
    
    if "ADMIN_SEC_001" in codes_a and "TENANT_SEC_NEW" not in codes_a:
        print("PASS: Admin sees Admin Framework and NOT Tenant Framework (V2).")
    else:
        print("FAIL: Admin visibility incorrect.")

    # 6. Verify Visibility FROM TENANT
    print("\n[CHECK] Tenant Visibility:")
    resp_t = requests.get(f"{API_URL}/frameworks/", headers=headers_tenant)
    fws_t = resp_t.json()
    codes_t = [f["code"] for f in fws_t]
    print(f"Tenant sees: {codes_t}")
    
    if "TENANT_SEC_NEW" in codes_t and "ADMIN_SEC_001" not in codes_t and "ISO27001" not in codes_t: 
        print("PASS: Tenant sees Tenant Framework (V2) and NOT Admin Framework.")
    else:
        print("FAIL: Tenant visibility incorrect.")
        
    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_isolation()
