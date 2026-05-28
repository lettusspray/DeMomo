# Phase 2 Setup Guide - Device-Based Runtime Analysis

**Objective**: Deploy Frida scripts to capture live API traffic from MoMo PSB  
**Duration**: 30-60 minutes setup + 2-3 hours analysis  
**Outcome**: Real API endpoints + authentication flows + Firebase operations

---

## ✅ Prerequisites Checklist

Before starting, verify you have:

```
[ ] Android device or emulator with MoMo PSB installed
[ ] USB cable (for physical device)
[ ] USB Debugging enabled on device
[ ] ADB installed: C:\Users\HP\platform-tools\adb.exe (✓ verified)
[ ] Frida installed: C:\Users\HP\.venv\Scripts\frida.exe (to verify)
[ ] Frida scripts ready: C:\Users\HP\momo\frida_*.js (✓ ready)
[ ] Python 3 installed (for optional logcat parsing)
```

---

## 🔧 STEP 1: Connect Device

### For Physical Device

```powershell
# 1. On your Android phone:
#    Settings > System > About Phone
#    Tap "Build Number" 7 times
#    Go to Settings > System > Developer Options
#    Enable "USB Debugging"
#
# 2. Connect USB cable to computer
#
# 3. On phone: Tap "Allow USB Debugging" when prompted
#
# 4. Verify connection:
C:\Users\HP\platform-tools\adb.exe devices

# Expected output:
# emulator-5554          device  (or your device serial)
```

### For Emulator

```powershell
# 1. Open Android Studio
# 2. Virtual Device Manager > Click Play on an emulator
# 3. Wait for emulator to boot
# 4. Verify connection:
C:\Users\HP\platform-tools\adb.exe devices

# Expected output:
# emulator-5554          device
```

---

## 📱 STEP 2: Install MoMo PSB on Device

### Option A: APK Installation (Fastest)

```powershell
# Install the APK we have:
C:\Users\HP\platform-tools\adb.exe install -r "C:\Users\HP\momo\MoMo PSB.apk"

# Wait for installation to complete
# Expected: "Success"
```

### Option B: Play Store (Alternative)

```
1. On device: Open Google Play Store
2. Search for "MoMo"
3. Install "MoMo - Mobile Money" by MTN
4. Wait for installation
```

### Verify Installation

```powershell
C:\Users\HP\platform-tools\adb.exe shell pm list packages | grep momo

# Should show: ng.mtn.android.psb.momo
```

---

## 🔴 STEP 3: Setup Frida

### Check Frida Installation

```powershell
# Verify Frida is installed:
C:\Users\HP\.venv\Scripts\frida.exe --version

# Expected: frida 17.9.1 (or similar)
```

### Start Frida Server on Device

```powershell
# 1. Download Frida server for your device architecture:
#    Architecture detection:
C:\Users\HP\platform-tools\adb.exe shell getprop ro.product.cpu.abi

# Common architectures:
# - arm64-v8a (most modern phones)
# - armeabi-v7a (older phones)
# - x86 or x86_64 (emulator)
#
# Download from: https://github.com/frida/frida/releases
# Look for: frida-server-17.9.1-android-{arch}.xz
#
# Extract the .xz file (use 7-Zip or similar)
# You should get a binary file: frida-server

# 2. Push frida-server to device:
C:\Users\HP\platform-tools\adb.exe push frida-server /data/local/tmp/

# 3. Make it executable:
C:\Users\HP\platform-tools\adb.exe shell chmod +x /data/local/tmp/frida-server

# 4. Start frida server (in background):
C:\Users\HP\platform-tools\adb.exe shell /data/local/tmp/frida-server -D &

# 5. Verify it's running:
C:\Users\HP\platform-tools\adb.exe shell ps | grep frida-server

# Expected: /data/local/tmp/frida-server in process list
```

### Alternative: Use frida-gadget (Simpler)

```powershell
# If frida-server doesn't work, use Frida in USB mode:
C:\Users\HP\.venv\Scripts\frida.exe -U -l frida_okhttp_interceptor.js --no-pause

# -U = USB mode (connects to first USB device)
# -l = Load script
# --no-pause = Don't pause when script loads
```

---
## 🚀 STEP 4: Deploy Basic Frida Script

### Run OkHttp Interceptor (Captures All HTTP)

```powershell
# Open terminal and run:
cd C:\Users\HP\momo

C:\Users\HP\.venv\Scripts\frida.exe -U -f ng.mtn.android.psb.momo -l frida_okhttp_interceptor.js --no-pause

# Expected output:
# [*] Spawning MoMo app...
# [*] Process ID: 12345
# [*] Attaching Frida agent...
# [*] Hooks installed, monitoring HTTP traffic...
```

### Interact with App While Frida Runs

In another terminal or on your device:

```
1. Log in to MoMo
2. View card details
3. Check account balance
4. Look at transactions
5. Try to set/verify PIN
```

### Expected Frida Output

```
[REQUEST] POST https://api.example.com/v1/auth/login
  Headers: {Authorization: Bearer eyJhbGc..., Content-Type: application/json}
  Body: {"phoneNumber": "+234...", "password": "***"}

[RESPONSE] Status: 200 OK
  Body: {"token": "eyJhbGc...", "user": {"id": "123", "name": "John"}}

[REQUEST] GET https://api.example.com/v1/cards
  Headers: {Authorization: Bearer eyJhbGc...}
  
[RESPONSE] Status: 200 OK
  Body: [{"id": "card_123", "balance": 50000, ...}]
```

---

## 🔍 STEP 5: Deploy Advanced Frida Script

### Run 7-Layer Analysis (Deeper Interception)

```powershell
# After basic script completes, run advanced hooks:
C:\Users\HP\.venv\Scripts\frida.exe -U -f ng.mtn.android.psb.momo -l frida_advanced_hooks.js --no-pause

# This captures:
# - Retrofit2 service instantiation
# - OkHttp3 requests/responses
# - Firebase database operations
# - Token storage (SharedPreferences)
# - MACLE mini-app communication
# - Cryptography operations
# - Exceptions/errors

# Expected output:
[RETROFIT] Service Created: NICardManagementAPI
[TOKEN_STORAGE] Stored: auth_token = eyJhbGc...
[FIREBASE] Database.setValue() called
[CRYPTO] Cipher.doFinal() called
```

---

## 📊 STEP 6: Capture Network Traffic (Optional)

### Method A: ADB tcpdump

```powershell
# Start packet capture on device:
C:\Users\HP\platform-tools\adb.exe shell tcpdump -i any -s 0 -w /sdcard/traffic.pcap &

# Let the app run for 2-3 minutes while you interact with it

# Stop capture (Ctrl+C or):
C:\Users\HP\platform-tools\adb.exe shell pkill tcpdump

# Pull the file:
C:\Users\HP\platform-tools\adb.exe pull /sdcard/traffic.pcap C:\Users\HP\momo\

# Analyze with Wireshark:
# Download Wireshark: https://www.wireshark.org/download/
# Open traffic.pcap and filter for:
#   ip.dst == 1.2.3.4  (backend server IP)
#   http or https
#   dns
```

### Method B: MITM Proxy

```powershell
# 1. Install mitmproxy:
pip install mitmproxy

# 2. Start mitmproxy:
mitmproxy --mode transparent -p 8080

# 3. Configure device proxy:
# On device: Settings > Wifi > Long-press network > Modify > Proxy
#   Proxy type: Manual
#   Proxy hostname: (your computer IP, e.g., 192.168.1.100)
#   Proxy port: 8080

# 4. Accept mitmproxy certificate when prompted

# 5. Monitor traffic in mitmproxy console
# Interact with app and watch traffic flow

# 6. Export captured requests:
# File > Save flows > Choose format (HAR, JSON, etc.)
```

---

## 📝 STEP 7: Capture Logcat (Application Logs)

### Real-time Log Monitoring

```powershell
# Open new terminal:
C:\Users\HP\platform-tools\adb.exe logcat | Select-String -Pattern "(MoMo|Firebase|Retrofit|API|Error|Exception)" -AllMatches

# This filters for relevant app logs

# Interact with app and watch for:
# - API calls
# - Errors
# - Firebase events
# - Network issues
```

### Save Logs to File

```powershell
# Capture logs while running app:
C:\Users\HP\platform-tools\adb.exe logcat > C:\Users\HP\momo\logcat_capture.txt

# Run for 5-10 minutes, then Ctrl+C

# Search log file:
Select-String -Path C:\Users\HP\momo\logcat_capture.txt -Pattern "(api|token|auth|firebase)" -CaseSensitive:$false
```

---

## 📋 STEP 8: Document Findings

### Create API Endpoint Map

Create file: `C:\Users\HP\momo\API_ENDPOINTS_CAPTURED.md`

```markdown
# Live API Endpoints Captured

## Authentication
POST /v1/auth/login
  Request: { phoneNumber, password }
  Response: { accessToken, refreshToken, expiresIn, user }

POST /v1/auth/refresh
  Request: { refreshToken }
  Response: { accessToken, expiresIn }

## Cards
GET /v1/cards
  Request: (auth header)
  Response: [ { id, cardNumber, balance, ... } ]

POST /v1/cards/{id}/pin/set
  Request: { pin }
  Response: { success }
```

### Save Request/Response Examples

```powershell
# Create file: C:\Users\HP\momo\API_EXAMPLES.json
# Manually copy examples from Frida output:

{
  "endpoints": [
    {
      "method": "POST",
      "url": "https://api.example.com/v1/auth/login",
      "request": {
        "phoneNumber": "+234...",
        "password": "..."
      },
      "response": {
        "accessToken": "eyJ...",
        "refreshToken": "ref_...",
        "user": { "id": "user_123" }
      }
    }
  ]
}
```

---

## ⚠️ Troubleshooting

### Issue: "Device not found"

```powershell
# Solution 1: Restart ADB
C:\Users\HP\platform-tools\adb.exe kill-server
C:\Users\HP\platform-tools\adb.exe devices

# Solution 2: Check USB connection
# - Unplug and re-plug USB cable
# - Try different USB port

# Solution 3: Install ADB drivers
# https://developer.android.com/studio/run/win-usb
```

### Issue: "Cannot spawn app"

```powershell
# Solution 1: App not installed
C:\Users\HP\platform-tools\adb.exe install -r "C:\Users\HP\momo\MoMo PSB.apk"

# Solution 2: App already running
C:\Users\HP\platform-tools\adb.exe shell am kill ng.mtn.android.psb.momo

# Solution 3: Frida not running
C:\Users\HP\platform-tools\adb.exe shell /data/local/tmp/frida-server -D &
```

### Issue: "Frida version mismatch"

```powershell
# Solution: Update Frida on host
pip install --upgrade frida

# Restart Frida server:
C:\Users\HP\platform-tools\adb.exe shell pkill frida-server
C:\Users\HP\platform-tools\adb.exe shell /data/local/tmp/frida-server -D &
```

### Issue: "No hooks installed"

```powershell
# Solution 1: Check script syntax
# Open frida_okhttp_interceptor.js and verify it's valid JavaScript

# Solution 2: Check app process name
C:\Users\HP\platform-tools\adb.exe shell pm list packages | grep momo

# Solution 3: Use simpler script first
C:\Users\HP\.venv\Scripts\frida.exe -U -l frida_okhttp_interceptor.js --no-pause
```

---

## 📱 Quick Command Reference

### Essential Commands

```powershell
# List devices
adb devices

# Install app
adb install -r "MoMo PSB.apk"

# View logs
adb logcat

# Run Frida script
frida -U -f ng.mtn.android.psb.momo -l script.js --no-pause

# Push file to device
adb push local_file /sdcard/

# Pull file from device
adb pull /sdcard/remote_file local_path

# Execute shell command
adb shell command

# Get device info
adb shell getprop ro.build.version.release
adb shell getprop ro.product.cpu.abi
```

---

## 📈 Analysis Timeline

### Typical Workflow

```
T+0:00    Setup complete
T+0:05    Deploy frida_okhttp_interceptor.js
T+0:15    Login to MoMo, capture auth flow
T+0:30    View cards, capture card API calls
T+0:45    Check transactions, capture transaction API
T+1:00    Set/verify PIN, capture PIN operations
T+1:15    Test mini-apps (if available), capture MACLE calls
T+1:30    Deploy frida_advanced_hooks.js for deeper analysis
T+2:00    Capture Firebase operations, token refresh
T+2:30    Analysis complete, document findings
T+3:00    Generate API endpoint map, security assessment
```

---

## 📊 Expected Discoveries

### What You'll Learn

✅ **Real API Endpoints** (not inferred)
✅ **Request/Response Formats** (actual JSON structures)
✅ **Authentication Tokens** (format, expiration, refresh mechanism)
✅ **Firebase Events** (what data is tracked)
✅ **Error Responses** (actual error codes/messages)
✅ **Mini-App Communication** (MACLE event format)
✅ **Performance Metrics** (latency, timeouts)
✅ **Network Flow** (which domains are contacted)

### Example Discoveries

```
Real endpoint discovered:
  POST https://api.momo-backend.io/v1/auth/login

Real token format:
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6I...

Firebase events tracked:
  - login_attempt
  - login_success
  - card_viewed
  - transaction_initiated
  - pin_operation

Mini-app launch data:
  {
    "appId": "mini_app_123",
    "userId": "user_456",
    "timestamp": 1715500000000
  }
```

---

## 🎯 Success Criteria

### Phase 2 Complete When You Have

- [ ] Connected device via ADB
- [ ] Deployed Frida successfully
- [ ] Captured login flow (auth endpoint, token)
- [ ] Captured at least 3 API endpoints
- [ ] Verified Redux state (via Frida hooks)
- [ ] Documented request/response format
- [ ] Identified all domains contacted
- [ ] Mapped authentication flow
- [ ] Generated API endpoint map

---

## 📖 Next Steps After Capture

1. **Analyze Captured Data**
   - Review all endpoints found
   - Document request/response structures
   - Identify data sensitivity

2. **Map to JavaScript Layer**
   - Cross-reference Frida findings with JAVASCRIPT_ANALYSIS_REPORT.md
   - Verify inferred Redux state shape
   - Confirm component-to-API mappings

3. **Security Assessment**
   - Test token expiration
   - Attempt authentication bypass
   - Validate SSL/TLS configuration
   - Check data encryption

4. **Generate Report**
   - Create RUNTIME_ANALYSIS_RESULTS.md
   - Document all endpoints (with real URLs)
   - Include request/response examples
   - Add security findings

---

**Status**: Phase 2 Setup Guide Complete  
**Next**: Connect device and follow steps 1-8  
**Questions?**: Refer to RUNTIME_ANALYSIS_GUIDE.md for detailed methodology  

Good luck! 🚀
