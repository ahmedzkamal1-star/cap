"""
Application configuration and constants
"""
import os
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# API Configuration
API_BASE_URL = "https://mr7riko.pythonanywhere.com"
API_TIMEOUT = 15
API_RETRIES = 3

# Application Configuration
APP_NAME = "El-Dahih"
APP_VERSION = "1.1.0"
APP_PACKAGE = "com.eldahih.platform"
APP_AUTHOR = "El-Dahih Team"

# Security Configuration
SECURITY_ENABLED = True
SCREENSHOT_PROTECTION = True
ROOT_CHECK_ENABLED = True
EMULATOR_CHECK_ENABLED = True
VPN_CHECK_ENABLED = True
DEBUGGER_CHECK_ENABLED = True
ANTI_TAMPER_ENABLED = True

# Encryption Configuration
ENCRYPTION_ENABLED = True
ENCRYPTION_ALGORITHM = "AES-256"
SECURE_STORAGE_ENABLED = True

# UI Configuration
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 640
THEME_DEFAULT = "Light"
LANGUAGE_DEFAULT = "ar"
FONT_DEFAULT = "Arial"

# Storage Configuration
STORAGE_DIR = os.path.expanduser("~/.eldahih")
CACHE_DIR = os.path.join(STORAGE_DIR, "cache")
SECURE_STORAGE_DIR = os.path.join(STORAGE_DIR, ".secure")
LOG_DIR = os.path.join(STORAGE_DIR, "logs")

# Feature Flags
FEATURE_OFFLINE_MODE = True
FEATURE_DARK_MODE = True
FEATURE_GOLD_MODE = True
FEATURE_LANGUAGE_SWITCH = True
FEATURE_ANALYTICS = False
FEATURE_CRASH_REPORTING = True

# Performance Configuration
CACHE_ENABLED = True
CACHE_EXPIRY = 3600  # 1 hour
CONNECTION_POOL_SIZE = 10
REQUEST_TIMEOUT = 30

# Permissions
REQUIRED_PERMISSIONS = [
    "INTERNET",
    "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE",
]

OPTIONAL_PERMISSIONS = [
    "CAMERA",
    "RECORD_AUDIO",
    "ACCESS_NETWORK_STATE",
]

# API Endpoints
API_ENDPOINTS = {
    'login': '/api/login',
    'logout': '/api/logout',
    'courses': '/api/courses',
    'lessons': '/api/lessons/{course_id}',
    'lesson_content': '/api/secure_content/lesson/{lesson_id}',
    'report_violation': '/api/report_violation',
    'user_profile': '/api/user/profile',
    'update_profile': '/api/user/profile/update',
}

# Error Messages
ERROR_MESSAGES = {
    'connection_error': 'خطأ في الاتصال بالخادم',
    'timeout_error': 'انتهت مهلة الاتصال',
    'invalid_credentials': 'بيانات الدخول غير صحيحة',
    'account_disabled': 'حسابك معطل أو محظور',
    'server_error': 'خطأ في السيرفر',
    'unauthorized': 'غير مصرح',
    'forbidden': 'ممنوع الوصول',
    'not_found': 'لم يتم العثور على المورد',
}

# Success Messages
SUCCESS_MESSAGES = {
    'login_success': 'تم تسجيل الدخول بنجاح',
    'logout_success': 'تم تسجيل الخروج بنجاح',
    'profile_updated': 'تم تحديث الملف الشخصي',
    'data_saved': 'تم حفظ البيانات',
}

# Validation Rules
VALIDATION_RULES = {
    'min_password_length': 6,
    'max_password_length': 50,
    'min_username_length': 3,
    'max_username_length': 50,
    'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}

# Theme Colors
COLORS = {
    'primary_blue': '#00A8E8',
    'primary_dark_blue': '#0D47A1',
    'accent_gold': '#FFD700',
    'accent_amber': '#FFC700',
    'success_green': '#4CAF50',
    'error_red': '#F44336',
    'warning_orange': '#FF9800',
    'info_cyan': '#00BCD4',
    'light_bg': '#FFFFFF',
    'dark_bg': '#121212',
    'gold_bg': '#FFFEF0',
}

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(LOG_DIR, 'eldahih.log')

# Development/Production
DEBUG_MODE = False
DEVELOPMENT_MODE = False

def get_api_url(endpoint_key, **kwargs):
    """Get full API URL for an endpoint"""
    if endpoint_key not in API_ENDPOINTS:
        raise ValueError(f"Unknown endpoint: {endpoint_key}")
    
    endpoint = API_ENDPOINTS[endpoint_key]
    
    # Replace placeholders
    for key, value in kwargs.items():
        endpoint = endpoint.replace(f"{{{key}}}", str(value))
    
    return f"{API_BASE_URL}{endpoint}"

def ensure_directories():
    """Ensure all required directories exist"""
    for directory in [STORAGE_DIR, CACHE_DIR, SECURE_STORAGE_DIR, LOG_DIR]:
        os.makedirs(directory, exist_ok=True)
        os.chmod(directory, 0o700)

# Initialize directories on import
try:
    ensure_directories()
except Exception as e:
    logging.error(f"Failed to create directories: {e}")
