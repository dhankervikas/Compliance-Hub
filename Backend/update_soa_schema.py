
from app.database import engine, Base
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        print("Checking for SoA columns in controls table...")
        
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(controls)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "is_applicable" not in columns:
            print("Adding is_applicable column...")
            conn.execute(text("ALTER TABLE controls ADD COLUMN is_applicable BOOLEAN DEFAULT 1"))
            
        if "justification" not in columns:
            print("Adding justification column...")
            conn.execute(text("ALTER TABLE controls ADD COLUMN justification TEXT"))

        if "implementation_method" not in columns:
            print("Adding implementation_method column...")
            conn.execute(text("ALTER TABLE controls ADD COLUMN implementation_method TEXT"))
            
        conn.commit()
        print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
