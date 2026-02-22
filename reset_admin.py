from app import create_app, db
from models import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 1. Try to add the master_key column if it doesn't exist (SQLite safe check)
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN master_key VARCHAR(100)"))
        db.session.commit()
        print("Column 'master_key' added to 'user' table.")
    except Exception as e:
        db.session.rollback()
        print("Note: Column 'master_key' might already exist or could not be added via script.")

    # 2. Find admin and set both password and master key
    admin = User.query.filter_by(role='admin').first()
        
    if admin:
        print(f"Admin found: {admin.full_name} (Code: {admin.code})")
        # We set the MASTER KEY to the value provided by the user
        admin.master_key = 'Riko00ooAa#'
        # We can also set a default password if they want, but let's stick to the master key setup
        db.session.commit()
        print(f"Master Security Key set to 'Riko00ooAa#' for admin {admin.code}.")
    else:
        print("Admin user not found. Please ensure you have an admin account created.")
