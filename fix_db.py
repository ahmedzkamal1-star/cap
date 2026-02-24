import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = 'student_management.db'

def fix_database():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Add missing columns to 'user' table
        user_columns = [
            ('last_seen', 'DATETIME'),
            ('created_by_id', 'INTEGER'),
            ('master_key', 'TEXT'),
            ('gender', 'TEXT DEFAULT "male"')
        ]
        
        for col_name, col_type in user_columns:
            try:
                cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
                print(f"Successfully added '{col_name}' column to 'user' table.")
            except sqlite3.OperationalError:
                pass # Already exists
        
        # 1.1 Add missing columns to 'home_post' table
        try:
            cursor.execute("ALTER TABLE home_post ADD COLUMN image_filename TEXT")
            print("Successfully added 'image_filename' column to 'home_post' table.")
        except sqlite3.OperationalError:
            pass # Already exists

        # 1.2 Schedule System Update (v25.0)
        # Create Schedule table if it doesn't exist
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS schedule 
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              title TEXT NOT NULL, 
                              content TEXT, 
                              filename TEXT, 
                              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            print("Successfully created/verified 'schedule' table.")
        except sqlite3.OperationalError as e:
            print(f"Error creating schedule table: {e}")

        # 2. Ensure SystemSettings entry
        try:
            cursor.execute("SELECT id FROM system_settings LIMIT 1")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO system_settings (system_name) VALUES ('Al-dahih System')")
                print("Added default SystemSettings.")
        except sqlite3.OperationalError:
            print("Warning: 'system_settings' table might be missing.")

        # 3. VERIFY/RESET ADMIN ACCOUNT
        # We will ensure an admin with code 'admin' exists and is approved.
        admin_code = 'admin'
        admin_password = 'admin123'
        pass_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
        
        cursor.execute("SELECT id FROM user WHERE code = ?", (admin_code,))
        user = cursor.fetchone()
        
        if user:
            # Update existing admin to ensure it's approved and has correct password
            cursor.execute("""
                UPDATE user 
                SET role = 'admin', is_approved = 1, password_hash = ? 
                WHERE code = ?
            """, (pass_hash, admin_code))
            print(f"Updated existing user '{admin_code}' to Admin status and reset password to '{admin_password}'.")
        else:
            # Create new admin
            cursor.execute("""
                INSERT INTO user (code, password_hash, full_name, role, is_approved)
                VALUES (?, ?, ?, ?, ?)
            """, (admin_code, pass_hash, 'System Administrator', 'admin', 1))
            print(f"Created new Admin account: User: '{admin_code}' / Pass: '{admin_password}'.")

        conn.commit()
        conn.close()
        print("Database synchronization and Admin recovery completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_database()
