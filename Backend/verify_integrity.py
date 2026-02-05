import requests
import time

urls = [
    "http://localhost:8000/health-api/security-integrity",
    "http://localhost:8000/api/v1/health-debug",
    "http://localhost:8000/"
]

for url in urls:
    print(f"Checking {url}...")
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
