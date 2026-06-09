"""Map unit IDs to game images — strict matching only.

Priority:
  1. {Name}_C.png — character portraits (verified correct names only)
  2. Card_{id}.png — card art by unit ID
  3. {id}.png — raw textures (model textures, may not be portraits)
"""

import json, os, shutil

IMG_SRC = 'data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/Texture2D'
IMG_AUTO = 'data/raw/_auto_extracted/Texture2D'
IMG_DST = 'public/images'
MAPPING_OUT = 'data/processed/unit_image_map.json'

BUILDING_IDS = {101, 104, 201, 203, 601, 3010, 3011, 3012, 3023, 3024, 3025, 3028, 3029, 3030, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3021, 3020, 3005, 3006, 3007, 3008, 3009, 3033, 3034, 3035, 3036, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3004, 3001, 3002, 3003, 3018, 3019, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3059}

NAMED_HEROES = {
    '30001': 'RomanEmperor_Caesar',
    '30002': 'KnightKing_Arthur',
    '30003': 'SpartanKing_Leonidas',
    '30004': 'NileQueen_Cleopatra',
}

def normalize(n):
    return n.lower().replace(' ', '').replace('-', '').replace("'", '').replace('.', '').replace('_', '')

def get_page_type(uid, unit):
    ut = unit.get('unit_type') or unit.get('unitType')
    if ut == 1: return 'heroes'
    if ut == 4: return 'hunting-bosses'
    if ut == 5: return 'buildings' if uid in BUILDING_IDS else 'special'
    if ut is None or ut == 0:
        if 2001 <= uid <= 2010: return 'followers'
        if uid in BUILDING_IDS: return 'buildings'
        return 'special'
    return 'special'

def build_mapping():
    os.makedirs(IMG_DST, exist_ok=True)

    name_map = json.load(open('data/processed/unit_name_map.json'))
    growth = json.load(open('data/processed/config/card_growth.json'))

    # Scan source directories
    c_map, card_map, num_map = {}, {}, {}

    for d in [IMG_SRC, IMG_AUTO]:
        if not os.path.isdir(d): continue
        for fn in os.listdir(d):
            if not fn.endswith('.png') or fn.startswith('.'): continue
            base = fn[:-4]
            if base.endswith('_C'):
                name_part = base[:-2]
                if name_part not in c_map or d == IMG_SRC:
                    c_map[name_part] = (d, fn)
            elif base.startswith('Card_') and base[5:].isdigit():
                uid = int(base[5:])
                if uid not in card_map or d == IMG_SRC:
                    card_map[uid] = (d, fn)
            elif base.isdigit():
                uid = int(base)
                if uid not in num_map or d == IMG_SRC:
                    num_map[uid] = (d, fn)

    # Add named hero overrides to c_map
    for uid_str, c_name in NAMED_HEROES.items():
        for d in [IMG_SRC, IMG_AUTO]:
            if not os.path.isdir(d): continue
            for fn in os.listdir(d):
                if fn.startswith(c_name) and fn.endswith('_C.png'):
                    c_map[c_name] = (d, fn)
                    break

    mapping = {}
    stats = {'portrait': 0, 'card': 0, 'texture': 0}

    def assign(key, src_dir, fn, stype):
        dst_fn = f'{key}.png'
        dst_path = os.path.join(IMG_DST, dst_fn)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(os.path.join(src_dir, fn), dst_path)
        mapping[key] = f'/images/{dst_fn}'
        stats[stype] += 1

    # Build normalized name lookup
    name_norms = {}
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        name = name_map.get(uid_str, '')
        if name:
            norm = normalize(name)
            if norm not in name_norms:
                name_norms[norm] = (uid, unit)

    # Pass 1: _C portrait by name
    for c_name, (d, fn) in c_map.items():
        c_norm = normalize(c_name)
        if c_norm in name_norms:
            uid, unit = name_norms[c_norm]
            pt = get_page_type(uid, unit)
            key = f'{pt}/{uid}'
            assign(key, d, fn, 'portrait')

    # Pass 2: card art by ID
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        pt = get_page_type(uid, unit)
        key = f'{pt}/{uid}'
        if key in mapping: continue
        if uid in card_map:
            d, fn = card_map[uid]
            assign(key, d, fn, 'card')

    # Pass 3: numeric texture by ID (last resort)
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        pt = get_page_type(uid, unit)
        key = f'{pt}/{uid}'
        if key in mapping: continue
        if uid in num_map:
            d, fn = num_map[uid]
            assign(key, d, fn, 'texture')

    # Named heroes
    for uid_str in NAMED_HEROES:
        key = f'heroes/{uid_str}'
        if key in mapping: continue
        uid = int(uid_str)
        if uid in card_map:
            d, fn = card_map[uid]
            assign(key, d, fn, 'card')
        elif uid in num_map:
            d, fn = num_map[uid]
            assign(key, d, fn, 'texture')

    print(f'Mapped {len(mapping)} unit IDs:')
    print(f'  {stats["portrait"]} character portraits (_C.png)')
    print(f'  {stats["card"]} card art (Card_*)')
    print(f'  {stats["texture"]} raw textures ({id}.png)')
    return mapping

if __name__ == '__main__':
    mapping = build_mapping()
    with open(MAPPING_OUT, 'w') as f:
        json.dump(mapping, f, indent=2)
