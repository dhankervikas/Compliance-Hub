from app.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            print("Adding 'status' column...")
            conn.execute(text("ALTER TABLE policies ADD COLUMN status VARCHAR DEFAULT 'Draft'"))
            print("Success.")
        except Exception as e:
            print(f"Skipped 'status': {e}")

        try:
            print("Adding 'owner' column...")
            conn.execute(text("ALTER TABLE policies ADD COLUMN owner VARCHAR DEFAULT 'Compliance Team'"))
            print("Success.")
        except Exception as e:
            print(f"Skipped 'owner': {e}")
            
        try:
            print("Adding 'linked_frameworks' column...")
            conn.execute(text("ALTER TABLE policies ADD COLUMN linked_frameworks VARCHAR"))
            print("Success.")
        except Exception as e:
            print(f"Skipped 'linked_frameworks': {e}")
            
        conn.commit()

if __name__ == "__main__":
    migrate()
