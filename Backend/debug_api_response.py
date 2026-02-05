
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user
from app.models.user import User

# Mock Auth
async def override_get_current_user():
    return User(id=1, username="admin", tenant_id="default_tenant", is_superuser=True)

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_processes():
    print("Fetching Processes...")
    response = client.get("/api/v1/processes/", params={"framework_code": "ISO27001"})
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    print(f"Received {len(data)} processes.")
    
    total_controls = 0
    for p in data:
        for sp in p.get("sub_processes", []):
            controls = sp.get("controls", [])
            total_controls += len(controls)
            if controls:
                c = controls[0]
                print(f"Sample Control in '{p['name']}': ID={c['id']}, FID={c.get('framework_id')}, Tenant={c.get('tenant_id')}")

    print(f"Total Controls in Response: {total_controls}")

if __name__ == "__main__":
    test_processes()
