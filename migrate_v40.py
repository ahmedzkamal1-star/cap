from app import create_app
from database import db
import sqlalchemy

app = create_app()

def migrate():
    with app.app_context():
        with db.engine.connect() as conn:
            # Table: user
            columns_user = {
                'is_approved': 'BOOLEAN DEFAULT 0',
                'last_seen': 'DATETIME',
                'gender': "VARCHAR(10) DEFAULT 'male'",
                'points': 'INTEGER DEFAULT 0'
            }
            
            # Table: system_settings
            columns_settings = {
                'show_schedule': 'BOOLEAN DEFAULT 1',
                'telegram_link': 'VARCHAR(500)',
                'whatsapp_link': 'VARCHAR(500)'
            }

            for col, spec in columns_user.items():
                try:
                    conn.execute(sqlalchemy.text(f'ALTER TABLE user ADD COLUMN {col} {spec}'))
                    print(f'Added column {col} to user table.')
                except Exception as e:
                    print(f'Column {col} already exists in user or error: {e}')

            for col, spec in columns_settings.items():
                try:
                    conn.execute(sqlalchemy.text(f'ALTER TABLE system_settings ADD COLUMN {col} {spec}'))
                    print(f'Added column {col} to system_settings table.')
                except Exception as e:
                    print(f'Column {col} already exists in system_settings or error: {e}')
            
            conn.commit()
            print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
