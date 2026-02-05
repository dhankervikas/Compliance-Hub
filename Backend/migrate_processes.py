
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_app.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Migrating Process Schema...")
        # 1. Add framework_code column
        try:
            cursor.execute("ALTER TABLE processes ADD COLUMN framework_code VARCHAR DEFAULT 'ISO27001'")
            print("Added framework_code column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column framework_code already exists.")
            else:
                raise e

        # 2. Update existing rows to ISO27001
        cursor.execute("UPDATE processes SET framework_code = 'ISO27001' WHERE framework_code IS NULL")
        print(f"Updated {cursor.rowcount} processes to ISO27001.")
        
        conn.commit()
        print("Migration Successful.")
        
    except Exception as e:
        print(f"Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
