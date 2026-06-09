"""Map unit IDs to extracted game character portraits.

Only uses actual character art:
  1. {Name}_C.png — character portraits (square, 1024x1024)
  2. Card_{id}.png — card art from the unit collection UI
  (No raw {id}.png textures — those are model UV maps, not portraits)

Routing mirrors generate_pages.py:
  unitType=1 → heroes
  unitType=4 → hunting-bosses
  unitType=5 + BUILDING_IDS → buildings
  unitType=5 → special
  unitType=None → followers (2001-2010) / buildings (BUILDING_IDS) / special
"""

import json, os, shutil

IMG_SRC = 'data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/Texture2D'
IMG_AUTO = 'data/raw/_auto_extracted/Texture2D'
IMG_DST = 'public/images'
MAPPING_OUT = 'data/processed/unit_image_map.json'

# Same BUILDING_IDS as generate_pages.py
BUILDING_IDS = {101, 104, 201, 203, 601, 3010, 3011, 3012, 3023, 3024, 3025,
                3028, 3029, 3030, 3037, 3038, 3039, 3040, 3041, 3042, 3043,
                3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053,
                3054, 3055, 3056, 3057, 3058, 3021, 3020, 3005, 3006, 3007,
                3008, 3009}


def normalize(name):
    return name.lower().replace(' ', '').replace('-', '').replace("'", '').replace('.', '').replace('_', '')


def get_page_type(uid: int, unit: dict) -> str:
    ut = unit.get('unit_type') or unit.get('unitType')
    if ut == 1:
        return 'heroes'
    if ut == 4:
        return 'hunting-bosses'
    if ut == 5:
        return 'buildings' if uid in BUILDING_IDS else 'special'
    if ut is None or ut == 0:
        if 2001 <= uid <= 2010:
            return 'followers'
        if uid in BUILDING_IDS:
            return 'buildings'
        return 'special'
    return 'special'


def build_mapping():
    os.makedirs(IMG_DST, exist_ok=True)

    with open('data/processed/unit_name_map.json') as f:
        name_map = json.load(f)
    with open('data/processed/config/card_growth.json') as f:
        growth = json.load(f)

    # Scan for portrait files (_C) and card art (Card_*)
    c_norm_map = {}
    card_map = {}

    for d in [IMG_SRC, IMG_AUTO]:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith('.png') or fn.startswith('.'):
                continue
            base = fn[:-4]
            if base.endswith('_C'):
                name_part = base[:-2]
                norm = normalize(name_part)
                if norm not in c_norm_map or d == IMG_SRC:
                    c_norm_map[norm] = (d, fn)
            elif base.startswith('Card_') and base[5:].isdigit():
                card_map.setdefault(int(base[5:]), (d, fn))

    # Explicit overrides for named heroes with different _C filenames
    named_heroes = {
        '30001': 'RomanEmperor_Caesar',
        '30002': 'KnightKing_Arthur',
        '30003': 'SpartanKing_Leonidas',
        '30004': 'NileQueen_Cleopatra',
    }
    for uid_str, c_name in named_heroes.items():
        norm = normalize(c_name)
        for d in [IMG_SRC, IMG_AUTO]:
            if not os.path.isdir(d): continue
            for fn in os.listdir(d):
                if fn.startswith(c_name) and fn.endswith('_C.png'):
                    c_norm_map[norm] = (d, fn)
                    break

    # Build mapping
    mapping = {}
    stats = {'portrait': 0, 'card': 0}

    def assign(key, src_dir, fn, stype):
        dst_fn = f'{key}.png'
        dst_path = os.path.join(IMG_DST, dst_fn)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(os.path.join(src_dir, fn), dst_path)
        mapping[key] = f'/images/{dst_fn}'
        stats[stype] += 1

    # Pass 1: _C character portraits
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        name = name_map.get(uid_str, '')
        if not name:
            continue
        page_type = get_page_type(uid, unit)
        key = f'{page_type}/{uid}'
        norm = normalize(name)
        if norm in c_norm_map:
            d, fn = c_norm_map[norm]
            assign(key, d, fn, 'portrait')

    # Pass 2: card art for unmapped
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        page_type = get_page_type(uid, unit)
        key = f'{page_type}/{uid}'
        if key in mapping:
            continue
        if uid in card_map:
            d, fn = card_map[uid]
            assign(key, d, fn, 'card')

    # Handle named heroes (30001-30004) not in battleUnits
    for uid_str, c_name in named_heroes.items():
        key = f'heroes/{uid_str}'
        if key in mapping:
            continue
        # Check for _C portrait (already in c_norm_map)
        norm = normalize(c_name)
        if norm in c_norm_map:
            d, fn = c_norm_map[norm]
            assign(key, d, fn, 'portrait')
        elif int(uid_str) in card_map:
            d, fn = card_map[int(uid_str)]
            assign(key, d, fn, 'card')

    print(f'Mapped {len(mapping)} unit IDs (portraits only, no raw textures):')
    print(f'  {stats["portrait"]} character portraits (_C.png)')
    print(f'  {stats["card"]} card art (Card_*.png)')

    return mapping


if __name__ == '__main__':
    mapping = build_mapping()
    with open(MAPPING_OUT, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f'Images in {IMG_DST}/')
    print(f'Mapping saved to {MAPPING_OUT}')
