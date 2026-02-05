
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_login(username, password, tenant_id=None):
    print(f"[-] Testing login for user: '{username}' in tenant: '{tenant_id}'")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    headers = {}
    if tenant_id:
        headers["X-Target-Tenant-ID"] = tenant_id
        
    try:
        response = requests.post(url, data=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("[SUCCESS] Login successful!")
            print(f"Token: {response.json().get('access_token')[:20]}...")
        else:
            print(f"[FAILED] Login failed: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    # Test 1: Admin in testtest (The failure case)
    test_login("admin", "admin", "testtest")
    
    print("-" * 20)
    
    # Test 2: Admin in default_tenant (Should work)
    test_login("admin", "admin", None)
