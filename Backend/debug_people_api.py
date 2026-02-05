
import requests
import json

BASE_URL = "http://127.0.0.1:8002/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
PEOPLE_URL = f"{BASE_URL}/people"

def test_people_workflow():
    print("=== TESTING PEOPLE API ===")
    
    # 1. Login as Admin
    print("1. Logging in...")
    try:
        res = requests.post(LOGIN_URL, data={"username": "admin", "password": "admin123"})
        if res.status_code != 200:
            print(f"Login Failed: {res.text}")
            return
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(" -> Success")
        
        # Get Current User Email to simulate Zombie
        user_res = requests.get(f"{BASE_URL}/people/../users/me", headers=headers)
        me = user_res.json()
        my_email = me.get("email")
        print(f" -> Current User Email: {my_email}")

        if not my_email:
             # Fallback if /users/me endpoint structure is different or email missing
             print(" -> WARNING: No email found for current user. Using 'admin@testtest.local'")
             my_email = "admin@testtest.local"

    except Exception as e:
        print(f"Login/Setup Failed: {e}")
        return

    # 2. Import People (One Active, One Zombie)
    print("\n2. Importing People...")
    payload = [
        {
            "full_name": "Alice Good",
            "email": "alice@example.com",
            "employment_status": "Active",
            "department": "Engineering"
        },
        {
            "full_name": "Zombie Admin",
            "email": my_email, # Matches the active admin user!
            "employment_status": "Inactive",
            "department": "IT",
            "job_title": "Ex-Admin"
        }
    ]
    
    try:
        res = requests.post(f"{PEOPLE_URL}/import", json=payload, headers=headers)
        print(f" -> Status: {res.status_code}")
        print(f" -> Response: {res.json()}")
    except Exception as e:
        print(f"Import Failed: {e}")

    # 3. Check Risks
    print("\n3. Checking for Zombie Accounts...")
    try:
        res = requests.get(f"{PEOPLE_URL}/risks", headers=headers)
        risks = res.json()
        print(f" -> Found {len(risks)} risks")
        print(json.dumps(risks, indent=2))
        
        if len(risks) > 0 and risks[0]['person']['email'] == my_email:
            print("\nSUCCESS: Zombie Account Detected!")
        else:
            print("\nFAILURE: Logic Failure - Zombie not detected.")
            
    except Exception as e:
        print(f"Risk Check Failed: {e}")

if __name__ == "__main__":
    test_people_workflow()
