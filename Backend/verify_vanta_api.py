import requests
import json

try:
    # 1. Login
    login_payload = {"username": "admin", "password": "admin123"}
    auth_response = requests.post("http://127.0.0.1:8002/api/v1/auth/login", data=login_payload)
    
    if auth_response.status_code != 200:
        print(f"Login Failed: {auth_response.status_code} - {auth_response.text}")
        exit(1)
        
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Processes
    response = requests.get("http://127.0.0.1:8002/api/v1/processes?framework_code=ISO27001", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"API Success. Found {len(data)} processes.")
        for p in data:
            print(f"Process: {p['name']}")
            # Check for controls wrapped in subprocess
            if p['sub_processes']:
                sp = p['sub_processes'][0]
                print(f"  -> SubProcess: {sp['name']} (Controls: {len(sp['controls'])})")
                if sp['controls']:
                    print(f"     First Control: {sp['controls'][0]['control_id']} - {sp['controls'][0]['title']}")
        
        # Calculate Grand Total
        total_controls = sum(len(p['sub_processes'][0]['controls']) for p in data if p['sub_processes'])
        print(f"\nGRAND TOTAL CONTROLS FOUND: {total_controls}")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection Failed: {e}")
