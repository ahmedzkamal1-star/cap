from app import create_app, db
from models import User, Course, Lesson, Exam, SystemSettings
import os

app = create_app()

with app.app_context():
    # Use drop_all to clear schema instead of deleting file (avoids lock issues)
    db.drop_all()
    db.create_all()
    
    # Admin
    if not User.query.filter_by(code='admin').first():
        admin = User(code='admin', 
                     # username removed
                     full_name='System Administrator', 
                     role='admin',
                     is_approved=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
    # Student 1 (Ahmed)
    if not User.query.filter_by(code='2023001').first():
        s1 = User(code='2023001', 
                  # username removed
                  full_name='أحمد محمد', 
                  phone='01012345678',
                  department='CS',
                  year='2',
                  role='student',
                  is_approved=True)
        s1.set_password('123456')
        db.session.add(s1)

    # Student 2 (Sarah)
    if not User.query.filter_by(code='2023002').first():
        s2 = User(code='2023002', 
                  # username removed
                  full_name='سارة علي', 
                  role='student',
                  is_approved=True)
        s2.set_password('123456')
        db.session.add(s2)

    # Courses
    math = Course(code='MATH101', name='رياضيات 1', description='مقدمة في التفاضل والتكامل', credits=3, instructor='د. علي')
    cs = Course(code='CS101', name='مقدمة علوم الحاسب', description='أساسيات البرمجة والخوارزميات', credits=4, instructor='د. منى')
    physics = Course(code='PHY101', name='فيزياء عامة', description='الميكانيكا والكهرباء', credits=3, instructor='د. حسن')
    english = Course(code='ENG101', name='لغة إنجليزية', description='مهارات الكتابة والقراءة', credits=2, instructor='د. نهى')
    history = Course(code='HIS101', name='تاريخ العلوم', description='تطور العلوم عبر العصور', credits=2, instructor='د. سامي')

    db.session.add_all([math, cs, physics, english, history])
    db.session.commit() # Commit to get IDs

    # Lessons & Exams for Math
    l1 = Lesson(course_id=math.id, title='الدرس الأول: النهايات', content='شرح مفهوم النهايات والاتصال...')
    l2 = Lesson(course_id=math.id, title='الدرس الثاني: قواعد الاشتقاق', content='قواعد القوة، الضرب، والقسمة...')
    e1 = Exam(course_id=math.id, title='امتحان منتصف الفصل', questions='س1: أوجد مشتقة الدالة...')
    
    db.session.add_all([l1, l2, e1])

    # Enroll Ahmed (s1) in all courses
    from models import Enrollment
    enrollments = [
        Enrollment(student_id=s1.id, course_id=math.id),
        Enrollment(student_id=s1.id, course_id=cs.id),
        Enrollment(student_id=s1.id, course_id=physics.id),
        Enrollment(student_id=s1.id, course_id=english.id),
        Enrollment(student_id=s1.id, course_id=history.id)
    ]
    db.session.add_all(enrollments)

    # Default System Settings
    if not SystemSettings.query.first():
        settings = SystemSettings(system_name='نظام الدحيح التعليمي',
                                  contact_email='support@aldahih.edu',
                                  contact_phone='0123456789')
        db.session.add(settings)

    # Sample Posts
    from models import HomePost
    p1 = HomePost(title='أهلاً بكم في نظام الدحيح المطور', 
                 content='هذا النظام مصمم لتسهيل العملية التعليمية وتوفير كافة المصادر للطلاب بشكل ميسر.')
    p2 = HomePost(title='تحديث جديد للمنصة', 
                 content='تم إضافة ميزة التفاعل مع المنشورات ومتابعة المواد بشكل أفضل على الهواتف.')
    db.session.add_all([p1, p2])

    db.session.commit()
    print("Database re-initialized with V2 schema and sample data.")
