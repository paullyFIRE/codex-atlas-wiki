#!/usr/bin/env bash
set -euo pipefail

# Full automated extraction pipeline
# Usage: ./scripts/extract.sh [version]
#   version: 1.0.7 (default)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APK_VERSION="${1:-1.0.7}"
APK_SRC="$ROOT_DIR/data/raw/_apk_source"

echo "=== 1. Download APK v$APK_VERSION ==="
apkeep -a "com.i89trillion.strategy.rising@$APK_VERSION" -d apk-pure "$APK_SRC/"

echo "=== 2. Extract XAPK ==="
unzip -q "$APK_SRC/com.i89trillion.strategy.rising@$APK_VERSION.xapk" \
  -d "$ROOT_DIR/data/raw/_apk_extracted/" 2>/dev/null

echo "=== 3. Decompile with apktool ==="
apktool d -f "$ROOT_DIR/data/raw/_apk_extracted/com.i89trillion.strategy.rising.apk" \
  -o "$ROOT_DIR/data/raw/_apk_decompiled_base/" 2>/dev/null
apktool d -f "$ROOT_DIR/data/raw/_apk_extracted/config.arm64_v8a.apk" \
  -o "$ROOT_DIR/data/raw/_apk_decompiled_config/" 2>/dev/null

echo "=== 4. Il2Cpp dump ==="
IL2CPP_DIR="$ROOT_DIR/data/raw/_il2cpp_output"
mkdir -p "$IL2CPP_DIR"
DOTNET_ROLL_FORWARD=LatestMajor ~/.dotnet/dotnet /tmp/il2cppdumper/Il2CppDumper.dll \
  "$ROOT_DIR/data/raw/_apk_decompiled_config/lib/arm64-v8a/libil2cpp.so" \
  "$ROOT_DIR/data/raw/_apk_decompiled_base/assets/bin/Data/Managed/Metadata/global-metadata.dat" \
  "$IL2CPP_DIR/" 2>/dev/null || true

echo "=== 5. Extract game configs and localization ==="
python3 "$ROOT_DIR/scripts/extract_all.py"

echo ""
echo "=== Extraction complete for v$APK_VERSION ==="
echo ""
echo "Next step (manual, requires GUI):"
echo "  /tmp/assetripper_extracted/AssetRipper.GUI.Free"
echo "  File > Load Folder > $ROOT_DIR/data/raw/_apk_extracted/"
echo "  Export > Unity Project > $ROOT_DIR/data/raw/unity/"
