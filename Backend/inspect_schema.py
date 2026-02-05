
import sqlite3

DB_PATH = "sql_app.db"

def inspect_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get Create Statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tenants'")
        schema = cursor.fetchone()
        
        if schema:
            print("SCHEMA for 'frameworks':")
            print(schema[0])
        else:
            print("Table 'frameworks' not found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    inspect_schema()
