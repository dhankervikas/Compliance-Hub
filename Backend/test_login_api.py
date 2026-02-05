import requests

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        print(f"Attempting login to {url}...")
        response = requests.post(url, data=payload)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Login SUCCESS!")
            print("Token received:", response.json().get("access_token")[:10] + "...")
        else:
            print("Login FAILED")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_login()
