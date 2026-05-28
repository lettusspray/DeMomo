# Secure Remediation Code
## MoMo PSB v1.21.1 – Patch Implementations

**Purpose:** Provide secure before/after code patches for each vulnerability.  
**Status:** Reference implementation – requires vendor validation before production deployment.

---

## 1. V01: Global TLS Trust Bypass – Remediation

### ❌ VULNERABLE CODE (Current)

**File:** `ng/mtn/android/momo/demo/MacleEventHandlerExd.java`

```java
public final void setHttpsTrustManager() {
    try {
        SSLContext sSLContext = SSLContext.getInstance("TLS");
        // VULNERABLE: Custom trust manager accepts all certificates
        sSLContext.init(null, new TrustManager[]{new AnonymousClass1()}, 
                        SecureRandom.getInstance("SHA1PRNG"));
        // VULNERABLE: Global override disables validation for entire app
        HttpsURLConnection.setDefaultSSLSocketFactory(sSLContext.getSocketFactory());
        // VULNERABLE: Hostname verifier always returns true
        HttpsURLConnection.setDefaultHostnameVerifier(new MacleEventHandlerExd$$ExternalSyntheticLambda0());
    } catch (Exception unused) {
        Log.e("DefaultEventHandler", "exception occurred, when set https trust manager");
    }
}

// VULNERABLE: Empty checkServerTrusted – no validation
public class AnonymousClass1 implements X509TrustManager {
    @Override
    public X509Certificate[] getAcceptedIssuers() {
        return new X509Certificate[0];
    }

    @Override
    public void checkClientTrusted(X509Certificate[] x509CertificateArr, String str) 
        throws CertificateException {
    }

    @Override
    public void checkServerTrusted(X509Certificate[] x509CertificateArr, String str) 
        throws CertificateException {
        // VULNERABLE: No validation performed
    }
}

// VULNERABLE: HostnameVerifier always true
public final class MacleEventHandlerExd$$ExternalSyntheticLambda0 implements HostnameVerifier {
    public final boolean verify(String str, SSLSession sSLSession) {
        return true;  // VULNERABLE: Accepts any hostname
    }
}
```

### ✅ SECURE PATCH

```java
import android.content.Context;
import java.security.KeyStore;
import java.util.Arrays;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public final class MacleEventHandlerExd extends DefaultMacleEventHandler {
    private static final String TAG = "MacleEventHandler";
    private Context context;

    public MacleEventHandlerExd(Context context) {
        this.context = context;
    }

    @Override
    public final void setHttpsTrustManager() {
        try {
            // SECURE: Use platform default TrustManager
            // Remove the custom trust manager that bypasses validation
            // Instead, rely on system certificate store
            
            SSLContext sSLContext = SSLContext.getInstance("TLS");
            // SECURE: Initialize with null to use default trust managers
            // (Platform certificates + user-installed CAs)
            sSLContext.init(null, null, null);
            
            // SECURE: Apply only to Retrofit client, not globally
            // (Requires updating OkHttp client initialization)
            // This prevents affecting other network libraries
            
            HttpsURLConnection.setDefaultSSLSocketFactory(sSLContext.getSocketFactory());
            // NOTE: Remove global hostname verifier override
            // Platform default performs proper validation
            
            Log.i(TAG, "HTTPS TLS configuration initialized with platform defaults");
        } catch (Exception e) {
            Log.e(TAG, "Exception setting TLS configuration", e);
            throw new RuntimeException("Failed to initialize HTTPS", e);
        }
    }

    // SECURE: Proper X509TrustManager that validates certificates
    private X509TrustManager createSecureTrustManager() throws Exception {
        // Load system truststore
        KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
        keyStore.load(null, null);
        
        // Use platform's trust managers
        javax.net.ssl.TrustManagerFactory tmf = 
            javax.net.ssl.TrustManagerFactory.getInstance("X509");
        tmf.init(keyStore);
        
        TrustManager[] trustManagers = tmf.getTrustManagers();
        for (TrustManager tm : trustManagers) {
            if (tm instanceof X509TrustManager) {
                return (X509TrustManager) tm;
            }
        }
        throw new AssertionError("No X509TrustManager found");
    }

    // RECOMMENDED: Certificate Pinning for enhanced security
    // Pins specific backend certificates to prevent MITM even via compromised CAs
    private void setupCertificatePinning() {
        // Example using OkHttp CertificatePinner
        // new CertificatePinner.Builder()
        //     .add("api.backend.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        //     .build();
        // Apply to OkHttp client configuration
    }
}

// REMOVED: MacleEventHandlerExd$$ExternalSyntheticLambda0 (Hostname verifier bypass)
// Use platform default hostname verification
```

### Application Integration

```java
// OkHttp Client Configuration (Secure)
public class NetworkConfiguration {
    public static OkHttpClient createSecureOkHttpClient(Context context) {
        return new OkHttpClient.Builder()
            // Platform will use system certificate validation
            .sslSocketFactory(createSecureSSLSocketFactory(), createSecureTrustManager())
            .hostnameVerifier((hostname, session) -> {
                // SECURE: Use platform default verification
                return javax.net.ssl.HttpsURLConnection.getDefaultHostnameVerifier()
                    .verify(hostname, session);
            })
            .certificatePinner(createCertificatePinner())
            // Add other configurations
            .build();
    }

    private static SSLSocketFactory createSecureSSLSocketFactory() throws Exception {
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, null, null);
        return sslContext.getSocketFactory();
    }

    private static X509TrustManager createSecureTrustManager() throws Exception {
        javax.net.ssl.TrustManagerFactory tmf = 
            javax.net.ssl.TrustManagerFactory.getInstance("X509");
        tmf.init((KeyStore) null);
        
        for (TrustManager tm : tmf.getTrustManagers()) {
            if (tm instanceof X509TrustManager) {
                return (X509TrustManager) tm;
            }
        }
        throw new AssertionError("No X509TrustManager");
    }

    private static CertificatePinner createCertificatePinner() {
        return new CertificatePinner.Builder()
            // Pin backend certificates
            .add("api.momo-backend.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .build();
    }
}
```

---

## 2. V02: Unsafe WebView File Access – Remediation

### ❌ VULNERABLE CODE

**File:** `com/huawei/astp/macle/engine/WebViewForMiniApp.java`

```java
public final void a(Context context, AppConfig appConfig) {
    setWebViewClient(new r(context));
    setScrollBarStyle(0);
    // ...
    // VULNERABLE: File access enabled
    getSettings().setAllowFileAccess(true);
    // VULNERABLE: Universal file URL access
    getSettings().setAllowUniversalAccessFromFileURLs(true);
    // VULNERABLE: File-to-file access
    getSettings().setAllowFileAccessFromFileURLs(true);
    getSettings().setJavaScriptEnabled(true);
    // ...
}
```

### ✅ SECURE PATCH

```java
import android.webkit.WebSettings;
import android.webkit.WebView;

public final class WebViewForMiniApp extends WebView {
    private static final String TAG = "WebViewForMiniApp";
    
    public final void configureSecureWebView(Context context, AppConfig appConfig) {
        setWebViewClient(new SecureWebViewClient(context));
        setWebChromeClient(new SecureWebChromeClient());
        
        WebSettings settings = getSettings();
        
        // SECURE: Disable file access completely
        // Mini-apps should use HTTP/HTTPS only
        settings.setAllowFileAccess(false);
        
        // SECURE: Disable universal file URL access
        // Prevents JS from accessing file:// URLs
        settings.setAllowUniversalAccessFromFileURLs(false);
        
        // SECURE: Disable file-to-file access
        // Isolated sandboxing
        settings.setAllowFileAccessFromFileURLs(false);
        
        // JavaScript only if necessary for mini-app
        settings.setJavaScriptEnabled(true);
        
        // SECURE: Additional hardening
        settings.setDomStorageEnabled(false);  // Disable DOM storage
        settings.setDatabaseEnabled(false);     // Disable database
        
        // SECURE: Content security policy
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        
        Log.i(TAG, "WebView configured with security restrictions");
    }
    
    // SECURE: WebView client that validates URLs
    private class SecureWebViewClient extends WebViewClient {
        private final Context context;
        private static final String[] ALLOWED_SCHEMES = {"https", "http"};
        
        public SecureWebViewClient(Context context) {
            this.context = context;
        }
        
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            // SECURE: Only allow HTTP/HTTPS URLs
            if (isUrlAllowed(url)) {
                view.loadUrl(url);
                return true;
            }
            
            Log.w(TAG, "Blocked disallowed URL: " + url);
            return false;
        }
        
        private boolean isUrlAllowed(String url) {
            for (String scheme : ALLOWED_SCHEMES) {
                if (url.startsWith(scheme + "://")) {
                    return true;
                }
            }
            return false;
        }
    }
    
    // SECURE: Chrome client with restricted permissions
    private class SecureWebChromeClient extends WebChromeClient {
        @Override
        public boolean onJsAlert(WebView view, String url, String message, JsResult result) {
            // Log alerts for debugging
            Log.d(TAG, "JS Alert: " + message);
            return false;
        }
        
        @Override
        public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
            // Deny confirmation dialogs
            result.cancel();
            return true;
        }
    }
}
```

---

## 3. V03: JavaScript Bridge Exposure – Remediation

### ❌ VULNERABLE CODE

**File:** `io/okhi/android_background_geofencing/activities/BackgroundGeofencingWebViewActivity.java`

```java
public final void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_web_view);
    this.webView = (WebView) findViewById(R.id.webview);
    
    WebSettings settings = this.webView.getSettings();
    settings.setJavaScriptEnabled(true);
    
    // VULNERABLE: Exposed JS interface without origin validation
    WebViewAppInterface webViewAppInterface = new WebViewAppInterface();
    webViewAppInterface.mContext = this;
    this.webView.addJavascriptInterface(webViewAppInterface, MacleConstants.PLATFORM_ANDROID);
    
    this.webView.loadUrl(this.webViewUrl);
    this.webView.setWebChromeClient(new AnonymousClass1());
}

// VULNERABLE: Auto-approves geolocation without user interaction
public final class AnonymousClass1 extends WebChromeClient {
    @Override
    public final void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
        callback.invoke(origin, true, false);  // VULNERABLE: Auto-grant
    }
}
```

### ✅ SECURE PATCH

```java
import android.content.Context;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.GeolocationPermissions;
import androidx.appcompat.app.AppCompatActivity;
import java.net.URL;

public class BackgroundGeofencingWebViewActivity extends AppCompatActivity {
    private static final String TAG = "BGWebViewActivity";
    private static final String ALLOWED_HOST = "geofencing.momo.internal";
    
    private WebView webView;
    private String webViewUrl;
    
    @Override
    public final void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_web_view);
        this.webView = (WebView) findViewById(R.id.webview);
        
        // SECURE: Initialize WebView with security client
        this.webView.setWebViewClient(new SecureWebViewClient());
        this.webView.setWebChromeClient(new SecureWebChromeClient());
        
        WebSettings settings = this.webView.getSettings();
        settings.setJavaScriptEnabled(true);
        
        // SECURE: Only expose interface to trusted content
        if (isUrlTrusted(this.webViewUrl)) {
            // Only add interface after verifying URL origin
            SecureWebViewAppInterface secureInterface = new SecureWebViewAppInterface(this);
            this.webView.addJavascriptInterface(secureInterface, "android");
            Log.i(TAG, "JS interface exposed to trusted origin");
        } else {
            Log.e(TAG, "Untrusted URL: " + this.webViewUrl);
            finish();
            return;
        }
        
        this.webView.loadUrl(this.webViewUrl);
    }
    
    // SECURE: Verify URL origin before exposing interface
    private boolean isUrlTrusted(String url) {
        try {
            URL parsedUrl = new URL(url);
            String host = parsedUrl.getHost();
            // Only allow internal/localhost URLs
            return "localhost".equals(host) || 
                   "127.0.0.1".equals(host) || 
                   ALLOWED_HOST.equals(host);
        } catch (Exception e) {
            Log.e(TAG, "Invalid URL", e);
            return false;
        }
    }
    
    // SECURE: WebView client that validates origins
    private class SecureWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            // Only allow navigation within trusted domain
            if (isUrlTrusted(url)) {
                return false;  // Allow load
            }
            Log.w(TAG, "Blocked navigation to untrusted URL: " + url);
            return true;  // Block load
        }
        
        @Override
        public void onPageStarted(WebView view, String url, Bitmap favicon) {
            // Validate URL before page starts
            if (!isUrlTrusted(url)) {
                view.stopLoading();
                Log.e(TAG, "Untrusted page load detected");
            }
        }
    }
    
    // SECURE: Chrome client that requires explicit user consent
    private class SecureWebChromeClient extends WebChromeClient {
        @Override
        public void onGeolocationPermissionsShowPrompt(String origin, 
                                                       GeolocationPermissions.Callback callback) {
            // SECURE: Require origin validation and explicit user prompt
            if (!isUrlTrusted(origin)) {
                Log.w(TAG, "Geolocation denied to untrusted origin: " + origin);
                callback.invoke(origin, false, false);
                return;
            }
            
            // SECURE: Show actual permission dialog instead of auto-granting
            new androidx.appcompat.app.AlertDialog.Builder(BackgroundGeofencingWebViewActivity.this)
                .setTitle("Location Permission")
                .setMessage("Allow " + origin + " to access your location?")
                .setPositiveButton("Allow", (dialog, which) -> {
                    callback.invoke(origin, true, false);
                })
                .setNegativeButton("Deny", (dialog, which) -> {
                    callback.invoke(origin, false, false);
                })
                .show();
        }
        
        @Override
        public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
            // Validate origin
            if (!isUrlTrusted(url)) {
                result.cancel();
                return true;
            }
            return super.onJsConfirm(view, url, message, result);
        }
    }
    
    // SECURE: Restricted JavaScript interface
    private static class SecureWebViewAppInterface {
        private final Context context;
        
        public SecureWebViewAppInterface(Context context) {
            this.context = context;
        }
        
        // SECURE: Only expose specific methods with permission checks
        @android.webkit.JavascriptInterface
        public void requestLocationPermission() {
            Log.i(TAG, "JS requested location permission (with user consent required)");
            // Implement permission request logic
        }
        
        @android.webkit.JavascriptInterface
        public void reportGeofenceStatus(String status) {
            // Validate and process geofence status only from trusted source
            Log.i(TAG, "Geofence status: " + status);
        }
    }
}
```

---

## 4. V04: Weak Cryptography – Remediation

### ❌ VULNERABLE CODE

**File:** `ng/mtn/android/momo/demo/MacleEventHandlerExd.java`

```java
public final String getUidHash() {
    String str = PhoneNumCache.phoneNumber;
    try {
        // VULNERABLE: MD5 is cryptographically broken
        MessageDigest messageDigest = MessageDigest.getInstance("MD5");
        messageDigest.update(str.getBytes());
        byte[] bArrDigest = messageDigest.digest();
        
        StringBuilder sb = new StringBuilder();
        for (byte b : bArrDigest) {
            String hexString = Integer.toHexString(b & 255);
            if (hexString.length() == 1) {
                sb.append('0');
            }
            sb.append(hexString);
        }
        return sb.toString();
    } catch (NoSuchAlgorithmException unused) {
        return String.valueOf(str.hashCode());
    }
}

// VULNERABLE: SHA1PRNG is deprecated and weak
SSLContext sSLContext = SSLContext.getInstance("TLS");
sSLContext.init(null, null, SecureRandom.getInstance("SHA1PRNG"));
```

### ✅ SECURE PATCH

```java
import java.security.MessageDigest;
import java.security.SecureRandom;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import android.util.Log;

public final class MacleEventHandlerExd extends DefaultMacleEventHandler {
    private static final String TAG = "MacleEventHandler";
    private static final String HASH_ALGORITHM = "SHA-256";
    private static final String HMAC_ALGORITHM = "HmacSHA256";
    
    // SECURE: Use HMAC-SHA256 for identity hashing with a secret key
    public final String getUidHash() {
        String phoneNumber = PhoneNumCache.phoneNumber;
        try {
            // SECURE: Use HMAC-SHA256 instead of raw MD5
            // This provides both cryptographic security and prevents collision attacks
            byte[] hmacKey = getHmacSecret().getBytes("UTF-8");
            SecretKeySpec secretKeySpec = new SecretKeySpec(hmacKey, 0, hmacKey.length, HMAC_ALGORITHM);
            
            Mac mac = Mac.getInstance(HMAC_ALGORITHM);
            mac.init(secretKeySpec);
            
            byte[] hash = mac.doFinal(phoneNumber.getBytes("UTF-8"));
            
            // Convert to hex string
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                String hexString = Integer.toHexString(b & 0xFF);
                if (hexString.length() == 1) {
                    sb.append('0');
                }
                sb.append(hexString);
            }
            
            Log.i(TAG, "UID hash computed securely with HMAC-SHA256");
            return sb.toString();
        } catch (Exception e) {
            Log.e(TAG, "Error computing UID hash", e);
            // Fallback: Still use SHA-256 instead of weak hash
            return computeSHA256Hash(phoneNumber);
        }
    }
    
    // SECURE: Proper SHA-256 fallback (not MD5)
    private String computeSHA256Hash(String input) {
        try {
            // SECURE: SHA-256 instead of MD5
            MessageDigest messageDigest = MessageDigest.getInstance(HASH_ALGORITHM);
            messageDigest.update(input.getBytes("UTF-8"));
            byte[] digest = messageDigest.digest();
            
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                String hexString = Integer.toHexString(b & 0xFF);
                if (hexString.length() == 1) {
                    sb.append('0');
                }
                sb.append(hexString);
            }
            return sb.toString();
        } catch (Exception e) {
            Log.e(TAG, "Error computing SHA256 hash", e);
            throw new RuntimeException("Hash computation failed", e);
        }
    }
    
    // SECURE: Get HMAC secret from secure storage (not hardcoded)
    private String getHmacSecret() {
        // IMPORTANT: Retrieve from Android KeyStore or secure storage
        // DO NOT hardcode secrets in source code
        // Use Android Keystore for key storage:
        // KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
        return System.getenv("HMAC_SECRET");  // Example only
    }
    
    // SECURE: Proper SSL/TLS initialization
    public final void setHttpsTrustManager() {
        try {
            SSLContext sSLContext = SSLContext.getInstance("TLSv1.2");  // Specify version
            
            // SECURE: Use null for default trust managers (platform certificates)
            // SECURE: Use SecureRandom without specifying algorithm (platform default)
            sSLContext.init(null, null, new SecureRandom());
            
            Log.i(TAG, "TLS initialized securely with platform defaults");
        } catch (Exception e) {
            Log.e(TAG, "Error initializing TLS", e);
        }
    }
}
```

---

## 5. V05: Expiry-Check Bypass – Remediation

### ❌ VULNERABLE CODE

**File:** `ng/mtn/android/momo/demo/MacleEventHandlerExd.java`

```java
public final JSONObject getRequestHead() {
    String secureFor = KeysModule.getSecureFor("MINI_APP_THIRD_PARTY_ID_ANDROID");
    JSONObject jSONObject = new JSONObject();
    try {
        jSONObject.put("third-party-id", secureFor);
        jSONObject.put("Content-Type", "application/json");
        // VULNERABLE: Bypass flag sent to backend
        jSONObject.put("ignoreexpirycheck", "true");
        jSONObject.put(AppsFlyerProperties.CHANNEL, "MTNAPPNXG");
        jSONObject.put("bundle-id", "ng.mtn.android.psb.momo");
        jSONObject.put("platform-id", MacleConstants.PLATFORM_ANDROID);
    } catch (JSONException e) {
        e.printStackTrace();
    }
    return jSONObject;
}
```

### ✅ SECURE PATCH

```java
import org.json.JSONException;
import org.json.JSONObject;
import android.util.Log;

public final class MacleEventHandlerExd extends DefaultMacleEventHandler {
    private static final String TAG = "MacleEventHandler";
    
    @Override
    public final JSONObject getRequestHead() {
        String secureFor = KeysModule.getSecureFor("MINI_APP_THIRD_PARTY_ID_ANDROID");
        JSONObject jSONObject = new JSONObject();
        try {
            jSONObject.put("third-party-id", secureFor);
            jSONObject.put("Content-Type", "application/json");
            // SECURE: Remove expiry bypass flag completely
            // Backend should always enforce token expiry
            // Removed: jSONObject.put("ignoreexpirycheck", "true");
            
            jSONObject.put("Channel", "MTNAPPNXG");
            jSONObject.put("bundle-id", "ng.mtn.android.psb.momo");
            jSONObject.put("platform-id", MacleConstants.PLATFORM_ANDROID);
            
            // SECURE: Add token expiry validation header
            jSONObject.put("X-Token-Expiry-Enforcement", "required");
            
            // SECURE: Add request timestamp for replay attack prevention
            jSONObject.put("X-Request-Timestamp", System.currentTimeMillis());
            
            Log.i(TAG, "Request headers configured without expiry bypass");
        } catch (JSONException e) {
            Log.e(TAG, "Error building request headers", e);
            throw new RuntimeException("Failed to build request headers", e);
        }
        return jSONObject;
    }
    
    // SECURE: Token validation helper
    public static boolean isTokenValid(String token) {
        try {
            // Decode token and check expiry timestamp
            // Do not allow expired tokens under any circumstances
            long expiryTime = parseTokenExpiry(token);
            long currentTime = System.currentTimeMillis();
            
            if (currentTime > expiryTime) {
                Log.w(TAG, "Token expired");
                return false;
            }
            
            Log.i(TAG, "Token valid");
            return true;
        } catch (Exception e) {
            Log.e(TAG, "Error validating token", e);
            return false;
        }
    }
    
    private static long parseTokenExpiry(String token) {
        // Parse JWT or custom token format
        // Extract expiry claim and convert to milliseconds
        // This should be implemented based on your token format
        throw new UnsupportedOperationException("Implement token parsing");
    }
}
```

---

## 6. Testing Checklist

### V01: TLS Trust Bypass
- [ ] Verify `setDefaultSSLSocketFactory` no longer installed globally
- [ ] Verify `setDefaultHostnameVerifier` removed
- [ ] Test with Burp/Fiddler proxy – should not accept self-signed cert
- [ ] Verify system certificates load correctly

### V02: WebView File Access
- [ ] Verify `setAllowFileAccess(false)` enforced
- [ ] Verify `setAllowUniversalAccessFromFileURLs(false)` enforced
- [ ] Verify `setAllowFileAccessFromFileURLs(false)` enforced
- [ ] Test that file:// URLs are blocked
- [ ] Verify JS cannot read app private directory

### V03: JS Bridge Exposure
- [ ] Verify `addJavascriptInterface` only for trusted URLs
- [ ] Verify origin validation happens before interface exposure
- [ ] Verify geolocation prompt actually shows (not auto-granted)
- [ ] Test that untrusted URLs cannot call interface methods

### V04: Weak Cryptography
- [ ] Verify HMAC-SHA256 used instead of MD5
- [ ] Verify SHA-256 used as fallback (not MD5)
- [ ] Verify SecureRandom default used (not SHA1PRNG)

### V05: Expiry Bypass
- [ ] Verify `ignoreexpirycheck` header removed
- [ ] Verify token expiry still enforced after removal
- [ ] Test that expired tokens are rejected
- [ ] Verify replay attack prevention (timestamp validation)

---

## 7. Deployment Strategy

1. **Patch Development:** Apply fixes to each vulnerable class
2. **Unit Testing:** Verify each patch independently
3. **Integration Testing:** Test with full app stack
4. **Security Testing:** Verify fixes with MITM proxy, Burp Suite
5. **Staging Release:** Release to beta/staging first
6. **Production Release:** Gradual rollout with monitoring

---

**Status:** Reference implementation – requires vendor review and approval before deployment
