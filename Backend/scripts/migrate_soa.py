import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path so we can import app settings if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def migrate():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing columns in 'controls' table...")
        
        # Helper to check and add column
        def add_column_if_not_exists(column_name, column_type):
            try:
                # Try to select the column to see if it exists
                conn.execute(text(f"SELECT {column_name} FROM controls LIMIT 1"))
                print(f"Column '{column_name}' already exists.")
            except Exception:
                # Column likely missing
                print(f"Adding column '{column_name}'...")
                conn.execute(text(f"ALTER TABLE controls ADD COLUMN {column_name} {column_type}"))
                conn.commit()
                print(f"Column '{column_name}' added successfully.")

        # Add SoA columns
        add_column_if_not_exists("is_applicable", "BOOLEAN DEFAULT 1")
        add_column_if_not_exists("justification", "TEXT")
        add_column_if_not_exists("justification_reason", "TEXT")
        add_column_if_not_exists("implementation_method", "TEXT")
        
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
