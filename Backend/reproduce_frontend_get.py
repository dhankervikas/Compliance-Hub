
import requests
import json

# Using the debug script to simulate what the frontend sees for /frameworks
# We need to see if the API returns them as "active" or just returns them at all for the tenant.

API_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123" # Confirmed via seed script output
TENANT_SLUG = "testtest" # Target tenant

def check_frontend_view():
    # Login as Global Admin (No Tenant Header)
    print("\n--- Login as Global Admin ---")
    res = requests.post(f"{API_URL}/auth/login", 
                       data={"username": USERNAME, "password": PASSWORD}) 
                       # No "X-Target-Tenant-ID" -> defaults to 'default_tenant'
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return

    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Simulate EntitlementContext logic for Admin viewing Tenant
    # "if (tenantId && user.role === 'admin' && user.tenant_id !== tenantId)"
    # It calls: /tenants/{id}/entitlements
    target_endpoint = f"{API_URL}/users/tenants/{TENANT_SLUG}/entitlements" # Added /users prefix
    print(f"\n--- GET {target_endpoint} ---")
    
    ent_res = requests.get(target_endpoint, headers=headers)
    print(f"Status: {ent_res.status_code}")
    if ent_res.status_code == 200:
        print(json.dumps(ent_res.json(), indent=2))
        data = ent_res.json()
        active_cnt = sum(1 for f in data["frameworks"] if f.get("is_active"))
        print(f"\nActive Frameworks Count: {active_cnt}")
    else:
        print(ent_res.text)

if __name__ == "__main__":
    check_frontend_view()
