import requests
import sys

try:
    print("Checking GET http://localhost:8000/health-api/security-integrity ...")
    r = requests.get("http://localhost:8000/health-api/security-integrity", timeout=5)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200:
        print("SUCCESS: Integrity API is UP.")
    else:
        print("FAIL: Integrity API returned error.")

except Exception as e:
    print(f"CRITICAL: Failed to connect to localhost:8000. {e}")
    sys.exit(1)
