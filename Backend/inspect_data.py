import os
import sys
from sqlalchemy import create_engine, text
from app.config import settings

# Force synchronous engine for script
DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(DATABASE_URL)

def inspect_data():
    print(f"DB URL: {DATABASE_URL}")
    with engine.connect() as conn:
        print("--- DUMPING FIRST 50 CONTROLS ---")
        stmt = text("SELECT id, control_id, title, category FROM controls LIMIT 50")
        result = conn.execute(stmt).fetchall()
        for row in result:
             print(f"Row: {row.control_id} | {row.category} | {row.title[:30]}...")

        print("\n--- FIXING 'Operations (General)' -> 'Operations' ---")
        # Update the category in the DB
        update_stmt = text("UPDATE controls SET category = 'Operations' WHERE category = 'Operations (General)'")
        result = conn.execute(update_stmt)
        conn.commit()
        print(f"Updated {result.rowcount} rows from 'Operations (General)' to 'Operations'")

        # Verify
        stmt = text("SELECT count(*) as count, category FROM controls WHERE category LIKE '%Operation%' GROUP BY category")
        result = conn.execute(stmt).fetchall()
        for row in result:
             print(f"Category: '{row.category}' - Count: {row.count}")

if __name__ == "__main__":
    inspect_data()
