#!/usr/bin/env bash
set -euo pipefail

# War Inc: Rising — APK extraction pipeline
# Usage: ./scripts/extract.sh [version]
#   version: 1.0.7 (default), or any version listed by apkeep -l

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data/raw"
APK_DIR="$DATA_DIR/_apk_source"
EXTRACTED_DIR="$DATA_DIR/_apk_extracted"
IL2CPP_DIR="$DATA_DIR/_il2cpp_output"
ASSETRIPPER_BIN="/tmp/assetripper_extracted/AssetRipper.GUI.Free"
DOTNET="$HOME/.dotnet/dotnet"
IL2CPPDUMPER="/tmp/il2cppdumper/Il2CppDumper.dll"
APK_VERSION="${1:-1.0.7}"

mkdir -p "$APK_DIR" "$EXTRACTED_DIR"

echo "=== Phase 1: Download APK v$APK_VERSION ==="
apkeep -a "com.i89trillion.strategy.rising@$APK_VERSION" -d apk-pure "$APK_DIR/"

echo "=== Phase 2: Extract XAPK ==="
unzip -q "$APK_DIR/com.i89trillion.strategy.rising@$APK_VERSION.xapk" -d "$EXTRACTED_DIR/"
ls -lh "$EXTRACTED_DIR/"

echo "=== Phase 3: Decompile APKs with apktool ==="
apktool d -f "$EXTRACTED_DIR/com.i89trillion.strategy.rising.apk" -o "$DATA_DIR/_apk_decompiled_base/" 2>/dev/null
apktool d -f "$EXTRACTED_DIR/config.arm64_v8a.apk" -o "$DATA_DIR/_apk_decompiled_config/" 2>/dev/null

echo "=== Phase 4: Il2Cpp dump ==="
mkdir -p "$IL2CPP_DIR"
DOTNET_ROLL_FORWARD=LatestMajor "$DOTNET" "$IL2CPPDUMPER" \
  "$DATA_DIR/_apk_decompiled_config/lib/arm64-v8a/libil2cpp.so" \
  "$DATA_DIR/_apk_decompiled_base/assets/bin/Data/Managed/Metadata/global-metadata.dat" \
  "$IL2CPP_DIR/" 2>/dev/null || true
echo "Il2Cpp DummyDlls in: $IL2CPP_DIR/DummyDll/"
echo "Dump in: $IL2CPP_DIR/dump.cs"

echo ""
echo "=== Phase 5: AssetRipper (manual browser step) ==="
echo "Run: $ASSETRIPPER_BIN --headless"
echo "Then open the URL in a browser and:"
echo "  1. File > Load Folder > $EXTRACTED_DIR"
echo "  2. Export > Export All Files > $DATA_DIR/_assetripper_export/"
echo ""

echo "=== Extraction complete for version $APK_VERSION ==="