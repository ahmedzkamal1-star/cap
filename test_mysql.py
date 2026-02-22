from app import create_app
from config import Config

# Test MySQL connection
print("Testing MySQL connection...")
print(f"Host: {Config.MYSQL_HOST}")
print(f"User: {Config.MYSQL_USER}")
print(f"Database: {Config.MYSQL_DB}")
print(f"Connection String: {Config.SQLALCHEMY_DATABASE_URI}")

try:
    app = create_app()
    with app.app_context():
        from database import db
        # Try to connect
        db.engine.connect()
        print("\n✅ SUCCESS: Connected to MySQL successfully!")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nPossible solutions:")
    print("1. Make sure MySQL server is running")
    print("2. Check if database 'student_management' exists")
    print("3. Verify username and password in config.py")
