import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the Backend directory to sys.path to ensure imports work if needed, 
# though we'll use direct SQL for simplicity.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Backend')))

# Database URL (assuming SQLite default)
# Database URL (Absolute Path) - trying sql_app.db
DATABASE_URL = r"sqlite:///C:\Projects\Compliance_Product\Backend\sql_app.db"

def count_controls():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Get SOC 2 Framework ID
        result = session.execute(text("SELECT id FROM frameworks WHERE code LIKE '%SOC2%'"))
        fw_row = result.fetchone()
        if not fw_row:
            print("SOC 2 Framework not found.")
            return

        fw_id = fw_row[0]
        print(f"SOC 2 Framework ID: {fw_id}")

        # 2. Count Controls by Category
        query = text("""
            SELECT category, COUNT(*) as count 
            FROM controls 
            WHERE framework_id = :fw_id 
            GROUP BY category
        """)
        
        result = session.execute(query, {"fw_id": fw_id})
        
        print("\n--- SOC 2 Control Counts by Category ---")
        total = 0
        counts = {}
        for row in result:
            category = row[0]
            count = row[1]
            print(f"{category}: {count}")
            counts[category] = count
            total += count
            
        print(f"\nTotal Controls: {total}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    count_controls()
