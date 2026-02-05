import requests
import sys

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    print(f"Testing login at {url}...")
    try:
        response = requests.post(url, data=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("LOGIN SUCCESS")
                print(f"Token: {data['access_token'][:10]}...")
            else:
                print(f"LOGIN FAILED: No token in response. {data}")
        else:
            print(f"LOGIN FAILED: {response.text}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to localhost:8000. Is the backend running?")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_login()
