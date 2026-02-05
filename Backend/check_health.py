import requests
try:
    resp = requests.get("http://localhost:8000/docs", timeout=5)
    print(f"Backend Status: {resp.status_code}")
except Exception as e:
    print(f"Backend Unreachable: {e}")
