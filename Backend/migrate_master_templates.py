from app.database import engine, Base
from sqlalchemy import text

def migrate():
    print("Migrating Master Templates Schema...")
    
    # 1. Create MasterTemplate Table
    # Using SQL directly for SQLite simplicity in this "patch" approach, 
    # or we can use Base.metadata.create_all if we import the model.
    # Let's use create_all for the new table to be safe.
    from app.models.master_template import MasterTemplate
    Base.metadata.create_all(bind=engine)
    print(" - Created 'master_templates' table")

    # 2. Alter Policies Table for Foreign Key
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE policies ADD COLUMN master_template_id INTEGER"))
            print(" - Added 'master_template_id' column to policies")
        except Exception as e:
            print(f" - 'master_template_id' column likely exists: {e}")

if __name__ == "__main__":
    migrate()
