
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()

print(f"{'Username':<20} | {'Tenant ID':<20} | {'Active'}")
print("-" * 50)
for u in users:
    print(f"{u.username:<20} | {u.tenant_id:<20} | {u.is_active}")
