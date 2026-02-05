import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def login(username, password, tenant_id):
    url = f"{BASE_URL}/auth/login"
    try:
        data = {
            "username": username,
            "password": password
        }
        headers = {"X-Target-Tenant-ID": tenant_id}
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()['access_token']
        print(f"Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def check_duplicates(token):
    headers = {"Authorization": f"Bearer {token}"}
    # Get all controls
    url = f"{BASE_URL}/controls/?limit=1000"
    print(f"Fetching controls from {url}...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch controls: {response.text}")
            return
        
        controls = response.json()
        print(f"Fetched {len(controls)} controls.")
        
        ids = [c['id'] for c in controls]
        unique_ids = set(ids)
        
        if len(ids) != len(unique_ids):
            print("DUPLICATES FOUND!")
            from collections import Counter
            counts = Counter(ids)
            dups = [id for id, count in counts.items() if count > 1]
            print(f"Duplicate IDs: {dups}")
            
            # Show details of first duplicate
            dup_id = dups[0]
            entries = [c for c in controls if c['id'] == dup_id]
            print(f"Entries for ID {dup_id}:")
            for e in entries:
                print(f" - Process: {e.get('process_name')}")
        else:
            print("No duplicates found in API response.")
            
    except Exception as e:
        print(f"Error checking duplicates: {e}")

if __name__ == "__main__":
    # Assuming default admin credentials
    token = login("admin", "password123", "default_tenant") 
    if not token:
        # Try testtest tenant if default failed
        print("Retrying with testtest tenant...")
        token = login("admin", "admin", "testtest")
    
    if token:
        check_duplicates(token)
