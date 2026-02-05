from app.database import SessionLocal, engine
from app.models.evidence import Evidence
from sqlalchemy import text

def reset_evidence():
    db = SessionLocal()
    try:
        print("Resetting Evidence table...")
        # Try truncate/delete
        db.query(Evidence).delete()
        db.commit()
        print("Evidence table cleared.")
    except Exception as e:
        print(f"Error resetting evidence: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_evidence()
