#!/usr/bin/env python3
"""
Download and deploy frida-server to Android device
"""
import urllib.request
import os
import subprocess
import time

# Download frida-server for Android ARM64
FRIDA_VERSION = "17.9.8"
URL = f"https://github.com/frida/frida/releases/download/{FRIDA_VERSION}/frida-server-{FRIDA_VERSION}-android-arm64.xz"
OUTPUT = r"C:\Users\HP\frida-server.xz"
EXTRACTED = r"C:\Users\HP\frida-server"
DEVICE_PATH = "/data/local/tmp/frida-server"

print(f"[*] Downloading frida-server {FRIDA_VERSION}...")
try:
    urllib.request.urlretrieve(URL, OUTPUT)
    print(f"[✓] Downloaded to {OUTPUT}")
except Exception as e:
    print(f"[✗] Download failed: {e}")
    exit(1)

# Extract XZ
print(f"[*] Extracting XZ...")
try:
    import lzma
    with lzma.open(OUTPUT, 'rb') as f:
        with open(EXTRACTED, 'wb') as out:
            out.write(f.read())
    print(f"[✓] Extracted to {EXTRACTED}")
except Exception as e:
    print(f"[✗] Extraction failed: {e}")
    exit(1)

# Push to device
print(f"[*] Pushing to device...")
try:
    subprocess.check_call([r"C:\Users\HP\platform-tools\adb.exe", "push", EXTRACTED, DEVICE_PATH])
    print(f"[✓] Pushed to {DEVICE_PATH}")
except Exception as e:
    print(f"[✗] Push failed: {e}")
    exit(1)

# Make executable
print(f"[*] Making executable...")
try:
    subprocess.check_call([r"C:\Users\HP\platform-tools\adb.exe", "shell", "chmod", "+x", DEVICE_PATH])
    print(f"[✓] Made executable")
except Exception as e:
    print(f"[✗] chmod failed: {e}")
    exit(1)

# Start frida-server
print(f"[*] Starting frida-server...")
try:
    subprocess.Popen([r"C:\Users\HP\platform-tools\adb.exe", "shell", DEVICE_PATH])
    print(f"[✓] frida-server started on device")
    time.sleep(2)
except Exception as e:
    print(f"[✗] Start failed: {e}")
    exit(1)

print(f"\n[✓] frida-server is ready! You can now attach to processes.")
