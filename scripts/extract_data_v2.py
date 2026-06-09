#!/usr/bin/env python3
"""
Improved extraction of War Inc: Rising game data.
"""
import UnityPy
import json
import os
from pathlib import Path

APK_DIR = Path("data/raw/_apk_extracted")
ASSETS_DIR = Path("data/raw/_apk_decompiled_assets/assets")
OUTPUT_DIR = Path("data/raw/_extracted_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Try different loading strategies
print("=== Strategy 1: Load individual files ===")
for f in sorted(ASSETS_DIR.rglob("*"))[:5]:
    if f.is_file() and f.stat().st_size > 1000:
        print(f"Trying: {f} ({f.stat().st_size} bytes)")
        try:
            env = UnityPy.load(str(f))
            for path, obj in env.container.items():
                print(f"  Asset: {path} (type: {obj.type.name})")
                
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    print(f"    Name: {data.m_Name}, Script length: {len(data.m_Script) if data.m_Script else 0}")
                    print(f"    Script bytes: {data.m_Script[:100] if data.m_Script else 'empty'}")
                elif obj.type.name == "MonoBehaviour":
                    data = obj.read()
                    print(f"    Name: {data.m_Name}, Type: {data.type_id}")
                    try:
                        tree = data.save()
                        print(f"    Tree keys: {list(tree.keys()) if tree else 'empty'}")
                    except Exception as e2:
                        print(f"    Error reading tree: {e2}")
        except Exception as e:
            print(f"  Error: {e}")

print("\n=== Strategy 2: Try loading from Assets directly ===")
# Unity assets are in specific asset files in the Data directory
data_dir = ASSETS_DIR / "bin" / "Data"
if data_dir.exists():
    for f in sorted(data_dir.iterdir())[:10]:
        print(f"File: {f.name} ({f.stat().st_size} bytes)")
        try:
            env = UnityPy.load(str(f))
            for path, obj in env.container.items():
                print(f"  Loaded: {path} ({obj.type.name})")
        except Exception as e:
            print(f"  Error: {e}")

print("\n=== Strategy 3: Try raw BytesAsset / TextAsset with different reader ===")
# Some Unity versions store text differently
for f in sorted(data_dir.iterdir())[:5]:
    if f.stat().st_size < 50000:
        continue
    try:
        env = UnityPy.load(str(f))
        for path, obj in env.container.items():
            if obj.type.name in ("TextAsset", "BytesAsset"):
                # Try reading via serialized data
                try:
                    raw = obj.read_raw()
                    print(f"  Raw {f.name}/{path}: {len(raw)} bytes")
                    if raw:
                        print(f"    First 200: {raw[:200]}")
                except:
                    pass
                    
                try:
                    # Try the standard read
                    data = obj.read()
                    name = getattr(data, 'm_Name', '?')
                    print(f"    Standard: name={name}, script={len(data.m_Script) if getattr(data, 'm_Script', None) else 'N/A'}")
                except Exception as e2:
                    print(f"    Standard error: {e2}")
    except Exception as e:
        pass
    break  # Just check one file

print("\nDone!")
