[app]
title = Guardian Box
package.name = guardianbox
package.domain = org.anthony
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
version = 1.0

# CRITICAL: Use headless OpenCV
requirements = python3,kivy,opencv-python-headless==4.9.0.80,numpy
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a