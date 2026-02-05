from app.database import SessionLocal
from app.models.framework import Framework

db = SessionLocal()

# Delete framework with id 5
framework = db.query(Framework).filter(Framework.id == 5).first()

if framework:
    print(f"Deleting: {framework.name} (ID: {framework.id})")
    db.delete(framework)
    db.commit()
    print("Deleted successfully!")
else:
    print("Framework not found")

db.close()