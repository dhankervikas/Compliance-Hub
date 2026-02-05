from app.database import engine, Base
from app.models.context import ContextIssue, InterestedParty, ScopeDocument
from app.models.policy import Policy
from sqlalchemy import text

def run_migration():
    print("Migrating Database Schema for ISO 27001 Upgrade...")
    
    # 1. Create New Tables
    print("Creating Context Tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Alter Policies Table (SQLite doesn't support IF NOT EXISTS for columns easily in pure SQL, so we try/except)
    print("Updating Policies Table Schema...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN is_template BOOLEAN DEFAULT 0"))
            print(" - Added 'is_template' column")
        except Exception as e:
            print(f" - 'is_template' column likely exists: {e}")

        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN parent_id INTEGER"))
            print(" - Added 'parent_id' column")
        except:
            pass
            
        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN approval_date DATETIME"))
            print(" - Added 'approval_date' column")
        except:
            pass

        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN approver VARCHAR"))
            print(" - Added 'approver' column")
        except:
            pass
            
        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN mapped_controls TEXT"))
            print(" - Added 'mapped_controls' column")
        except:
            pass

    print("Migration Complete.")

if __name__ == "__main__":
    run_migration()
