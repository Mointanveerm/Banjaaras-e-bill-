[app]

# Title of your application
title = Banjaaras Catering

# Package name
package.name = banjaaras

# Package domain (needed for android packaging)
package.domain = org.banjaaras

# Source files to include (let it point to the root directory)
source.dir = .

# Source files to include (let it find python code and images/kv files)
source.include_exts = py,png,jpg,kv,atlas

# Application versioning
version = 0.1

# List of prerequisites (unpinned to prevent download gateway timeouts)
requirements = python3,kivy,kivymd,pillow

# Supported orientations
orientation = portrait

# List the Android permissions your app needs
android.permissions = INTERNET

# Automatically accept Android SDK licenses to prevent build freezes
android.accept_sdk_license = True

# Android API level to target
android.api = 33

# Minimum API level
android.minapi = 21

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Warn on root building (needed for GitHub Actions)
warn_on_root = 1
