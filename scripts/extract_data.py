#!/usr/bin/env python3
"""
Extract game data from War Inc: Rising Unity assets using UnityPy.
"""
import UnityPy
import json
import sys
import os
from pathlib import Path

APK_DIR = Path("data/raw/_apk_extracted")
OUTPUT_DIR = Path("data/raw/_assetripper_export")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Extract the Unity assets from the APK
print("=== Extracting Unity assets ===")

# UnityDataAssetPack.apk is actually a zip containing Unity serialized files
# Let's point UnityPy to the extracted assets directory
assets_dir = Path("data/raw/_apk_decompiled_assets/assets")

# Instead of loading the whole APK, try loading individual files
all_assets = {}
file_count = 0
mono_count = 0
text_count = 0

for f in sorted(assets_dir.rglob("*")):
    if f.is_file() and f.stat().st_size > 100:
        try:
            env = UnityPy.load(str(f))
            file_count += 1
            for path, obj in env.container.items():
                all_assets[path] = obj
                if obj.type.name == "MonoBehaviour":
                    mono_count += 1
                elif obj.type.name == "TextAsset":
                    text_count += 1
        except Exception as e:
            pass  # Not a Unity file or unsupported format

print(f"Processed {file_count} files")
print(f"Found {len(all_assets)} assets ({mono_count} MonoBehaviour, {text_count} TextAsset)")

# Save TextAssets (JSON, CSV, etc.)
print("\n=== Extracting TextAssets ===")
text_dir = OUTPUT_DIR / "TextAssets"
text_dir.mkdir(exist_ok=True)

for path, obj in all_assets.items():
    if obj.type.name == "TextAsset":
        try:
            data = obj.read()
            name = data.m_Name or path.split("/")[-1].split(".")[0]
            fname = f"{name}.txt"
            with open(text_dir / fname, "wb") as fp:
                fp.write(data.m_Script)
            print(f"  {fname} ({len(data.m_Script)} bytes)")
        except Exception as e:
            print(f"  Error reading {path}: {e}")

# Try to read MonoBehaviour objects (ScriptableObjects with game data)
print("\n=== Extracting MonoBehaviour (ScriptableObjects) ===")
mono_dir = OUTPUT_DIR / "MonoBehaviour"
mono_dir.mkdir(exist_ok=True)

sample_count = 0
for path, obj in list(all_assets.items()):
    if obj.type.name == "MonoBehaviour" and sample_count < 50:
        try:
            data = obj.read()
            name = data.m_Name or f"type_{data.type_id}"
            fname = f"{name}.json" if name else f"unknown_{sample_count}.json"
            
            # Try to get the serialized data
            node = data.save()  # Returns a dict-like structure
            if node:
                with open(mono_dir / fname, "w") as fp:
                    json.dump(node, fp, indent=2, default=str)
                print(f"  {fname}")
                sample_count += 1
        except Exception as e:
            pass

if sample_count == 0:
    print("  No MonoBehaviour assets could be read directly.")
    print("  The data is in Il2Cpp serialized format and needs type info.")

# Save asset inventory
print("\n=== Asset Inventory ===")
inventory = {}
for path, obj in all_assets.items():
    t = obj.type.name
    if t not in inventory:
        inventory[t] = []
    inventory[t].append(path)

for t, paths in sorted(inventory.items()):
    print(f"  {t}: {len(paths)} assets")

with open(OUTPUT_DIR / "asset_inventory.json", "w") as fp:
    json.dump(inventory, fp, indent=2, default=str)

print(f"\nOutput directory: {OUTPUT_DIR}")
print("Done!")
