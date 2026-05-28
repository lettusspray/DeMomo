#!/usr/bin/env python3
"""
Capture MoMo app logs and API patterns from logcat
Works on non-rooted devices
"""
import subprocess
import re
from datetime import datetime

print("[*] Starting MoMo logcat capture...")
print("[*] Make sure MoMo app is running and performing actions (login, view cards, etc.)")
print("[*] Saving logs to: c:/Users/HP/momo/momo_logcat.log")
print("[*] Press Ctrl+C to stop\n")

# Clear existing logs
subprocess.call([r"C:\Users\HP\platform-tools\adb.exe", "logcat", "-c"])

# Capture logcat with specific tags
try:
    with open(r"c:/Users/HP/momo/momo_logcat.log", "w") as f:
        proc = subprocess.Popen(
            [r"C:\Users\HP\platform-tools\adb.exe", "logcat", "-v", "threadtime", 
             "ng.mtn.android.psb.momo:V", "*:S"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        for line in proc.stdout:
            print(line, end='')
            f.write(line)
            f.flush()
            
except KeyboardInterrupt:
    print("\n[*] Logcat capture stopped")
    proc.terminate()
