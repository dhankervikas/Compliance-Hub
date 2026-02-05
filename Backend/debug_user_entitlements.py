import requests
import json

# URL that Frontend calls:
AUTH_URL = "http://localhost:8000/api/v1/auth/login"
ENTITLEMENTS_URL = "http://localhost:8000/api/v1/users/me/entitlements"

def debug_user_entitlements():
    # 1. Login as Tenant User 'testtest'
    # Assuming standard pattern: testtest@assurisk.ai / testtest123 OR just username 'testtest'
    # Backend create_tenant uses 'admin_username' as username. 
    # usually it's just the username provided in wizard.
    # Let's try likely candidates.
    
    token = None
    
    # Try header based masquerade first (as frontend might be doing if Admin is logged in??)
    # Wait, the user is likely logged in as the Tenant Admin created during onboarding.
    # The screenshot URL is /t/testtest/dashboard.
    # If I can't guess pass, I will use Admin Impersonation to get a token for that tenant context.
    
    print("Attempting to get token via Admin (Impersonation)...")
    # Login as Super Admin
    resp = requests.post(AUTH_URL, data={"username": "admin", "password": "admin123"})
    if resp.status_code == 200:
        admin_token = resp.json()["access_token"]
        # Impersonate
        headers = {"Authorization": f"Bearer {admin_token}"}
        imp_resp = requests.post("http://localhost:8000/api/v1/auth/impersonate", 
                               json={"tenant_id": "testtest"}, headers=headers)
        if imp_resp.status_code == 200:
            token = imp_resp.json()["access_token"]
            print("Got Impersonation Token for 'testtest'")
    
    if not token:
        print("Failed to get token.")
        return

    # 2. Call /me/entitlements
    headers = {"Authorization": f"Bearer {token}"}
    print(f"GET {ENTITLEMENTS_URL}...")
    resp = requests.get(ENTITLEMENTS_URL, headers=headers)
    
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
        
        # Check active status
        frameworks = data.get("frameworks", [])
        active_cnt = len([f for f in frameworks if f.get("is_active")])
        print(f"Active Frameworks Found: {active_cnt}")
        iso = next((f for f in frameworks if "ISO" in f["name"] or "27001" in f["code"]), None)
        if iso:
             print(f"ISO 27001: {iso}")
    else:
        print(resp.text)

if __name__ == "__main__":
    debug_user_entitlements()
