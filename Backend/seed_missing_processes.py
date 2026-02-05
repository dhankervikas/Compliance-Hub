from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings
from app.models.process import Process

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_missing_processes():
    print("[-] Seeding Missing Processes...")
    
    missing = ["Performance Evaluation", "Change Management"]
    count = 0 
    
    for name in missing:
        exists = db.query(Process).filter(Process.name == name).first()
        if not exists:
            p = Process(name=name, description="System Generated Process")
            db.add(p)
            count += 1
            print(f"Created Process: {name}")
        else:
            print(f"Process already exists: {name}")
            
    db.commit()
    print(f"\n[+] Created {count} missing processes.")

if __name__ == "__main__":
    seed_missing_processes()
