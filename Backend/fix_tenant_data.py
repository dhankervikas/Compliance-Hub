from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_framework import TenantFramework
from app.models.user import User

db = SessionLocal()

print("--- ANALYZING TENANTS ---")
tenants = db.query(Tenant).all()
test_tenants = []
for t in tenants:
    s_repr = repr(t.slug)
    print(f"ID={t.id} Slug={s_repr} Name={t.name} Internal={t.internal_tenant_id}")
    if "testtest" in t.slug:
        test_tenants.append(t)

print(f"\nFound {len(test_tenants)} candidates for 'testtest'.")

if len(test_tenants) == 0:
    print("No 'testtest' tenant found. Please create it via onboarding.")
else:
    # Pick the 'best' one (probably the one with links) or clean up
    # We want exact 'testtest'
    exact = [t for t in test_tenants if t.slug == 'testtest']
    
    if len(exact) == 1:
        target = exact[0]
        print(f"Exact match found: {target.slug}. Verifying links...")
        
        links = db.query(TenantFramework).filter(TenantFramework.tenant_id == target.internal_tenant_id).all()
        print(f"Existing Links: {[l.framework_id for l in links]}")
        
        # Ensure ISO 27001 (ID 1) is Active
        iso_link = next((l for l in links if l.framework_id == 1), None)
        if iso_link:
            print(f"ISO 27001 Link exists. Active={iso_link.is_active}")
            if not iso_link.is_active:
                print("FIX: Activating ISO 27001...")
                iso_link.is_active = True
                db.commit()
                print("FIX: Done.")
        else:
            print("FIX: Creating ISO 27001 Link...")
            new_link = TenantFramework(
                tenant_id=target.internal_tenant_id,
                framework_id=1,
                is_active=True
            )
            db.add(new_link)
            db.commit()
            print("FIX: Done.")
            
    else:
        print("Ambiguous state! Multiple or no exact 'testtest'.")
        # If multiple, maybe delete the ones without links?
        # For safety in this agent run, if we see duplicates, we might want to just fix the first one found?
        # Or delete all and ask user to start over? 
        # Better: detailed output for me to decide next step.
        pass

db.close()
