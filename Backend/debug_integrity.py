
import requests

def test_integrity():
    url = "http://127.0.0.1:8002/api/v1/health/security-integrity"
    print(f"Testing Integrity Endpoint: {url}")
    try:
        res = requests.get(url, timeout=2)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_integrity()
