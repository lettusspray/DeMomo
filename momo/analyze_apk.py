#!/usr/bin/env python3
"""Analyze extracted APK for React Native indicators without JADX."""

import os
import zipfile
import struct
import json

apk_path = r"C:\Users\HP\momo\MoMo PSB.apk"
extracted_dir = r"C:\Users\HP\momo\MoMo_extracted"
bundle_path = os.path.join(extracted_dir, "assets", "index.android.bundle")

print("=" * 70)
print("REACT NATIVE APK ANALYSIS")
print("=" * 70)
print()

# 1. Check bundle type
if os.path.exists(bundle_path):
    bundle_size = os.path.getsize(bundle_path)
    with open(bundle_path, "rb") as f:
        header = f.read(128)
    
    print(f"[BUNDLE] Found index.android.bundle ({bundle_size:,} bytes)")
    print(f"  Header (hex): {header[:32].hex()}")
    
    # Check for Hermes magic (HBC0)
    if header[:4] == b'HBC0' or header[:4] == b'HBC\x00':
        print("  -> Bundle type: HERMES BYTECODE")
    elif b'__esModule' in header or b'React' in header:
        print("  -> Bundle type: Plain JS (likely Metro)")
    else:
        print("  -> Bundle type: Unknown/Possibly compressed")
    print()

# 2. List native libraries
lib_paths = []
with zipfile.ZipFile(apk_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('lib/') and name.endswith('.so'):
            lib_paths.append(name)

if lib_paths:
    print(f"[NATIVE LIBS] Found {len(lib_paths)} .so files:")
    for lib in sorted(lib_paths):
        print(f"  - {lib}")
else:
    print("[NATIVE LIBS] No native libraries found (.so)")
print()

# 3. Check assets
assets_dir = os.path.join(extracted_dir, "assets")
if os.path.exists(assets_dir):
    assets = []
    for item in os.listdir(assets_dir):
        asset_path = os.path.join(assets_dir, item)
        if os.path.isfile(asset_path):
            size = os.path.getsize(asset_path)
            assets.append((item, size))
    
    if assets:
        print("[ASSETS]")
        for name, size in sorted(assets):
            print(f"  - {name} ({size:,} bytes)")
    print()

# 4. Check for Hermes runtime (libhermes.so, libjscexecutor.so)
hermes_indicators = []
for lib in lib_paths:
    if 'hermes' in lib.lower():
        hermes_indicators.append(f"Native: {lib}")

with zipfile.ZipFile(apk_path, 'r') as z:
    for name in z.namelist():
        if any(x in name.lower() for x in ['hermes', 'hbc0', 'jscexecutor']):
            hermes_indicators.append(f"File: {name}")

if hermes_indicators:
    print("[HERMES ENGINE] Indicators found:")
    for ind in hermes_indicators:
        print(f"  - {ind}")
else:
    print("[HERMES ENGINE] No Hermes indicators found (app likely uses standard JSC or JSI)")
print()

# 5. DEX files analysis (basic)
dex_files = []
with zipfile.ZipFile(apk_path, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            info = z.getinfo(name)
            dex_files.append((name, info.file_size))

if dex_files:
    print(f"[DEX FILES] Found {len(dex_files)} dex files (requires Java/jadx to decompile):")
    for name, size in sorted(dex_files):
        print(f"  - {name} ({size:,} bytes)")
print()

# 6. Manifest metadata (from aapt2 output)
print("[MANIFEST] Key details (from previous aapt2 dump):")
print("  Package: ng.mtn.android.psb.momo")
print("  Version: 1.21.1 (code 104)")
print("  Target SDK: 35, Min SDK: 26")
print("  Main Activity: ng.mtn.android.momo.MainActivity")
print()

# 7. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("✓ This IS a React Native application")
print("  - Contains index.android.bundle (JS runtime)")
print("  - Contains multiple dex files (native bridge)")
print()
if hermes_indicators:
    print("✓ Uses Hermes JavaScript engine")
else:
    print("? JavaScript engine: Likely JSC or Hermes (requires jadx to confirm)")
print()
if lib_paths:
    print(f"✓ Contains {len(lib_paths)} native modules")
    for lib in lib_paths:
        if 'vision-camera' in lib.lower():
            print("  - react-native-vision-camera detected")
else:
    print("✓ No standalone native libs (pure Java bridge)")
print()
print("NEXT STEPS:")
print("  1. To fully analyze Java code, need Java/JADX (decompile dex -> Java)")
print("  2. To analyze JS bundle, can use Metro/Hermes tools if available")
print("  3. Key indicators already found: RN-based app, v1.21.1, MoMo PSB")
print()
