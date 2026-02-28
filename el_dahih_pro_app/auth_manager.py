import requests
import json
import os
import uuid
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL - Set to your PythonAnywhere URL
BASE_URL = "https://mr7riko.pythonanywhere.com"

class AuthManager:
    """Singleton class for managing authentication and API communication"""
    _instance = None
    _encryption_key = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance.token = None
            cls._instance.user_data = {}
            cls._instance.device_id = cls._generate_device_id()
            cls._instance.session = requests.Session()
            cls._instance.session.headers.update({
                'User-Agent': 'ElDahih-Mobile/1.1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
        return cls._instance

    @staticmethod
    def _generate_device_id():
        """Generate a unique device ID"""
        try:
            from kivy.utils import platform as kivy_platform
            if kivy_platform == 'android':
                try:
                    from jnius import autoclass
                    Build = autoclass('android.os.Build')
                    device_id = f"{Build.DEVICE}_{Build.SERIAL}_{Build.MODEL}"
                    return device_id
                except:
                    pass
        except:
            pass
        
        # Fallback: generate UUID
        return str(uuid.uuid4())

    @staticmethod
    def base_url():
        return BASE_URL

    def login(self, code, password):
        """Authenticate user with code and password"""
        try:
            payload = {
                "code": code,
                "password": password,
                "device_id": self.device_id
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/login",
                json=payload,
                timeout=15,
                verify=True
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_data = data
                self.token = data.get('token')
                logger.info("Login successful")
                return True, "تم تسجيل الدخول بنجاح"
            elif response.status_code == 401:
                return False, "بيانات الدخول غير صحيحة"
            elif response.status_code == 403:
                return False, "حسابك معطل أو محظور"
            elif response.status_code == 500:
                return False, "خطأ في السيرفر، يرجى المحاولة لاحقاً"
            else:
                try:
                    error_msg = response.json().get('error', f'خطأ: {response.status_code}')
                except:
                    error_msg = f"خطأ في الاتصال: {response.status_code}"
                return False, error_msg
                
        except requests.exceptions.Timeout:
            return False, "انتهت مهلة الاتصال، تحقق من اتصالك بالإنترنت"
        except requests.exceptions.ConnectionError:
            return False, "فشل الاتصال بالخادم، تحقق من الإنترنت"
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"خطأ: {str(e)}"

    def logout(self):
        """Logout user and clear session"""
        try:
            if self.token:
                headers = self.get_headers()
                self.session.post(
                    f"{BASE_URL}/api/logout",
                    headers=headers,
                    timeout=10
                )
        except:
            pass
        finally:
            self.token = None
            self.user_data = {}
            logger.info("Logout successful")

    def get_courses(self):
        """Fetch user's courses from the platform"""
        if not self.token:
            return None, "غير مصرح"
            
        try:
            headers = self.get_headers()
            response = self.session.get(
                f"{BASE_URL}/api/courses",
                headers=headers,
                timeout=15,
                verify=True
            )
            
            if response.status_code == 200:
                return response.json(), None
            elif response.status_code == 401:
                self.token = None
                return None, "جلستك انتهت، يرجى تسجيل الدخول مجدداً"
            else:
                return None, f"خطأ: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return None, "انتهت مهلة الاتصال"
        except Exception as e:
            logger.error(f"Get courses error: {str(e)}")
            return None, str(e)

    def get_lessons(self, course_id):
        """Fetch lessons for a specific course"""
        if not self.token:
            return None, "غير مصرح"
            
        try:
            headers = self.get_headers()
            response = self.session.get(
                f"{BASE_URL}/api/lessons/{course_id}",
                headers=headers,
                timeout=15,
                verify=True
            )
            
            if response.status_code == 200:
                return response.json(), None
            elif response.status_code == 401:
                self.token = None
                return None, "جلستك انتهت"
            else:
                return None, f"خطأ: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Get lessons error: {str(e)}")
            return None, str(e)

    def get_lesson_content(self, lesson_id):
        """Fetch secure content for a lesson"""
        if not self.token:
            return None, "غير مصرح"
            
        try:
            headers = self.get_headers()
            response = self.session.get(
                f"{BASE_URL}/api/secure_content/lesson/{lesson_id}",
                headers=headers,
                timeout=60,
                stream=True,
                verify=True
            )
            
            if response.status_code == 200:
                return response, None
            elif response.status_code == 401:
                self.token = None
                return None, "جلستك انتهت"
            else:
                return None, f"خطأ: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Get content error: {str(e)}")
            return None, str(e)

    def report_violation(self, reason, details):
        """Report a security violation to the server"""
        if not self.token:
            return False
            
        try:
            payload = {
                "reason": reason,
                "details": details,
                "device_id": self.device_id
            }
            headers = self.get_headers()
            response = self.session.post(
                f"{BASE_URL}/api/report_violation",
                json=payload,
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Report violation error: {str(e)}")
            return False

    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Device-ID": self.device_id
        } if self.token else {}

    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.token is not None

    def get_user_info(self):
        """Get current user information"""
        return self.user_data if self.is_authenticated() else None
