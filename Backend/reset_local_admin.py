from app.database import SessionLocal
from app import models, auth

db = SessionLocal()

user = db.query(models.User).filter(models.User.username == "admin").first()
if not user:
    print("User 'admin' not found. Creating it...")
    user = models.User(
        username="admin",
        hashed_password=auth.get_password_hash("admin123"),
        role="admin"
    )
    db.add(user)
    print("Created 'admin' user.")
else:
    print("User 'admin' found. Resetting password...")
    user.hashed_password = auth.get_password_hash("admin123")

db.commit()
print("✅ Admin password set to: admin123")
db.close()
