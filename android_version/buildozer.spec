[app]

# (str) Title of your application
title = MikroLink

# (str) Package name
package.name = mikrolink


# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.1,kivymd==1.1.1,paramiko,cryptography,requests,oscpy,urllib3,certifi,idna,charset-normalizer

# (str) Custom source folders for requirements
# сад_folder = ../libs

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/mikrolink_mobile_icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# Example: services = NAME:SERVICE_FILE
services = MikroLinkService:service.py

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,FOREGROUND_SERVICE,POST_NOTIFICATIONS

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK manual installation path (if empty, it will be automatically installed)
#android.ndk_path =

# (str) Android SDK manual installation path (if empty, it will be automatically installed)
#android.sdk_path =

# (str) ANT manual installation path (if empty, it will be automatically installed)
#android.ant_path =

# (list) Android entry point, default is to use start.py
#android.entrypoint = org.kivy.android.PythonActivity

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so

# (str) Android additionnal Java classes to add to the project.
#android.add_src =

# (bool) If splash screen should be used
android.skip_update = 0

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android 6.0+)
android.allow_backup = True

# (list) List of Java .jar files to add to the libs dir
#android.add_jars = foo.jar,bar.jar,libs/baz.jar

# (str) python-for-android branch to use, if not master
#p4a.branch = master

# (str) format used to package the app, can be apk or aab
android.release_artifact = apk

# (str) The name of the build to use for release
android.release_build = release

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
