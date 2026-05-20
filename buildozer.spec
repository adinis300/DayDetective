[app]
title = Day Detective
package.name = daydetective
package.domain = com.daydetective

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json

version = 1.0
requirements = python3,kivy==2.2.1,pillow

orientation = portrait
fullscreen = 0

android.minapi = 21
android.ndk = 28c
android.sdk = 34
android.accept_sdk_license = True
android.archs = arm64-v8a

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
presplash.color = #080910

[buildozer]
log_level = 2
warn_on_root = 1
