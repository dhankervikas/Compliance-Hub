import requests
import json

BASE_URL = "http://localhost:8000"

def test_routes():
    print(f"Testing routes against {BASE_URL}...")
    
    # 1. Health check (Root)
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"GET /health: {r.status_code}")
    except Exception as e:
        print(f"GET /health failed: {e}")

    # 2. Health check (Prefix)
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"GET /api/v1/health: {r.status_code}")
    except: pass

    # 3. SoA Update (Root)
    try:
        r = requests.post(f"{BASE_URL}/controls/soa-update", json=[])
        print(f"POST /controls/soa-update: {r.status_code}")
    except: pass

    # 4. SoA Update (Prefix)
    try:
        r = requests.post(f"{BASE_URL}/api/v1/controls/soa-update", json=[])
        print(f"POST /api/v1/controls/soa-update: {r.status_code}")
        if r.status_code == 422:
            print("  (422 is good - means validation took place)")
        if r.status_code == 200:
            print("  (200 OK)")
    except: pass
    
    # 5. AI Suggest (Root)
    try:
        r = requests.post(f"{BASE_URL}/ai/suggest-justification", json={})
        print(f"POST /ai/suggest-justification: {r.status_code}")
    except: pass
    
    # 6. AI Suggest (Prefix)
    try:
        r = requests.post(f"{BASE_URL}/api/v1/ai/suggest-justification", json={})
        print(f"POST /api/v1/ai/suggest-justification: {r.status_code}")
    except: pass

if __name__ == "__main__":
    test_routes()
