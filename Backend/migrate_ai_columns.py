from app.database import engine
from sqlalchemy import text

def add_columns():
    with engine.connect() as conn:
        print("Migrating 'controls' table...")
        try:
            conn.execute(text("ALTER TABLE controls ADD COLUMN ai_explanation TEXT"))
            print("Added 'ai_explanation'.")
        except Exception as e:
            print(f"Skipping 'ai_explanation' (likely exists): {e}")

        try:
            conn.execute(text("ALTER TABLE controls ADD COLUMN ai_requirements_json TEXT"))
            print("Added 'ai_requirements_json'.")
        except Exception as e:
            print(f"Skipping 'ai_requirements_json' (likely exists): {e}")
            
        conn.commit()
        print("Migration done.")

if __name__ == "__main__":
    add_columns()
