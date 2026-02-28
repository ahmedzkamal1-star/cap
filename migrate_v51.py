import sqlite3
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_management.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE system_settings ADD COLUMN platform_url VARCHAR(500)")
        print("Added platform_url column.")
    except Exception as e:
        print(f"Error or already exists: {e}")
        
    conn.commit()
    conn.close()
    print("Migration completed.")
else:
    print("Database not found.")
