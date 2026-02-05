from app.database import SessionLocal
import sqlalchemy

def upgrade_evidence_schema():
    db = SessionLocal()
    print("--- UPGRADING EVIDENCE SCHEMA ---")
    try:
        # check if column exists
        result = db.execute(sqlalchemy.text("PRAGMA table_info(evidence)"))
        columns = [row[1] for row in result.fetchall()]
        if "master_intent_id" not in columns:
            print("Adding master_intent_id column...")
            db.execute(sqlalchemy.text("ALTER TABLE evidence ADD COLUMN master_intent_id VARCHAR"))
            db.commit()
            print("Column added successfully.")
        else:
            print("Column 'master_intent_id' already exists.")
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    upgrade_evidence_schema()
