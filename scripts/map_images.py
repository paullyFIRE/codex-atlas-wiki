"""Map unit IDs to game images — ONLY official site portraits.

Official site images (21 mythic heroes) are manually mapped.
APK-extracted textures are NOT used — they're sprite atlases, not portraits.
"""

import json, os, shutil

IMG_DST = 'public/images'
MAPPING_OUT = 'data/processed/unit_image_map.json'

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

OFFICIAL_SRC = 'public/images/official-site'
OFFICIAL_DST = 'public/images/heroes'

def build_mapping():
    os.makedirs(OFFICIAL_DST, exist_ok=True)
    mapping = {}

    for uid, mythic_id in OFFICIAL_MAP.items():
        src = os.path.join(OFFICIAL_SRC, f'{mythic_id}.png')
        dst = os.path.join(OFFICIAL_DST, f'{uid}.png')
        if os.path.exists(src):
            shutil.copy2(src, dst)
            mapping[f'heroes/{uid}'] = f'/images/heroes/{uid}.png'

    print(f'Mapped {len(mapping)} official site portraits')
    return mapping

if __name__ == '__main__':
    mapping = build_mapping()
    with open(MAPPING_OUT, 'w') as f:
        json.dump(mapping, f, indent=2)
