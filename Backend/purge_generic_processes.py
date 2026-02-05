from app.database import SessionLocal
from app.models.process import Process
from app.models.person import Person # Fix for Mapper Registry

CANONICAL_PROCESSES = [
    "Governance & Policy",
    "HR Security",
    "Asset Management",
    "Access Control (IAM)",
    "Physical Security",
    "Operations", # Renamed from Operations (General)
    "Configuration Management",
    "Cryptography",
    "Logging & Monitoring",
    "Clock Synchronization",
    "Vulnerability Management",
    "Capacity Management",
    "Backup Management",
    "Network Security",
    "SDLC (Development)",
    "Supplier Mgmt",
    "Incident & Resilience",
    "Threat Intel",
    "Legal & Compliance",
    "Risk Management",
    "Improvement",
    "Internal Audit",
    "Management Review"
]

def purge_generics():
    db = SessionLocal()
    print("--- PURGING GENERIC PROCESSES ---")
    
    all_procs = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    deleted_count = 0
    
    for p in all_procs:
        if p.name not in CANONICAL_PROCESSES:
            print(f"Deleting Generic Process: {p.name} (ID: {p.id})")
            db.delete(p)
            deleted_count += 1
            
    db.commit()
    print(f"Purge Complete. Deleted {deleted_count} processes.")
    
    # Verify
    remaining = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    print(f"Remaining ISO 27001 Processes ({len(remaining)}):")
    for p in remaining:
        print(f" - {p.name}")
        
    db.close()

if __name__ == "__main__":
    purge_generics()
