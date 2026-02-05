import requests

BASE_URL = "http://localhost:8001/api/v1"
SLUG = "testtest"
# I need the UUID. I'll use the one I found earlier or fetch it from DB if needed, 
# but hardcoding it from previous logs is faster: a61624c9-b0d9-4125-9bd5-edf7af8fb78e
UUID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" 

# Authenticate
try:
    auth_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
    if auth_res.status_code != 200:
        print(f"Auth Failed: {auth_res.text}")
        exit()
    token = auth_res.json()["access_token"]
    print("Auth Successful. Token obtained.")
except Exception as e:
    print(f"Auth Error: {e}")
    exit()

def test_header(val, label):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Tenant-ID": val
    }

    print(f"--- Testing Framework Details for ID 1 with {label}: {val} ---")
    try:
        res = requests.get(f"{BASE_URL}/frameworks/1", headers=headers) 
        if res.status_code == 200:
            data = res.json()
            print(f"Framework 1: {data.get('name')} (Code: {data.get('code')}) - Active: {data.get('is_active')}")
        else:
            print(f"Framework 1 Status: {res.status_code}")
            print(res.text) 
            
        res_stats = requests.get(f"{BASE_URL}/frameworks/1/stats", headers=headers)
        if res_stats.status_code == 200:
             print(f"Stats: {res_stats.json()}")
        else:
             print(f"Stats Failed: {res_stats.status_code} - {res_stats.text}")
             
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

if __name__ == "__main__":
    # Test 1: Slug
    test_header(SLUG, "Slug")
    
    # Test 2: No Header (Default Context - likely Admin's own tenant)
    print("--- Testing DEFAULT Context (No X-Target-Tenant-ID) ---")
    headers_default = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{BASE_URL}/frameworks/1", headers=headers_default)
        print(f"Default Framework 1: {res.status_code}")
        if res.status_code != 200:
            print(res.text)
    except Exception as e:
        print(f"Default Error: {e}")

    # Test 3: Controls (Heavy Load)
    print("--- Testing CONTROLS Endpoint ---")
    try:
        # Use headers with SLUG to match dashboard behavior if possible
        headers_slug = {"Authorization": f"Bearer {token}", "X-Target-Tenant-ID": SLUG}
        res = requests.get(f"{BASE_URL}/controls/?limit=10", headers=headers_slug)
        print(f"Controls: {res.status_code}")
        if res.status_code != 200:
            print(res.text)
    except Exception as e:
        print(f"Controls Error: {e}")

    # Test 4: Settings
    print("--- Testing SETTINGS Endpoint ---")
    try:
        res = requests.get(f"{BASE_URL}/settings", headers=headers_slug)
        print(f"Settings: {res.status_code}")
        if res.status_code != 200:
            print(res.text)
    except Exception as e:
        print(f"Settings Error: {e}")
