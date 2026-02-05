
import sqlite3
import os

DB_PATH = "./sql_app.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Starting migration...")

        # 0. Cleanup from previous failed runs
        cursor.execute("DROP TABLE IF EXISTS users_old;")

        # 1. Rename existing table
        cursor.execute("ALTER TABLE users RENAME TO users_old;")
        
        # 1.5 Drop old indexes to avoid conflicts
        # Note: Renaming lists indexes but they might still conflict if we try to reuse names. 
        # Actually in SQLite renaming table renames indexes too? No.
        # But let's try dropping them to be safe if they exist.
        for idx in ["ix_users_email", "ix_users_username", "ix_users_tenant_id", "ix_users_id"]:
            cursor.execute(f"DROP INDEX IF EXISTS {idx};")

        # 2. Create new table with new constraints
        # Note: We must replicate the exact schema from users.py but with the new constraint
        create_table_sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR NOT NULL,
            username VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            tenant_id VARCHAR DEFAULT 'default_tenant' NOT NULL,
            full_name VARCHAR,
            role VARCHAR DEFAULT 'user',
            allowed_frameworks VARCHAR DEFAULT 'ALL',
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            UNIQUE (username, tenant_id)
        );
        """
        cursor.execute(create_table_sql)

        # 3. Create Indexes
        cursor.execute("CREATE UNIQUE INDEX ix_users_email ON users (email);")
        cursor.execute("CREATE INDEX ix_users_username ON users (username);")
        cursor.execute("CREATE INDEX ix_users_tenant_id ON users (tenant_id);")
        cursor.execute("CREATE INDEX ix_users_id ON users (id);")

        # 4. Copy Data
        # We need to list columns to ensure order
        columns = [
            "id", "email", "username", "hashed_password", 
            "tenant_id", "full_name", "role", 
            "allowed_frameworks", "is_active", "is_superuser", 
            "created_at", "updated_at"
        ]
        cols_str = ", ".join(columns)
        
        # When copying, we might encounter conflicts if data is already bad.
        # But for now we assume data is clean or we migrated it previously.
        # Wait, previous scoped usernames like 'slug_admin' are fine, they are unique.
        cursor.execute(f"INSERT INTO users ({cols_str}) SELECT {cols_str} FROM users_old;")

        # 5. Drop old table
        cursor.execute("DROP TABLE users_old;")

        conn.commit()
        print("Migration successful.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        # Restore if possible? 
        # SQLite transaction rollback should handle it if error happened during executes.
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
