"""Map unit IDs to extracted game images and copy to public/images/"""

import json, os, shutil

IMG_SRC = 'data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/Texture2D'
IMG_AUTO = 'data/raw/_auto_extracted/Texture2D'
IMG_DST = 'public/images'
MAPPING_OUT = 'data/processed/unit_image_map.json'


def normalize(name):
    return name.lower().replace(' ', '').replace('-', '').replace("'", '').replace('.', '').replace('_', '')


def build_mapping():
    os.makedirs(IMG_DST, exist_ok=True)

    # Load unit names
    with open('data/processed/unit_name_map.json') as f:
        name_map = json.load(f)

    with open('data/processed/config/card_growth.json') as f:
        growth = json.load(f)

    # Scan source directories
    numeric_map = {}
    card_map = {}
    c_map = {}
    c_auto_map = {}

    if os.path.isdir(IMG_SRC):
        for fn in os.listdir(IMG_SRC):
            if not fn.endswith('.png') or fn.startswith('.'):
                continue
            base = fn[:-4]
            if base.isdigit():
                numeric_map[int(base)] = (IMG_SRC, fn)
            elif base.startswith('Card_') and base[5:].isdigit():
                card_map[int(base[5:])] = (IMG_SRC, fn)
            elif base.endswith('_C'):
                c_map[base[:-2]] = (IMG_SRC, fn)

    if os.path.isdir(IMG_AUTO):
        for fn in os.listdir(IMG_AUTO):
            if not fn.endswith('_C.png') or fn.startswith('.'):
                continue
            base = fn[:-6]
            if base not in c_map:
                c_auto_map[base] = (IMG_AUTO, fn)

    # Build mapping for all battle units
    mapping = {}
    for uid_str, unit in growth['battleUnits'].items():
        uid = int(uid_str)
        name = name_map.get(uid_str, '')
        key = f'heroes/{uid}' if unit.get('unitType') == 1 else \
              f'buildings/{uid}' if unit.get('unitType') == 4 else \
              f'special/{uid}'

        # Priority 1: numeric filename
        if uid in numeric_map:
            src_dir, fn = numeric_map[uid]
            copy_and_assign(mapping, key, src_dir, fn)
            continue

        # Priority 2: Card_{id}.png
        if uid in card_map:
            src_dir, fn = card_map[uid]
            copy_and_assign(mapping, key, src_dir, fn)
            continue

        # Priority 3: {NormalizedName}_C.png
        if name:
            norm = normalize(name)
            for cname, (src_dir, fn) in c_map.items():
                if normalize(cname) == norm:
                    copy_and_assign(mapping, key, src_dir, fn)
                    break
            else:
                # Try auto_extracted
                for cname, (src_dir, fn) in c_auto_map.items():
                    if normalize(cname) == norm:
                        copy_and_assign(mapping, key, src_dir, fn)
                        break

    # Handle named heroes (30001-30004) with special _C filenames
    named_hero_c = {
        '30001': 'RomanEmperor_Caesar',
        '30002': 'KnightKing_Arthur',
        '30003': 'SpartanKing_Leonidas',
        '30004': 'NileQueen_Cleopatra',
    }
    for uid_str, c_name in named_hero_c.items():
        key = f'heroes/{uid_str}'
        if key not in mapping:
            # Check both dirs
            for src_dir in [IMG_SRC, IMG_AUTO]:
                if os.path.isdir(src_dir):
                    for fn in os.listdir(src_dir):
                        if not fn.endswith('.png') or fn.startswith('.'):
                            continue
                        if fn.startswith(c_name) and fn.endswith('_C.png'):
                            copy_and_assign(mapping, key, src_dir, fn)
                            break
                    if key in mapping:
                        break

    return mapping


def copy_and_assign(mapping, key, src_dir, fn):
    dst_fn = f'{key}.png'
    dst_path = os.path.join(IMG_DST, dst_fn)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(os.path.join(src_dir, fn), dst_path)
    mapping[key] = f'/images/{dst_fn}'


if __name__ == '__main__':
    mapping = build_mapping()
    with open(MAPPING_OUT, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f'Mapped {len(mapping)} unit IDs to images in {IMG_DST}/')
    print(f'Mapping saved to {MAPPING_OUT}')
