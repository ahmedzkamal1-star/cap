"""
Language management for El-Dahih application
Supports Arabic and English with RTL/LTR support
"""
import logging
from arabic_reshaper import reshape
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)


class LanguageManager:
    """Manages application languages and translations"""
    
    # Comprehensive translations
    TRANSLATIONS = {
        'ar': {
            # Authentication
            'login_title': 'تسجيل الدخول',
            'login_subtitle': 'الرجاء إدخال بياناتك للوصول للمواد',
            'student_code': 'كود الطالب',
            'password': 'كلمة المرور',
            'login_btn': 'الدخول الآن',
            'remember_me': 'تذكرني',
            'forgot_password': 'هل نسيت كلمة المرور؟',
            
            # Dashboard
            'dashboard_title': 'لوحة التحكم',
            'welcome_msg': 'مرحباً بك يا بطل!',
            'welcome_sub': 'الداحي معاك خطوة بخطوة',
            'courses_header': 'المواد الدراسية',
            'lessons_header': 'دروس المادة',
            'no_courses': 'لا توجد مواد مسجلة',
            'no_lessons': 'لا توجد دروس في هذه المادة',
            
            # Menu
            'menu_lang_en': 'English Language',
            'menu_lang_ar': 'اللغة العربية',
            'menu_theme_dark': 'الوضع المظلم',
            'menu_theme_light': 'الوضع الفاتح',
            'menu_theme_gold': 'الوضع الذهبي',
            'menu_settings': 'الإعدادات',
            'menu_about': 'حول التطبيق',
            'menu_help': 'المساعدة',
            
            # Actions
            'logout': 'تسجيل خروج',
            'back_btn': 'رجوع',
            'cancel': 'إلغاء',
            'ok': 'حسناً',
            'yes': 'نعم',
            'no': 'لا',
            'retry': 'إعادة محاولة',
            'exit': 'خروج',
            
            # Messages
            'footer_version': 'الإصدار 1.1.0 - منصة الداحي التعليمية',
            'loading': 'جاري التحميل...',
            'error': 'خطأ',
            'success': 'نجح',
            'connection_error': 'خطأ في الاتصال',
            'timeout_error': 'انتهت مهلة الاتصال',
            'server_error': 'خطأ في السيرفر',
            'invalid_credentials': 'بيانات الدخول غير صحيحة',
            'account_disabled': 'حسابك معطل أو محظور',
            'session_expired': 'جلستك انتهت، يرجى تسجيل الدخول مجدداً',
            
            # Security
            'security_alert': 'تحذير أمني!',
            'violation_msg': 'تم رصد مخالفة أمنية! سيتم إغلاق التطبيق.',
            'root_detected': 'عذراً، لا يمكن تشغيل التطبيق على أجهزة بصلاحيات روت',
            'emulator_detected': 'عذراً، يمنع استخدام المحاكيات',
            'vpn_detected': 'تم رصد استخدام VPN',
            'debugger_detected': 'تم رصد debugger',
            
            # Validation
            'field_required': 'هذا الحقل مطلوب',
            'invalid_email': 'البريد الإلكتروني غير صحيح',
            'password_too_short': 'كلمة المرور قصيرة جداً',
            'passwords_not_match': 'كلمات المرور غير متطابقة',
        },
        'en': {
            # Authentication
            'login_title': 'Student Login',
            'login_subtitle': 'Please enter your credentials',
            'student_code': 'Student Code',
            'password': 'Password',
            'login_btn': 'Login Now',
            'remember_me': 'Remember Me',
            'forgot_password': 'Forgot Password?',
            
            # Dashboard
            'dashboard_title': 'Dashboard',
            'welcome_msg': 'Welcome Hero!',
            'welcome_sub': 'Ready to study today?',
            'courses_header': 'Your Courses',
            'lessons_header': 'Course Lessons',
            'no_courses': 'No courses found',
            'no_lessons': 'No lessons in this course',
            
            # Menu
            'menu_lang_en': 'English Language',
            'menu_lang_ar': 'اللغة العربية',
            'menu_theme_dark': 'Dark Mode',
            'menu_theme_light': 'Light Mode',
            'menu_theme_gold': 'Gold Mode',
            'menu_settings': 'Settings',
            'menu_about': 'About',
            'menu_help': 'Help',
            
            # Actions
            'logout': 'Logout',
            'back_btn': 'Back',
            'cancel': 'Cancel',
            'ok': 'OK',
            'yes': 'Yes',
            'no': 'No',
            'retry': 'Retry',
            'exit': 'Exit',
            
            # Messages
            'footer_version': 'Version 1.1.0 - El-Dahih Platform',
            'loading': 'Loading...',
            'error': 'Error',
            'success': 'Success',
            'connection_error': 'Connection Error',
            'timeout_error': 'Connection Timeout',
            'server_error': 'Server Error',
            'invalid_credentials': 'Invalid Credentials',
            'account_disabled': 'Account Disabled',
            'session_expired': 'Session Expired',
            
            # Security
            'security_alert': 'Security Alert!',
            'violation_msg': 'Security violation detected! App will close.',
            'root_detected': 'Cannot run on rooted devices',
            'emulator_detected': 'Emulators are not allowed',
            'vpn_detected': 'VPN detected',
            'debugger_detected': 'Debugger detected',
            
            # Validation
            'field_required': 'This field is required',
            'invalid_email': 'Invalid email address',
            'password_too_short': 'Password is too short',
            'passwords_not_match': 'Passwords do not match',
        }
    }
    
    _current_language = 'ar'
    
    @classmethod
    def get_text(cls, key, language=None):
        """Get translated text"""
        if language is None:
            language = cls._current_language
        
        translations = cls.TRANSLATIONS.get(language, {})
        text = translations.get(key, key)
        
        # Format Arabic text
        if language == 'ar':
            return cls.format_arabic(text)
        
        return text
    
    @classmethod
    def set_language(cls, language):
        """Set current language"""
        if language in cls.TRANSLATIONS:
            cls._current_language = language
            logger.info(f"Language changed to: {language}")
            return True
        return False
    
    @classmethod
    def get_current_language(cls):
        """Get current language"""
        return cls._current_language
    
    @classmethod
    def get_available_languages(cls):
        """Get list of available languages"""
        return list(cls.TRANSLATIONS.keys())
    
    @classmethod
    def is_rtl(cls, language=None):
        """Check if language is RTL (Right-to-Left)"""
        if language is None:
            language = cls._current_language
        return language == 'ar'
    
    @classmethod
    def format_arabic(cls, text):
        """Format Arabic text for proper display"""
        if not text:
            return ""
        try:
            reshaped_text = reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logger.error(f"Error formatting Arabic text: {e}")
            return text
    
    @classmethod
    def get_text_direction(cls, language=None):
        """Get text direction for language"""
        if language is None:
            language = cls._current_language
        return 'rtl' if cls.is_rtl(language) else 'ltr'
    
    @classmethod
    def get_halign(cls, language=None):
        """Get horizontal alignment for language"""
        if language is None:
            language = cls._current_language
        return 'right' if cls.is_rtl(language) else 'left'
    
    @classmethod
    def add_translation(cls, language, key, value):
        """Add or update translation"""
        if language not in cls.TRANSLATIONS:
            cls.TRANSLATIONS[language] = {}
        
        cls.TRANSLATIONS[language][key] = value
        logger.info(f"Translation added: {language}/{key}")
    
    @classmethod
    def add_translations(cls, language, translations_dict):
        """Add multiple translations"""
        if language not in cls.TRANSLATIONS:
            cls.TRANSLATIONS[language] = {}
        
        cls.TRANSLATIONS[language].update(translations_dict)
        logger.info(f"Multiple translations added for: {language}")
    
    @classmethod
    def get_all_translations(cls, language=None):
        """Get all translations for a language"""
        if language is None:
            language = cls._current_language
        
        return cls.TRANSLATIONS.get(language, {})
    
    @classmethod
    def export_translations(cls, language=None):
        """Export translations as dictionary"""
        if language is None:
            language = cls._current_language
        
        return cls.TRANSLATIONS.get(language, {}).copy()
