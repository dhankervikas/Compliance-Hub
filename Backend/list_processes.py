
import sqlite3

DB_PATH = "sql_app.db"

def list_processes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM processes ORDER BY id")
    print(f"{'ID':<5} | {'Process Name'}")
    print("-" * 40)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} | {row[1]}")
    conn.close()

if __name__ == "__main__":
    list_processes()
