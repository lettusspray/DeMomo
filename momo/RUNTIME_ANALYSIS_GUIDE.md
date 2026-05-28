# Runtime Analysis Guide - MoMo PSB v1.21.1

## Phase 2: Network & Runtime Intelligence Gathering

This guide covers methods to capture real API traffic and analyze runtime behavior of MoMo PSB using available tools.

---

## Prerequisites

### 1. Required Components
- ✅ **Frida Framework**: v17.9.1 (already in `.venv`)
- ✅ **Android ADB**: `C:\Users\HP\platform-tools\adb.exe`
- ✅ **JADX Decompiled Source**: 17,798 Java files analyzed
- ⚠️ **Android Device/Emulator**: Required (rooted preferred)

### 2. Environment Setup

```powershell
# Activate Frida environment
& 'C:\Users\HP\.venv\Scripts\Activate.ps1'

# Verify Frida installation
frida --version
# Expected: 17.9.1

# Verify ADB
& 'C:\Users\HP\platform-tools\adb.exe' devices
# Should list connected devices or emulators
```

---

## Method 1: Frida Hook-based Interception

### 1.1 Basic OkHttp Interception

**Purpose**: Capture all HTTP requests/responses in real-time

```powershell
# Start app with Frida
frida -U -f ng.mtn.android.psb.momo -l frida_okhttp_interceptor.js --no-pause
```

**Expected Output**:
```
[REQUEST #1] POST https://api-server.example.com/v1/login
[HEADERS]
  Content-Type: application/json
  Authorization: Bearer [REDACTED]
  User-Agent: Dalvik/2.1.0
[BODY]
  {"phone": "+234...", "password": "****"}

[RESPONSE] Status: 200 OK
[RESPONSE HEADERS]
  Content-Type: application/json
[RESPONSE BODY]
  {"token": "eyJhbGciOiJIUzI1NiIs...", "user_id": "..."}
```

### 1.2 Advanced Multi-layer Hooks

```powershell
# Deploy comprehensive hooks
frida -U -f ng.mtn.android.psb.momo -l frida_advanced_hooks.js --no-pause
```

**Captures**:
- ✓ Retrofit service instantiation (endpoint discovery)
- ✓ Firebase database reads/writes
- ✓ Token storage operations
- ✓ MACLE mini-app HTTP calls
- ✓ Cryptography operations

---

## Method 2: Network Traffic Interception (MITM)

### 2.1 Configure Proxy with Burp Suite or mitmproxy

**Using mitmproxy** (lightweight alternative):

```powershell
# Install mitmproxy
pip install mitmproxy

# Start mitmproxy
mitmproxy -p 8080

# In Android Settings → WiFi → Proxy:
# Set HTTP Proxy: <PC_IP>:8080
```

**Expected Capture**:
- All HTTP/HTTPS requests (requires certificate installation)
- Real endpoint URLs
- Actual request/response payloads
- Header inspection

### 2.2 Certificate Installation on Device

```powershell
# Forward mitmproxy certificate to device
adb push ~/.mitmproxy/mitmproxy-ca-cert.pem /sdcard/

# Install as system certificate (rooted device)
adb shell
su
cp /sdcard/mitmproxy-ca-cert.pem /system/etc/security/cacerts/
chmod 644 /system/etc/security/cacerts/mitmproxy-ca-cert.pem
```

---

## Method 3: Logcat Analysis

### 3.1 Capture App Logs

```powershell
# Clear existing logs
adb logcat -c

# Start app and capture logs
adb logcat | Select-String -Pattern "MoMo|Firebase|Retrofit|MACLE|API" -HighlightMatch
```

**Key Log Patterns to Watch**:
```
# Firebase initialization
FirebaseInit: Current Process: 1234 : ng.mtn.android.psb.momo

# Network requests
okhttp3.OkHttpClient: --> POST https://api...

# Mini-app communication
MACLE: Framework Initialized

# Token management
TokenManager: Token stored/refreshed
```

### 3.2 Crash/Exception Logs

```powershell
# Capture exceptions
adb logcat | Select-String "Exception|Error|FATAL"
```

---

## Method 4: Traffic Analysis with ADB + tcpdump

### 4.1 Capture Network Packets

```powershell
# Install tcpdump on device (if not present)
adb install tcpdump  # or push binary

# Capture packets
adb shell tcpdump -i any -s 0 -w /sdcard/traffic.pcap

# Let app run for 2-3 minutes...
# (Open various screens, make transactions)

# Pull capture file
adb pull /sdcard/traffic.pcap C:\Users\HP\momo\

# Analyze with Wireshark
# Open traffic.pcap in Wireshark
```

**Wireshark Filters**:
```
# Filter to Firebase
frame contains "firebase"

# Filter to API calls
http.request.method == POST

# Filter by port
tcp.port == 443 or tcp.port == 8443
```

---

## Method 5: Reverse Engineering Encrypted Traffic

### 5.1 Export SSL Master Secret

```powershell
# Using Frida to extract SSL keys
$script = @"
const SSLContext = Java.use('javax.net.ssl.SSLContext');
const SSLSessionImpl = Java.use('com.android.org.conscrypt.SSLSessionImpl');

// Hook to extract master secrets (for SSLKEYLOGFILE equivalent)
SSLSessionImpl.getMasterSecret.implementation = function() {
    const secret = this.getMasterSecret();
    console.log("[SSL_KEY] " + arrayToHex(secret));
    return secret;
};

function arrayToHex(arr) {
    return Java.use('java.lang.String').$new(
        Java.use('java.util.Base64').getEncoder().encode(arr), 'UTF-8');
}
"@

$script | Out-File -Encoding UTF8 frida_ssl_extract.js
frida -U -f ng.mtn.android.psb.momo -l frida_ssl_extract.js --no-pause
```

---

## Key Objectives for Each Method

### Objective 1: Identify Backend Infrastructure
**Question**: What servers/domains does the app connect to?

```powershell
# From Frida output or Burp, look for:
# - API base URLs
# - Firebase project IDs
# - MACLE server configuration
# - CDN domains
```

### Objective 2: Map API Endpoints
**Question**: What endpoints exist and what do they do?

```
Expected Endpoints (from code analysis + runtime capture):
POST   /v1/auth/login
POST   /v1/auth/refresh
POST   /v1/cards/details
POST   /v1/pins/view
POST   /v1/pins/set
POST   /v1/pins/verify
POST   /v1/pins/change
POST   /v1/transactions/list
GET    /v1/user/profile
```

### Objective 3: Understand Authentication
**Question**: How are tokens acquired and maintained?

```
Expected Flow:
1. POST /v1/auth/login → Get access_token + refresh_token
2. Store token in SharedPrefs/MMKV (encrypted)
3. Attach to requests: Authorization: Bearer <token>
4. On 401: POST /v1/auth/refresh → New access_token
```

### Objective 4: Analyze Data Encryption
**Question**: Is data encrypted in transit beyond TLS?

```
Expected Indicators:
- Custom encryption layer on top of TLS
- Encrypted request bodies (not plaintext JSON)
- Decryption hooks show cipher operations
```

---

## Step-by-Step Runtime Analysis Procedure

### Step 1: Initialize Monitoring
```powershell
# Terminal 1: Start Frida hooking
frida -U -f ng.mtn.android.psb.momo -l frida_advanced_hooks.js --no-pause

# Terminal 2: Capture logcat
adb logcat > logcat_capture.txt
```

### Step 2: Exercise App Functionality
1. Open app → Wait for splash screen
2. Login → Observe token acquisition
3. Navigate to card management
4. Request card details
5. Attempt PIN operations
6. Check account/transaction history

### Step 3: Analyze Captured Data

From Frida output:
- ✓ Extract API URLs
- ✓ Identify request/response patterns
- ✓ Note authentication headers
- ✓ Document data structures

From Logcat:
- ✓ Search for error messages
- ✓ Find Firebase event logs
- ✓ Note permission requests
- ✓ Track lifecycle events

### Step 4: Map Architecture

Create diagram:
```
User Interaction
    ↓
React Native Layer
    ↓
NativeModule (MiniAppViewModule/AthenaModule)
    ↓
Retrofit Service (dynamically created)
    ↓
OkHttp3 Client (w/ Firebase interceptor)
    ↓
[Frida Hook Point] ← CAPTURE HERE
    ↓
TLS/SSL Socket
    ↓
Backend Server
```

---

## Expected API Response Structures

### Authentication Response
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "user_123",
      "phone": "+234...",
      "name": "John Doe"
    }
  }
}
```

### Card Details Response
```json
{
  "status": "success",
  "data": {
    "card_id": "card_456",
    "last_four": "1234",
    "card_type": "Visa",
    "expiry": "12/25",
    "balance": 50000.00,
    "currency": "NGN"
  }
}
```

---

## Troubleshooting

### Issue: Frida "Unable to connect to device"
```powershell
# Ensure USB debugging enabled
adb devices  # Should show device

# Verify Frida server on device
adb shell ls -la /data/local/tmp/frida-server

# If missing, push Frida server
adb push C:\Users\HP\frida-server-arm64 /data/local/tmp/
adb shell chmod +x /data/local/tmp/frida-server
```

### Issue: "Certificate verify failed" in MITM
- Install system certificate on device
- Configure app to trust proxy certificate
- Use Frida to bypass certificate pinning (if present)

### Issue: No HTTPS traffic visible
- Check if app uses certificate pinning
- May need to hook SSLContext/TrustManager
- Verify proxy settings are applied

---

## Output Deliverables

After runtime analysis, capture:

1. **API Endpoint Mapping** (endpoints.json)
   ```json
   {
     "endpoints": [
       {"method": "POST", "path": "/v1/auth/login", "auth": true},
       {"method": "POST", "path": "/v1/cards/details", "auth": true}
     ]
   }
   ```

2. **Request/Response Examples** (api_samples.txt)
   - 5-10 real requests with sanitized data
   - Response structures

3. **Authentication Flow** (auth_flow.md)
   - How tokens are obtained
   - How tokens are refreshed
   - Token storage location

4. **Firebase Configuration** (firebase_config.json)
   - Project ID
   - Database URL
   - Collections/references

5. **Network Diagram** (architecture.txt or Mermaid)
   - Client → Server architecture
   - Service dependencies

---

## Next Steps

After completing runtime analysis:

1. **JavaScript Bundle Analysis**
   - Decompress Metro bundle
   - Extract React components
   - Map Redux actions to API calls

2. **Firebase Data Analysis**
   - Identify Firestore collections
   - Map document structure
   - Reverse engineer data schema

3. **Security Assessment**
   - Validate token expiration
   - Test authentication bypass
   - Check for common vulnerabilities

---

**Status**: Ready for Phase 2 Runtime Analysis  
**Timeline**: 2-4 hours for comprehensive capture  
**Output**: API Mapping + Security Assessment Report
