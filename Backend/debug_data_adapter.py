import sys
import os
from app.database import SessionLocal
from app.services.data_adapter import DataSourceAdapter

def test_adapter():
    db = SessionLocal()
    adapter = DataSourceAdapter()
    
    # Force SIMULATION mode logic if needed, but it defaults to env
    print(f"Adapter Mode: {adapter.mode}")
    
    results = adapter.get_all_evidence(db)
    print(f"Total Items: {len(results)}")
    
    nist_items = [i for i in results if i['control_id'].startswith('GV') or i['control_id'].startswith('ID')]
    soc_items = [i for i in results if i['control_id'].startswith('CC')]
    
    print(f"NIST Items Found: {len(nist_items)}")
    if nist_items:
        print(f"Sample NIST ID: {nist_items[0]['control_id']}")
        
    print(f"SOC2 Items Found: {len(soc_items)}")
    
    # Check for IDs with prefix
    prefixed = [i['control_id'] for i in results if 'NIST' in i['control_id']]
    print(f"Items with 'NIST' in ID: {len(prefixed)}")
    if prefixed:
        print(f"Sample Prefixed: {prefixed[0]}")

if __name__ == "__main__":
    test_adapter()
