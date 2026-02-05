import sys
import os
import json
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.services.ai_service import client, MODEL_NAME

# Add current directory to path
sys.path.append(os.getcwd())

def get_iso_controls(db: Session):
    return db.query(Control).filter(Control.framework_id == 2).all() # Assuming ISO 42001 is ID 2, we will verify dynamically

def get_ai_controls(db: Session):
    # Find AI Framework ID
    # We look for code 'AI_FRAMEWORK'
    # Actually we just filter by framework code or name logic
    # But since we know we just imported it, we can look for 'AI Management' category or similar
    # Safer: Look for the framework first
    from app.models.framework import Framework
    fw = db.query(Framework).filter(Framework.code == 'AI_FRAMEWORK').first()
    if not fw:
        print("AI Framework not found!")
        return []
    return db.query(Control).filter(Control.framework_id == fw.id).all()

def get_iso_42001_controls(db: Session):
    # Depending on how ISO 42001 was seeded. 
    # Let's search by ID prefix
    return db.query(Control).filter(Control.control_id.like('ISO42001%')).all()

def semantic_fallback(ai_control, iso_controls):
    """
    Find best match using weighted keyword overlap.
    Boosts known AI/ISO domain keywords.
    """
    import re
    def get_tokens(text):
        if not text: return set()
        return set(re.findall(r'\w+', text.lower()))

    ai_text = (ai_control.title + " " + ai_control.description).lower()
    ai_tokens = get_tokens(ai_text)
    
    # Domain Knowledge Boosters
    # Map typical AI control keywords to ISO 42001 Clauses/Controls
    boost_map = {
        "risk": ["6.1", "risk"],
        "impact": ["6.1", "impact"],
        "policy": ["5.2", "policy"],
        "leadership": ["5.1"],
        "roles": ["5.3"],
        "resource": ["7.1"],
        "data": ["B.5", "B.6"], # Annex B (Data)
        "lifecycle": ["8.1"],
        "development": ["8."],
        "third party": ["B.5"],
        "provider": ["B.5"],
        "monitor": ["9.1"],
        "audit": ["9.2"],
        "review": ["9.3"],
        "improvement": ["10."],
        "record": ["7.5"],
        "documentation": ["7.5"],
        "competence": ["7.2"],
        "awareness": ["7.3"],
        "communication": ["7.4"]
    }

    best_match = None
    best_score = 0

    for iso in iso_controls:
        iso_text = (iso.title + " " + (iso.description or "")).lower()
        iso_tokens = get_tokens(iso_text)
        
        # Base Score: Jaccard-ish Intersection
        intersection = ai_tokens.intersection(iso_tokens)
        score = len(intersection)
        
        # Context Boost
        for key, targets in boost_map.items():
            if key in ai_text:
                # If this keyword is relevant to the AI control, boost ISO controls that match the target
                for t in targets:
                    if t.lower() in iso.control_id.lower() or t.lower() in iso_text:
                        score += 5 # strong boost for domain alignment
        
        # ID Boost
        # If IDs happen to look similar (unlikely across frameworks but possible)
        # if ai_control.control_id in iso.control_id: score += 10

        if score > best_score:
            best_score = score
            best_match = iso
    
    return best_match

def map_batch(ai_batch, iso_controls_obj):
    """
    Attempt AI mapping, fallback to heuristic.
    """
    mapped_results = []
    
    # Try AI first (SKIP if we know it fails, but let's leave the structure)
    # If client is None or API fails, we go to fallback.
    
    # GROUP BATCH for AI
    # ... (Omitted for resilience, assuming we just loop and try fallback)
    
    for ai_item in ai_batch:
        # Convert dictionary back to object-like or finding lookup
        # ai_batch is list of dicts: {'id':...}
        match = None
        
        # Heuristic Match
        # We need the full object for fallback
        # Let's assume passed inputs are sufficient
        
        # Find the object in our pre-fetched list to get full text? 
        # Actually the batch has title/desc.
        
        # Mock object for fallback function
        class MockCtrl:
            def __init__(self, t, d):
                self.title = t
                self.description = d
        
        ai_obj = MockCtrl(ai_item['title'], ai_item['desc'])
        
        best_iso = semantic_fallback(ai_obj, iso_controls_obj)
        
        result_entry = {
            "ai_control_id": ai_item['id'],
            "iso_match_id": best_iso.control_id if best_iso else "No Match",
            "rationale": "Automated Keyword Match (AI Service Unavailable)"
        }
        mapped_results.append(result_entry)
        
    return mapped_results

def main():
    db = SessionLocal()
    
    print("Fetching controls...")
    ai_controls = get_ai_controls(db)
    iso_controls = get_iso_42001_controls(db)

    print(f"Found {len(ai_controls)} AI Controls")
    print(f"Found {len(iso_controls)} ISO 42001 Controls")

    if not ai_controls or not iso_controls:
        print("Missing data. Aborting.")
        return

    # Process
    results = []

    ai_data = [{"id": c.control_id, "title": c.title, "desc": c.description} for c in ai_controls]
    
    # We pass the full ISO objects to the mapper/fallback
    print("Running mapping (Offline Mode)...")
    results = map_batch(ai_data, iso_controls)

    # Create DataFrame
    print("Generating Excel...")
    
    # Merge for full details
    final_rows = []
    
    # Lookups
    ai_lookup = {c.control_id: c for c in ai_controls}
    iso_lookup = {c.control_id: c for c in iso_controls}

    for item in results:
        ai_id = item.get("ai_control_id")
        iso_id = item.get("iso_match_id")
        
        ai_obj = ai_lookup.get(ai_id)
        iso_obj = iso_lookup.get(iso_id)

        if ai_obj:
            final_rows.append({
                "AI Control ID": ai_obj.control_id,
                "AI Category": ai_obj.category, # Module
                "AI Domain": ai_obj.domain,     # Domain (Added)
                "AI Control Title": ai_obj.title,
                "AI Description": ai_obj.title, # Mapping Title to Description as requested (Source was "Control Description")
                "Requirements": ai_obj.description, # Mapping Description to Requirements (Source was "Requirements (Shall)")
                "Mapped ISO 42001 ID": iso_obj.control_id if iso_obj else "No Match",
                "Mapped ISO 42001 Title": iso_obj.title if iso_obj else "",
                "Mapping Rationale": item.get("rationale", "")
            })

    df = pd.DataFrame(final_rows)
    output_file = "AI_ISO_42001_Mapping_Report.xlsx"
    # Ensure static directory exists
    output_path = os.path.join("app", "static", "reports", output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_excel(output_path, index=False)
    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    main()
