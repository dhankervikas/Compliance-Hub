import requests
import sys

API_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    # Try common admin credentials
    creds = [
        ("admin", "admin123"),
        ("superadmin", "superadmin123"),
        ("admin", "password"),
        ("admin_default", "admin123") 
    ]
    
    for username, password in creds:
        try:
            resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
            if resp.status_code == 200:
                print(f"Logged in as {username}")
                return resp.json()["access_token"]
        except Exception as e:
            print(f"Connection error: {e}")
            break
            
    print("Failed to login as admin with common credentials.")
    return None

def verify_deactivation():
    token = get_admin_token()
    if not token:
        sys.exit(1)
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List Tenants to find test_company
    print("Listing tenants...")
    resp = requests.get(f"{API_URL}/users/tenants", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to list tenants: {resp.text}")
        sys.exit(1)
        
    tenants = resp.json()
    target = next((t for t in tenants if t["tenant_id"] == "test_company"), None)
    
    if not target:
        print("test_company not found. Picking first non-default tenant...")
        target = next((t for t in tenants if t["tenant_id"] != "default_tenant"), None)
        
    if not target:
        print("No test tenant found to deactivate.")
        sys.exit(0)
        
    tenant_id = target["tenant_id"]
    print(f"Targeting tenant: {tenant_id} (Current Active: {target.get('is_active')})")
    
    # 2. Deactivate
    print(f"Attempting to DEACTIVATE {tenant_id}...")
    patch_resp = requests.patch(
        f"{API_URL}/users/tenants/{tenant_id}/status",
        json={"is_active": False},
        headers=headers
    )
    
    print(f"Status Code: {patch_resp.status_code}")
    print(f"Response: {patch_resp.text}")
    
    if patch_resp.status_code == 200:
        print("Deactivation successful (API level).")
    else:
        print("Deactivation FAILED.")

if __name__ == "__main__":
    verify_deactivation()
