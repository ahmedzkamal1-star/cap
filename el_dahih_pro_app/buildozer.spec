[app]

# (str) Title of your application
title = El-Dahih

# (str) Package name
package.name = eldahih

# (str) Package domain (needed for android/ios packaging)
package.domain = com.eldahih.platform

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) Application version
version = 1.1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,cryptography,pyjnius,android,arabic-reshaper,python-bidi,openssl,certifi,pillow

# (str) Custom source folders for requirements
# packagelist.source_dirs = 

# (list) Garden requirements
# garden_requirements = 

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 20

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use FLAG_SECURE for screenshot prevention (optional, we do it in code anyway)
# android.meta_data = android.window.WindowManager.LayoutParams.FLAG_SECURE=1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) enables Android auto backup feature, false by default
android.allow_backup = False

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Logcat filter to use
android.logcat_filters = *:S python:D

# (str) Path to a custom whitelist file
# android.whitelist = 

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aab)
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
