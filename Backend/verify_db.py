from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control

db = SessionLocal()
frameworks = db.query(Framework).all()

print("Frameworks in Database:")
for f in frameworks:
    count = db.query(Control).filter(Control.framework_id == f.id).count()
    print(f"{f.name} - Controls: {count}")

db.close()