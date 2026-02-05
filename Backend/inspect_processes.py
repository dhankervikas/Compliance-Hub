import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.process import Process, SubProcess

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inspect():
    session = SessionLocal()
    try:
        print("--- Inspecting Processes ---")
        processes = session.query(Process).all()
        print(f"Total Processes: {len(processes)}")
        
        iso_count = 0
        for p in processes:
            if p.framework_code == 'ISO27001':
                iso_count += 1
                sp_count = len(p.sub_processes)
                print(f"ID: {p.id}, Name: '{p.name}', FrameworkCode: '{p.framework_code}', SubProcesses: {sp_count}")
        
        print(f"\nTotal ISO27001 Processes: {iso_count}")
        
    finally:
        session.close()

if __name__ == "__main__":
    inspect()
