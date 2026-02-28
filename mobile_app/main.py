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
import os

# Standard phone resolution (approximate for desktop testing)
Window.size = (360, 640)

class LoginScreen(Screen):
    def on_enter(self, *args):
        # Initial device checks before allowing login
        shield = SecurityShield()
        if shield.check_root():
            self.show_fatal_error("عذراً، لا يمكن تشغيل التطبيق على أجهزة تحتوي على صلاحيات الروت لضمان الأمان.")
        elif shield.is_emulator():
            self.show_fatal_error("عذراً، يمنع استخدام المحاكيات. يرجى استخدام هاتف حقيقي.")

    def do_login(self, code, password):
        if not code or not password:
            self.show_error("يرجى إدخال البيانات كاملة")
            return
            
        auth = AuthManager()
        success, message = auth.login(code, password)
        
        if success:
            MDApp.get_running_app().root.current = 'dashboard'
            MDApp.get_running_app().root.get_screen('dashboard').on_enter()
        else:
            self.show_error(message)

    def show_error(self, text):
        self.dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
        
    def show_fatal_error(self, text):
        self.dialog = MDDialog(
            text=text,
            title="تحذير أمني!",
            buttons=[MDFlatButton(text="خروج", on_release=lambda x: os._exit(0))],
        )
        self.dialog.auto_dismiss = False
        self.dialog.open()

class DashboardScreen(Screen):
    def on_enter(self, *args):
        # Refresh courses list from API
        print(f"Logged in as: {AuthManager().user_data.get('full_name')}")
        
        # Continuous Security Monitoring
        Clock.schedule_once(self.monitor_security, 10)

    def monitor_security(self, dt):
        shield = SecurityShield()
        violation_reason = None
        
        if shield.check_vpn():
            violation_reason = "VPN Detected"
        elif shield.check_root():
            violation_reason = "Root Access Detected"

        if violation_reason:
            AuthManager().report_violation(violation_reason, "Real-time monitor caught unauthorized state")
            self.show_violation_alert(violation_reason)
        else:
            # Check again in 30 seconds
            Clock.schedule_once(self.monitor_security, 30)

    def show_violation_alert(self, reason):
        dialog = MDDialog(
            title="تم رصد مخالفة أمنية!",
            text=f"تم رصد {reason}. سيتم إغلاق التطبيق وتجميد حسابك.",
            buttons=[MDFlatButton(text="إغلاق", on_release=lambda x: os._exit(0))],
        )
        dialog.auto_dismiss = False
        dialog.open()

class SecurePlatformApp(MDApp):
    def build(self):
        # Activate Screenshot & Screen Recording Protection
        SecurityShield.enable_screenshot_protection()

        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_color = get_color_from_hex("#00b4d8")
        
        # Load KV string or file
        Builder.load_file('app_ui.kv')
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    SecurePlatformApp().run()
