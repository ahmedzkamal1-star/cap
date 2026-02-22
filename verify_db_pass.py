from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(code='231266').first()
    if user:
        result = user.check_password('123456')
        print(f"User: {user.code}")
        print(f"Hash in DB: {user.password_hash}")
        print(f"Check Result for '123456': {result}")
    else:
        print("User not found.")
