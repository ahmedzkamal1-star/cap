from datetime import datetime
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False) # University Code (Username)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    department = db.Column(db.String(50))
    year = db.Column(db.String(20))
    role = db.Column(db.String(20), default='student')  # 'admin' or 'student'
    is_approved = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade="all, delete-orphan")
    
    # Friends System: Self-referential relationship
    friends_requested = db.relationship('Friend', 
                                foreign_keys='Friend.user_code',
                                backref='requester', 
                                lazy='dynamic',
                                cascade="all, delete")
    friends_received = db.relationship('Friend', 
                               foreign_keys='Friend.friend_code',
                               backref='receiver', 
                               lazy='dynamic',
                               cascade="all, delete")
    
    # Messaging
    # A message has two parents (sender/recipient), so we use "all, delete" without orphan protection to avoid conflicts
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic', cascade="all, delete")
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic', cascade="all, delete")
    
    # Social & Activity (Single parent relations, safe for delete-orphan)
    activities = db.relationship('ActivityLog', backref='user', cascade="all, delete-orphan")
    post_likes = db.relationship('PostLike', backref='user', cascade="all, delete-orphan")
    post_views = db.relationship('PostView', backref='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(20), db.ForeignKey('user.code'), nullable=False)
    friend_code = db.Column(db.String(20), db.ForeignKey('user.code'), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructor = db.Column(db.String(100))
    credits = db.Column(db.Integer, default=3)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    lessons = db.relationship('Lesson', backref='course', lazy=True)
    exams = db.relationship('Exam', backref='course', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text) # Could be text or link to PDF/Video
    pdf_filename = db.Column(db.String(255)) # Store filename of uploaded PDF

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    questions = db.Column(db.Text) # JSON string or text content

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True) # Optional grade
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(100), default='Al-dahih System')
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    allow_registration = db.Column(db.Boolean, default=True)
    maintenance_mode = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # NULL means to Admin
    subject = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Relationships are now defined in the User model for better cascade control
    # sender, recipient backrefs are automatically created
    pass

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

    # user backref is now defined in User model
    pass

class HomePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    views = db.relationship('PostView', backref='post', lazy='dynamic', cascade="all, delete-orphan")

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('home_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # user backref is now defined in User model
    pass

class PostView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('home_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # user backref is now defined in User model
    pass
