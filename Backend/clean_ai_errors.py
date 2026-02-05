from app.database import SessionLocal
from app.models import Assessment

db = SessionLocal()

print("Cleaning stale AI Error records...")
# Find assessments with "AI Error" in gaps
errors = db.query(Assessment).filter(Assessment.gaps.like("AI Error%")).all()

count = len(errors)
for err in errors:
    db.delete(err)

db.commit()
print(f"Deleted {count} stale assessments with AI Errors.")
