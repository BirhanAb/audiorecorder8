[app]

# (str) Title of your application
title = Audio Recorder

# (str) Package name
package.name = recorder

# (str) Package domain
package.domain = org.ownuse

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, venv, .buildozer, __pycache__

# (str) Application versioning
version = 0.4

# (list) Application requirements
# ADDED 'android' requirement to enable access to public storage paths
requirements = python3,kivy,kivymd,pillow,plyer,sounddevice,numpy,cffi,libffi,android

# (str) Presplash and Icon
presplash.filename = %(source.dir)s/soundrecorder.png
icon.filename = %(source.dir)s/Recorder.png

# (list) Supported orientations
orientation = landscape

#
# Android specific
#

# (list) Permissions 
# Optimized for Android 14. Note: READ_MEDIA_AUDIO is the modern replacement for READ_EXTERNAL_STORAGE.
#android.permissions = RECORD_AUDIO, READ_MEDIA_AUDIO, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.permissions = RECORD_AUDIO, READ_MEDIA_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API - 34 is Android 14
android.api = 34

# (int) Minimum API - 23 is Android 6.0
android.minapi = 23

# (bool) Use AndroidX libraries (Required for modern APIs)
android.useandroidx = 1

# (bool) Enable SAF (Storage Access Framework)
# SET TO 0 to allow the app to write directly to the path provided in main.py
android.experimental_use_saf = 0

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

#
# Python for android (p4a) specific
#

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

#
# Buildozer specific settings
#
[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build output (relative to spec file)

bin_dir = ./bin
