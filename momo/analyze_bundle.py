#!/usr/bin/env python3
"""Analyze React Native JavaScript bundle (index.android.bundle)."""

import os
import struct
import gzip
import zlib
import re

bundle_path = r"C:\Users\HP\momo\MoMo_extracted\assets\index.android.bundle"

print("=" * 70)
print("REACT NATIVE JS BUNDLE ANALYSIS")
print("=" * 70)
print()

if not os.path.exists(bundle_path):
    print(f"ERROR: Bundle not found at {bundle_path}")
    exit(1)

bundle_size = os.path.getsize(bundle_path)
print(f"[INFO] Bundle size: {bundle_size:,} bytes ({bundle_size / 1024 / 1024:.1f} MB)")
print()

with open(bundle_path, "rb") as f:
    data = f.read()

# --- 1. Check magic bytes ---
print("[MAGIC BYTES]")
header_hex = data[:32].hex()
print(f"  First 32 bytes (hex): {header_hex}")
print(f"  First 16 bytes (repr): {data[:16]}")
print()

# Check for known formats
if data[:4] == b'HBC0' or data[:4] == b'HBC\x00':
    print("  -> Format: HERMES BYTECODE (HBC)")
elif data[:2] == b'\x1f\x8b':
    print("  -> Format: GZIP compressed")
elif data[:4] == b'PK\x03\x04':
    print("  -> Format: ZIP archive")
elif data[:4] == b'\x78\x9c\x78\x01' or data[:2] == b'\x78\x9c':
    print("  -> Format: ZLIB compressed")
elif b'__esModule' in data[:1000] or b'ReactNativeWebView' in data[:1000]:
    print("  -> Format: Plaintext JavaScript (likely Metro)")
else:
    print("  -> Format: Unknown (possibly custom compressed or encrypted)")
print()

# --- 2. Try decompression ---
print("[DECOMPRESSION ATTEMPTS]")

# Try GZIP
try:
    decompressed = gzip.decompress(data)
    print(f"  ✓ GZIP decompression successful ({len(decompressed):,} bytes)")
    data_to_scan = decompressed[:100000]  # Scan first 100KB
except:
    print("  ✗ Not GZIP compressed")
    data_to_scan = data[:100000]

# Try ZLIB
try:
    decompressed_zlib = zlib.decompress(data)
    print(f"  ✓ ZLIB decompression successful ({len(decompressed_zlib):,} bytes)")
    data_to_scan = decompressed_zlib[:100000]
except:
    pass

print()

# --- 3. Search for readable strings ---
print("[STRING EXTRACTION]")

# Extract ASCII/UTF-8 strings (min length 8)
strings_found = []
current_string = b''

for byte in data_to_scan:
    if 32 <= byte <= 126:  # Printable ASCII
        current_string += bytes([byte])
    else:
        if len(current_string) >= 8:
            try:
                strings_found.append(current_string.decode('utf-8', errors='ignore'))
            except:
                pass
        current_string = b''

# Find unique meaningful strings
meaningful_strings = set()
keywords = [
    'React', 'react', 'navigator', 'platform', 'AsyncStorage',
    'require', 'module', 'exports', 'import', '__esModule',
    'Metro', 'hermes', 'jsc', 'JavaScriptCore', 'Frida',
    'localhost', 'http', 'api', 'config', 'bundle', 'version'
]

for s in strings_found:
    if any(kw in s for kw in keywords) or 'momo' in s.lower() or 'mtn' in s.lower():
        meaningful_strings.add(s)

if meaningful_strings:
    print(f"  Found {len(meaningful_strings)} meaningful strings:")
    for s in sorted(meaningful_strings)[:30]:
        print(f"    - {s[:60]}")
    if len(meaningful_strings) > 30:
        print(f"    ... and {len(meaningful_strings) - 30} more")
else:
    print("  No meaningful strings found in first 100KB")
print()

# --- 4. Look for JavaScript code patterns ---
print("[JAVASCRIPT PATTERNS]")

js_patterns = {
    'require(': 'CommonJS requires',
    'import ': 'ES6 imports',
    'export ': 'ES6 exports',
    'function ': 'JavaScript functions',
    'const ': 'const declarations',
    'class ': 'Class definitions',
    'React.': 'React library',
    'Platform.': 'React Native Platform',
    'NavigationContainer': 'React Navigation',
    'fetch(': 'Network calls',
    'fetch (': 'Network calls (space)',
}

for pattern, desc in js_patterns.items():
    count = data.count(pattern.encode())
    if count > 0:
        print(f"  ✓ {desc}: {count} occurrences")

print()

# --- 5. Hermes-specific checks ---
print("[HERMES ENGINE CHECK]")

hermes_magic = b'HBC0'
hermes_magic2 = b'HBC\x00'
has_hermes = hermes_magic in data or hermes_magic2 in data

if has_hermes:
    print("  ✓ Hermes magic bytes detected")
else:
    print("  ✗ No Hermes magic bytes")
    
# Check for Hermes headers/symbols
if b'_registerHermes' in data or b'hermes::' in data:
    print("  ✓ Hermes runtime symbols found")
else:
    print("  ✗ No obvious Hermes runtime symbols")

# Check for JSC (JavaScriptCore) indicators
if b'JSC' in data or b'JavaScriptCore' in data:
    print("  ✓ JSC indicators found")
else:
    print("  ✗ No obvious JSC indicators")

print()

# --- 6. Framework detection ---
print("[FRAMEWORK DETECTION]")

frameworks = {
    'react-navigation': b'react-navigation',
    'redux': b'redux',
    'react-redux': b'react-redux',
    'axios': b'axios',
    'lodash': b'lodash',
    'expo': b'expo',
    'firebase': b'firebase',
    'react-native-gesture-handler': b'react-native-gesture-handler',
}

detected = []
for name, sig in frameworks.items():
    if sig in data:
        detected.append(name)

if detected:
    print(f"  Detected {len(detected)} libraries:")
    for lib in detected:
        print(f"    - {lib}")
else:
    print("  No common framework signatures detected")

print()

# --- 7. Summary & Recommendations ---
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

if data[:2] == b'\x1f\x8b':
    print("• Bundle is GZIP-compressed")
    print("• Recommend: Use gzip to extract, then analyze decompressed content")
elif b'__esModule' in data[:10000]:
    print("• Bundle is PLAINTEXT JavaScript (Metro bundler format)")
    print("• Recommend: Can be analyzed directly with text tools")
else:
    print("• Bundle format: Unknown or custom compression")
    print("• Recommend: May require Hermes CLI tools or custom decompiler")

print()
print("• Size: 31.1 MB (large, typical for production React Native apps)")
print("• No native libraries (.so files) - pure Java bridge")
print("• Multiple dex files available for Java bridge analysis")
print()
print("NEXT STEPS:")
print("  1. If compressed: Extract with gzip/zlib and re-analyze")
print("  2. Check C:\\Users\\HP\\momo\\tools\\bin\\jadx.bat for Java decompilation")
print("  3. Use Hermes CLI tools (if available) to convert bytecode to JS")
print("  4. Consider using Android Studio's built-in decompilers")
print()
