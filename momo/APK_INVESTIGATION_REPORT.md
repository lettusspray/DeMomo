MoMo PSB APK Investigation Report
================================================================================
Date: May 10, 2026
APK: C:\Users\HP\momo\MoMo PSB.apk

================================================================================
EXECUTIVE SUMMARY
================================================================================

MoMo PSB is a production React Native application built for Android that provides
financial services (payment, transfers, balance checks) with modern mobile 
capabilities (camera, biometric, location).

Technology Stack:
- Framework: React Native (JSC engine)
- State Management: Redux
- Navigation: React Navigation
- Backend: Firebase
- Development: Expo (build tooling)
- Version: 1.21.1
- Minimum Android: API 26 (Android 8.0)
- Target Android: API 35 (Android 15)

================================================================================
APK METADATA
================================================================================

Package Name:       ng.mtn.android.psb.momo
Version Name:       1.21.1
Version Code:       104
Platform Build:     API 35 (Android 15)
Compile SDK:        35
Min SDK:            26 (Android 8.0)
Target SDK:         35 (Android 15)

Application Label:  MoMo PSB
Main Activity:      ng.mtn.android.momo.MainActivity
Icon:               res/mipmap-mdpi-v4/momo_psb.png

Code Modules:
- classes.dex (10.6 MB) - Java/Kotlin bridge layer
- classes2.dex (11.6 MB) - Extended Java/Kotlin code
- classes3.dex (4.1 MB) - Additional Java/Kotlin code
- Total compiled code: ~26.3 MB

================================================================================
PERMISSIONS (KEY ONES LISTED)
================================================================================

Financial/Personal:
- READ_PHONE_STATE / READ_PRIVILEGED_PHONE_STATE
- ACCESS_FINE_LOCATION / ACCESS_COARSE_LOCATION / ACCESS_BACKGROUND_LOCATION

Media & Sensors:
- CAMERA / RECORD_AUDIO / MODIFY_AUDIO_SETTINGS
- READ_MEDIA_AUDIO / WRITE_EXTERNAL_STORAGE

Biometric & Security:
- USE_BIOMETRIC / USE_FINGERPRINT

Connectivity:
- INTERNET / ACCESS_NETWORK_STATE / ACCESS_WIFI_STATE
- BLUETOOTH / BLUETOOTH_ADMIN / BLUETOOTH_SCAN / BLUETOOTH_CONNECT

Notifications & System:
- POST_NOTIFICATIONS / RECEIVE_BOOT_COMPLETED
- WAKE_LOCK / DOWNLOAD_WITHOUT_NOTIFICATION

Third-party Services:
- BIND_GET_INSTALL_REFERRER_SERVICE
- com.google.android.c2dm.permission.RECEIVE (Firebase Cloud Messaging)
- com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE
- com.samsung.android.mapsagent.permission.READ_APP_INFO
- com.huawei.appmarket.service.commondata.permission.GET_COMMON_DATA
- com.transsion.dataservice.permission.READ/WRITE

================================================================================
REACT NATIVE COMPONENTS
================================================================================

JavaScript Bundle:
- Path: assets/index.android.bundle
- Size: 31,148,152 bytes (29.7 MB)
- Engine: JavaScriptCore (JSC)
- Format: Metro bundler (custom compressed format)
- Compression: Not GZIP/ZLIB; uses app-level compression

Code Metrics:
- Functions: 578 declarations
- Constants: 605 declarations
- Classes: 13 class definitions
- React components: Multiple (37 React library references)
- React Navigation: 10 references (multi-screen app)
- Network calls: fetch-based API communication

Native Assets:
- No standalone .so files (pure Java/Kotlin bridge)
- Uses React Native built-in modules
- No Hermes bytecode engine

Assets:
- framework.zip (187 KB) - Firebase or other framework config
- index.android.bundle (31.1 MB) - JavaScript runtime
- term_condition.pdf (210 KB) - Terms and conditions

Libraries Detected:
✓ react-navigation - Screen routing and navigation
✓ redux - Centralized state management
✓ react-native-gesture-handler - Advanced gesture recognition
✓ lodash - Utility functions (array, object manipulation)
✓ firebase - Backend services (database, auth, messaging)
✓ expo - Build/development framework

================================================================================
ARCHITECTURE ANALYSIS
================================================================================

Application Architecture:
┌─────────────────────────────────────────┐
│  React Native JavaScript Layer (JSC)    │ <- 31 MB bundle
│  - Redux state management               │
│  - React Navigation routing             │
│  - Firebase integration                 │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│  Java/Kotlin Bridge Layer (26.3 MB)     │ <- 3 dex files
│  - Native module bindings               │
│  - Android system integrations          │
│  - Device capability access             │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│  Android Framework (SDK 35)             │
│  - Camera, Biometric, Location, Audio   │
│  - Bluetooth, Network, Notifications    │
└─────────────────────────────────────────┘

Design Pattern: Standard React Native single-threaded model
- JS execution on JavaScript thread (JSC)
- Bridge communication for native calls
- No Hermes performance optimization (uses slower JSC)

================================================================================
CAPABILITIES ASSESSMENT
================================================================================

Platform Detection:
✓ Detects Android platform (React.Native.Platform checks)
✓ Handles version-specific features (API level branching)

User Interface:
✓ Multi-screen navigation (React Navigation >= 2 screens)
✓ Redux state for navigation persistence
✓ Gesture-based interactions (react-native-gesture-handler)

Data & Connectivity:
✓ Network access (fetch patterns detected)
✓ Firebase integration (real-time database, authentication, messaging)
✓ Local storage capability (AsyncStorage implicit in RN)

Hardware Integration:
✓ Camera access (detected via permissions)
✓ Biometric/fingerprint (USE_BIOMETRIC permission)
✓ Location tracking (FINE + COARSE + BACKGROUND)
✓ Bluetooth connectivity (BLE + classic Bluetooth)
✓ Audio recording and playback

================================================================================
SECURITY OBSERVATIONS
================================================================================

Positive Signs:
✓ Target API 35 (latest, enforced modern security)
✓ Biometric support (modern security)
✓ Uses Firebase (managed security)
✓ Platform-specific permission checks (SDK detection)

Items Requiring Further Analysis (Java code level):
- SSL pinning implementation (JAX/decompilation needed)
- Data encryption at rest (requires Java code review)
- Credentials storage mechanism (requires Java code review)
- Obfuscation status (requires Proguard/R8 check via jadx)

Sensitive Permissions:
⚠ BACKGROUND_LOCATION - Always-on location tracking
⚠ RECORD_AUDIO - Microphone access
⚠ READ_PHONE_STATE - IMEI/phone info access
⚠ Bluetooth access - Device pairing capability

================================================================================
EXTRACTED ARTIFACTS
================================================================================

Location: C:\Users\HP\momo\MoMo_extracted\

Generated Analysis Tools:
- analyze_apk.py - APK structure and metadata analysis
- analyze_bundle.py - JavaScript bundle analysis

Decompilation Status:
❌ JADX decompilation: Blocked by Java runtime setup
   (JDK download had corruption; manual Java installation needed)
✓ APK extraction: Complete (tar-based extraction successful)
✓ Manifest analysis: Complete (aapt2 dump successful)
✓ JavaScript analysis: Complete (Python-based string/pattern matching)

================================================================================
RECOMMENDATIONS FOR FURTHER INVESTIGATION
================================================================================

1. Java Code Analysis (HIGH PRIORITY):
   - Install Java 11+ manually
   - Run: jadx -d MoMo_decompiled "MoMo PSB.apk"
   - Review: ng.mtn.android.momo.MainActivity entry point
   - Check: Firebase configuration, API endpoints, credential handling

2. Network Traffic Analysis:
   - Use Frida to intercept API calls
   - Capture Firebase endpoints and message formats
   - Identify data serialization format (JSON, Protocol Buffers, etc.)

3. JavaScript Bundle Reverse Engineering:
   - Extract Metro bundle metadata
   - Identify React Navigation screen names
   - Check Redux action types and state shape
   - Profile bundle size contributors

4. Runtime Behavior Analysis:
   - Deploy on Android device/emulator with adb
   - Use Frida for runtime function hooking
   - Monitor native bridge calls
   - Track user interaction flows

5. Firebase Integration Mapping:
   - Extract Firebase config (google-services.json via apktool)
   - Map Firestore collections and documents
   - Identify authentication mechanisms (Google, Phone, etc.)

================================================================================
TECHNICAL SPECIFICATIONS SUMMARY
================================================================================

Build Information:
- MinSdkVersion: 26
- TargetSdkVersion: 35
- CompileSdkVersion: 35
- PlatformBuildVersionCode: 35
- PlatformBuildVersionName: "15"

Dependencies (Major):
- androidx (46 libraries detected in META-INF)
- kotlin-stdlib
- kotlinx-coroutines
- google-material
- dagger (dependency injection)
- databinding / viewbinding

Deployment:
- APK size: ~62 MB total (estimated with resources)
- Dex count: 3 (multidex enabled)
- Dynamic delivery: Not detected
- App bundle: Not used (legacy APK format)

================================================================================
CONCLUSION
================================================================================

MoMo PSB is a well-structured React Native financial application using modern
tooling (Redux, React Navigation, Firebase). The app prioritizes financial
transaction features with appropriate permission requests for camera
(QR/barcode scanning), location (merchant nearby?), and biometric security.

The use of JavaScriptCore (instead of Hermes) suggests either:
1. Development phase (Expo build config)
2. Deliberate choice for JSC compatibility
3. Historical build artifact not yet migrated to Hermes

The 29.7 MB JavaScript bundle is typical for production RN apps with Redux
and multiple navigation screens. Full source code retrieval requires:
- Java decompilation (jadx) for native bridge inspection
- Metro bundle decompilation for JavaScript source recovery

Estimated effort for full source recovery: 4-6 hours with proper tooling.

================================================================================
Files Generated:
- C:\Users\HP\momo\analyze_apk.py
- C:\Users\HP\momo\analyze_bundle.py
- C:\Users\HP\momo\MoMo_extracted\ (APK contents)
- C:\Users\HP\momo\tools\bin\jadx.bat (ready for Java decompilation)

================================================================================
