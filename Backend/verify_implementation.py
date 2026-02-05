from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Control, Assessment

client = TestClient(app)

def test_policies():
    print("\nTesting GET /policies/ ...")
    response = client.get("/api/v1/policies/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Count: {len(data)}")
        for p in data:
            print(f"- {p['name']} (v{p['version']})")
        if len(data) == 5:
            print("[PASS] 5 Policies found.")
        else:
            print("[FAIL] Expected 5 policies.")
    else:
        print(f"[FAIL] {response.text}")

def test_assessment():
    print("\nTesting POST /assessments/analyze/ ...")
    # First get a control ID
    db = SessionLocal()
    control = db.query(Control).first()
    db.close()
    
    if not control:
        print("[SKIP] No controls found to analyze.")
        return

    print(f"Analyzing Control ID: {control.id}")
    response = client.post(f"/api/v1/assessments/analyze/{control.id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response:", data)
        if "compliance_score" in data and "recommendations" in data:
             print("[PASS] Assessment analysis returned score and recommendations.")
        else:
             print("[FAIL] Missing fields in response.")
    else:
        print(f"[FAIL] {response.text}")

if __name__ == "__main__":
    test_policies()
    test_assessment()
