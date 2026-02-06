import requests
import json
import sys

# Config
BASE_URL = "http://localhost:8000/api/v1"
TENANT_SLUG = "testtest"
# Token from verify_wizard_backend.py (valid until ~03:56 Z)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInRlbmFudF9pZCI6ImRlZmF1bHRfdGVuYW50IiwiZXhwIjoxNzcwMzUwMTY1fQ.sqiggW_js59QCQprqh6Z9hnfil4yYP8C7s0O9sJ0Edc"

def check_entitlements(token, tenant_slug):
    # Endpoint: /users/me/entitlements
    # Note: Logic uses current_user.tenant_id, but the token has "default_tenant". 
    # However, the endpoint `_get_entitlements_logic` is also used by `get_tenant_entitlements` (Admin only).
    # Since we are using an admin token (default_tenant), we should use the ADMIN endpoint to check a specific tenant.
    # OR, we need to impersonate? 
    # The token above is for "admin" in "default_tenant".
    # If I call /users/me/entitlements, it will check "default_tenant" which is not what we want.
    
    # We should call /tenants/{tenant_id}/entitlements
    url = f"{BASE_URL}/users/tenants/{tenant_slug}/entitlements" 
    # Wait, the route in users.py is: @router.get("/tenants/{tenant_id}/entitlements", ...)
    url = f"{BASE_URL}/users/tenants/{tenant_slug}/entitlements"
    
    print(f"Checking entitlements for {tenant_slug}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(json.dumps(data, indent=2))
            
            # Validation
            frameworks = data.get("frameworks", [])
            active = [f for f in frameworks if f["is_active"]]
            print(f"Active Frameworks: {[f['code'] for f in active]}")
            
            if not active:
                print("FAIL: No active frameworks found in entitlements!")
                sys.exit(1)
            else:
                print("PASS: Active frameworks found.")
        else:
            print(f"Failed: {response.status_code} {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_entitlements(TOKEN, TENANT_SLUG)
