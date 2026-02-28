import sqlite3
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_management.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE system_settings ADD COLUMN telegram_bot_token VARCHAR(255)")
        print("Added telegram_bot_token column.")
    except Exception as e:
        print(f"Error or already exists: {e}")
        
    try:
        cursor.execute("ALTER TABLE system_settings ADD COLUMN telegram_chat_id VARCHAR(255)")
        print("Added telegram_chat_id column.")
    except Exception as e:
        print(f"Error or already exists: {e}")
        
    conn.commit()
    conn.close()
    print("Database migration completed.")
else:
    print("Database file not found.")
