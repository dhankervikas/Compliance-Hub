import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.control import Control
from app.api.processes import get_actionable_title

# Setup Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify():
    session = SessionLocal()
    try:
        print("--- Verifying Actionable Titles ---")
        # Check a few keys I added
        test_ids = ["A.5.1", "A.8.12", "A.6.1", "A.5.15"] 
        
        controls = session.query(Control).filter(Control.control_id.in_(test_ids)).all()
        
        for c in controls:
            act_title = get_actionable_title(c)
            print(f"ID: {c.control_id} | Title: {c.title[:20]}... | Actionable: '{act_title}'")
            
    finally:
        session.close()

if __name__ == "__main__":
    verify()
