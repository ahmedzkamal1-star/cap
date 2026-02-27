from app import create_app
from database import db
import sqlalchemy
from models import *

app = create_app()

def migrate():
    with app.app_context():
        # First, ensure all tables are created (especially new ones like Schedule)
        try:
            db.create_all()
            print("db.create_all() ran successfully.")
        except Exception as e:
            print(f"Error during db.create_all(): {e}")

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

            for table, cols in [('user', columns_user), ('system_settings', columns_settings)]:
                for col, spec in cols.items():
                    try:
                        conn.execute(sqlalchemy.text(f'ALTER TABLE {table} ADD COLUMN {col} {spec}'))
                        print(f'Added column {col} to {table} table.')
                    except Exception as e:
                        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                            print(f'Column {col} already exists in {table}.')
                        else:
                            print(f'Error adding {col} to {table}: {e}')
            
            conn.commit()
            print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
