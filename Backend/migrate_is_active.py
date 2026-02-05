
import sqlite3

DB_PATH = "sql_app.db"

def migrate():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("Checking for is_active column...")
        try:
            cursor.execute("SELECT is_active FROM frameworks LIMIT 1")
            print("Column exists.")
        except sqlite3.OperationalError:
            print("Column missing. Adding...")
            cursor.execute("ALTER TABLE frameworks ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("Column added.")
            
        conn.commit()
        conn.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
