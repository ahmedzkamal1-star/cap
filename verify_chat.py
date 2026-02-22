from app import create_app, db
from models import User, Message

app = create_app()
with app.app_context():
    student = User.query.filter_by(code='231266').first()
    admin = User.query.filter_by(code='admin').first()
    
    if student and admin:
        # 1. Student sends message
        msg1 = Message(sender_id=student.id, subject="سؤال عن جدول المحاضرات", body="مرحبا أدمن، متى سيتم تنزيل جدول محاضرات الترم الثاني؟")
        db.session.add(msg1)
        db.session.commit()
        print(f"Message sent from student {student.code} to Admin.")
        
        # 2. Admin replies
        reply = Message(sender_id=admin.id, recipient_id=student.id, body="أهلاً بك، الجدول سيكون متاحاً يوم السبت القادم إن شاء الله.")
        db.session.add(reply)
        db.session.commit()
        print(f"Reply sent from Admin to student {student.code}.")
        
        # Verify
        messages = Message.query.filter(
            ((Message.sender_id == student.id) | (Message.recipient_id == student.id))
        ).all()
        print(f"Total messages in conversation: {len(messages)}")
    else:
        print("Required users not found.")
