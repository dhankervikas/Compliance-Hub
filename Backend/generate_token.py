from datetime import timedelta
from app.utils.security import create_access_token
from app.config import settings
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin", User.tenant_id == "default_tenant").first()

if not user:
    print("User not found!")
    exit(1)

access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
access_token = create_access_token(
    data={"sub": user.username, "tenant_id": user.tenant_id}, 
    expires_delta=access_token_expires
)

print(f"TOKEN: {access_token}")
