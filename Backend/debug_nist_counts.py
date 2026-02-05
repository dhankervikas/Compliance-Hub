
import sys
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.tenant import Tenant
from data.nist_csf_2_0 import NIST_CSF_DATA

def analyze_nist_counts():
    print("--- 1. Analyzing Data Source (NIST_CSF_DATA) ---")
    funcs = 0
    cats = 0
    subs = 0
    
    for f in NIST_CSF_DATA:
        funcs += 1
        for c in f.get("categories", []):
            cats += 1
            for s in c.get("subcategories", []):
                subs += 1
                
    total = funcs + cats + subs
    print(f"Functions: {funcs}")
    print(f"Categories: {cats}")
    print(f"Subcategories: {subs}")
    print(f"TOTAL Expected: {total}")
    
    print("\n--- 2. Analyzing Database Content ---")
    db = SessionLocal()
    try:
        # LIST ALL FRAMEWORKS
        print("LISTING ALL FRAMEWORKS:")
        fws = db.query(Framework).all()
        for f in fws:
            c_count = db.query(Control).filter(Control.framework_id == f.id).count()
            print(f" - ID: {f.id}, Code: {f.code}, Name: {f.name}, Controls: {c_count}")
            
        tenant = db.query(Tenant).filter(Tenant.slug == "testtest").first()
        if not tenant:
            print("Tenant 'testtest' not found.")
            return

        fw = db.query(Framework).filter(Framework.code == "NIST_CSF_2.0").first()
        if not fw:
             # Try fallback name
             fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
        
        if not fw:
            print("Framework NIST CSF 2.0 not found.")
            return

        # 1. Check Global Controls for this Framework (All Tenants)
        global_controls = db.query(Control).filter(
            Control.framework_id == fw.id
        ).all()
        print(f"Framework ID: {fw.id}")
        print(f"Total Controls GLOBALLY for this Framework: {len(global_controls)}")

        # 2. Check Targeted Tenant Controls
        controls = db.query(Control).filter(
            Control.framework_id == fw.id,
            Control.tenant_id == tenant.internal_tenant_id
        ).all()
        print(f"Target Tenant UUID: {tenant.internal_tenant_id}")
        print(f"Total Controls for THIS Tenant: {len(controls)}")
        
        # 3. Check for Duplicate Frameworks
        all_fws = db.query(Framework).filter(Framework.code == "NIST_CSF_2.0").all()
        if len(all_fws) > 1:
            print(f"WARNING: Multiple Frameworks found with code 'NIST_CSF_2.0': {len(all_fws)}")
            for f in all_fws:
                print(f" - ID: {f.id}, Name: {f.name}")
        
        # Check for duplicates by title or ID prefix
        seen_ids = {}
        for c in controls:
            # Strip tenant suffix for cleaner viewing
            clean_id = c.control_id.split('#')[0]
            if clean_id in seen_ids:
                seen_ids[clean_id] += 1
            else:
                seen_ids[clean_id] = 1
                
        duplicates = {k: v for k, v in seen_ids.items() if v > 1}
        if duplicates:
            print(f"\nPotential Duplicates Found ({len(duplicates)}):")
            for k, v in list(duplicates.items())[:10]:
                print(f" - {k}: {v} times")
            if len(duplicates) > 10:
                print("...")
        else:
            print("\nNo ID duplicates found (based on cleaned ID).")
            
        # Check categories usage
        cat_counts = {}
        for c in controls:
            cat = c.category or "None"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            
        print("\nBreakdown by Category Field:")
        for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
            print(f" - {k}: {v}")

    finally:
        db.close()

if __name__ == "__main__":
    analyze_nist_counts()
