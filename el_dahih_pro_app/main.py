"""
El-Dahih Educational Platform - Mobile Application
Advanced Kivy/KivyMD Application with Multi-language and Theme Support
"""

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

from auth_manager import AuthManager
from security_logic import SecurityShield, AntiTamper
from encryption_utils import EncryptionManager, SecureStorage
from arabic_reshaper import reshape
from bidi.algorithm import get_display

import os
import platform
import logging
import requests
import json
from kivy.core.text import LabelBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register Arabic font
if platform.system() == 'Windows':
    arial_path = 'C:\\Windows\\Fonts\\arial.ttf'
    if os.path.exists(arial_path):
        LabelBase.register(
            name='Arabic',
            fn_regular=arial_path,
            fn_bold='C:\\Windows\\Fonts\\arialbd.ttf'
        )

# Set window size for mobile
Window.size = (360, 640)

# Translations Dictionary with comprehensive support
TRANSLATIONS = {
    'ar': {
        'login_title': 'تسجيل الدخول',
        'login_subtitle': 'الرجاء إدخال بياناتك للوصول للمواد',
        'student_code': 'كود الطالب',
        'password': 'كلمة المرور',
        'login_btn': 'الدخول الآن',
        'footer_version': 'الإصدار 1.1.0 - منصة الداحي التعليمية',
        'dashboard_title': 'لوحة التحكم',
        'welcome_msg': 'مرحباً بك يا بطل!',
        'welcome_sub': 'الداحي معاك خطوة بخطوة',
        'courses_header': 'المواد الدراسية',
        'lessons_header': 'دروس المادة',
        'menu_lang_en': 'English Language',
        'menu_lang_ar': 'اللغة العربية',
        'menu_theme_dark': 'الوضع المظلم',
        'menu_theme_light': 'الوضع الفاتح',
        'menu_theme_gold': 'الوضع الذهبي',
        'logout': 'تسجيل خروج',
        'back_btn': 'رجوع',
        'no_courses': 'لا توجد مواد مسجلة',
        'no_lessons': 'لا توجد دروس في هذه المادة',
        'security_alert': 'تحذير أمني!',
        'violation_msg': 'تم رصد مخالفة أمنية! سيتم إغلاق التطبيق.',
        'exit': 'خروج',
        'loading': 'جاري التحميل...',
        'error': 'خطأ',
        'success': 'نجح',
        'connection_error': 'خطأ في الاتصال',
        'retry': 'إعادة محاولة'
    },
    'en': {
        'login_title': 'Student Login',
        'login_subtitle': 'Please enter your credentials',
        'student_code': 'Student Code',
        'password': 'Password',
        'login_btn': 'Login Now',
        'footer_version': 'Version 1.1.0 - El-Dahih Platform',
        'dashboard_title': 'Dashboard',
        'welcome_msg': 'Welcome Hero!',
        'welcome_sub': 'Ready to study today?',
        'courses_header': 'Your Courses',
        'lessons_header': 'Course Lessons',
        'menu_lang_en': 'English Language',
        'menu_lang_ar': 'اللغة العربية',
        'menu_theme_dark': 'Dark Mode',
        'menu_theme_light': 'Light Mode',
        'menu_theme_gold': 'Gold Mode',
        'logout': 'Logout',
        'back_btn': 'Back',
        'no_courses': 'No courses found',
        'no_lessons': 'No lessons in this course',
        'security_alert': 'Security Alert!',
        'violation_msg': 'Security violation detected! App will close.',
        'exit': 'Exit',
        'loading': 'Loading...',
        'error': 'Error',
        'success': 'Success',
        'connection_error': 'Connection Error',
        'retry': 'Retry'
    }
}


def f_ar(text):
    """Reshape and reorder Arabic text for Kivy labels"""
    if not text:
        return ""
    try:
        reshaped_text = reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text


class LoginScreen(Screen):
    """Login screen with authentication"""
    
    def on_enter(self, *args):
        """Perform security checks when entering login screen"""
        try:
            # Perform comprehensive security check
            violations = SecurityShield.perform_security_check()
            
            if violations:
                logger.warning(f"Security violations detected: {violations}")
                for violation in violations:
                    if violation in ["ROOT_DETECTED", "EMULATOR_DETECTED"]:
                        self.show_fatal_error(
                            f_ar("عذراً، لا يمكن تشغيل التطبيق في هذه البيئة لضمان الأمان.")
                        )
                        return
        except Exception as e:
            logger.error(f"Security check error: {e}")

    def do_login(self, code, password):
        """Handle login action"""
        if not code or not password:
            self.show_error(f_ar("يرجى إدخال البيانات كاملة"))
            return
        
        # Show loading snackbar
        Snackbar(text=MDApp.get_running_app().get_text('loading')).open()
        
        auth = AuthManager()
        success, message = auth.login(code, password)
        
        if success:
            # Save session securely
            try:
                SecureStorage.save_secure('auth_token', auth.token)
                SecureStorage.save_secure('user_code', code)
            except Exception as e:
                logger.error(f"Failed to save session: {e}")
            
            MDApp.get_running_app().root.current = 'dashboard'
        else:
            self.ids.user_code.error = True
            self.ids.password.error = True
            self.show_error(message)

    def show_error(self, text):
        """Show error dialog"""
        self.dialog = MDDialog(
            title=MDApp.get_running_app().get_text('error'),
            text=text,
            buttons=[
                MDFlatButton(
                    text=MDApp.get_running_app().get_text('exit'),
                    theme_text_color="Custom",
                    text_color=MDApp.get_running_app().theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def show_fatal_error(self, text):
        """Show fatal error dialog"""
        self.dialog = MDDialog(
            text=text,
            title=MDApp.get_running_app().get_text('security_alert'),
            buttons=[
                MDFlatButton(
                    text=MDApp.get_running_app().get_text('exit'),
                    on_release=lambda x: os._exit(0)
                )
            ],
        )
        self.dialog.auto_dismiss = False
        self.dialog.open()


class DashboardScreen(Screen):
    """Dashboard screen showing courses and lessons"""
    
    def on_enter(self, *args):
        """Load courses when entering dashboard"""
        self.load_courses()
        Clock.schedule_once(self.monitor_security, 10)

    def load_courses(self):
        """Load user's courses from the platform"""
        auth = AuthManager()
        app = MDApp.get_running_app()
        
        try:
            courses, error = auth.get_courses()
            
            if error:
                logger.error(f"Error loading courses: {error}")
                self.show_error(error)
                return
            
            self.ids.courses_list.clear_widgets()
            
            if not courses:
                self.ids.courses_list.add_widget(
                    MDLabel(
                        text=app.get_text('no_courses'),
                        halign="center",
                        theme_text_color="Hint"
                    )
                )
                return
            
            # Add courses as cards
            for course in courses:
                card = MDCard(
                    size_hint_y=None,
                    height="80dp",
                    padding="10dp",
                    radius="12dp",
                    elevation=2,
                    md_bg_color=get_color_from_hex("#F5F9FD") if app.theme_cls.theme_style == "Light" else get_color_from_hex("#2C2C2C")
                )
                card.bind(on_release=lambda x, c=course: self.show_lessons(c['id'], c['name']))
                
                layout = MDBoxLayout(orientation='horizontal', padding="10dp", spacing="10dp")
                icon = MDIcon(
                    icon="book-open-page-variant",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex("#00A8E8"),
                    size_hint_x=None,
                    width="40dp"
                )
                label = MDLabel(
                    text=app.f_ar(course.get('name', 'Unknown')),
                    font_name="Arabic",
                    halign="right" if app.current_lang == 'ar' else "left"
                )
                
                layout.add_widget(icon)
                layout.add_widget(label)
                card.add_widget(layout)
                self.ids.courses_list.add_widget(card)
                
        except Exception as e:
            logger.error(f"Error loading courses: {e}")
            self.show_error(str(e))

    def show_lessons(self, course_id, course_name):
        """Show lessons for a specific course"""
        auth = AuthManager()
        app = MDApp.get_running_app()
        
        try:
            lessons, error = auth.get_lessons(course_id)
            
            if error:
                logger.error(f"Error loading lessons: {error}")
                self.show_error(error)
                return
            
            self.ids.courses_list.clear_widgets()
            self.ids.section_title.text = app.f_ar(course_name)
            
            # Add back button
            back_btn = MDRectangleFlatIconButton(
                text=app.get_text('back_btn'),
                icon="arrow-left" if app.current_lang == 'en' else "arrow-right",
                size_hint_y=None,
                height="48dp"
            )
            back_btn.bind(on_release=lambda x: self.load_courses())
            self.ids.courses_list.add_widget(back_btn)
            
            if not lessons:
                self.ids.courses_list.add_widget(
                    MDLabel(
                        text=app.get_text('no_lessons'),
                        halign="center"
                    )
                )
                return
            
            # Add lessons as list items
            for lesson in lessons:
                item = OneLineIconListItem(
                    text=app.f_ar(lesson.get('title', 'Unknown')),
                    size_hint_y=None,
                    height="48dp"
                )
                icon_name = "file-pdf-box" if lesson.get('content_type') == 'pdf' else "video"
                item.add_widget(IconLeftWidget(icon=icon_name))
                item.bind(on_release=lambda x, l=lesson: self.open_lesson(l['id'], l['title']))
                self.ids.courses_list.add_widget(item)
                
        except Exception as e:
            logger.error(f"Error showing lessons: {e}")
            self.show_error(str(e))

    def open_lesson(self, lesson_id, title):
        """Open a lesson"""
        auth = AuthManager()
        app = MDApp.get_running_app()
        
        try:
            Snackbar(text=app.f_ar(f"جاري تحميل '{title}'...")).open()
            
            content, error = auth.get_lesson_content(lesson_id)
            
            if error:
                logger.error(f"Error loading lesson: {error}")
                self.show_error(error)
                return
            
            Snackbar(text=app.f_ar(f"تم تحميل '{title}' بنجاح")).open()
            
        except Exception as e:
            logger.error(f"Error opening lesson: {e}")
            self.show_error(str(e))

    def monitor_security(self, dt):
        """Monitor security violations periodically"""
        violations = SecurityShield.perform_security_check()
        
        if violations:
            logger.critical(f"Security violations detected: {violations}")
            SecurityShield.handle_violation(f"Multiple violations: {violations}")
        
        Clock.schedule_once(self.monitor_security, 30)

    def show_error(self, text):
        """Show error dialog"""
        dialog = MDDialog(
            title=MDApp.get_running_app().get_text('error'),
            text=text,
            buttons=[
                MDFlatButton(
                    text=MDApp.get_running_app().get_text('exit'),
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()


class ElDahihApp(MDApp):
    """Main application class"""
    
    current_lang = StringProperty('ar')
    current_theme = StringProperty('Light')
    
    def get_text(self, key):
        """Get translated text"""
        text = TRANSLATIONS.get(self.current_lang, {}).get(key, key)
        return f_ar(text) if self.current_lang == 'ar' else text

    def f_ar(self, text):
        """Format Arabic text"""
        return f_ar(text)

    def change_language(self, lang):
        """Change application language"""
        self.current_lang = lang
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        # Reload dashboard if on it
        if self.root.current == 'dashboard':
            self.root.get_screen('dashboard').load_courses()

    def set_theme(self, theme):
        """Set application theme"""
        self.current_theme = theme
        self.theme_cls.theme_style = theme
        
        if hasattr(self, 'menu'):
            self.menu.dismiss()

    def show_settings_menu(self, button):
        """Show settings dropdown menu"""
        menu_items = [
            {
                "text": self.get_text('menu_lang_en'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="en": self.change_language(x)
            },
            {
                "text": self.get_text('menu_lang_ar'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ar": self.change_language(x)
            },
            {
                "text": self.get_text('menu_theme_light'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Light": self.set_theme(x)
            },
            {
                "text": self.get_text('menu_theme_dark'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Dark": self.set_theme(x)
            },
            {
                "text": self.get_text('menu_theme_gold'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Gold": self.set_theme(x)
            }
        ]
        
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    def logout_user(self):
        """Logout user"""
        try:
            auth = AuthManager()
            auth.logout()
            SecureStorage.clear_all()
        except:
            pass
        
        self.root.current = 'login'

    def build(self):
        """Build the application"""
        # Set theme colors
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Enable security features
        try:
            SecurityShield.enable_screenshot_protection()
        except Exception as e:
            logger.error(f"Failed to enable screenshot protection: {e}")
        
        # Verify app integrity
        try:
            AntiTamper.verify_app_signature()
        except Exception as e:
            logger.error(f"Failed to verify app signature: {e}")
        
        # Setup SSL certificates
        try:
            import certifi
            os.environ['SSL_CERT_FILE'] = certifi.where()
        except:
            pass
        
        # Load UI
        Builder.load_file('app_ui.kv')
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        
        return sm


if __name__ == '__main__':
    ElDahihApp().run()
