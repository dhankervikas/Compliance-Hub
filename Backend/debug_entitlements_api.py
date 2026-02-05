
import requests
import json
import sys

# Config
API_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "password" # Assuming default from initial setup or seeding
TENANT_SLUG = "testtest"

def debug_api():
    print(f"Target: {API_URL}")
    
    # 1. Login as Admin
    try:
        login_url = f"{API_URL}/auth/login"
        login_payload = {
            "username": USERNAME,
            "password": PASSWORD
        }
        # Explicitly target testtest tenant context
        headers = {"X-Target-Tenant-ID": TENANT_SLUG}
        
        print(f"Logging in to {login_url} with context {TENANT_SLUG}...")
        res = requests.post(login_url, data=login_payload, headers=headers) 
        
        if res.status_code != 200:
            print(f"Login Failed: {res.status_code} - {res.text}")
            return

        admin_token = res.json().get("access_token")
        print("Admin Login Successful.")
        
        # 2. Impersonate Tenant
        impersonate_url = f"{API_URL}/auth/impersonate"
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"tenant_id": TENANT_SLUG}
        
        print(f"Impersonating {TENANT_SLUG}...")
        res = requests.post(impersonate_url, json=payload, headers=headers)
        
        if res.status_code != 200:
            print(f"Impersonation Failed: {res.status_code} - {res.text}")
            return
            
        tenant_token = res.json().get("access_token")
        print("Impersonation Successful. Tenant Token obtained.")

        # 3. Fetch Entitlements
        tenant_headers = {"Authorization": f"Bearer {tenant_token}"}
        ent_url = f"{API_URL}/users/me/entitlements"
        print(f"Fetching entitlements from {ent_url}...")
        ent_res = requests.get(ent_url, headers=tenant_headers)
        
        print("\n--- ENTITLEMENTS RESPONSE ---")
        print(json.dumps(ent_res.json(), indent=2))
        
        # 4. Check Frameworks Endpoint directly (Catalog)
        fw_res = requests.get(f"{API_URL}/frameworks/", headers=tenant_headers)
        print("\n--- FRAMEWORKS API RESPONSE ---")
        fws = fw_res.json()
        for fw in fws:
             print(f"ID: {fw.get('id')} | Code: {fw.get('code')} | Name: {fw.get('name')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
