
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"

def debug_api():
    # 1. Login
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            # Try new admin email format if simple admin fails
            resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin_1@default_tenant.local", "password": "admin123"})
            if resp.status_code != 200:
                print("Double login failure. Credentials changed?")
                return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in. Token acquired.")

    # 2. Fetch Processes
    print("Fetching ISO27001 processes...")
    resp = requests.get(f"{BASE_URL}/processes/", params={"framework_code": "ISO27001"}, headers=headers)
    
    if resp.status_code != 200:
        print(f"Fetch failed: {resp.status_code} {resp.text}")
        return

    data = resp.json()
    print(f"Got {len(data)} processes.")
    
    # 3. Inspect first control
    if data and data[0].get("sub_processes"):
        sp = data[0]["sub_processes"][0]
        print(f"SubProcess: {sp['name']}")
        if sp.get("controls"):
            c = sp["controls"][0]
            print(f"Control: {c['control_id']}")
            print(f"  Framework ID: {c.get('framework_id')}")
            print(f"  Status: {c.get('status')}")
        else:
            print("  No controls in first subprocess.")
    else:
        print("  Structure unexpected or empty.")

if __name__ == "__main__":
    debug_api()
