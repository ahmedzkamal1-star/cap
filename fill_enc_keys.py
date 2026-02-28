from app import create_app
from models import User, db
from security_utils import generate_user_key

app = create_app()
with app.app_context():
    users = User.query.filter(User.enc_key == None).all()
    print(f"Generating keys for {len(users)} users...")
    for u in users:
        u.enc_key = generate_user_key()
    db.session.commit()
    print("Done.")
