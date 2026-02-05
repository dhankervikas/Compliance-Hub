from app.database import engine, Base
from app.models.control import Control
from app.models.framework import Framework
from app.models.evidence import Evidence
from app.models.user import User

def init_db():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    # Create Admin User
    from sqlalchemy.orm import Session
    from app.utils.security import get_password_hash
    db = Session(bind=engine)
    if not db.query(User).filter(User.username == "admin").first():
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        print("Admin user created.")
    db.close()

if __name__ == "__main__":
    init_db()
