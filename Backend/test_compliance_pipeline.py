import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_pipeline():
    print("--- Testing Compliance Engine Pipeline ---")
    
    # 1. Fetch Master Templates
    try:
        r = requests.get(f"{BASE_URL}/master-templates/")
    except Exception as e:
        print(f"[FAIL] Connection Failed: {e}")
        return

    if r.status_code != 200:
        print(f"[FAIL] GET /master-templates/ returned {r.status_code}: {r.text}")
        return
        
    masters = r.json()
    print(f"[OK] Fetched {len(masters)} Master Templates")
    if not masters:
        print("[FAIL] No master templates found. Did seeder run?")
        return

    template_id = masters[0]['id']
    print(f"Using Template ID: {template_id} ({masters[0]['title']})")

    # 2. Clone Template
    print(f"Cloning Template {template_id}...")
    r = requests.post(f"{BASE_URL}/policies/clone-master/{template_id}")
    if r.status_code != 201:
        print(f"[FAIL] Clone failed: {r.text}")
        return
    
    policy = r.json()
    policy_id = policy['id']
    print(f"[OK] Created Draft Policy ID: {policy_id}")
    print(f"     Content Snippet: {policy['content'][:50]}...")
    
    # Verify Variable Injection
    if "AssuRisk" in policy['content']:
        print("[OK] Variable Injected: 'AssuRisk' found in content")
    else:
        print("[WARN] Variable Injection might have failed")

    # 3. Edit Policy (User Draft)
    print("Simulating User Edit...")
    new_content = policy['content'] + "\n<p>-- EDITED BY USER --</p>"
    r = requests.put(f"{BASE_URL}/policies/{policy_id}", json={"content": new_content})
    assert r.status_code == 200
    print("[OK] Policy Detail Updated")

    # 4. Restore Policy
    print("Restoring Policy from Master...")
    r = requests.post(f"{BASE_URL}/policies/{policy_id}/restore")
    if r.status_code == 200:
        restored = r.json()
        if "-- EDITED BY USER --" not in restored['content']:
             print("[OK] Policy Restored (User edits removed)")
        else:
             print("[FAIL] Restore seemed to fail, edit still present")
    else:
        print(f"[FAIL] Restore failed: {r.text}")

if __name__ == "__main__":
    test_pipeline()
