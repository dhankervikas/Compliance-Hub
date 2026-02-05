
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add regex support for sqlite
import re
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# Setup DB
DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_duplicates():
    db = SessionLocal()
    conn = db.connection()
    # Register regex function for SQLite
    conn.connection.create_function("REGEXP", 2, regexp)

    print("--- CHECKING FOR DUPLICATE CONTROL MAPPINGS ---")
    
    sql = """
    SELECT 
        c.control_id, 
        c.title, 
        COUNT(DISTINCT ui.category) as process_count,
        GROUP_CONCAT(DISTINCT ui.category) as processes
    FROM controls c
    JOIN intent_framework_crosswalk ifc ON ifc.control_reference = c.control_id
    JOIN universal_intents ui ON ui.id = ifc.intent_id
    WHERE c.framework_id IN (SELECT id FROM frameworks WHERE code LIKE '%ISO%27001%')
    GROUP BY c.control_id
    HAVING process_count > 1
    ORDER BY process_count DESC;
    """
    
    results = conn.execute(text(sql)).fetchall()
    
    if not results:
        print("[OK] No duplicates found! All controls map to exactly one process.")
    else:
        print(f"[FAIL] Found {len(results)} controls with duplicate mappings:")
        for row in results:
            print(f"[{row[0]}] {row[1]}")
            print(f"   Mapped to {row[2]} processes: {row[3]}")
    
    # Also check total count
    count_sql = """
    SELECT COUNT(DISTINCT c.id) 
    FROM controls c
    JOIN intent_framework_crosswalk ifc ON ifc.control_reference = c.control_id
    WHERE c.framework_id IN (SELECT id FROM frameworks WHERE code LIKE '%ISO%27001%')
    """
    total = conn.execute(text(count_sql)).scalar()
    print(f"\nTotal Unique Mapped Controls: {total}")

if __name__ == "__main__":
    check_duplicates()
