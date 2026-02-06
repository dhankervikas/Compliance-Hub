
from sqlalchemy import text
from app.database import SessionLocal, engine

def cleanup_placeholders():
    db = SessionLocal()
    try:
        print("Checking for placeholder controls...")
        
        # 1. Identify Placeholder Controls
        placeholders = db.execute(text("SELECT id, control_id, title, framework_id FROM controls WHERE title LIKE '%Placeholder%'")).fetchall()
        
        if not placeholders:
            print("No placeholder controls found.")
            return

        print(f"Found {len(placeholders)} placeholder controls:")
        placeholder_ids = []
        for p in placeholders:
            print(f" - ID: {p.id} | Control: {p.control_id} | Title: {p.title}")
            placeholder_ids.append(p.id)
        
        if not placeholder_ids:
            return

        id_list = ",".join(map(str, placeholder_ids))

        # 2. Check for dependencies (Optional/Informational)
        # We'll just try to delete dependencies first as requested
        
        # Evidence
        print("Cleaning up Evidence...")
        db.execute(text(f"DELETE FROM evidence WHERE control_id IN ({id_list})"))
        
        # Process Mappings
        print("Cleaning up Process Mappings...")
        try:
             db.execute(text(f"DELETE FROM process_control_mapping WHERE control_id IN ({id_list})"))
        except Exception as e:
            print(f"Note: process_control_mapping cleanup failed (might not exist or different schema): {e}")

        # Control Requirements (if table exists, or if it's a join table)
        # Assuming requirements are linked? Or maybe not. Let's just proceed to controls.
        
        # 3. Delete Controls
        print("Deleting Placeholder Controls...")
        db.execute(text(f"DELETE FROM controls WHERE id IN ({id_list})"))
        
        db.commit()
        print("Successfully deleted placeholder controls.")
        
        # Verify
        remaining = db.execute(text(f"SELECT count(*) FROM controls WHERE id IN ({id_list})")).scalar()
        print(f"Remaining placeholders: {remaining}")

    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_placeholders()
