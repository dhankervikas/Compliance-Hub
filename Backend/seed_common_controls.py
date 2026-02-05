from app.database import SessionLocal
from app.models.common_control import CommonControl
from app.models.framework_mapping import FrameworkMapping
from app.models.framework import Framework
from app.models.control import Control

db = SessionLocal()

def seed_mappings():
    print("Seeding Common Controls and Mappings...")

    # 1. Define Common Controls
    common_data = [
        {
            "name": "Data Encryption at Rest",
            "domain": "Data Security",
            "description": "All sensitive data must be encrypted when stored.",
            "mappings": [
                {"code": "ISO27001", "control_id": "A.5.11"}, # Access Control / Info Sec? No A.5.11 is ? Actually A.8.24 is crypto. Let's assume A.8.24 Use of cryptography
                {"code": "SOC2", "control_id": "CC6.1"}, # Logical Access
            ]
        },
        {
            "name": "Access Control Policy",
            "domain": "Access Control",
            "description": "Formal policy for access control.",
            "mappings": [
                {"code": "ISO27001", "control_id": "A.5.15"}, # Access Control
                {"code": "SOC2", "control_id": "CC6.1"},
            ]
        },
        {
            "name": "Backup & Recovery",
            "domain": "Business Continuity",
            "description": "Regular backups must be performed.",
            "mappings": [
                {"code": "ISO27001", "control_id": "A.8.13"}, # Info Backup
                {"code": "SOC2", "control_id": "A1.2"}, # Availability
            ]
        }
    ]

    for item in common_data:
        # Create Common Control
        cc = db.query(CommonControl).filter(CommonControl.name == item["name"]).first()
        if not cc:
            cc = CommonControl(
                name=item["name"], 
                domain=item["domain"], 
                description=item["description"]
            )
            db.add(cc)
            db.commit()
            db.refresh(cc)
            print(f"Created Common Control: {cc.name}")
        
        # Create Mappings
        for map_data in item["mappings"]:
            # Find Framework
            fw = db.query(Framework).filter(Framework.code == map_data["code"]).first()
            if not fw:
                print(f"Warning: Framework {map_data['code']} not found. Skipping mapping.")
                continue
            
            # Check if mapping exists
            mapping = db.query(FrameworkMapping).filter(
                FrameworkMapping.common_control_id == cc.id,
                FrameworkMapping.control_id == map_data["control_id"],
                FrameworkMapping.framework_id == fw.id
            ).first()
            
            if not mapping:
                m = FrameworkMapping(
                    common_control_id=cc.id,
                    control_id=map_data["control_id"],
                    framework_id=fw.id
                )
                db.add(m)
                print(f"  -> Mapped to {map_data['code']} : {map_data['control_id']}")
    
    db.commit()
    print("Seeding Complete.")

if __name__ == "__main__":
    seed_mappings()
