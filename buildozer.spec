[app]
title = ID Llamadas Colombia
package.name = calleridcolombia
package.domain = org.callerid.colombia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.1.0,kivymd==1.1.1,requests,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_PHONE_STATE, PROCESS_OUTGOING_CALLS
android.api = 30
android.minapi = 21
android.ndk = 28c
android.sdk = 30
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
