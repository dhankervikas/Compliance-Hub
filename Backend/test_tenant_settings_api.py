
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Login as Super Admin
def login_admin():
    url = f"{BASE_URL}/auth/login"
    payload = {"username": "admin", "password": "admin"}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Login failed: {response.text}")
    return None

def test_tenant_frameworks():
    token = login_admin()
    if not token:
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get first tenant (not default)
    tenants = requests.get(f"{BASE_URL}/users/tenants", headers=headers).json()
    if not tenants:
        print("No tenants found.")
        return
        
    target_tenant = next((t for t in tenants if t['tenant_id'] != 'default_tenant'), None)
    if not target_tenant:
        print("No test tenant found.")
        return
        
    slug = target_tenant['tenant_id']
    print(f"Testing for Tenant: {slug}")
    
    # 3. List Frameworks
    res = requests.get(f"{BASE_URL}/users/tenants/{slug}/frameworks", headers=headers)
    print(f"GET Status: {res.status_code}")
    if res.status_code == 200:
        frameworks = res.json()
        print("Current Frameworks:")
        for fw in frameworks:
            print(f" - {fw['name']} ({fw['code']}): {'Active' if fw['is_active'] else 'Inactive'}")
            
        # 4. Toggle the first framework
        if frameworks:
            first_fw = frameworks[0]
            new_state = not first_fw['is_active']
            
            # Construct payload with ALL currently active IDs + toggled one
            active_ids = [fw['id'] for fw in frameworks if fw['is_active']]
            
            if new_state:
                if first_fw['id'] not in active_ids:
                    active_ids.append(first_fw['id'])
            else:
                if first_fw['id'] in active_ids:
                    active_ids.remove(first_fw['id'])
            
            print(f"Updating... Setting {first_fw['code']} to {new_state}")
            update_res = requests.put(
                f"{BASE_URL}/users/tenants/{slug}/frameworks",
                headers=headers,
                json={"framework_ids": active_ids}
            )
            print(f"PUT Status: {update_res.status_code}")
            print(update_res.json())
            
            # Verify update
            verify_res = requests.get(f"{BASE_URL}/users/tenants/{slug}/frameworks", headers=headers)
            verify_fw = next(f for f in verify_res.json() if f['id'] == first_fw['id'])
            print(f"Verification: {first_fw['code']} is now {'Active' if verify_fw['is_active'] else 'Inactive'}")

if __name__ == "__main__":
    test_tenant_frameworks()
