import sqlite3

def migrate():
    print("Migrating database...")
    conn = sqlite3.connect("sql_app.db") # Corrected DB name
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "allowed_frameworks" not in columns:
            print("Adding 'allowed_frameworks' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN allowed_frameworks TEXT DEFAULT 'ALL'")
            conn.commit()
            print("Success.")
        else:
            print("Column 'allowed_frameworks' already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
