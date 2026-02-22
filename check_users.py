from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("--- Users in DB ---")
    for u in users:
        print(f"Code: {u.code}, Role: {u.role}, Name: {u.full_name}")
