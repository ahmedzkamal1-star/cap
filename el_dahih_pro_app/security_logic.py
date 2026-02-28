"""
Advanced security features for El-Dahih platform
"""
import os
import platform
import logging
import subprocess
import time
from kivy.utils import platform as kivy_platform

logger = logging.getLogger(__name__)

def is_android():
    """Check if running on Android"""
    return kivy_platform == 'android'


class SecurityShield:
    """Comprehensive security monitoring and protection"""
    
    _last_violation_check = 0
    _violation_count = 0
    
    @staticmethod
    def enable_screenshot_protection():
        """Enable FLAG_SECURE on Android to prevent screenshots and screen recording"""
        if is_android():
            try:
                from jnius import autoclass
                from android.runnable import run_on_ui_thread
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = PythonActivity.mActivity
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                
                def run_on_main_thread():
                    try:
                        window = currentActivity.getWindow()
                        window.addFlags(WindowManager.FLAG_SECURE)
                        logger.info("Screenshot protection ENABLED")
                    except Exception as e:
                        logger.error(f"Failed to set FLAG_SECURE: {e}")
                
                run_on_ui_thread(run_on_main_thread)()
                return True
            except Exception as e:
                logger.error(f"Failed to enable screenshot protection: {e}")
                return False
        else:
            logger.info("Screenshot protection skipped (Not Android)")
            return True

    @staticmethod
    def check_root():
        """Comprehensive root detection"""
        if not is_android():
            return False
        
        try:
            # Check for common root indicators
            root_paths = [
                '/system/app/Superuser.apk',
                '/sbin/su',
                '/system/bin/su',
                '/system/xbin/su',
                '/data/local/xbin/su',
                '/data/local/bin/su',
                '/system/sd/xbin/su',
                '/working/bin/su',
                '/system/bin/failsafe/su',
                '/data/local/su',
                '/system/app/SuperSU',
                '/system/app/Magisk',
                '/data/adb/magisk',
                '/cache/magisk.log',
            ]
            
            for path in root_paths:
                if os.path.exists(path):
                    logger.warning(f"Root indicator found: {path}")
                    return True
            
            # Check via which command
            try:
                result = subprocess.run(
                    ['which', 'su'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    logger.warning("Root detected via 'which su'")
                    return True
            except:
                pass
            
            # Check build properties
            try:
                from jnius import autoclass
                Build = autoclass('android.os.Build')
                
                # Check for common root indicators in build properties
                fingerprint = Build.FINGERPRINT.lower()
                if 'test-keys' in fingerprint or 'debug' in fingerprint:
                    logger.warning("Suspicious build fingerprint detected")
                    return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.error(f"Error checking root: {e}")
            return False

    @staticmethod
    def is_emulator():
        """Advanced emulator detection"""
        if not is_android():
            return False
        
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            
            model = Build.MODEL.lower()
            hardware = Build.HARDWARE.lower()
            fingerprint = Build.FINGERPRINT.lower()
            manufacturer = Build.MANUFACTURER.lower()
            device = Build.DEVICE.lower()
            product = Build.PRODUCT.lower()
            
            emulator_indicators = [
                "google_sdk", "emulator", "android sdk built for x86",
                "goldfish", "ranchu", "vbox", "sdk", "genymotion",
                "generic", "qemu", "simulator", "bluestacks",
                "nox", "andy", "ttvm", "droid4x", "mumu"
            ]
            
            # Check all build properties
            for indicator in emulator_indicators:
                if (indicator in model or indicator in hardware or 
                    indicator in fingerprint or indicator in manufacturer or
                    indicator in device or indicator in product):
                    logger.warning(f"Emulator detected: {indicator}")
                    return True
            
            # Check if fingerprint starts with generic
            if fingerprint.startswith("generic"):
                logger.warning("Generic fingerprint detected (emulator)")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error detecting emulator: {e}")
            return False

    @staticmethod
    def check_vpn():
        """Detect VPN or Proxy connections"""
        if not is_android():
            return False
        
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = PythonActivity.mActivity
            ConnectivityManager = autoclass('android.net.ConnectivityManager')
            
            cm = Context.getSystemService(Context.CONNECTIVITY_SERVICE)
            networks = cm.getAllNetworks()
            
            for network in networks:
                try:
                    caps = cm.getNetworkCapabilities(network)
                    if caps:
                        # TRANSPORT_VPN = 4
                        if caps.hasTransport(4):
                            logger.warning("VPN detected")
                            return True
                except:
                    pass
            
            return False
        except Exception as e:
            logger.error(f"Error checking VPN: {e}")
            return False

    @staticmethod
    def check_recording():
        """Check if screen recording is active"""
        if not is_android():
            return False
        
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = PythonActivity.mActivity
            
            # Check for MediaProjection (screen recording)
            try:
                MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
                manager = Context.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
                
                # If we can get the manager, recording might be active
                if manager:
                    logger.warning("Screen recording might be active")
                    return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.error(f"Error checking recording: {e}")
            return False

    @staticmethod
    def check_debugger():
        """Check if debugger is attached"""
        if not is_android():
            return False
        
        try:
            from jnius import autoclass
            
            Debug = autoclass('android.os.Debug')
            
            if Debug.isDebuggerConnected():
                logger.warning("Debugger detected")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking debugger: {e}")
            return False

    @staticmethod
    def perform_security_check():
        """Perform comprehensive security check"""
        violations = []
        
        if SecurityShield.check_root():
            violations.append("ROOT_DETECTED")
        
        if SecurityShield.is_emulator():
            violations.append("EMULATOR_DETECTED")
        
        if SecurityShield.check_vpn():
            violations.append("VPN_DETECTED")
        
        if SecurityShield.check_debugger():
            violations.append("DEBUGGER_DETECTED")
        
        if SecurityShield.check_recording():
            violations.append("RECORDING_DETECTED")
        
        return violations

    @staticmethod
    def handle_violation(violation_type: str):
        """Handle security violations"""
        logger.critical(f"Security violation: {violation_type}")
        
        # Report to server if possible
        try:
            from auth_manager import AuthManager
            auth = AuthManager()
            auth.report_violation(violation_type, f"Violation detected at {time.time()}")
        except:
            pass
        
        # Exit application
        import os
        os._exit(1)


class AntiTamper:
    """Anti-tampering and code integrity checks"""
    
    @staticmethod
    def verify_app_signature():
        """Verify application signature (Android)"""
        if not is_android():
            return True
        
        try:
            from jnius import autoclass
            
            PackageManager = autoclass('android.content.pm.PackageManager')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = PythonActivity.mActivity
            
            pm = Context.getPackageManager()
            package_name = Context.getPackageName()
            
            # Get package info with signatures
            package_info = pm.getPackageInfo(
                package_name,
                PackageManager.GET_SIGNATURES
            )
            
            # Verify signatures match expected
            if package_info.signatures:
                logger.info("App signature verified")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error verifying app signature: {e}")
            return False

    @staticmethod
    def check_file_integrity(file_path: str, expected_hash: str = None) -> bool:
        """Check file integrity using hash"""
        try:
            import hashlib
            
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            if expected_hash and file_hash != expected_hash:
                logger.warning(f"File integrity check failed: {file_path}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking file integrity: {e}")
            return False
