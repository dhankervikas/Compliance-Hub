
import requests

def check_controls():
    # 1. Login
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
        print("Login Success.")
        
        # 2. List Controls
        auth_header = {"Authorization": f"Bearer {token}"}
        # Try fetching ISO 27001 controls (Assuming ID 1)
        url = "http://localhost:8002/api/v1/controls/?framework_id=1&limit=5"
        resp = sess.get(url, headers=auth_header)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Controls Found: {len(data)}")
            for c in data:
                print(f" - {c.get('control_id')}: {c.get('title')}")
        else:
             print(f"Controls Check Failed: {resp.text}")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_controls()
