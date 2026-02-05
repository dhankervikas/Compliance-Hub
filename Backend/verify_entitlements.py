
import requests

# Use the token returned from the previous successful login check
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInRlbmFudF9pZCI6ImE2MTYyNGM5LWIwZDktNDEyNS05YmQ1LWVkZjdhZjhmYjc4ZSIsImV4cCI6MTc2OTkzNTcwM30.l8Mrj3zFMilu1vH0aAj37iiF8kJf2TzuXzvlHVD8RTU"
# Note: Token might be expired or invalid if server restarted, but payload structure is key. 
# Better to re-login to be safe.

def check_entitlements():
    # 1. Login to get fresh token
    login_url = "http://localhost:8002/api/v1/auth/login"
    login_data = {"username": "admin", "password": "password"}
    headers = {"X-Target-Tenant-ID": "testtest"} 
    
    try:
        sess = requests.Session()
        resp = sess.post(login_url, headers=headers, data=login_data)
        if resp.status_code != 200:
            print(f"Login Failed: {resp.text}")
            return
            
        token = resp.json()['access_token']
        print("Login Success. Checking Entitlements...")
        
        # 2. Get Entitlements
        auth_header = {"Authorization": f"Bearer {token}"}
        ent_url = "http://localhost:8002/api/v1/users/me/entitlements"
        ent_resp = sess.get(ent_url, headers=auth_header)
        
        if ent_resp.status_code == 200:
            data = ent_resp.json()
            print(f"Frameworks Found: {len(data.get('frameworks', []))}")
            for fw in data.get('frameworks', []):
                print(f" - {fw.get('name')} (Active: {fw.get('is_active')})")
        else:
             print(f"Entitlement Check Failed: {ent_resp.text}")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_entitlements()
