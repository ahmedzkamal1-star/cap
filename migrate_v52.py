import sqlite3
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_management.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN telegram_id VARCHAR(50)")
        cursor.execute("CREATE INDEX idx_user_telegram_id ON user(telegram_id)")
        print("Added telegram_id column and index.")
    except Exception as e:
        print(f"Error or already exists: {e}")
        
    conn.commit()
    conn.close()
    print("Migration completed.")
else:
    print("Database not found.")
