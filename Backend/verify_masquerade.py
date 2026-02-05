
import requests
import sys
import os

# Add backend to path to import utils
sys.path.append(os.path.join(os.getcwd(), "Backend"))
from app.utils.security import create_access_token
from app.config import settings

def get_admin_token():
    # Generate a token for admin@default_tenant
    data = {"sub": "admin", "tenant_id": "default_tenant"}
    token = create_access_token(data=data)
    return token

def verify_masquerade(base_url, token, target_tenant_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Tenant-ID": target_tenant_id
    }
    
    # 1. Check Framework Stats (The endpoint that was failing)
    # NIST CSF 2.0 has ID 5 (from previous steps)
    url = f"{base_url}/frameworks/5/stats" 
    
    print(f"Checking {url} with Header X-Target-Tenant-ID: {target_tenant_id}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Stats Code: {response.status_code}")
            print(f"Total Controls: {data['total_controls']}")
            
            if data['total_controls'] > 0:
                print("PASS: Controls found for target tenant.")
            else:
                print("FAIL: Still showing 0 controls.")
        else:
            print(f"Request failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    BASE_URL = "http://localhost:8005/api/v1"
    TARGET_TENANT = "testtest" 
    
    print("--- Verifying Masquerade Logic (With Generated Token) ---")
    
    try:
        # Generate Token Locally (Bypassing Login)
        print("Generating Super Admin Token...")
        token = get_admin_token()
        print(f"Token: {token[:10]}...")
        
        # Test 1: Check Stats
        verify_masquerade(BASE_URL, token, TARGET_TENANT)
        
    except Exception as e:
        print(f"Error: {e}")
