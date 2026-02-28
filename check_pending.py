from app import create_app
from models import User, db

app = create_app()
with app.app_context():
    pending = User.query.filter_by(is_approved=False).all()
    print(f"Total Pending: {len(pending)}")
    for u in pending:
        print(f"ID: {u.id}, Name: {u.full_name}, Code: {u.code}, Role: {u.role}")
