[app]
title = BanjaarasCatering
package.name = banjaarascatering
package.domain = org.banjaaras

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Dependencies required for modern UI and saving images
requirements = python3,kivy==2.3.0,kivymd,pillow

# Orientation and Fullscreen
orientation = portrait
fullscreen = 0

# Android specific configurations
# Targeting API 34 (Android 14) which is the current stable maximum for buildozer. 
# Android 16 (API 36) compatibility is handled smoothly by this backward compatibility.
android.api = 34
android.minapi = 21

# Permissions needed to download/save the bill to device storage
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# CPU architecture for modern Android devices (including Vivo Y-series)
android.archs = arm64-v8a, armeabi-v7a

# P4A specific
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
