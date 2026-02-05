
import requests
import json
import sys
import os

# Add current directory to path to import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User
from app.utils.security import create_access_token
from datetime import timedelta

BASE_URL = "http://localhost:8000/api/v1"
TENANT_TO_FIX = "testtest"

def main():
    print(f"[-] Generating Admin Token directly...")
    db = SessionLocal()
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        print("[!] Admin user not found in DB!")
        return
    
    # Generate Token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "tenant_id": user.tenant_id, "mode": "admin"},
        expires_delta=access_token_expires
    )
    print(f"[+] Token generated.")
    
    token = access_token
    db.close()

    # 1. Impersonate to get a proper tenant-scoped token
    print(f"[-] Exchanging token for impersonation token for {TENANT_TO_FIX}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Use JSON body for Pydantic model
        imp_resp = requests.post(f"{BASE_URL}/auth/impersonate", json={"tenant_id": TENANT_TO_FIX}, headers=headers)
        
        if imp_resp.status_code != 200:
            print(f"[!] Impersonation failed: {imp_resp.text}")
            # Fallback: Try running seed with Admin token but X-Target-Tenant-ID header if supported, 
            # Or assume the issue is strict multitenancy API.
            return
            
        imp_token = imp_resp.json()["access_token"]
        imp_headers = {"Authorization": f"Bearer {imp_token}"}
        print(f"[+] Impersonation successful.")

        # 2. List Frameworks to find IDs
        print(f"[-] Listing frameworks for {TENANT_TO_FIX}...")
        fw_resp = requests.get(f"{BASE_URL}/frameworks/", headers=imp_headers)
        if fw_resp.status_code != 200:
             print(f"[!] Failed to list frameworks: {fw_resp.text}")
             return
        
        frameworks = fw_resp.json()
        print(f"[+] Found {len(frameworks)} frameworks.")
        
        for fw in frameworks:
            print(f"    - ID: {fw['id']} | Code: {fw['code']} | Name: {fw['name']}")
            
            # 3. Trigger Seed if ISO
            if "ISO" in fw['code'] or "27001" in fw['code']:
                print(f"[*] SEEDING CONTROLS for {fw['code']} (ID: {fw['id']})...")
                seed_resp = requests.post(f"{BASE_URL}/frameworks/{fw['id']}/seed-controls", headers=imp_headers)
                
                if seed_resp.status_code == 201:
                    print(f"    [SUCCESS] Controls seeded.")
                else:
                    print(f"    [FAILED] {seed_resp.status_code} - {seed_resp.text}")
                    
    except requests.exceptions.ConnectionError:
        print("[!] Connection Error: Is the backend server running on port 8000?")

    print("[*] Fix script completed.")

if __name__ == "__main__":
    main()
