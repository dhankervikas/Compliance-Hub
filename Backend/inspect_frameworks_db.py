import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.framework import Framework

# Setup Database logic similar to main app
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inspect_duplicates():
    session = SessionLocal()
    try:
        print("--- Inspecting Frameworks Table ---")
        frameworks = session.query(Framework).all()
        print(f"Total Frameworks Found: {len(frameworks)}")
        
        counts = {}
        for f in frameworks:
            key = f.code
            if key not in counts:
                counts[key] = []
            counts[key].append(f)
            
        print("\n--- All Frameworks (by Code) ---")
        for code, items in counts.items():
            for item in items:
                 print(f"Code: '{code}' | ID: {item.id} | Name: '{item.name}'")
                
        if not has_duplicates:
            print("\nNo duplicates found based on 'code'.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    inspect_duplicates()
