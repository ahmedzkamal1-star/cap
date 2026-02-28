import os
import platform
from kivy.utils import platform as kivy_platform

def is_android():
    return kivy_platform == 'android'

class SecurityShield:
    @staticmethod
    def enable_screenshot_protection():
        """Enables FLAG_SECURE on Android to prevent screenshots and screen recording."""
        if is_android():
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = PythonActivity.mActivity
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                
                def run_on_main_thread():
                    window = currentActivity.getWindow()
                    window.addFlags(WindowManager.FLAG_SECURE)
                
                # In Kivy, some Android UI changes must happen on the main thread
                from android.runnable import run_on_ui_thread
                run_on_ui_thread(run_on_main_thread)()
                print("Screenshot protection ENABLED")
                return True
            except Exception as e:
                print(f"Failed to enable screenshot protection: {e}")
                return False
        else:
            print("Screenshot protection skipped (Not Android)")
            return True

    @staticmethod
    def check_root():
        """Checks for common root indicators (su binary, busybox, etc)."""
        if is_android():
            paths = [
                '/system/app/Superuser.apk',
                '/sbin/su',
                '/system/bin/su',
                '/system/xbin/su',
                '/data/local/xbin/su',
                '/data/local/bin/su',
                '/system/sd/xbin/su',
                '/working/bin/su',
                '/system/bin/failsafe/su',
                '/data/local/su'
            ]
            for path in paths:
                if os.path.exists(path):
                    return True
            return False
        return False

    @staticmethod
    def is_emulator():
        """Detects if the app is running on an emulator."""
        if is_android():
            try:
                from jnius import autoclass
                Build = autoclass('android.os.Build')
                model = Build.MODEL.lower()
                hardware = Build.HARDWARE.lower()
                fingerprint = Build.FINGERPRINT.lower()
                
                is_emu = (
                    "google_sdk" in model or 
                    "emulator" in model or 
                    "android sdk built for x86" in model or
                    "goldfish" in hardware or
                    "ranchu" in hardware or
                    "vbox" in hardware or
                    fingerprint.startswith("generic")
                )
                return is_emu
            except:
                return False
        return False

    @staticmethod
    def check_vpn():
        """Detects if a VPN or Proxy is active."""
        if is_android():
            try:
                from jnius import autoclass
                Context = autoclass('org.kivy.android.PythonActivity').mActivity
                ConnectivityManager = autoclass('android.net.ConnectivityManager')
                cm = Context.getSystemService(Context.CONNECTIVITY_SERVICE)
                networks = cm.getAllNetworks()
                for network in networks:
                    caps = cm.getNetworkCapabilities(network)
                    # TRANSPORT_VPN = 4
                    if caps.hasTransport(4):
                        return True
            except:
                pass
        return False
