from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(code='231266').first()
    if user:
        print(f"User found: {user.full_name}")
        user.set_password('123456')
        db.session.commit()
        print("Password reset to '123456' successfully.")
    else:
        print("User '231266' not found.")
