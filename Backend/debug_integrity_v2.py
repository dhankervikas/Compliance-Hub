
import requests

try:
    print("Testing /health/security-integrity...")
    res = requests.get("http://127.0.0.1:8002/api/v1/health/security-integrity")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
