import sqlite3
import os

db_path = 'student_management.db'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Add missing columns to 'user' table
        user_columns = [
            ('last_seen', 'DATETIME'),
            ('created_by_id', 'INTEGER'),
            ('master_key', 'TEXT')
        ]
        
        for col_name, col_type in user_columns:
            try:
                cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
                print(f"Successfully added '{col_name}' column to 'user' table.")
            except sqlite3.OperationalError as e:
                pass # Already exists
        
        # 2. Check if SystemSettings has at least one entry
        try:
            cursor.execute("SELECT id FROM system_settings LIMIT 1")
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO system_settings (system_name) VALUES ('Al-dahih System')")
                print("Added default entry to 'system_settings' table.")
        except sqlite3.OperationalError:
            # Table doesn't exist? Create all missing tables by running the app's create_all later or doing it here
            print("Warning: 'system_settings' table might be missing.")
        
        conn.commit()
        conn.close()
        print("Database synchronization completed.")
    except Exception as e:
        print(f"An error occurred: {e}")
