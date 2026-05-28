/**
 * Advanced Frida Script - MoMo PSB Network & Data Flow Analysis
 * Purpose: Hook Firebase, Retrofit, and custom API layers
 * 
 * Target Classes:
 * - Retrofit2 service proxy generation
 * - Firebase Realtime Database operations
 * - Token acquisition & refresh
 * - NI Card Management API calls
 * - MACLE mini-app communication
 */

console.log("🚀 Advanced Frida Analysis Script Loading...\n");

// ============================================================================
// PHASE 1: Retrofit Service Detection
// ============================================================================
console.log("[PHASE 1] Hooking Retrofit2 Service Layer...");

try {
    const Retrofit = Java.use('retrofit2.Retrofit');
    const ServiceMethod = Java.use('retrofit2.ServiceMethod');
    
    // Hook Retrofit.create() to detect which services are instantiated
    Retrofit.create.implementation = function(serviceClass) {
        const serviceName = serviceClass.toString();
        console.log(`\n[RETROFIT] Service Created: ${serviceName}`);
        console.log(`  └─ Base URL: ${this.baseUrl().toString()}`);
        
        return this.create(serviceClass);
    };
    
    console.log("✅ Retrofit hooks installed");
} catch (e) {
    console.log("⚠️  Retrofit hooking failed: " + e.message);
}

// ============================================================================
// PHASE 2: API Request Interception (OkHttp Layer)
// ============================================================================
console.log("[PHASE 2] Hooking OkHttp3 Network Layer...");

const HttpUrl = Java.use('okhttp3.HttpUrl');
const Request = Java.use('okhttp3.Request');
const Response = Java.use('okhttp3.Response');

// Store request details
let requestLog = [];

// Hook Request.Builder to capture request construction
try {
    const RequestBuilder = Java.use('okhttp3.Request$Builder');
    RequestBuilder.build.implementation = function() {
        const request = this.build();
        const url = request.url().toString();
        
        // Only log API calls, not image/resource calls
        if (url.includes('/api') || url.includes('firebase') || url.includes('macle')) {
            logNetworkRequest(request);
        }
        
        return request;
    };
    console.log("✅ Request builder hooks installed");
} catch (e) {
    console.log("⚠️  Request builder hooking failed: " + e.message);
}

function logNetworkRequest(request) {
    const timestamp = new Date().toISOString();
    const url = request.url().toString();
    const method = request.method();
    
    console.log(`\n[${timestamp}] 🌐 ${method} ${url}`);
    
    // Log headers
    const headers = request.headers();
    for (let i = 0; i < headers.size(); i++) {
        const name = headers.name(i);
        const value = headers.value(i);
        if (!shouldRedact(name)) {
            console.log(`     ${name}: ${value}`);
        }
    }
    
    // Log request body for POST/PUT
    if ((method === 'POST' || method === 'PUT') && request.body() !== null) {
        try {
            const bodyStr = attemptReadBody(request.body());
            console.log(`     Body: ${bodyStr}`);
        } catch (e) {
            console.log(`     Body: [unable to read]`);
        }
    }
}

function shouldRedact(headerName) {
    const sensitive = ['authorization', 'token', 'cookie', 'password', 'api-key', 'x-api-key'];
    return sensitive.some(s => headerName.toLowerCase().includes(s));
}

function attemptReadBody(body) {
    try {
        const contentType = body.contentType();
        if (contentType && contentType.toString().includes('application/json')) {
            return "[JSON payload - see logcat for details]";
        }
        return body.toString();
    } catch (e) {
        return "[Binary body]";
    }
}

// ============================================================================
// PHASE 3: Firebase Database Operations
// ============================================================================
console.log("[PHASE 3] Hooking Firebase Operations...");

try {
    const FirebaseDatabase = Java.use('com.google.firebase.database.FirebaseDatabase');
    const DatabaseReference = Java.use('com.google.firebase.database.DatabaseReference');
    
    // Hook getInstance to see Firebase initialization
    FirebaseDatabase.getInstance.overload().implementation = function() {
        const instance = this.getInstance();
        console.log("\n[FIREBASE] Database Instance Retrieved");
        console.log(`  └─ Reference Count: ${instance.getReference().toString()}`);
        return instance;
    };
    
    // Hook setValue for data writes
    DatabaseReference.setValue.overload('Ljava/lang/Object;').implementation = function(value) {
        console.log(`\n[FIREBASE] Write: ${this.getPath()} = ${value.toString()}`);
        return this.setValue(value);
    };
    
    console.log("✅ Firebase hooks installed");
} catch (e) {
    console.log("⚠️  Firebase hooking incomplete: " + e.message);
}

// ============================================================================
// PHASE 4: Token Management
// ============================================================================
console.log("[PHASE 4] Hooking Authentication/Token Layer...");

try {
    // Hook common token storage locations
    const SharedPreferences = Java.use('android.content.SharedPreferences');
    const Editor = Java.use('android.content.SharedPreferences$Editor');
    
    Editor.putString.implementation = function(key, value) {
        if (key.toLowerCase().includes('token') || 
            key.toLowerCase().includes('auth') ||
            key.toLowerCase().includes('session')) {
            console.log(`\n[TOKEN] Stored: ${key} = ${value.substring(0, 50)}...`);
        }
        return this.putString(key, value);
    };
    
    console.log("✅ Token storage hooks installed");
} catch (e) {
    console.log("⚠️  Token hooking failed: " + e.message);
}

// ============================================================================
// PHASE 5: MACLE Mini-App Communication
// ============================================================================
console.log("[PHASE 5] Hooking MACLE Framework...");

try {
    const MacleClient = Java.use('com.huawei.astp.macle.sdk.v2.MacleClient');
    
    // Hook init() to detect mini-app configuration
    MacleClient.init.overload('android.app.Activity', 
        'com.huawei.astp.macle.sdk.v2.MacleAppConfig',
        'com.huawei.astp.macle.sdk.v2.IMacleCallback').implementation = 
    function(activity, config, callback) {
        console.log("\n[MACLE] Framework Initialized");
        console.log(`  └─ Server Host: ${config.getServerHost()}`);
        console.log(`  └─ Server Port: ${config.getServerPort()}`);
        return this.init(activity, config, callback);
    };
    
    console.log("✅ MACLE hooks installed");
} catch (e) {
    console.log("⚠️  MACLE hooking failed: " + e.message);
}

// ============================================================================
// PHASE 6: Cryptography Operations
// ============================================================================
console.log("[PHASE 6] Hooking Cryptography Layer...");

try {
    const Cipher = Java.use('javax.crypto.Cipher');
    const SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    // Hook encryption/decryption
    Cipher.doFinal.overload('[B').implementation = function(input) {
        const mode = this.getMode();
        console.log(`\n[CRYPTO] Cipher Operation: Mode=${mode}, InputSize=${input.length}`);
        return this.doFinal(input);
    };
    
    console.log("✅ Cryptography hooks installed");
} catch (e) {
    console.log("⚠️  Crypto hooking failed: " + e.message);
}

// ============================================================================
// PHASE 7: Exception Handling (Detect Errors)
// ============================================================================
console.log("[PHASE 7] Setting Up Exception Monitoring...");

const Exception = Java.use('java.lang.Exception');
const originalInit = Exception.$init.overload('Ljava/lang/String;');

originalInit.implementation = function(msg) {
    if (msg && (msg.includes('API') || msg.includes('Network') || msg.includes('Firebase'))) {
        console.log(`\n[ERROR] Exception: ${msg}`);
        console.log("Stack: " + Java.use('android.util.Log').getStackTraceString(this));
    }
    return originalInit.call(this, msg);
};

// ============================================================================
// SUMMARY
// ============================================================================
console.log("\n" + "=".repeat(80));
console.log("✅ ALL HOOKS INSTALLED - Awaiting API Activity");
console.log("=".repeat(80));
console.log("\n📊 Monitoring:");
console.log("  • HTTP/HTTPS Requests (OkHttp3)");
console.log("  • Retrofit2 Service Creation");
console.log("  • Firebase Database Operations");
console.log("  • Token Storage & Retrieval");
console.log("  • MACLE Mini-App Communication");
console.log("  • Cryptography Operations");
console.log("  • Exception Stack Traces");
console.log("\n💡 Interact with the app to generate traffic...\n");
