
import requests
import sys
import os

# Add data dir to path (optional, but we import directly)
from data.iso_27001_full import ISO_CONTROLS_DATA

BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

def classify_control(title, desc):
    text = (title + " " + desc).lower()
    triggers = [
        "cloud", "aws", "azure", "network", "backup", "log", "monitor", 
        "encrypt", "crypto", "malware", "vulnerability", "patch", 
        "config", "source code", "endpoint", "technical", "access rights",
        "authentication", "mfa"
    ]
    if any(t in text for t in triggers):
        return "AUTO"
    return "MANUAL"

def get_token():
    print(f"Logging in as {USERNAME}...")
    try:
        resp = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        if resp.status_code == 200:
            return resp.json().get("access_token")
        else:
            print(f"Login failed: {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

def main():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Ensure ISO Framework Exists
    print("Checking ISO 27001 Framework...")
    fw_code = "ISO27001_2022"
    fw_id = None
    
    fws = requests.get(f"{BASE_URL}/frameworks/", headers=headers).json()
    existing_fw = next((f for f in fws if f["code"] == fw_code), None)
    
    if existing_fw:
        fw_id = existing_fw["id"]
        print(f"Found Framework ID: {fw_id}")
    else:
        print("Creating Framework...")
        payload = {
            "name": "ISO/IEC 27001:2022",
            "code": fw_code,
            "description": "Information security management systems",
            "version": "2022"
        }
        res = requests.post(f"{BASE_URL}/frameworks/", json=payload, headers=headers)
        if res.status_code in [200, 201]:
            fw_id = res.json()["id"]
        else:
            print("Failed to create framework")
            sys.exit(1)

    # Fetch existing controls to handle updates
    print("Fetching existing controls...")
    existing_controls = {}
    c_res = requests.get(f"{BASE_URL}/controls/?limit=1000", headers=headers)
    if c_res.status_code == 200:
        for c in c_res.json():
            if c["framework_id"] == fw_id:
                existing_controls[c["control_id"]] = c["id"]

    # Seed Controls
    print(f"\nSeeding {len(ISO_CONTROLS_DATA)} Controls...")
    
    for c in ISO_CONTROLS_DATA:
        classification = classify_control(c["title"], c["desc"])
        
        payload = {
            "control_id": c["id"],
            "title": c["title"],
            "description": c["desc"],
            "category": c["category"],
            "priority": "high",
            "framework_id": fw_id,
            "classification": classification
        }
        
        if c["id"] in existing_controls:
            # UPDATE
            db_id = existing_controls[c["id"]]
            # We use PUT to update
            # Note: PUT usually requires full object, but FASTAPI generated update often allows partial if using defaults or PATCH
            # Let's try PUTting the fields we care about. app/schemas/control.py defines ControlUpdate as optional fields.
            # endpoint is likely PUT /controls/{id} expecting ControlUpdate
            res = requests.put(f"{BASE_URL}/controls/{db_id}", json=payload, headers=headers)
            if res.status_code == 200:
                 print(f"[UPDATED] {c['id']} -> {classification}")
            else:
                 print(f"[UPDATE FAIL] {c['id']}: {res.text}")
        else:
            # CREATE
            res = requests.post(f"{BASE_URL}/controls/", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                print(f"[CREATED] {c['id']} ({classification})")
            else:
                print(f"[ERROR] {c['id']}: {res.text}")

if __name__ == "__main__":
    main()
