from app.database import SessionLocal
import sqlalchemy

def verify_evidence_schema():
    db = SessionLocal()
    try:
        result = db.execute(sqlalchemy.text("PRAGMA table_info(evidence)"))
        columns = [row[1] for row in result.fetchall()]
        if "master_intent_id" in columns:
            print("VERIFICATION PASS: master_intent_id exists.")
        else:
            print("VERIFICATION FAIL: master_intent_id missing.")
    finally:
        db.close()

if __name__ == "__main__":
    verify_evidence_schema()
