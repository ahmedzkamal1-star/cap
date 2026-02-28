from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from auth_manager import AuthManager

# Standard phone resolution (approximate for desktop testing)
Window.size = (360, 640)

class LoginScreen(Screen):
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

class DashboardScreen(Screen):
    def on_enter(self, *args):
        # Refresh courses list from API (Phase 2)
        print(f"Logged in as: {AuthManager().user_data.get('full_name')}")

class SecurePlatformApp(MDApp):
    def build(self):
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

if __name__ == '__main__':
    SecurePlatformApp().run()
