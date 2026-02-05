
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.tenant import Tenant
from data.nist_business_mapping import NIST_BUSINESS_MAP, get_nist_business_domain

def update_nist_domains():
    db = SessionLocal()
    tenant_slug = "testtest"
    print(f"--- UPDATING NIST BUSINESS DOMAINS for tenant: {tenant_slug} ---")

    # 1. Resolve Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        print("Tenant not found")
        return
    tenant_uuid = tenant.internal_tenant_id
    print(f"Tenant UUID: {tenant_uuid}")

    # 2. Resolve NIST Framework
    fw = db.query(Framework).filter(Framework.code == "NIST-CSF").first()
    if not fw:
         fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
    
    if not fw:
        print("NIST Framework not found.")
        return
        
    print(f"Target Framework: {fw.name} (ID: {fw.id})")

    # 3. Get All NIST Controls for Tenant
    controls = db.query(Control).filter(
        Control.framework_id == fw.id,
        Control.tenant_id == tenant_uuid
    ).all()
    
    print(f"Found {len(controls)} controls to update.")
    
    # 4. Update Domain Field
    updated_count = 0
    
    for c in controls:
        # Extract Category Code from Control ID
        # Format: GV.OC-01#UUID -> GV.OC
        # Format: GV.OC#UUID -> GV.OC
        clean_id = c.control_id.split('#')[0]
        
        # logic to extract category code (e.g. GV.OC from GV.OC-01)
        # 1. Check if it IS a category (GV.OC)
        if clean_id in NIST_BUSINESS_MAP:
            new_domain = NIST_BUSINESS_MAP[clean_id]
        else:
            # 2. Try to split by '-' to get parent category (GV.OC-01 -> GV.OC)
            parts = clean_id.split('-')
            if len(parts) > 1:
                parent_cat = parts[0] # GV.OC
                new_domain = get_nist_business_domain(parent_cat)
            else:
                # 3. Fallback: Check prefix or use Function code
                # e.g. GV -> Governance & Strategy
                if clean_id.startswith("GV"): new_domain = "Governance & Strategy"
                elif clean_id.startswith("ID"): new_domain = "Asset & Inventory" # Fallback, likely overridden by specific map
                elif clean_id.startswith("PR"): new_domain = "Protect (General)" # Needs specific mapping
                elif clean_id.startswith("DE"): new_domain = "Security Monitoring (SOC)"
                elif clean_id.startswith("RS"): new_domain = "Incident Management"
                elif clean_id.startswith("RC"): new_domain = "Business Continuity"
                else:
                    new_domain = "Uncategorized"
                    
                # Explicit check for PR.AA, PR.DS etc overrides from mapping if prefix matches
                # This is weak, let's try to find matching key in map
                for map_key in NIST_BUSINESS_MAP:
                    if clean_id.startswith(map_key):
                        new_domain = NIST_BUSINESS_MAP[map_key]
                        break
        
        c.domain = new_domain
        updated_count += 1

    db.commit()
    print(f"Successfully updated {updated_count} controls with Business Domains.")
    db.close()

if __name__ == "__main__":
    update_nist_domains()
