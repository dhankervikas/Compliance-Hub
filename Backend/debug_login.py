
import requests

def debug_login():
    url = "http://localhost:8002/api/v1/auth/login"
    username = "admin"
    password = "admin123"
    tenant_id = "testtest"
    
    print(f"Attempting Login to: {url}")
    print(f"User: {username}, Tenant: {tenant_id}")
    
    # 1. Try with Header
    try:
        res = requests.post(
            url,
            data={"username": username, "password": password},
            headers={"X-Target-Tenant-ID": tenant_id}
        )
        print(f"\n[Header Auth] Status: {res.status_code}")
        if res.status_code == 200:
            print(" -> SUCCESS")
            print(res.json())
        else:
            print(f" -> FAILED: {res.text}")
    except Exception as e:
        print(f" -> ERROR: {e}")

    # 2. Try without Header (Default Tenant)
    try:
        print(f"\n[Default Auth] Attempting without header...")
        res = requests.post(
            url,
            data={"username": username, "password": password}
        )
        print(f" -> Status: {res.status_code}")
        if res.status_code == 200:
             print(" -> SUCCESS (Logged into default?)")
             print(res.json())
    except Exception as e:
        print(f" -> ERROR: {e}")

if __name__ == "__main__":
    debug_login()
