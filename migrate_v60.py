import sqlite3
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_management.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add columns to user table
    columns_to_add = [
        ("enc_key", "VARCHAR(64)"),
        ("pan_level", "INTEGER DEFAULT 0"),
        ("is_frozen", "BOOLEAN DEFAULT 0"),
        ("freeze_until", "DATETIME"),
        ("device_id", "VARCHAR(100)")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to user table.")
        except Exception as e:
            print(f"Column {col_name} might already exist: {e}")

    # Create Penalty table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS penalty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reason VARCHAR(200) NOT NULL,
                level INTEGER NOT NULL,
                timestamp DATETIME DEFAULT (datetime('now')),
                details TEXT,
                evidence_path VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("Created penalty table.")
    except Exception as e:
        print(f"Error creating penalty table: {e}")
        
    conn.commit()
    conn.close()
    print("Migration v60 completed.")
else:
    print("Database not found.")
