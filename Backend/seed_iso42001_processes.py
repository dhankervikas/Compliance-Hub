
from app.database import SessionLocal
from app.models.process import Process, SubProcess

ISO42001_PROCESSES = [
    {
        "name": "AI Strategy & Governance",
        "subs": ["AI Policy", "Role Definitions", "Management Review"]
    },
    {
        "name": "AI Risk Management",
        "subs": ["Risk Assessment", "Impact Analysis", "Risk Treatment"]
    },
    {
        "name": "Data Lifecycle Management",
        "subs": ["Data Collection", "Data Quality", "Data Annotation", "Data Privacy"]
    },
    {
        "name": "Model Development",
        "subs": ["Model Selection", "Training", "Testing & Validation", "Model Documentation"]
    },
    {
        "name": "System Operations (ML Ops)",
        "subs": ["Deployment", "Monitoring", "Incident Management", "Versioning"]
    },
    {
        "name": "Ethics & Responsible AI",
        "subs": ["Fairness", "Transparency", "Accountability", "Societal Impact"]
    },
    {
        "name": "Third-Party AI Management",
        "subs": ["Vendor Assessment", "Supply Chain Security"]
    }
]

def seed():
    db = SessionLocal()
    try:
        print("Seeding ISO 42001 Processes...")
        
        # Check if already exists to avoid dupes (naive check)
        existing = db.query(Process).filter(Process.framework_code == 'ISO42001').first()
        if existing:
            print("ISO 42001 Processes might already exist. Skipping to avoid duplicates.")
            return

        for p_data in ISO42001_PROCESSES:
            # Create Process
            process = Process(
                name=p_data["name"],
                description=f"ISO 42001 Process: {p_data['name']}",
                framework_code="ISO42001"
            )
            db.add(process)
            db.flush() # Get ID
            
            # Create SubProcesses
            for sub_name in p_data["subs"]:
                sub = SubProcess(
                    name=sub_name,
                    description=f"{sub_name} for {p_data['name']}",
                    process_id=process.id
                )
                db.add(sub)
        
        db.commit()
        print("Seeding Complete.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
