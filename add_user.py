from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    # Add new user
    user = User(code='231266', full_name='New User', role='student')
    user.set_password('11223300')
    db.session.add(user)
    db.session.commit()
    print('User added successfully!')
