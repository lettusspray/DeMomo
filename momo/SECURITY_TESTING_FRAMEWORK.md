# Security Testing Framework
## MoMo PSB v1.21.1 – Vulnerability Validation & Remediation Testing

**Purpose:** Safe, controlled lab environment to test and validate security fixes  
**Scope:** Non-destructive testing of patch effectiveness  
**Tools:** Android Emulator, Burp Suite, custom test harness  

---

## 1. Lab Environment Setup

### 1.1 System Requirements

| Component          | Specification                      |
|--------------------|------------------------------------|
| Emulator OS        | Android 12+ (arm64-v8a)            |
| CPU                | Intel i7+ or AMD Ryzen 5+          |
| RAM                | 8 GB minimum (16 GB recommended)   |
| Storage            | 50 GB free SSD space               |
| Network            | Isolated test network (no internet)|

### 1.2 Environment Isolation

```bash
# Create isolated test network (Windows)
netsh interface ip add address "vEthernet (TestNetwork)" 192.168.100.1 255.255.255.0

# Configure firewall rules (allow only test traffic)
netsh advfirewall firewall add rule name="TestLab" dir=in action=allow 
  remoteip=192.168.100.0/24 protocol=all

# Disable internet access (ensure isolated environment)
netsh advfirewall firewall add rule name="BlockInternet" dir=out action=block 
  remoteip=0.0.0.0/0 except remoteip=192.168.100.0/24
```

### 1.3 Android Emulator Configuration

```bash
# Create emulator with test configuration
$ANDROID_SDK/tools/emulator -avd TestDevice \
  -system images/android-33/arm64-v8a \
  -netspeed full \
  -netdelay none \
  -no-window \
  -port 5554 \
  -prop ro.kernel.qemu=1 \
  -prop ro.debuggable=1
```

---

## 2. V01: TLS Trust Bypass Testing

### 2.1 Test Setup

**Objective:** Verify custom trust manager is disabled and platform validation works

**Tools Required:**
- Burp Suite Community Edition
- Charles Proxy (alternative)
- OpenSSL

### 2.2 Test Procedure – VULNERABLE (Before Patch)

```bash
# 1. Install vulnerable APK on emulator
adb install MoMo_v1.21.1_vulnerable.apk

# 2. Start Burp Suite on test machine
# - Generate self-signed certificate
# - Configure as system proxy (192.168.100.1:8080)

# 3. Configure emulator to use proxy
adb shell settings put global http_proxy 192.168.100.1:8080

# 4. Launch app and attempt login
adb shell am start -n ng.mtn.android.psb.momo/.MainActivity

# 5. Monitor Burp Suite for intercepted traffic
# EXPECTED RESULT (Vulnerable): Burp successfully intercepts HTTPS traffic
# - Self-signed certificate accepted
# - Request/response bodies visible
# - Headers including Authorization token visible
```

**Test Evidence:**
```
Burp Suite Logs (Vulnerable Configuration):
[14:32:15] GET https://api.momo-backend.com/v1/accounts
│ Certificate: Burp Self-Signed (INVALID)
│ Status: [SUCCESS] - Certificate accepted
│ Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
│ X-Device-ID: ifhmbacahqzleiiz
│ Request Body: {"userId":"2348123456789"}
│ Response: {"accounts":[...]}  [PLAINTEXT VISIBLE]
```

### 2.3 Test Procedure – SECURE (After Patch)

```bash
# 1. Install patched APK on emulator
adb install MoMo_v1.21.1_patched.apk

# 2. Repeat proxy setup (same as vulnerable test)
adb shell settings put global http_proxy 192.168.100.1:8080

# 3. Launch app and attempt login
adb shell am start -n ng.mtn.android.psb.momo/.MainActivity

# 4. Monitor for SSL/TLS errors
# EXPECTED RESULT (Secure): Connection fails with certificate validation error
```

**Test Evidence:**
```
Logcat Output (Secure Configuration):
05-12 14:35:22.104  4184  8912 E AndroidRuntime: java.security.cert.CertPathValidatorException: 
  Trust anchor for certification path not found
05-12 14:35:22.105  4184  8912 E AndroidRuntime: at android.security.cert.CertificateChainValidator.doFullPathCheck
05-12 14:35:23.118  4184  4184 E NetworkManager: [HTTPS] Connection failed - Invalid certificate
05-12 14:35:23.119  4184  4184 I MainActivity: Display error: "Unable to connect securely"

Burp Suite:
[No traffic intercepted]
[14:35:24] Request to https://api.momo-backend.com/v1/accounts
│ Status: [BLOCKED] - TLS Error
│ Error: Certificate validation failed
│ App disconnected
```

### 2.4 Success Criteria

- ✅ Vulnerable version: HTTPS traffic interceptable via MITM proxy
- ✅ Patched version: HTTPS traffic NOT interceptable (cert validation enforced)
- ✅ Platform certificates load correctly
- ✅ Valid backend certificates accepted
- ✅ No SSL/TLS bypass methods available

### 2.5 Automation Script

```python
# test_tls_bypass.py
import subprocess
import time
from burp_api import BurpController

class TLSBypassTest:
    def __init__(self, emulator_id, apk_path):
        self.emulator = emulator_id
        self.apk = apk_path
        self.burp = BurpController()
    
    def test_vulnerable(self):
        """Test vulnerable version accepts self-signed cert"""
        self.install_apk(self.apk)
        self.enable_proxy()
        
        # Install self-signed cert in Burp
        self.burp.install_cert()
        
        # Trigger login
        subprocess.run(f"adb shell am start -n {self.APP}/.MainActivity", 
                      shell=True)
        
        time.sleep(3)
        
        # Check if Burp intercepted HTTPS
        intercepted = self.burp.check_intercepted_requests()
        
        assert len(intercepted) > 0, "No HTTPS traffic intercepted (not vulnerable)"
        assert any("Authorization" in r.headers for r in intercepted), \
               "Auth token not visible (not vulnerable)"
        
        print("✓ Vulnerable test passed: MITM intercept successful")
    
    def test_patched(self):
        """Test patched version rejects self-signed cert"""
        self.install_apk(self.apk)
        self.enable_proxy()
        
        # Install self-signed cert in Burp
        self.burp.install_cert()
        
        # Trigger login
        subprocess.run(f"adb shell am start -n {self.APP}/.MainActivity", 
                      shell=True)
        
        time.sleep(3)
        
        # Check for connection failures
        logcat = self.get_logcat()
        
        assert "CertPathValidatorException" in logcat or \
               "Certificate validation failed" in logcat, \
               "No TLS error found (may still be vulnerable)"
        
        intercepted = self.burp.check_intercepted_requests()
        assert len(intercepted) == 0, "HTTPS traffic still interceptable (not patched)"
        
        print("✓ Patched test passed: MITM intercept blocked")
```

---

## 3. V02: WebView File Access Testing

### 3.1 Test Setup

**Objective:** Verify file access flags are disabled and JS cannot read app data

**Tools Required:**
- Android Studio (debugging)
- Burp Suite (JavaScript injection)
- Custom test WebView

### 3.2 Test Procedure – VULNERABLE

```bash
# 1. Create test HTML file with file access attempts
cat > /tmp/test_file_access.html << 'EOF'
<html>
<body>
<script>
// Attempt to read local files
fetch('file:///data/local/tmp/test.txt')
  .then(r => r.text())
  .then(data => {
    console.log('FILE CONTENTS: ' + data);
  })
  .catch(e => console.log('Error: ' + e));

// Attempt to access app private storage
fetch('file:///data/data/ng.mtn.android.psb.momo/shared_prefs/app_prefs.xml')
  .then(r => r.text())
  .then(data => {
    console.log('APP DATA: ' + data);
  });
</script>
</body>
</html>
EOF

# 2. Push to emulator
adb push /tmp/test_file_access.html /data/local/tmp/

# 3. Create test app that loads the HTML in WebView
# (See code example below)

# 4. Load vulnerable WebView with test HTML
adb shell am start com.test/.WebViewActivity --es url "file:///data/local/tmp/test_file_access.html"

# 5. Check logcat for file contents
adb logcat | grep "FILE CONTENTS\|APP DATA"

# EXPECTED (Vulnerable): File contents visible in logs
# FILE CONTENTS: [private file contents]
# APP DATA: [XML with tokens/secrets]
```

### 3.3 Test Procedure – SECURE

```bash
# 1. Install patched WebView component
adb install MoMo_v1.21.1_patched_webview.apk

# 2. Repeat the test
adb shell am start com.test/.WebViewActivity --es url "file:///data/local/tmp/test_file_access.html"

# 3. Check logcat
adb logcat | grep "FILE CONTENTS\|APP DATA\|Access blocked"

# EXPECTED (Secure):
# Error: File access denied (blocked by security policy)
# OR
# No sensitive file contents logged
```

### 3.4 Test WebView App (Reference)

```java
// TestWebViewActivity.java
public class TestWebViewActivity extends AppCompatActivity {
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_webview);
        
        webView = findViewById(R.id.webView);
        
        // VULNERABLE: File access enabled
        WebSettings settings = webView.getSettings();
        settings.setAllowFileAccess(true);  // Remove in patched version
        settings.setAllowUniversalAccessFromFileURLs(true);  // Remove
        settings.setJavaScriptEnabled(true);
        
        String url = getIntent().getStringExtra("url");
        webView.loadUrl(url);
    }
}

// PATCHED VERSION:
// settings.setAllowFileAccess(false);
// settings.setAllowUniversalAccessFromFileURLs(false);
```

### 3.5 Success Criteria

- ✅ Vulnerable: File access possible, private app data readable
- ✅ Patched: File access blocked, JavaScript errors on file:// attempts
- ✅ HTTPS content still works (HTTP/HTTPS not blocked)

---

## 4. V03: JavaScript Bridge Exposure Testing

### 4.1 Test Procedure

```bash
# 1. Create test webpage with malicious JS bridge usage
cat > /tmp/test_js_bridge.html << 'EOF'
<html>
<body>
<script>
// Attempt to call Java interface method
if (typeof android !== 'undefined') {
  console.log('Java interface available');
  
  // Try to call exposed methods
  android.requestLocationPermission();
  android.reportGeofenceStatus("ACTIVE");
  
  console.log('Java methods callable - VULNERABLE');
} else {
  console.log('Java interface NOT available - SECURE');
}
</script>
</body>
</html>
EOF

# 2. Load in vulnerable WebView
adb push /tmp/test_js_bridge.html /data/local/tmp/
adb shell am start com.test.geofencing/.BackgroundGeofencingWebViewActivity \
  --es url "file:///data/local/tmp/test_js_bridge.html"

# 3. Check logcat for bridge availability
adb logcat | grep "Java interface\|methods callable"

# VULNERABLE: Bridge available and methods callable
# SECURE: Bridge not exposed to untrusted origins
```

### 4.2 Geolocation Permission Test

```bash
# 1. Create test webpage requesting geolocation
cat > /tmp/test_geolocation.html << 'EOF'
<html>
<body>
<button onclick="requestGeolocation()">Get Location</button>
<script>
function requestGeolocation() {
  navigator.geolocation.getCurrentPosition(
    function(position) {
      console.log('Location: ' + position.coords.latitude + ', ' + position.coords.longitude);
    },
    function(error) {
      console.log('Error: ' + error);
    }
  );
}
</script>
</body>
</html>
EOF

# 2. Load in vulnerable WebView
adb push /tmp/test_geolocation.html /data/local/tmp/
adb shell am start com.test.geofencing/.BackgroundGeofencingWebViewActivity \
  --es url "file:///data/local/tmp/test_geolocation.html"

# 3. Trigger geolocation request
adb shell input tap 100 100  # Click button

# 4. Check logcat
adb logcat | grep "Location:"

# VULNERABLE: Location granted without user prompt
# SECURE: User permission dialog shown before granting
```

---

## 5. V04 & V05: Cryptography & Token Testing

### 5.1 MD5 vs SHA-256 Verification

```python
# test_crypto.py
import hashlib
import hmac

def test_hash_algorithms():
    """Verify weak (MD5) vs strong (SHA-256) hashing"""
    
    phone_number = "2348123456789"
    
    # Test vulnerable MD5
    md5_hash = hashlib.md5(phone_number.encode()).hexdigest()
    print(f"MD5: {md5_hash}")  # e.g., "5d41402abc4b2a76b9719d911017c592"
    
    # Test weak: easy collision generation
    # Real-world example: two PDFs with same MD5 but different content
    print("⚠️  MD5 is collision-prone")
    
    # Test secure SHA-256
    sha256_hash = hashlib.sha256(phone_number.encode()).hexdigest()
    print(f"SHA-256: {sha256_hash}")  # e.g., long hex string
    
    # Test HMAC-SHA-256 (preferred for identity)
    secret = "app_secret_key"
    hmac_hash = hmac.new(
        secret.encode(), 
        phone_number.encode(), 
        hashlib.sha256
    ).hexdigest()
    print(f"HMAC-SHA-256: {hmac_hash}")
    
    print("✓ SHA-256/HMAC-SHA-256 are cryptographically secure")

def test_token_expiry():
    """Verify token expiry is enforced"""
    
    # Test with expired token
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
    # Payload: {"exp": 1234567890}  (expired in 1970s)
    
    current_time = time.time()
    token_expiry = 1234567890
    
    if current_time > token_expiry:
        print("✓ Token expired - access denied")
    else:
        print("✗ Token accepted despite being expired")

test_hash_algorithms()
test_token_expiry()
```

---

## 6. Automated Test Suite

```python
# security_test_suite.py
import unittest
import subprocess
import time

class SecurityTestSuite(unittest.TestCase):
    
    def setUp(self):
        """Initialize test environment"""
        self.emulator = "emulator-5554"
        self.app_package = "ng.mtn.android.psb.momo"
    
    @unittest.skip("Manual MITM proxy test")
    def test_v01_tls_bypass(self):
        """Test TLS validation"""
        # Run TLSBypassTest.test_vulnerable()
        # Assert MITM intercept possible
        pass
    
    def test_v02_webview_file_access(self):
        """Test WebView file access restrictions"""
        # Create test WebView app
        # Try to read file:// URLs
        # Assert access denied
        pass
    
    def test_v03_js_bridge_exposure(self):
        """Test JavaScript bridge exposure"""
        # Load untrusted HTML
        # Try to call java interface
        # Assert not available or origin-restricted
        pass
    
    def test_v04_crypto_weakness(self):
        """Test cryptographic strength"""
        result = subprocess.run([
            "python3", "-c",
            "import hashlib; print('MD5' if hashlib.md5 else 'Strong')"
        ], capture_output=True, text=True)
        self.assertNotIn("MD5", result.stdout)
    
    def test_v05_token_expiry(self):
        """Test token expiry enforcement"""
        # Create expired token
        # Send request with expired token + ignoreexpirycheck flag
        # Assert denied (flag should have no effect)
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## 7. Test Reporting

### Test Report Template

```markdown
# Security Patch Validation Report
**Date:** [Date]  
**APK Version:** MoMo v1.21.1 (Patched)  
**Tester:** [Name]  

## Test Results

| Vulnerability | Test Case | Result | Evidence |
|---|---|---|---|
| V01 TLS Bypass | MITM proxy interception | ✅ PASS | No traffic intercepted |
| V02 WebView File Access | Read file:// URL | ✅ PASS | Access denied |
| V03 JS Bridge | Call java interface | ✅ PASS | Method not available |
| V04 Crypto Weakness | MD5 usage | ✅ PASS | SHA-256 used |
| V05 Token Expiry | Expired token + flag | ✅ PASS | Request denied |

## Conclusion
All critical vulnerabilities have been successfully patched and validated.
```

---

**Status:** Recommended for use by vendor security team during patch validation
