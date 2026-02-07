
from app.database import SessionLocal
from sqlalchemy import text

def add_folder_column():
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("PRAGMA table_info(policies)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "folder" not in columns:
            print("Adding 'folder' column to policies table...")
            db.execute(text("ALTER TABLE policies ADD COLUMN folder VARCHAR DEFAULT 'Uncategorized'"))
            db.commit()
            print("Column added.")
        else:
            print("'folder' column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_folder_column()
