import requests
import json

# Login as admin to get token
BASE_URL = "http://localhost:8000/api/v1"

def debug_entitlements():
    # 1. Login
    login_payload = {"username": "admin@assurisk.ai", "password": "admin123"} # Use email if username fails, or check auth.py. 
    # Actually backend uses OAuth2PasswordRequestForm which takes username/password fields.
    # The default admin username is 'admin', password 'admin123'. 
    # But endpoint requires form data.
    resp = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": "admin", "password": "admin123"})
    if resp.status_code != 200:
        print("Login Failed")
        print(resp.text)
        return
        
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Tenant Slug
    # We are impersonating or just accessing as admin? 
    # API /tenants/{id}/entitlements is Admin Only.
    # Frontend uses /me/entitlements (User) or /tenants/... (Admin)
    
    # Let's check the ADMIN view for 'testtest'
    target_slug = "testtest"
    
    print(f"Fetching Entitlements for {target_slug}...")
    url = f"{BASE_URL}/users/tenants/{target_slug}/entitlements"
    
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
        
        # Check active status of ISO
        frameworks = data.get("frameworks", [])
        iso = next((f for f in frameworks if "ISO" in f["name"] or "27001" in f["code"]), None)
        if iso:
            print(f"ISO 27001 Found: Active={iso.get('is_active')}")
        else:
            print("ISO 27001 NOT FOUND in response")
            
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(resp.text)

if __name__ == "__main__":
    debug_entitlements()
