from app.database import SessionLocal
from app.models.framework import Framework

db = SessionLocal()

test_frameworks = db.query(Framework).filter(Framework.id.in_([2, 4])).all()

for f in test_frameworks:
    print(f"Deleting: {f.name}")
    db.delete(f)

db.commit()
print("Test frameworks deleted!")
db.close()