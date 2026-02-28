from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from auth_manager import AuthManager
from security_logic import SecurityShield
from kivy.core.text import LabelBase
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from kivy.properties import StringProperty
import os
import platform
import logging
import security_utils
import requests
import json
import base64

# Register Arabic font globally
if platform.system() == 'Windows':
    arial_path = 'C:\\Windows\\Fonts\\arial.ttf'
    if os.path.exists(arial_path):
        LabelBase.register(name='Roboto', 
                           fn_regular=arial_path,
                           fn_bold='C:\\Windows\\Fonts\\arialbd.ttf',
                           fn_italic='C:\\Windows\\Fonts\\ariali.ttf',
                           fn_bolditalic='C:\\Windows\\Fonts\\arialbi.ttf')
        LabelBase.register(name='Arabic', fn_regular=arial_path)
    else:
        # Fallback if arial not found
        print("Warning: Arial font not found on this Windows system.")
else:
    # On Android, Kivy uses the system fonts. 
    # But if we need a specific Arabic font, we can bundle it or use system one
    # For now, we rely on the reshapher + bidi to work on system default
    pass

class SecurePlatformApp(MDApp):
    current_lang = StringProperty('ar')
    
    def get_text(self, key):
        """Helper to get translated text based on current language."""
        text = TRANSLATIONS[self.current_lang][key]
        if self.current_lang == 'ar':
            return f_ar(text)
        return text

    def switch_language(self, lang):
        self.current_lang = lang
        logging.info(f"Language switched to {lang}")

    def show_settings_menu(self, button):
        menu_items = [
            {
                "text": self.get_text('menu_lang_en'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="en": self.change_language(x),
            },
            {
                "text": self.get_text('menu_lang_ar'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ar": self.change_language(x),
            },
            {
                "text": self.get_text('menu_theme_dark'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Dark": self.set_theme(x),
            },
            {
                "text": self.get_text('menu_theme_light'),
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Light": self.set_theme(x)
            }
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def change_language(self, lang):
        self.current_lang = lang
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        logging.info(f"Language changed to: {lang}")

    def set_theme(self, theme):
        self.theme_cls.theme_style = theme
        if hasattr(self, 'menu'):
            self.menu.dismiss()

    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def f_ar(self, text):
        return f_ar(text)

def f_ar(text):
    """Reshapes and reorders Arabic text for Kivy labels on Windows."""
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# Standard phone resolution (approximate for desktop testing)
Window.size = (360, 640)

class LoginScreen(Screen):
    def on_enter(self, *args):
        # Initial device checks before allowing login
        try:
            shield = SecurityShield()
            if shield.check_root():
                self.show_fatal_error(f_ar("عذراً، لا يمكن تشغيل التطبيق على أجهزة تحتوي على صلاحيات الروت لضمان الأمان."))
            elif shield.is_emulator():
                self.show_fatal_error(f_ar("عذراً، يمنع استخدام المحاكيات. يرجى استخدام هاتف حقيقي."))
        except Exception as e:
            print(f"Startup check bypass: {e}")

    def do_login(self, code, password):
        if not code or not password:
            self.show_error(f_ar("يرجى إدخال البيانات كاملة"))
            return
            
        auth = AuthManager()
        success, message = auth.login(code, password)
        
        if success:
            MDApp.get_running_app().root.current = 'dashboard'
            MDApp.get_running_app().root.get_screen('dashboard').on_enter()
        else:
            # Show error in red and set textfield errors
            self.ids.user_code.error = True
            self.ids.password.error = True
            self.show_error(f_ar(message))
            
            from kivymd.uix.snackbar import Snackbar
            Snackbar(
                text=f_ar(message),
                font_name="Arabic",
                bg_color=(1, 0, 0, 1),
                duration=3
            ).open()

    def show_error(self, text):
        self.dialog = MDDialog(
            title=f_ar("خطأ في الدخول"),
            text=text,
            radius=[20, 7, 20, 7],
            buttons=[
                MDFlatButton(
                    text=f_ar("حسناً"),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()
        
    def show_fatal_error(self, text):
        self.dialog = MDDialog(
            text=text,
            title=f_ar("تحذير أمني!"),
            buttons=[MDFlatButton(text=f_ar("خروج"), on_release=lambda x: os._exit(0))],
        )
        self.dialog.auto_dismiss = False
        self.dialog.open()

class DashboardScreen(Screen):
    def on_enter(self, *args):
        # Refresh courses list from API
        print(f"Logged in as: {AuthManager().user_data.get('full_name')}")
        self.load_courses()
        
        # Continuous Security Monitoring
        Clock.schedule_once(self.monitor_security, 10)

    def load_courses(self):
        # In a real app, we'd fetch from /api/courses
        # For now, we simulate the structure
        pass

    def open_lesson(self, lesson_id, content_type='lesson'):
        auth = AuthManager()
        # 1. Fetch encrypted content
        try:
            url = f"{AuthManager.base_url()}/api/secure_content/{content_type}/{lesson_id}"
            headers = auth.get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                encrypted_data = response.content
                # 2. Decrypt in memory
                from secure_viewer import SecureViewer
                decrypted_bytes = SecureViewer.decrypt_in_memory(encrypted_data, auth.token)
                
                if decrypted_bytes:
                    print(f"Success! Content {lesson_id} decrypted in memory ({len(decrypted_bytes)} bytes)")
                    # 3. Handle viewing (Phase 4 final)
                else:
                    self.show_error(f_ar("فشل فك تشفير الملف"))
            else:
                self.show_error(f_ar("فشل جلب الملف من الموقع"))
        except Exception as e:
            self.show_error(f_ar(f"خطأ في الاتصال: {str(e)}"))

    def monitor_security(self, dt):
        shield = SecurityShield()
        violation_reason = None
        
        if shield.check_vpn():
            violation_reason = f_ar("تم اكتشاف اتصال VPN")
        elif shield.check_root():
            violation_reason = f_ar("تم اكتشاف صلاحيات روت")
        elif shield.check_recording():
             violation_reason = f_ar("تم اكتشاف محاولة تسجيل شاشة")

        if violation_reason:
            AuthManager().report_violation(violation_reason, "Real-time monitor caught unauthorized state")
            self.show_violation_alert(violation_reason)
        else:
            # Check again in 30 seconds
            Clock.schedule_once(self.monitor_security, 30)

    def show_violation_alert(self, reason):
        dialog = MDDialog(
            title=f_ar("تم رصد مخالفة أمنية!"),
            text=f_ar(f"تم رصد {reason}. سيتم إغلاق التطبيق وتجميد حسابك."),
            buttons=[MDFlatButton(text=f_ar("إغلاق"), on_release=lambda x: os._exit(0))],
        )
        dialog.auto_dismiss = False
        dialog.open()

class SecurePlatformApp(MDApp):
    def f_ar(self, text):
        return f_ar(text)

    def build(self):
        logging.info("Building App UI...")
        try:
            # Activate Screenshot & Screen Recording Protection
            SecurityShield.enable_screenshot_protection()
        except Exception as e:
            logging.error(f"Screenshot protection failed: {e}")
            
        logging.info(f"Connecting to {AuthManager().base_url()}")
        
        try:
            import certifi
            os.environ['SSL_CERT_FILE'] = certifi.where()
            logging.info("SSL Certs configured via certifi")
        except Exception as e:
            logging.error(f"Certifi config failed: {e}")

        # Branded Palette: Sky Blue (#00B4D8) and Gold (#FFD700)
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.accent_palette = "Amber" # Gold-like
        self.theme_cls.theme_style = "Light"
        
        # Load KV string or file
        try:
            Builder.load_file('app_ui.kv')
            logging.info("KV file loaded successfully")
        except Exception as e:
            logging.error(f"KV Load Failure: {e}")
            return MDLabel(text=f"UI Error: {e}", halign="center")
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"

if __name__ == '__main__':
    SecurePlatformApp().run()
