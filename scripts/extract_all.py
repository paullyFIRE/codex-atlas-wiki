#!/usr/bin/env python3
"""
Automated extraction of War Inc: Rising game data.
Runs everything that doesn't require the AssetRipper GUI.
"""
import json, os, zipfile, io, csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
OUT = ROOT / "data/processed"
os.makedirs(OUT / "config", exist_ok=True)
os.makedirs(OUT / "localization", exist_ok=True)

def extract_config_json():
    """Extract JSON configs from battle_pack_bundle/Common/Config/"""
    config_dir = RAW / "_battle_bundle" / "Common" / "Config"
    if not config_dir.exists():
        print("[SKIP] Config dir not found (extract battle_pack_bundle.zip first)")
        return
    count = 0
    for f in sorted(config_dir.iterdir()):
        if not f.is_file(): continue
        with open(f, 'rb') as fp:
            raw = fp.read()
        start = raw.find(b'{')
        end = raw.rfind(b'}')
        if start < 0 or end <= start: continue
        try:
            data = json.loads(raw[start:end+1])
            # Extract config name from file (before first double-underscore or hash)
            parts = f.name.rsplit('_', 1)[0]  # Remove hash
            name = parts.split('_')[0] if '_' in parts else parts
            # Map file names to clean config names
            name_map = [
                ('battle_conf_lib', 'battle_conf_lib'),
                ('battle_synergy_config', 'battle_synergy'),
                ('battle_config', 'battle_config'),
                ('card_growth_config', 'card_growth'),
                ('equip_battle_config', 'equip_battle'),
                ('field_buff_config', 'field_buff'),
                ('lay_map_lib', 'lay_map_lib'),
                ('layout_strategy_config', 'layout_strategy'),
            ]
            name = f.name
            for key, val in name_map:
                if name.startswith(key):
                    name = val; break
            else:
                name = name.split('_')[0]
            out_path = OUT / "config" / f"{name}.json"
            with open(out_path, 'w') as out:
                json.dump(data, out, indent=2)
            count += 1
            print(f"  ✓ {name}.json ({len(data)} keys)")
        except json.JSONDecodeError:
            print(f"  ✗ {f.name}: JSON parse error")
    print(f"  Configs extracted: {count}")

def extract_localization():
    """Extract localization CSV files from language_conf AssetBundle ZIP"""
    bundles_dir = RAW / "_apk_decompiled_assets" / "assets" / "Bundles"
    if not bundles_dir.exists():
        print("[SKIP] Bundles dir not found")
        return
    lang_bundle = None
    for f in bundles_dir.iterdir():
        if "language_conf" in f.name:
            lang_bundle = f; break
    if not lang_bundle:
        print("[SKIP] Language bundle not found")
        return
    with open(lang_bundle, 'rb') as fp:
        raw = fp.read()
    zip_start = raw.find(b'PK\x03\x04')
    if zip_start < 0:
        print("[ERROR] ZIP signature not found in language bundle")
        return
    count = 0
    with io.BytesIO(raw[zip_start:]) as bio:
        with zipfile.ZipFile(bio) as zf:
            for name in zf.namelist():
                if name.endswith('.csv'):
                    data = zf.read(name)
                    with open(OUT / "localization" / name, 'wb') as out:
                        out.write(data)
                    count += 1
                    lines = data.decode('utf-8-sig', errors='replace').count('\n')
                    print(f"  ✓ {name} ({lines} lines)")
    # Generate name maps from English CSV
    en_path = OUT / "localization" / "en.csv"
    if en_path.exists():
        unit_names = {}
        hero_names = {}
        with open(en_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if not row: continue
                key, val = row[0], row[1] if len(row) > 1 else ''
                if key.startswith('unit_name_') and val:
                    uid = key.replace('unit_name_', '')
                    if uid.isdigit(): unit_names[int(uid)] = val
                elif key.startswith('hero_name_') and not key.startswith('hero_name_abbr_') and val:
                    hid = key.replace('hero_name_', '')
                    if hid.isdigit(): hero_names[int(hid)] = val
        with open(OUT / "unit_name_map.json", 'w') as f:
            json.dump(unit_names, f, indent=2)
        with open(OUT / "hero_name_map.json", 'w') as f:
            json.dump(hero_names, f, indent=2)
        print(f"  Name maps: {len(unit_names)} units, {len(hero_names)} heroes")
    print(f"  Localization CSVs: {count}")

def extract_unity_assets():
    """Extract assets via UnityPy from ALL Unity asset directories"""
    try:
        import UnityPy
    except ImportError:
        print("[SKIP] UnityPy not installed (pip install UnityPy)")
        return

    # Scan multiple directories for Unity assets
    scan_dirs = [
        RAW / "_apk_decompiled_assets" / "assets" / "bin" / "Data",
        RAW / "_apk_decompiled_assets" / "assets" / "Bundles",
        RAW / "_apk_decompiled_assets" / "assets" / "embeddedpackages",
    ]
    
    found = False
    for d in scan_dirs:
        if d.exists():
            found = True
            break
    if not found:
        print("[SKIP] No Unity asset directories found")
        return

    out_dir = ROOT / "data/raw/_auto_extracted"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    text_dir = out_dir / "TextAssets"
    tex_dir = out_dir / "Texture2D"
    sprite_dir = out_dir / "Sprite"
    text_dir.mkdir(exist_ok=True)
    tex_dir.mkdir(exist_ok=True)
    sprite_dir.mkdir(exist_ok=True)

    text_count = tex_count = sprite_count = 0
    file_count = 0

    for scan_dir in scan_dirs:
        if not scan_dir.exists(): continue
        for f in sorted(scan_dir.rglob("*")):
            if not f.is_file() or f.stat().st_size < 200: continue
            try:
                env = UnityPy.load(str(f))
                file_count += 1
            except: continue
            for path, obj in env.container.items():
                try:
                    if obj.type.name == "TextAsset":
                        data = obj.read()
                        script = data.m_Script
                        if script:
                            name = data.m_Name or f"text_{text_count}"
                            fname = re.sub(r'[\\/*?:"<>|]', '_', name)
                            with open(text_dir / f"{fname}.txt", 'wb') as fp:
                                fp.write(script if isinstance(script, bytes) else script.encode())
                            text_count += 1
                    elif obj.type.name == "Texture2D":
                        try:
                            data = obj.read()
                            img = data.image
                            if img:
                                name = data.m_Name or f"tex_{tex_count}"
                                fname = re.sub(r'[\\/*?:"<>|]', '_', name)
                                img.save(tex_dir / f"{fname}.png")
                                tex_count += 1
                        except: pass
                    elif obj.type.name == "Sprite":
                        try:
                            data = obj.read()
                            img = data.image
                            if img:
                                name = data.m_Name or f"sprite_{sprite_count}"
                                fname = re.sub(r'[\\/*?:"<>|]', '_', name)
                                img.save(sprite_dir / f"{fname}.png")
                                sprite_count += 1
                        except: pass
                except: pass

    print(f"  Files processed: {file_count}")
    print(f"  TextAssets: {text_count}")
    print(f"  Texture2D: {tex_count}")
    print(f"  Sprites: {sprite_count}")

def extract_other_bundles():
    """Extract JSON configs from Unity AssetBundles"""
    bundles_dir = RAW / "_apk_decompiled_assets" / "assets" / "Bundles"
    if not bundles_dir.exists(): return
    targets = ['card_show', 'cardattr', 'avatar_config']
    for f in bundles_dir.iterdir():
        for kw in targets:
            if kw not in f.name: continue
            with open(f, 'rb') as fp:
                raw = fp.read()
            start = raw.find(b'{')
            end = raw.rfind(b'}')
            if start < 0 or end <= start: break
            try:
                data = json.loads(raw[start:end+1])
                out_name = kw.replace('cardattr', 'card_attr').replace('avatar_config', 'avatar')
                out_path = OUT / "config" / f"{out_name}_config.json"
                with open(out_path, 'w') as fp:
                    json.dump(data, fp, indent=2)
                print(f"  ✓ {out_name}_config.json")
            except: pass
            break

if __name__ == "__main__":
    print("=" * 50)
    print("War Inc: Rising - Automated Extraction")
    print("=" * 50)
    
    print("\n1. Extracting config JSONs...")
    extract_config_json()
    
    print("\n2. Extracting localization CSVs...")
    extract_localization()
    
    print("\n3. Extracting Unity assets...")
    extract_unity_assets()
    
    print("\n4. Extracting other bundle configs...")
    extract_other_bundles()
    
    print("\n" + "=" * 50)
    print("Done! Run './scripts/extract.sh' for Il2Cpp dump.")
    print("AssetRipper GUI still needed for: full MonoBehaviour resolution.")
    print("=" * 50)
