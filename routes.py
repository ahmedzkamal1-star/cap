from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, 
    current_app, send_from_directory, jsonify, make_response
)
from flask_login import login_user, logout_user, login_required, current_user
from models import (
    User, Course, Enrollment, Friend, Lesson, Exam, SystemSettings, 
    Message, ActivityLog, HomePost, ExamResult, Schedule, PostLike, PostComment, db
)
import json
import random

main = Blueprint('main', __name__)

@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@main.app_context_processor
def inject_global_vars():
    settings = SystemSettings.query.first()
    return dict(settings=settings, datetime=datetime, timedelta=timedelta)

def log_activity(action, details=None):
    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, action=action, details=details)
        db.session.add(log)
        db.session.commit()

@main.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'manifest.json')

@main.route('/sw.js')
def service_worker():
    response = send_from_directory(os.path.join(current_app.root_path, 'static'), 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@main.route('/')
def splash():
    # If the user is already logged in, we might skip the splash, 
    # but usually splash is for the landing brand experience.
    return render_template('splash.html')

@main.route('/home')
def index():
    from models import HomePost, PostView, Schedule
    posts = HomePost.query.order_by(HomePost.timestamp.desc()).all()
    latest_schedule = Schedule.query.order_by(Schedule.timestamp.desc()).first()
    
    if current_user.is_authenticated and current_user.role == 'student':
        # Track views for each post
        for post in posts:
            existing_view = PostView.query.filter_by(post_id=post.id, user_id=current_user.id).first()
            if not existing_view:
                view = PostView(post_id=post.id, user_id=current_user.id)
                db.session.add(view)
        db.session.commit()
        
    return render_template('index.html', posts=posts, latest_schedule=latest_schedule)

@main.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    from models import PostLike
    if current_user.role != 'student':
        return {"error": "Only students can like posts"}, 403
    
    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_like:
        db.session.delete(existing_like)
        status = 'unliked'
        # Optional: remove points? Better to leave them to avoid frustration
    else:
        new_like = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(new_like)
        status = 'liked'
        # Reward points for liking (+5)
        current_user.points += 5
    
    db.session.commit()
    return jsonify({'status': status, 'count': PostLike.query.filter_by(post_id=post_id).count()})

@main.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
    
    content = request.form.get('content')
    if content:
        comment = PostComment(post_id=post_id, user_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('تم إضافة تعليقك بنجاح!', 'success')
    return redirect(url_for('main.index'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        password = request.form.get('password')
        user = User.query.filter_by(code=code).first()
        
        if user and user.check_password(password):
            if not user.is_approved:
                flash('حسابك قيد المراجعة من قبل الإدارة. يرجى المحاولة لاحقاً.', 'warning')
                return redirect(url_for('main.login'))
            
            remember = request.form.get('remember') == 'on'
            login_user(user, remember=remember)
            log_activity("تسجيل دخول", f"المستخدم {user.code} سجل دخوله. (تذكرني: {remember})")
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.index'))
        else:
            print(f"Debug: Login failed for code '{code}'. User found: {user is not None}")
            flash('فشل تسجيل الدخول. تأكد من الكود الجامعي وكلمة المرور.', 'danger')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    from models import User, Course, Lesson, Enrollment
    if current_user.role == 'admin':
        students_count = User.query.filter_by(role='student').count()
        courses_count = Course.query.count()
        lessons_count = Lesson.query.count()
        enrollments_count = Enrollment.query.count()
        return render_template('admin_dashboard.html', 
                               students_count=students_count, 
                               courses_count=courses_count,
                               lessons_count=lessons_count,
                               enrollments_count=enrollments_count)
    
    # For students, show enrolled courses
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_course_ids = [e.course_id for e in enrollments]
    
    if enrolled_course_ids:
        available_courses = Course.query.filter(Course.id.notin_(enrolled_course_ids)).all()
    else:
        available_courses = Course.query.all()
        
    return render_template('dashboard.html', enrollments=enrollments, available_courses=available_courses)

@main.route('/view_pdf/<filename>')
@login_required
def view_pdf(filename):
    # Redirect directly to the file - most reliable across all devices
    return redirect(url_for('main.uploaded_file', filename=filename))

@main.route('/exam/<int:exam_id>')
@login_required
def view_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Check if user is enrolled in the course
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=exam.course_id).first()
    if not enrollment and current_user.role != 'admin':
        flash('يجب التسجيل في المادة أولاً لدخول الامتحان.', 'warning')
        return redirect(url_for('main.course_details', course_id=exam.course_id))

    try:
        questions_list = json.loads(exam.questions) if exam.questions else []
    except:
        questions_list = []
        
    if not questions_list:
        flash('لا توجد أسئلة في هذا الامتحان حالياً.', 'info')
        return redirect(url_for('main.course_details', course_id=exam.course_id))

    # Shuffle for randomization
    random.shuffle(questions_list)
    
    return render_template('view_exam.html', exam=exam, questions=questions_list)

@main.route('/submit_exam/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    import json
    exam = Exam.query.get_or_404(exam_id)
    questions = json.loads(exam.questions) if exam.questions else []
    
    score = 0
    total = len(questions)
    
    for i, q in enumerate(questions):
        answer = request.form.get(f'q{i}')
        if answer == q.get('correct'):
            score += 1
            
    final_score = (score / total * 100) if total > 0 else 0
    
    # Save result
    result = ExamResult(user_id=current_user.id, exam_id=exam.id, score=final_score, total_questions=total)
    db.session.add(result)
    
    # Reward points for passing (score >= 50%)
    if final_score >= 50:
        current_user.points += 50
        flash('ممتاز! حصلت على 50 نقطة لاجتيازك الامتحان بنجاح. 🚀', 'success')
    
    db.session.commit()
    return redirect(url_for('main.exam_result', result_id=result.id))

@main.route('/admin/exam/<int:exam_id>/results')
@login_required
def admin_view_exam_results(exam_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    exam = Exam.query.get_or_404(exam_id)
    results = ExamResult.query.filter_by(exam_id=exam_id).order_by(ExamResult.timestamp.desc()).all()
    
    return render_template('admin_exam_results.html', exam=exam, results=results)

@main.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    # Fetch lessons and exams related to the course explicitly
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.id).all()
    exams = Exam.query.filter_by(course_id=course_id).order_by(Exam.id).all()
    
    return render_template('course.html', course=course, lessons=lessons, exams=exams)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/schedules')
@login_required
def student_view_schedules():
    from models import Schedule
    all_schedules = Schedule.query.order_by(Schedule.timestamp.desc()).all()
    return render_template('schedules.html', schedules=all_schedules)

@main.route('/admin/secure-reset', methods=['GET', 'POST'])
def secure_reset():
    if request.method == 'POST':
        user_code = request.form.get('code')
        m_key = request.form.get('master_key')
        new_pass = request.form.get('new_password')
        
        user = User.query.filter_by(code=user_code).first()
        if user and user.master_key == m_key:
            user.set_password(new_pass)
            db.session.commit()
            flash('تم تغيير كلمة المرور بنجاح باستخدام كود الأمان.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('كود المستخدم أو كود الأمان غير صحيح.', 'danger')
            
    return render_template('secure_reset.html')

@main.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    # Check if already enrolled
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('أنت مسجل بالفعل في هذه المادة.', 'info')
        return redirect(url_for('main.dashboard'))
        
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    
    # Reward points for enrollment (+20)
    current_user.points += 20
    
    db.session.commit()
    flash('تم التسجيل في المادة بنجاح! حصلت على 20 نقطة. 🚀', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    if request.method == 'POST':
        friend_code = request.form.get('friend_code')
        if friend_code == current_user.code:
            flash('لا يمكنك إضافة نفسك كصديق.', 'warning')
        else:
            friend_user = User.query.filter_by(code=friend_code).first()
            if not friend_user:
                flash('لم يتم العثور على طالب بهذا الكود.', 'danger')
            else:
                # Check directly using db query for simplicity 
                existing = Friend.query.filter(
                    ((Friend.user_code == current_user.code) & (Friend.friend_code == friend_code)) |
                    ((Friend.user_code == friend_code) & (Friend.friend_code == current_user.code))
                ).first()
                
                if existing:
                    flash('أنتم أصدقاء بالفعل أو يوجد طلب معلق.', 'info')
                else:
                    new_friend = Friend(user_code=current_user.code, friend_code=friend_code, status='accepted')
                    db.session.add(new_friend)
                    db.session.commit()
                    flash('تم إضافة الصديق بنجاح!', 'success')
    
    # Get friends
    friends_list = []
    friendships = Friend.query.filter(
        ((Friend.user_code == current_user.code) | (Friend.friend_code == current_user.code)) &
        (Friend.status == 'accepted')
    ).all()
    
    for f in friendships:
        code = f.friend_code if f.user_code == current_user.code else f.user_code
        user = User.query.filter_by(code=code).first()
        if user:
            friends_list.append(user)
            
    return render_template('friends.html', friends=friends_list)

@main.route('/chat/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def private_chat(recipient_id):
    if current_user.role != 'student':
        return redirect(url_for('main.dashboard'))
    
    recipient = User.query.get_or_404(recipient_id)
    if recipient.role != 'student':
        return redirect(url_for('main.friends'))
    
    if request.method == 'POST':
        body = request.form.get('message')
        if body:
            new_msg = Message(sender_id=current_user.id, recipient_id=recipient.id, body=body, subject=f"Private Chat")
            db.session.add(new_msg)
            db.session.commit()
            return redirect(url_for('main.private_chat', recipient_id=recipient.id))

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient.id)) |
        ((Message.sender_id == recipient.id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark messages as read
    Message.query.filter_by(sender_id=recipient.id, recipient_id=current_user.id).update({Message.is_read: True})
    db.session.commit()

    return render_template('student_chat.html', recipient=recipient, messages=messages)


# --- Admin Routes ---

@main.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    from models import User, Course, Lesson, Enrollment
    students_count = User.query.filter_by(role='student').count()
    courses_count = Course.query.count()
    lessons_count = Lesson.query.count()
    enrollments_count = Enrollment.query.count()
    
    return render_template('admin_dashboard.html', 
                           students_count=students_count,
                           courses_count=courses_count,
                           lessons_count=lessons_count,
                           enrollments_count=enrollments_count)

@main.route('/admin/students')
@login_required
def admin_students():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    students = User.query.filter_by(role='student').all()
    return render_template('admin_students.html', students=students)

@main.route('/admin/moderators')
@login_required
def admin_moderators():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Super Admin (123456) sees ALL admins in the system
    if current_user.code == '123456':
        moderators = User.query.filter(
            User.role == 'admin',
            User.code != 'test'  # exclude test accounts
        ).all()
    else:
        # Each admin ONLY sees the moderators they personally appointed
        moderators = User.query.filter_by(
            role='admin',
            created_by_id=current_user.id
        ).all()
        
    return render_template('admin_moderators.html', moderators=moderators)

@main.route('/admin/pending_users')
@login_required
def admin_pending_users():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('admin_pending.html', pending=pending_users)

@main.route('/admin/approve_user/<int:user_id>/<string:action>')
@login_required
def admin_approve_user(user_id, action):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    if action == 'approve':
        user.is_approved = True
        flash(f'تم قبول الطالب {user.full_name} بنجاح.', 'success')
    elif action == 'reject':
        db.session.delete(user)
        flash(f'تم رفض وحذف طلب {user.full_name}.', 'info')
    
    db.session.commit()
    return redirect(url_for('main.admin_pending_users'))

@main.route('/admin/moderator/<int:user_id>/demote', methods=['POST'])
@login_required
def admin_demote_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Protected Super Admin logic (123456)
    if user.code == '123456':
        flash('لا يمكن تخفيض رتبة المشرف الرئيسي للنظام.', 'danger')
        return redirect(url_for('main.admin_moderators'))

    # Only Super Admin or the creator can demote
    if current_user.code != '123456' and user.created_by_id != current_user.id:
        flash('ليس لديك صلاحية لتخفيض رتبة هذا المشرف.', 'danger')
        return redirect(url_for('main.admin_moderators'))

    user.role = 'student'
    db.session.commit()
    log_activity("تخفيض رتبة", f"تم تخفيض رتبة {user.full_name} إلى طالب")
    flash(f'تم تخفيض رتبة {user.full_name} بنجاح.', 'success')
    return redirect(url_for('main.admin_moderators'))

@main.route('/admin/student/new', methods=['GET', 'POST'])
@login_required
def admin_add_student():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        phone = request.form.get('phone')
        department = request.form.get('department')
        year = request.form.get('year')
        
        if User.query.filter_by(code=code).first():
            flash('Error: User code already exists.', 'danger')
        else:
            role = request.form.get('role', 'student')
            new_student = User(code=code, full_name=full_name, phone=phone, 
                               department=department, year=year, role=role,
                               created_by_id=current_user.id)
            new_student.set_password(password)
            db.session.add(new_student)
            db.session.commit()
            log_activity("إضافة مستخدم", f"تم إضافة {'مشرف' if role=='admin' else 'طالب'} جديد: {full_name} ({code})")
            flash('User added successfully!', 'success')
            return redirect(url_for('main.admin_students'))
            
    return render_template('admin_student_form.html', action='Add')

@main.route('/admin/student/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_student(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    student = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.phone = request.form.get('phone')
        student.email = request.form.get('email')
        student.department = request.form.get('department')
        student.year = request.form.get('year')
        
        new_role = request.form.get('role')
        if new_role:
            # Protect Super Admin from role changes
            if student.code == '123456' and new_role != 'admin':
                flash('لا يمكن تغيير رتبة المشرف الرئيسي للنظام.', 'warning')
            else:
                if student.role != new_role:
                    log_activity("تغيير صلاحية", f"تم تغيير دور {student.full_name} من {student.role} إلى {new_role}")
                student.role = new_role
                # Hierarchy fix: if promoted to admin and doesn't have a creator, set current admin as creator
                if new_role == 'admin' and not student.created_by_id:
                    student.created_by_id = current_user.id
        
        # Update password only if provided
        new_password = request.form.get('password')
        if new_password:
            student.set_password(new_password)
            log_activity("تغيير كلمة مرور", f"تم تغيير كلمة مرور المستخدم {student.code}")
        
        db.session.commit()
        log_activity("تعديل مستخدم", f"تم تحديث بيانات المستخدم {student.code}")
        flash('تم تحديث بيانات المستخدم بنجاح!', 'success')
        return redirect(url_for('main.admin_students'))
        
    return render_template('admin_student_form.html', action='Edit', student=student)

@main.route('/admin/student/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_student(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    log_activity("حذف مستخدم", f"تم حذف المستخدم: {name} ({user_id})")
    flash('تم حذف الطالب وكامل بياناته بنجاح.', 'success')
    return redirect(url_for('main.admin_students'))

@main.route('/admin/courses')
@login_required
def admin_courses():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    courses = Course.query.all()
    return render_template('admin_courses.html', courses=courses)

@main.route('/admin/course/new', methods=['GET', 'POST'])
@login_required
def admin_add_course():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name')
        description = request.form.get('description')
        credits = request.form.get('credits')
        instructor = request.form.get('instructor')
        
        # Simple validation
        if Course.query.filter_by(code=code).first():
            flash('Error: Course code already exists.', 'danger')
        else:
            new_course = Course(code=code, name=name, description=description, 
                                credits=int(credits), instructor=instructor)
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')
            return redirect(url_for('main.admin_courses'))
            
    return render_template('admin_course_form.html', action='Add')

@main.route('/admin/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_course(course_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.name = request.form.get('name')
        course.description = request.form.get('description')
        course.credits = int(request.form.get('credits'))
        course.instructor = request.form.get('instructor')
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('main.admin_courses'))
        
    return render_template('admin_course_form.html', action='Edit', course=course)

@main.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@login_required
def admin_delete_course(course_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    course = Course.query.get_or_404(course_id)
    # Delete related enrollments, lessons, and exams
    Enrollment.query.filter_by(course_id=course.id).delete()
    Lesson.query.filter_by(course_id=course.id).delete()
    Exam.query.filter_by(course_id=course.id).delete()
    
    db.session.delete(course)
    db.session.commit()
    flash('Course and all its content deleted successfully.', 'success')
    return redirect(url_for('main.admin_courses'))

@main.route('/admin/course/<int:course_id>/content')
@login_required
def admin_course_content(course_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    course = Course.query.get_or_404(course_id)
    return render_template('admin_course_content.html', course=course)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

@main.route('/admin/course/<int:course_id>/lesson/new', methods=['GET', 'POST'])
@login_required
def admin_add_lesson(course_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        pdf_filename = None
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file and file.filename != '' and allowed_file(file.filename):
                import uuid
                # Get extension from original filename before secure_filename strips Arabic
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'pdf'
                filename = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                pdf_filename = filename

        new_lesson = Lesson(course_id=course.id, title=title, content=content, pdf_filename=pdf_filename)
        db.session.add(new_lesson)
        db.session.commit()
        flash('تم إضافة الدرس بنجاح!', 'success')
        return redirect(url_for('main.admin_course_content', course_id=course.id))
        
    return render_template('admin_lesson_form.html', course=course)

@main.route('/admin/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def admin_delete_lesson(lesson_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    db.session.delete(lesson)
    db.session.commit()
    flash('تم حذف الدرس بنجاح.', 'info')
    return redirect(url_for('main.admin_course_content', course_id=course_id))

@main.route('/admin/course/<int:course_id>/exam/new', methods=['GET', 'POST'])
@login_required
def admin_add_exam(course_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
        
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        questions = request.form.get('questions')
        
        new_exam = Exam(course_id=course.id, title=title, questions=questions)
        db.session.add(new_exam)
        db.session.commit()
        flash('تم إضافة الامتحان بنجاح!', 'success')
        return redirect(url_for('main.admin_course_content', course_id=course.id))
        
    return render_template('admin_exam_form.html', course=course)

@main.route('/admin/exam/<int:exam_id>/delete', methods=['POST'])
@login_required
def admin_delete_exam(exam_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    exam = Exam.query.get_or_404(exam_id)
    course_id = exam.course_id
    db.session.delete(exam)
    db.session.commit()
    flash('تم حذف الامتحان بنجاح.', 'info')
    return redirect(url_for('main.admin_course_content', course_id=course_id))

@main.route('/admin/online')
@login_required
def admin_online_users():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    from datetime import timedelta
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    online_users = User.query.filter(User.last_seen >= five_minutes_ago).all()
    return render_template('admin_online.html', students=online_users)

@main.route('/admin/activity')
@login_required
def admin_activity():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(100).all()
    return render_template('admin_activity.html', logs=logs)

@main.route('/admin/students/reset-all', methods=['POST'])
@login_required
def admin_reset_all_passwords():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    students = User.query.filter_by(role='student').all()
    temp_pass = "123456"
    for student in students:
        student.set_password(temp_pass)
    
    db.session.commit()
    log_activity("تصفير كلمات المرور", f"تم تصفير كلمات مرور جميع الطلاب ({len(students)} طالب) إلى '123456'")
    flash(f"تم تصفير كلمات مرور {len(students)} طالب بنجاح إلى '123456'.", 'success')
    return redirect(url_for('main.admin_students'))

@main.route('/admin/students/delete-all', methods=['POST'])
@login_required
def admin_delete_all_students():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    confirm = request.form.get('confirm')
    if confirm != 'DELETE_ALL':
        flash('يرجى كتابة الكود الصحيح للتأكيد.', 'danger')
        return redirect(url_for('main.admin_students'))
    
    students = User.query.filter_by(role='student').all()
    count = len(students)
    for student in students:
        Enrollment.query.filter_by(student_id=student.id).delete()
        db.session.delete(student)
    
    db.session.commit()
    log_activity("حذف جماعي للطلاب", f"تم حذف جميع الطلاب ({count} طالب) من النظام.")
    flash(f"تم حذف {count} طالب بنجاح.", 'success')
    return redirect(url_for('main.admin_students'))

@main.route('/admin-chat', methods=['GET', 'POST'])
@login_required
def admin_chat():
    if current_user.role != 'student':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        body = request.form.get('message')
        
        new_msg = Message(sender_id=current_user.id, subject=subject, body=body)
        db.session.add(new_msg)
        db.session.commit()
        flash('تم إرسال رسالتك بنجاح! سيرد عليك الأدمن قريباً.', 'success')
        return redirect(url_for('main.admin_chat'))

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template('admin_chat.html', messages=messages)

@main.route('/admin/messages')
@login_required
def admin_messages():
    from models import Message
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    # Get all students who have sent messages to admin (recipient_id is None)
    student_ids = db.session.query(Message.sender_id).filter(Message.recipient_id.is_(None)).distinct().all()
    student_ids = [s[0] for s in student_ids]
    students = User.query.filter(User.id.in_(student_ids)).all()
    
    return render_template('admin_messages.html', students=students, Message=Message)

@main.route('/admin/message/<int:student_id>', methods=['GET', 'POST'])
@login_required
def admin_view_student_messages(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    student = User.query.get_or_404(student_id)
    
    if request.method == 'POST':
        body = request.form.get('message')
        new_msg = Message(sender_id=current_user.id, recipient_id=student.id, body=body, subject=f"Re: From Admin")
        db.session.add(new_msg)
        
        # Mark student's messages as read
        Message.query.filter_by(sender_id=student.id).filter(Message.recipient_id.is_(None)).update({Message.is_read: True})
        
        db.session.commit()
        flash('تم إرسال الرد بنجاح!', 'success')
        return redirect(url_for('main.admin_view_student_messages', student_id=student.id))

    messages = Message.query.filter(
        ((Message.sender_id == student.id) & (Message.recipient_id.is_(None))) |
        ((Message.sender_id == current_user.id) & (Message.recipient_id == student.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template('admin_reply.html', student=student, messages=messages)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Gated route to serve files with proper headers for mobile compatibility."""
    import mimetypes
    directory = current_app.config['UPLOAD_FOLDER']
    
    # Determine proper content type and clean download name
    mime_type, _ = mimetypes.guess_type(filename)
    download_name = filename
    
    if not mime_type:
        # Old files saved as "uuid_pdf" or "uuid_jpg" without a dot
        if filename.lower().endswith('pdf'):
            mime_type = 'application/pdf'
            download_name = filename + '.pdf' if '.' not in filename else filename
        elif filename.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
            ext = filename.rsplit('_', 1)[-1] if '_' in filename else 'jpg'
            mime_type = f'image/{ext}'
            download_name = filename + f'.{ext}' if '.' not in filename else filename
        else:
            mime_type = 'application/octet-stream'
    
    response = send_from_directory(directory, filename)
    response.headers["Content-Type"] = mime_type
    response.headers["Content-Disposition"] = f"inline; filename=\"{download_name}\""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@main.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.system_name = request.form.get('system_name')
        settings.contact_email = request.form.get('contact_email')
        settings.contact_phone = request.form.get('contact_phone')
        settings.telegram_link = request.form.get('telegram_link', '').strip()
        settings.whatsapp_link = request.form.get('whatsapp_link', '').strip()
        settings.allow_registration = 'allow_registration' in request.form
        settings.maintenance_mode = 'maintenance_mode' in request.form
        settings.show_schedule = 'show_schedule' in request.form
        
        # Security Updates for Admin
        new_pass = request.form.get('admin_password')
        new_master = request.form.get('master_key')
        
        if new_pass:
            current_user.set_password(new_pass)
            flash('تم تحديث كلمة مرور الأدمن بنجاح.', 'success')
            
        if new_master:
            current_user.master_key = new_master
            flash('تم تحديث كود الأمان بنجاح.', 'success')
            
        # Schedule Update
        if 'schedule_file' in request.files:
            file = request.files['schedule_file']
            if file and file.filename != '':
                import uuid
                filename = secure_filename(file.filename)
                filename = f"schedule_{uuid.uuid4().hex[:8]}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                settings.schedule_filename = filename
                flash('تم رفع الجدول الدراسي بنجاح.', 'success')

        db.session.commit()
        flash('تم تحديث إعدادات النظام بنجاح!', 'success')
        return redirect(url_for('main.admin_settings'))
        
    unread_count = Message.query.filter_by(recipient_id=None, is_read=False).count()
    return render_template('admin_settings.html', settings=settings, unread_count=unread_count)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    settings = SystemSettings.query.first()
    if settings and not settings.allow_registration:
        flash('عذراً، التسجيل مغلق حالياً من قبل الإدارة.', 'warning')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        phone = request.form.get('phone')
        department = request.form.get('department')
        year = request.form.get('year')
        
        if User.query.filter_by(code=code).first():
            flash('هذا الكود الجامعي مسجل بالفعل.', 'danger')
        else:
            gender = request.form.get('gender', 'male')
            new_student = User(code=code, full_name=full_name, phone=phone, 
                              department=department, year=year, role='student', 
                              is_approved=False, gender=gender)
            new_student.set_password(password)
            db.session.add(new_student)
            db.session.commit()
            flash('تم إنشاء الحساب بنجاح! بانتظار موافقة الأدمن لتتمكن من الدخول.', 'success')
            return redirect(url_for('main.login'))
            
    return render_template('register.html')

@main.route('/admin/posts', methods=['GET', 'POST'])
@login_required
def admin_posts():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        image_filename = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                filename = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        pdf_filename = None
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file and file.filename != '':
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'pdf'
                filename = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                pdf_filename = filename
        
        new_post = HomePost(title=title, content=content, image_filename=image_filename, pdf_filename=pdf_filename)
        db.session.add(new_post)
        db.session.commit()
        flash('تم نشر الخبر بنجاح على الصفحة الرئيسية.', 'success')
        return redirect(url_for('main.admin_posts'))

    posts = HomePost.query.order_by(HomePost.timestamp.desc()).all()
    return render_template('admin_posts.html', posts=posts)

@main.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    post = HomePost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('تم حذف المنشور.', 'info')
    return redirect(url_for('main.admin_posts'))

@main.route('/admin/schedules', methods=['GET', 'POST'])
@login_required
def admin_manage_schedules():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        filename = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                filename = f"sch_{uuid.uuid4().hex[:8]}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        new_sch = Schedule(title=title, content=content, filename=filename)
        db.session.add(new_sch)
        db.session.commit()
        flash('تم إضافة الجدول بنجاح.', 'success')
        return redirect(url_for('main.admin_manage_schedules'))

    schedules = Schedule.query.order_by(Schedule.timestamp.desc()).all()
    return render_template('admin_schedules.html', schedules=schedules)

@main.route('/admin/schedule/<int:sch_id>/delete', methods=['POST'])
@login_required
def admin_delete_schedule(sch_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    sch = Schedule.query.get_or_404(sch_id)
    db.session.delete(sch)
    db.session.commit()
    flash('تم حذف الجدول.', 'info')
    return redirect(url_for('main.admin_manage_schedules'))

