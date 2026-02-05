
import requests
import sys

BASE_URL = "http://localhost:8002/api/v1"

def test_http_get():
    # 1. Login
    login_url = f"{BASE_URL}/auth/login"
    creds = {
        "username": "admin",
        "password": "admin123"
    }
    # Important: Set the X-Target-Tenant-ID header if needed? 
    # But wait, "admin" is globally unique in my head, but user logic says "admin" in "testtest".
    # User model says `unique_username_per_tenant`.
    # Login endpoint uses `X-Target-Tenant-ID` header to distinguish if usernames are duplicated across tenants.
    # If I don't send it, it defaults to "default_tenant".
    # And "admin" exists in "default_tenant" (System Admin).
    # So if I login as "admin" without header, I get System Admin token!
    # System Admin -> default_tenant -> get_settings -> default_tenant settings -> Success (probably).
    
    # BUT the user is trying to access "testtest".
    # The Frontend Login component for "Magic Link" /t/testtest/login sends `X-Target-Tenant-ID`.
    # Let's assume the user logged in via the Tenant Login page.
    
    headers = {
        "X-Target-Tenant-ID": "testtest" 
    }
    
    print(f"Logging in as 'admin' for tenant 'testtest'...")
    try:
        res = requests.post(login_url, data=creds, headers=headers)
    except requests.exceptions.ConnectionError:
        print("CRITICAL: Backend not running at http://localhost:8000")
        sys.exit(1)
        
    if res.status_code != 200:
        print(f"Login Failed: {res.status_code} {res.text}")
        # Try without header just in case I messed up the header name
        # res = requests.post(login_url, data=creds)
        # print(f"Login Retry: {res.status_code} {res.text}")
        return

    token = res.json().get("access_token")
    print("Login Success. Token received.")
    
    # 2. Get Settings
    settings_url = f"{BASE_URL}/settings/org_profile"
    auth_headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"GET {settings_url}...")
    res = requests.get(settings_url, headers=auth_headers)
    
    print(f"Status: {res.status_code}")
    print(f"content-type: {res.headers.get('content-type')}")
    print(f"Body: {res.text}")

if __name__ == "__main__":
    test_http_get()
