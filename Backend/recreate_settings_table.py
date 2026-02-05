
from app.database import engine, Base
from app.models.settings import ComplianceSettings
from sqlalchemy import text

def recreate_table():
    print("Dropping compliance_settings table...")
    # Use raw SQL to force drop, as metadata might be out of sync
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS compliance_settings"))
        conn.commit()
    print("Table dropped. It will be recreated automatically by the backend startup or next request interacting with it if auto-create is enabled, or we can force create now.")
    
    # Force create
    print("Recreating table from new schema...")
    ComplianceSettings.__table__.create(bind=engine)
    print("Table recreated with new schema (including tenant_id).")

if __name__ == "__main__":
    recreate_table()
