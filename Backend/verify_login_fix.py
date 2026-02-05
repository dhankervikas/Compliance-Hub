
import requests

URL = "http://localhost:8002/api/v1/auth/login"
HEADERS = {"X-Target-Tenant-ID": "testtest"}
DATA = {"username": "admin", "password": "password"}

try:
    print(f"Attempting login to {URL}...")
    # Form data encoding for OAuth2
    resp = requests.post(URL, headers=HEADERS, data=DATA)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    if resp.status_code == 200:
        print("LOGIN SUCCESS!")
    else:
        print("LOGIN FAILED.")
except Exception as e:
    print(f"Error: {e}")
