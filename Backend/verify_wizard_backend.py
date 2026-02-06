import requests
import json
import sys

# Config
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123" 
TENANT_SLUG = "testtest"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        if response.content:
             print(response.content)
        sys.exit(1)

def get_catalog(token):
    url = f"{BASE_URL}/frameworks/?catalog=true"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Catalog fetch success")
        mj = response.json()
        print(f"   Found {len(mj)} frameworks in catalog.")
        return mj
    else:
        print(f"Catalog fetch failed: {response.status_code} {response.text}")
        sys.exit(1)

def link_frameworks(token, tenant_slug, framework_ids):
    url = f"{BASE_URL}/frameworks/tenant-link"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Tenant-ID": tenant_slug 
    }
    data = {"framework_ids": framework_ids}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Link frameworks success")
        print(response.json())
    else:
        print(f"Link frameworks failed: {response.status_code} {response.text}")

def main():
    print("1. Logging in... (BYPASSED)")
    # token = login(USERNAME, PASSWORD)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInRlbmFudF9pZCI6ImRlZmF1bHRfdGVuYW50IiwiZXhwIjoxNzcwMzUwMTY1fQ.sqiggW_js59QCQprqh6Z9hnfil4yYP8C7s0O9sJ0Edc"
    
    print("\n2. Fetching Catalog (as Tenant)...")
    catalog = get_catalog(token)
    
    if not catalog:
        print("No frameworks found in catalog.")
        sys.exit(1)
        
    iso = next((f for f in catalog if "ISO" in f["code"] or "ISO" in f["name"]), None)
    if not iso:
        print("ISO framework not found in catalog.")
        
    target_ids = [iso["id"]] if iso else [catalog[0]["id"]]
    print(f"   Selected Framework IDs: {target_ids}")

    print(f"\n3. Linking Frameworks to '{TENANT_SLUG}'...")
    link_frameworks(token, TENANT_SLUG, target_ids)
    
    print("\n4. Verifying Link...")
    # Now fetch WITHOUT catalog=true, should see the linked framework.
    url = f"{BASE_URL}/frameworks/"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Target-Tenant-ID": TENANT_SLUG
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        linked = res.json()
        print(f"   Tenant now has {len(linked)} frameworks.")
        found = any(f["id"] in target_ids for f in linked)
        if found:
            print("Verification Successful: Framework linked.")
        else:
            print("Verification Failed: Linked framework not found in list.")
            print(linked)
    else:
        print(f"Verification Fetch Failed: {res.status_code}")

if __name__ == "__main__":
    main()
