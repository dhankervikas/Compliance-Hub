
import requests

def check_processes():
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
        
        # 2. Get Processes (ISO 27001)
        auth_header = {"Authorization": f"Bearer {token}"}
        url = "http://localhost:8002/api/v1/processes/?framework_code=ISO27001"
        resp = sess.get(url, headers=auth_header)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Processes Found: {len(data)}")
            
            total_mapped = 0
            for p in data:
                stats = p.get('stats', {})
                total = stats.get('total', 0)
                total_mapped += total
                if total > 0:
                    print(f" - {p.get('name')}: {total} Controls Mapped")
            
            if total_mapped == 0:
                print("WARNING: ALL Processes have 0 mapped controls!")
            else:
                print(f"SUCCESS: Total {total_mapped} controls mapped across all processes.")
                
        else:
             print(f"Process Check Failed: {resp.text}")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_processes()
