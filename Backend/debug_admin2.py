
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user
from app.models.user import User

# Mock Auth for Admin ID 2 (Tenant: testtest)
async def override_get_current_user_admin2():
    return User(id=2, username="admin", tenant_id="testtest", is_superuser=True)

app.dependency_overrides[get_current_user] = override_get_current_user_admin2

client = TestClient(app)

def test_admin2_view():
    print("Fetching Processes as Admin ID 2 (Tenant: testtest)...")
    response = client.get("/api/v1/processes/", params={"framework_code": "ISO27001"})
    
    data = response.json()
    total_stats = {"total": 0, "implemented": 0}
    
    for p in data:
        # Check stats directly from process response
        if "stats" in p:
            total_stats["total"] += p["stats"].get("total", 0)
            total_stats["implemented"] += p["stats"].get("implemented", 0)
            
    print(f"Total Controls Visible to Admin 2: {total_stats['total']}")

if __name__ == "__main__":
    test_admin2_view()
