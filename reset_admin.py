from app import create_app, db
from models import User
from sqlalchemy import text
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # 1. Try to add the master_key column (SQLite safe check)
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN master_key VARCHAR(100)"))
        db.session.commit()
        print("Column 'master_key' added to 'user' table.")
    except Exception as e:
        db.session.rollback()
        print("Note: Column 'master_key' already exists.")

    # 2. Update Admin User
    admin = User.query.filter_by(role='admin').first()
    if admin:
        admin.master_key = 'Riko00ooAa#'
        # Update password using pbkdf2:sha256 for OpenSSL 3.0 compatibility
        admin.password_hash = generate_password_hash('Riko00ooAa#', method='pbkdf2:sha256')
        db.session.commit()
        print(f"Admin {admin.code} updated: Password & Master Key set to 'Riko00ooAa#'.")
    else:
        print("Admin user not found.")
