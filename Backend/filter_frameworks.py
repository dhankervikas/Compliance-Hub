import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.framework import Framework
from app.models.control import Control

# Setup Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def filter_frameworks():
    session = SessionLocal()
    try:
        # IDs identified to be deleted
        IDS_TO_DELETE = [19, 20, 21, 22, 23, 24]
        
        print(f"--- Filtering Frameworks: Deleting IDs {IDS_TO_DELETE} ---")
        
        frameworks_to_delete = session.query(Framework).filter(Framework.id.in_(IDS_TO_DELETE)).all()
        
        if not frameworks_to_delete:
            print("No matching frameworks found to delete.")
            return

        print(f"Found {len(frameworks_to_delete)} frameworks to delete.")
        
        for f in frameworks_to_delete:
            print(f"Deleting: ID={f.id}, Code='{f.code}', Name='{f.name}'")
            # Manually delete controls
            controls_count = session.query(Control).filter(Control.framework_id == f.id).delete()
            print(f" - Deleted {controls_count} related controls.")
            
            session.delete(f)
            
        session.commit()
        print("--- Filter Complete: Unwanted records removed. ---")
            
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    filter_frameworks()
