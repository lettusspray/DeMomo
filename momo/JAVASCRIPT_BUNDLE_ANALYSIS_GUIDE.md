# JavaScript Bundle Analysis - MoMo PSB

## Overview

The MoMo PSB app's JavaScript logic (29.7 MB bundle at `assets/index.android.bundle`) contains:
- React components and screens
- Redux state management
- API call definitions
- Navigation routing
- Business logic

---

## Bundle Format Analysis

### Current Status
- **Format**: Metro Bundler (custom compressed)
- **Magic Bytes**: `c61fbc03c103191f...` (non-standard)
- **Compression**: App-level compression (not GZIP/ZLIB)
- **Engine**: JavaScriptCore (JSC), not Hermes

### Code Metrics (from previous analysis)
- Functions: 578 declarations
- Constants: 605 declarations
- Classes: 13 class definitions
- React library: 37 references
- React Navigation: 10 references
- Redux: Integration confirmed

---

## Method 1: Manual String Extraction (Current Approach)

### 1.1 High-Value Strings to Search

```powershell
# Search for API endpoints in bundle
$bundlePath = "C:\Users\HP\momo\MoMo_extracted\assets\index.android.bundle"

# Method: Binary file search for common patterns
$patterns = @(
    "/api/",
    "/v1/",
    "http",
    "https",
    "endpoint",
    "firebase",
    "collection",
    "action",
    "reducer",
    "selector"
)

foreach ($pattern in $patterns) {
    Write-Host "Searching for: $pattern"
    # Use binary search
    $found = Select-String -Path $bundlePath -Pattern $pattern -AllMatches | Select-Object -First 5
    $found | ForEach-Object { Write-Host "  $_" }
}
```

### 1.2 Expected Discoverable Artifacts

```
Redux Action Types:
- [auth/login]
- [auth/logout]
- [auth/refreshToken]
- [cards/fetchDetails]
- [cards/setPIN]
- [transactions/fetchList]

Screen Names (React Navigation):
- LoginScreen
- DashboardScreen
- CardsScreen
- TransactionsScreen
- SettingsScreen
- ProfileScreen

Redux State Keys:
- auth.token
- auth.user
- cards.details
- cards.pins
- transactions.list
- ui.loading
```

---

## Method 2: Metro Bundler Decompression

### 2.1 Identify Bundle Structure

Metro bundles have structure:
```
[Header Metadata]
[Main Module Factories]
[Async Module Chunks]
[Startup Code]
```

### 2.2 Python-based Decompression

```python
#!/usr/bin/env python3
"""
Metro Bundle Decompressor
Attempts to decompress and extract Metro-bundled JavaScript
"""

import struct
import sys
import os

class MetroBundleExtractor:
    def __init__(self, bundle_path):
        self.bundle_path = bundle_path
        self.data = open(bundle_path, 'rb').read()
        
    def analyze_header(self):
        """Analyze bundle header for compression info"""
        # Metro bundles typically start with magic bytes
        header = self.data[:16]
        print(f"Header (hex): {header.hex()}")
        print(f"Header (ascii): {header}")
        
        # Check for common compression markers
        if header.startswith(b'\x78\x9c'):  # ZLIB
            print("✓ ZLIB compressed")
        elif header.startswith(b'\x1f\x8b'):  # GZIP
            print("✓ GZIP compressed")
        elif header.startswith(b'c61fbc03'):  # Custom
            print("! Custom compression detected")
        else:
            print("? Unknown format")
    
    def extract_strings(self, min_length=4):
        """Extract readable strings from bundle"""
        strings = []
        current_string = b''
        
        for byte in self.data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += bytes([byte])
            else:
                if len(current_string) >= min_length:
                    try:
                        strings.append(current_string.decode('utf-8'))
                    except:
                        pass
                current_string = b''
        
        return strings
    
    def find_patterns(self):
        """Search for meaningful patterns"""
        patterns = {
            'API endpoints': [],
            'Redux actions': [],
            'Screen names': [],
            'Function names': []
        }
        
        strings = self.extract_strings(min_length=3)
        
        for s in strings:
            if s.startswith('/api') or s.startswith('/v'):
                patterns['API endpoints'].append(s)
            elif '_' in s and s.isupper():
                patterns['Redux actions'].append(s)
            elif 'Screen' in s or 'View' in s or 'Page' in s:
                patterns['Screen names'].append(s)
            elif s.startswith('_') and len(s) > 5:
                patterns['Function names'].append(s)
        
        return patterns
    
    def save_report(self, output_file='bundle_analysis.txt'):
        """Generate analysis report"""
        with open(output_file, 'w') as f:
            f.write("=== Metro Bundle Analysis ===\n\n")
            
            self.analyze_header()
            patterns = self.find_patterns()
            
            for category, items in patterns.items():
                f.write(f"\n{category}:\n")
                for item in set(items)[:20]:  # Top 20
                    f.write(f"  - {item}\n")

if __name__ == '__main__':
    bundle_path = r"C:\Users\HP\momo\MoMo_extracted\assets\index.android.bundle"
    extractor = MetroBundleExtractor(bundle_path)
    extractor.save_report()
    print("✓ Analysis complete: bundle_analysis.txt")
```

**Run it**:
```powershell
python bundle_extractor.py
```

---

## Method 3: React Navigation Route Extraction

### 3.1 Expected Navigation Structure

From code analysis, expect:
```
Stack Navigator:
  - LoginStack
    ├─ Login (phone/email entry)
    ├─ OTP Verification
    └─ Password Reset

AppStack:
  - Dashboard (tabs)
  - Cards
    ├─ Card Details
    ├─ Add Card
    ├─ Card Management
    └─ PIN Operations
  - Transactions
  - Mini-Apps
  - Profile
  - Settings
```

### 3.2 Extract from Decompiled Kotlin/Java

```java
// From MiniAppViewModule.java - MACLE integration
MacleClient.searchApplets(...)  // Fetch mini-app list
MacleClient.startApplet(...)    // Launch mini-app

// Expected React Navigation mapping
const navigation = {
  'Dashboard': <DashboardScreen />,
  'Cards': <CardsStack />,
  'Transactions': <TransactionHistoryScreen />,
  'Profile': <ProfileScreen />,
  'Settings': <SettingsScreen />
}
```

---

## Method 4: Redux Store Analysis

### 4.1 Expected Redux Structure

From Firebase integration and API patterns:

```javascript
// Initial State
{
  auth: {
    isAuthenticated: false,
    user: null,
    token: null,
    refreshToken: null,
    expiresAt: null
  },
  
  cards: {
    list: [],
    selectedCard: null,
    details: {},
    isLoading: false,
    error: null
  },
  
  transactions: {
    list: [],
    filters: { dateRange, type, status },
    pagination: { page, limit },
    isLoading: false,
    total: 0
  },
  
  miniApps: {
    categories: [],
    apps: [],
    favorites: [],
    isLoading: false
  },
  
  ui: {
    isLoading: false,
    notifications: [],
    modals: {}
  }
}
```

### 4.2 Action Types to Look For

```javascript
// Auth
AUTH_LOGIN
AUTH_LOGIN_SUCCESS
AUTH_LOGIN_FAILURE
AUTH_LOGOUT
AUTH_REFRESH_TOKEN

// Cards
FETCH_CARDS
FETCH_CARD_DETAILS
SET_PIN
VERIFY_PIN
CHANGE_PIN
VIEW_PIN

// Transactions
FETCH_TRANSACTIONS
FILTER_TRANSACTIONS
SEARCH_TRANSACTIONS
TRANSACTION_SUCCESS
TRANSACTION_FAILURE

// Mini-apps
FETCH_MINI_APP_CATEGORIES
FETCH_MINI_APPS
LAUNCH_MINI_APP
SET_MINI_APP_FAVORITE
```

---

## Method 5: API Call Integration Points

### 5.1 Search for API Service Layer

```javascript
// Expected pattern in bundle (look for these):
const apiService = {
  login: (credentials) => fetch(BASE_URL + '/auth/login', ...),
  getCards: () => fetch(BASE_URL + '/cards', ...),
  setPin: (cardId, pin) => fetch(BASE_URL + `/cards/${cardId}/pin`, ...),
  getTransactions: (filters) => fetch(...)
}

// Or using Axios/Fetch patterns:
axios.post('/api/auth/login', data)
axios.get('/api/cards')
fetch(`${API_BASE}/transactions?limit=20`)
```

### 5.2 Map JS API Calls to Java Layer

```
JavaScript Action
  → Redux Dispatch
  → Middleware intercepts
  → NativeModule call (MiniAppViewModule)
  → Java implementation
  → Retrofit service
  → OkHttp3 client
  → Network request
```

---

## Step-by-Step Bundle Analysis

### Step 1: Extract Readable Content

```powershell
# Use Python script from Method 2
python3 bundle_extractor.py
cat bundle_analysis.txt
```

### Step 2: Identify Key Patterns

From `bundle_analysis.txt`:
- ✓ API endpoints (if hardcoded)
- ✓ Redux action types
- ✓ Screen/component names
- ✓ Function names

### Step 3: Cross-Reference with Decompiled Java

Compare JS findings with Java:
```
JavaScript Redux Action: FETCH_CARDS
  ↓ Maps to
Native Module Call: cardService.getCards()
  ↓ Resolves to
Java Layer: NICardManagement.getCardDetails()
  ↓ Results in
API Call: POST /api/cards/details
```

### Step 4: Document Flow Diagram

Create mapping for each major feature:
```
Login Flow (JS to Java):
  LoginScreen component
    → Redux: auth/login action
    → Middleware: calls NativeModule
    → Java: AuthService.login(credentials)
    → Network: POST /v1/auth/login
    → Response: { token, user, expiresIn }
    → Redux: auth/loginSuccess
    → Navigation: to Dashboard
```

---

## Expected Discoveries

After bundle analysis, expect to find:

### 1. Complete API Endpoint List
```
POST   /auth/login
POST   /auth/refresh
GET    /cards
POST   /cards/{id}/pin
GET    /transactions
POST   /transactions/initiate
POST   /mini-apps/search
```

### 2. Redux Store Structure
- Exact state shape
- Selectors used
- Middleware hooks
- Error handling

### 3. Navigation Graph
- All screens
- Route parameters
- Tab/stack structure
- Modal handling

### 4. Third-party Integration
- Analytics events
- Firebase calls
- MACLE framework usage
- Error tracking

---

## Tools & Scripts

### bundle_extractor.py
- Analyze Metro bundle format
- Extract strings
- Identify patterns
- Generate report

### frida_bundle_interceptor.js (optional)
```javascript
// Hook into React Navigation to see screen transitions
const NavigationContainer = Java.use('com.facebook.react.bridge.NativeModule');
// Hook to log when screens change
```

---

## Troubleshooting Bundle Analysis

### Issue: Bundle too large to decompress
- Use Method 1 (string extraction) instead
- Search for specific patterns incrementally
- Focus on high-value strings first

### Issue: No readable strings found
- Bundle might be additional obfuscated
- Try binary search for null-terminated strings
- Look for UTF-16LE encoding

### Issue: Can't map JS to Java
- Use Frida to trace NativeModule calls
- Log what functions are called and with what arguments
- Cross-reference timestamps

---

## Output Format

Generate: **JAVASCRIPT_ANALYSIS_REPORT.md**

Contents:
1. Bundle Structure Analysis
2. Discovered API Endpoints
3. Redux State Diagram
4. Navigation Graph
5. Component/Screen List
6. API Call Flow Mappings
7. Third-party Integration Points
8. Recommendations for Next Phase

---

## Next Phase Trigger

When to move to Firebase Analysis:
- ✓ All API endpoints mapped
- ✓ Redux store structure understood
- ✓ Navigation flow documented
- ✓ Calling patterns established

When to move to Security Testing:
- ✓ Authentication flow verified
- ✓ Token management understood
- ✓ Data encryption validated
- ✓ API security assessed

---

**Status**: Bundle analysis methodology documented  
**Timeline**: 1-2 hours with automated extraction  
**Outcome**: Fully mapped JavaScript layer integration
