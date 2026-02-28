from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from auth_manager import AuthManager
from security_logic import SecurityShield
from kivy.core.text import LabelBase
import arabic_reshaper
from bidi.algorithm import get_display
import os

import platform

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
        shield = SecurityShield()
        if shield.check_root():
            self.show_fatal_error(f_ar("عذراً، لا يمكن تشغيل التطبيق على أجهزة تحتوي على صلاحيات الروت لضمان الأمان."))
        elif shield.is_emulator():
            self.show_fatal_error(f_ar("عذراً، يمنع استخدام المحاكيات. يرجى استخدام هاتف حقيقي."))

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
        # Activate Screenshot & Screen Recording Protection
        SecurityShield.enable_screenshot_protection()
        print(f"DEBUG: Connecting to {AuthManager().base_url()}")

        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Light"
        # In KivyMD 1.2.0 primary_color is derived from primary_palette and is read-only
        
        # Load KV string or file
        Builder.load_file('app_ui.kv')
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    SecurePlatformApp().run()
