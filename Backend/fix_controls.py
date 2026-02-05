
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "password"
TENANT_TO_FIX = "testtest"

def main():
    print(f"[-] Authenticating as {USERNAME}...")
    # 1. Login
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": USERNAME, "password": PASSWORD})
    if resp.status_code != 200:
        print(f"[!] Login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    print(f"[+] Authenticated. Token received.")

    # 2. Get Entitlements (and Framework IDs) for Target Tenant (Impersonation)
    print(f"[-] Fetching entitlements for tenant: {TENANT_TO_FIX}...")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Tenant-ID": TENANT_TO_FIX # Frontend uses this, backend auth might use URL param or this header?
        # Actually my auth.py fix uses token payload.
        # But wait, to impersonate, I need to get an IMPERSONATION token first?
        # No, the 'impersonate' endpoint returns a new token.
    }
    
    # 2a. Impersonate to get a proper tenant-scoped token
    print(f"[-] exchanging token for impersonation token for {TENANT_TO_FIX}...")
    imp_resp = requests.post(f"{BASE_URL}/auth/impersonate", params={"tenant_id": TENANT_TO_FIX}, headers=headers)
    
    if imp_resp.status_code != 200:
        print(f"[!] Impersonation failed: {imp_resp.text}")
        return
        
    imp_token = imp_resp.json()["access_token"]
    imp_headers = {"Authorization": f"Bearer {imp_token}"}
    print(f"[+] Impersonation successful.")

    # 3. List Frameworks to find IDs
    print(f"[-] Listing frameworks for {TENANT_TO_FIX}...")
    fw_resp = requests.get(f"{BASE_URL}/frameworks/", headers=imp_headers)
    if fw_resp.status_code != 200:
         print(f"[!] Failed to list frameworks: {fw_resp.text}")
         return
    
    frameworks = fw_resp.json()
    print(f"[+] Found {len(frameworks)} frameworks.")
    
    for fw in frameworks:
        print(f"    - ID: {fw['id']} | Code: {fw['code']} | Name: {fw['name']}")
        
        # 4. Trigger Seed for ISO 27001 (or all?)
        # Logic: If it's ISO 27001, seed it.
        # The prompt mentioned "ISO 27001:2022" having 0 controls.
        
        if "ISO" in fw['code'] or "27001" in fw['code']:
            print(f"[*] SEEDING CONTROLS for {fw['code']} (ID: {fw['id']})...")
            seed_resp = requests.post(f"{BASE_URL}/frameworks/{fw['id']}/seed-controls", headers=imp_headers)
            
            if seed_resp.status_code == 201:
                print(f"    [SUCCESS] Controls seeded.")
            else:
                print(f"    [FAILED] {seed_resp.status_code} - {seed_resp.text}")

    print("[*] Fix script completed.")

if __name__ == "__main__":
    main()
