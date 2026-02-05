
import requests
import json
import sys

# Set encoding to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://assurisk-backend.onrender.com/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

def get_token():
    try:
        resp = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        if resp.status_code == 200:
            return resp.json().get("access_token")
        else:
            print(f"Login failed: {resp.text}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def list_processes():
    token = get_token()
    if not token: return

    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching Processes...")
    try:
        resp = requests.get(f"{BASE_URL}/processes/", headers=headers)
        if resp.status_code == 200:
            procs = resp.json()
            print(f"Found {len(procs)} Process Groups:\n")
            for p in procs:
                print(f"* {p['name']}")
                if "sub_processes" in p and p["sub_processes"]:
                    for sp in p["sub_processes"]:
                        print(f"    - {sp['name']}")
                else:
                    print("    (No sub-processes)")
                print("")
        else:
            print(f"Error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error fetching: {e}")

if __name__ == "__main__":
    list_processes()
