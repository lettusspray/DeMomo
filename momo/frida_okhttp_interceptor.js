/**
 * Frida OkHttp3 Interceptor Script
 * Purpose: Capture all HTTP requests/responses from MoMo PSB app
 * Usage: frida -U -f ng.mtn.android.psb.momo -l frida_okhttp_interceptor.js
 * 
 * Hooks into:
 * - okhttp3.Request (URL, headers, body)
 * - okhttp3.Response (status, headers, body)
 * - retrofit2.ServiceMethod (endpoint detection)
 */

console.log("🔍 Starting OkHttp3 Interceptor for MoMo PSB...\n");

// Hook okhttp3.OkHttpClient to intercept all HTTP calls
const OkHttpClient = Java.use('okhttp3.OkHttpClient');
const Request = Java.use('okhttp3.Request');
const Response = Java.use('okhttp3.Response');
const RealCall = Java.use('okhttp3.RealCall');
const HttpUrl = Java.use('okhttp3.HttpUrl');

// Counter for tracking requests
let requestCounter = 0;

// Hook RealCall.execute() to intercept synchronous calls
RealCall.execute.implementation = function() {
    const request = this.request();
    logRequest(request);
    
    try {
        const response = this.execute(); // Call original
        logResponse(response);
        return response;
    } catch (e) {
        console.log("[ERROR] " + e);
        throw e;
    }
};

// Hook RealCall.enqueue() for async calls
RealCall.enqueue.implementation = function(callback) {
    const request = this.request();
    logRequest(request);
    
    // Wrap callback to log response
    const wrappedCallback = Java.use('okhttp3.Callback').$new(Java.use('java.lang.Object'));
    
    return this.enqueue(callback);
};

// Hook Retrofit's ServiceMethod.invoke to detect endpoint names
try {
    const ServiceMethod = Java.use('retrofit2.ServiceMethod');
    const HttpServiceMethod = Java.use('retrofit2.HttpServiceMethod');
    
    if (HttpServiceMethod) {
        HttpServiceMethod.invoke.overload('[Ljava/lang/Object;').implementation = function(args) {
            const methodName = this.toString();
            console.log(`[RETROFIT] Endpoint: ${methodName}`);
            return this.invoke(args);
        };
    }
} catch (e) {
    console.log("[INFO] Retrofit hook unavailable (may be obfuscated)");
}

// Hook Firebase Crashlytics to detect crash reporting
try {
    const FirebaseCrashlytics = Java.use('com.google.firebase.crashlytics.FirebaseCrashlytics');
    FirebaseCrashlytics.recordException.implementation = function(exception) {
        console.log("[FIREBASE] Crash logged: " + exception.toString());
        return this.recordException(exception);
    };
} catch (e) {
    console.log("[INFO] Firebase Crashlytics hook unavailable");
}

// Main request logging function
function logRequest(request) {
    requestCounter++;
    const url = request.url().toString();
    const method = request.method();
    const headers = request.headers();
    
    console.log("\n" + "=".repeat(80));
    console.log(`[REQUEST #${requestCounter}] ${method} ${url}`);
    console.log("=".repeat(80));
    
    // Log headers
    console.log("[HEADERS]");
    const headerCount = headers.size();
    for (let i = 0; i < headerCount; i++) {
        const name = headers.name(i);
        const value = headers.value(i);
        // Redact sensitive headers
        const displayValue = (name.toLowerCase().includes('token') || 
                             name.toLowerCase().includes('authorization') ||
                             name.toLowerCase().includes('password')) 
                            ? "[REDACTED]" 
                            : value;
        console.log(`  ${name}: ${displayValue}`);
    }
    
    // Log body
    try {
        const body = request.body();
        if (body !== null) {
            console.log("[BODY]");
            const bodyStr = readBody(body);
            console.log("  " + bodyStr.substring(0, 500)); // First 500 chars
            if (bodyStr.length > 500) console.log("  ... [truncated]");
        }
    } catch (e) {
        console.log("[BODY] Unable to read: " + e.message);
    }
}

// Response logging function
function logResponse(response) {
    const code = response.code();
    const message = response.message();
    const headers = response.headers();
    
    console.log("\n[RESPONSE] Status: " + code + " " + message);
    console.log("[RESPONSE HEADERS]");
    
    const headerCount = headers.size();
    for (let i = 0; i < headerCount; i++) {
        const name = headers.name(i);
        const value = headers.value(i);
        console.log(`  ${name}: ${value}`);
    }
    
    // Log response body
    try {
        const body = response.body();
        if (body !== null) {
            console.log("[RESPONSE BODY]");
            const bodyStr = readResponseBody(body);
            console.log("  " + bodyStr.substring(0, 500));
            if (bodyStr.length > 500) console.log("  ... [truncated]");
        }
    } catch (e) {
        console.log("[RESPONSE BODY] Unable to read: " + e.message);
    }
}

// Utility to read request body
function readBody(body) {
    try {
        const FormBody = Java.use('okhttp3.FormBody');
        const MultipartBody = Java.use('okhttp3.MultipartBody');
        const RequestBody = Java.use('okhttp3.RequestBody');
        
        if (body.$className === 'okhttp3.FormBody') {
            let params = "";
            const formBody = Java.cast(body, FormBody);
            for (let i = 0; i < formBody.size(); i++) {
                params += formBody.name(i) + "=" + formBody.value(i) + "&";
            }
            return params.slice(0, -1);
        } else {
            // For other body types, try to get content
            const contentType = body.contentType();
            if (contentType && contentType.toString().includes("application/json")) {
                // Attempt to read as buffer (limited approach)
                return "[JSON Body - use runtime inspection]";
            }
            return "[Binary/Other Body Type]";
        }
    } catch (e) {
        return "[Unable to parse body]";
    }
}

// Utility to read response body
function readResponseBody(responseBody) {
    try {
        // ResponseBody is typically consumed once, so we can't read it directly
        return "[Response Body - implement streaming capture for full content]";
    } catch (e) {
        return "[Unable to read response]";
    }
}

console.log("✅ OkHttp3 Interceptor loaded!");
console.log("📱 Awaiting app requests...\n");
