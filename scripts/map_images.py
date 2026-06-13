"""Map unit IDs to game images.

Priority:
  1. Official site portraits (21 mythic heroes) — highest quality
  2. Battleunit FBX renders (85+ heroes) — 512x512 character card art
  (APK textures are NOT used — they're sprite atlases, not portraits)
"""

import json, os, shutil, re

IMG_DST = 'public/images'
MAPPING_OUT = 'data/processed/unit_image_map.json'

OFFICIAL_SRC = 'public/images/official-site'
OFFICIAL_DST = 'public/images/heroes'

# Official site images: hero unit ID -> mythic filename
OFFICIAL_MAP = {
    637: 'mythic1',   # Gryphon Knight
    638: 'mythic2',   # Geomancer
    704: 'mythic3',   # Storm Maiden
    706: 'mythic4',   # Starlight Apostle
    739: 'mythic5',   # Fury Cannoneer
    744: 'mythic6',   # Flame Duelist
    749: 'mythic7',   # The Knight King
    846: 'mythic8',   # Blazeking
    845: 'mythic9',   # Tide Lord
    703: 'mythic10',  # Frost Queen
    708: 'mythic11',  # Darkmoon Queen
    734: 'mythic12',  # Nine-Tailed Fox
    762: 'mythic13',  # Radiant Warrior
    711: 'mythic14',  # Bone Marksman
    735: 'mythic15',  # Woodland Guardian
    847: 'mythic17',  # Red Blade
    736: 'mythic18',  # Melody Weaver
    738: 'mythic19',  # Ripple Wizard
    740: 'mythic20',  # Firepower Vanguard
    742: 'mythic21',  # Jungle Ranger
    743: 'mythic22',  # Barbarian Tyrant
}

# Battleunit FBX render directory
BATTLEUNIT_DIR = 'data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/artofwar-ii_art/fbx/battleunit'
BATTLEUNIT_UI_DIR = 'data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/artofwar-ii_art/fbx/battleunit_ui'


def build_mapping():
    os.makedirs(OFFICIAL_DST, exist_ok=True)
    mapping = {}
    
    # Pass 1: Official site images (highest priority)
    for uid, mythic_id in OFFICIAL_MAP.items():
        src = os.path.join(OFFICIAL_SRC, f'{mythic_id}.png')
        dst = os.path.join(OFFICIAL_DST, f'{uid}.png')
        if os.path.exists(src):
            shutil.copy2(src, dst)
            mapping[f'heroes/{uid}'] = f'/images/heroes/{uid}.png'
    
    # Pass 2: Battleunit FBX renders for remaining heroes
    for bu_root in [BATTLEUNIT_UI_DIR, BATTLEUNIT_DIR]:
        if not os.path.isdir(bu_root): continue
        for d in os.listdir(bu_root):
            full_d = os.path.join(bu_root, d)
            if not os.path.isdir(full_d): continue
            m = re.match(r'battleunit_(\d+)$', d)
            if not m: continue
            uid = int(m.group(1))
            key = f'heroes/{uid}'
            if key in mapping: continue  # Official image already set
            
            # Find the best _C.png in this directory (prefer shallow paths)
            best_fn = None
            best_depth = 99
            for root, dirs, files in os.walk(full_d):
                for fn in files:
                    if fn.endswith('_C.png') and not fn.startswith('.'):
                        rel_depth = len(os.path.relpath(os.path.join(root, fn), full_d).split(os.sep))
                        if rel_depth < best_depth:
                            best_fn = os.path.join(root, fn)
                            best_depth = rel_depth
            
            if best_fn:
                dst = os.path.join(OFFICIAL_DST, f'{uid}.png')
                shutil.copy2(best_fn, dst)
                mapping[key] = f'/images/heroes/{uid}.png'
    
    print(f'Mapped {len(mapping)} hero portraits:')
    official = sum(1 for k in mapping if k.split('/')[1] in OFFICIAL_MAP)
    battleunit = len(mapping) - official
    print(f'  {official} official site portraits (best quality)')
    print(f'  {battleunit} battleunit FBX renders')
    
    return mapping


if __name__ == '__main__':
    mapping = build_mapping()
    with open(MAPPING_OUT, 'w') as f:
        json.dump(mapping, f, indent=2)
