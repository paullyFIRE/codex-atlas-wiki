# Data Analysis — War Inc: Rising

## Entity Catalog

| Entity Type | Count | Named | Page Potential |
|---|---|---|---|
| Battle Units | 316 | 293 | 293 |
| — Heroes/Units (type 1) | 181 | 179 | 179 |
| — Buildings/Towers (type 4) | 76 | 55 | 55 |
| — Special (type 5) | 59 | 59 | 59 |
| Followers | 10 | 10 | 10 |
| Equipment | 160 | — | 160 |
| Game Modes | 5 | — | 5 |
| Synergies | 9 | — | 9 |
| Field Buffs | 36 | — | 36 |
| **Total** | | | **~513** |

## Rarity Distribution

| Rarity | Count |
|---|---|
| Common | 84 |
| Rare | 84 |
| Epic | 14 |
| Legendary | 39 |
| Mythic | 95 |

## Professions

| ID | Name |
|---|---|
| 2 | Warrior |
| 3 | Tank |
| 4 | Assassin |
| 5 | Mage |
| 6 | Support |
| 7 | Ranger |

## Game Modes Found

| Mode | Layout | Max Enemies | Duration |
|---|---|---|---|
| 1 | 1003 | 90 | 60 min |
| 3 | 1003 | 90 | 60 min |
| 4 | 0 | 60 | 60 min |
| 5 | 0 | 60 | 60 min |
| 6 | 1003 | 60 | 60 min |

## Followers (Troops)

Frieda, Toasty, Flory, Donnie, Poopy, Steaky, Burgie, Eglet, Cacto, Froggle

## Sample 30 Named Heroes

| ID | Name | Rarity |
|---|---|---|
| 43 | Skeleton Troop | Common |
| 142 | Tempest Core | Legendary |
| 144-147 | Castle Assassin/Archer/Mage/Guard | Legendary |
| 618 | Archer | Common |
| 619 | Berserker | Rare |
| 620 | Rock Thrower | Epic |
| 621 | Sakura Ronin | Legendary |
| 622-625 | Gunner, Demoman, Poison Master, Ghost Assassin | Common→Legendary |
| 626-632 | Snowman Warrior, Flame Mage, Ursa Champion, etc. | Epic→Legendary |
| 635-652 | Flail Warden, Gryphon Knight, Geomancer, etc. | Rare→Mythic |

## Stats Available Per Unit

From `card_growth.json`:
- `id`, `unitType`, `rarity`, `profession`
- `combatPower`, `cost`
- `atkRange` (attack range coordinates)
- `levelCombatPower` (power per level, up to 12 tiers)
- `skills` (skill IDs)
- `skillsForMode` (mode-specific skill overrides)
- `unlockCond`, `unlockCondParams`
- `relatedBattleUnits`, `showAttr`

## Per-Equipment Stats

From `equip_battle.json`:
- `id`, `targetCamp`
- `conds` (unlock conditions)
- `levels` (5 upgrade tiers with stat values per tier)

## Data Relationships

```
Unit (316) ──has──> Skills
    │
    ├── can equip ──> Equipment (160, 5 tiers each)
    │
    ├── can have ──> Followers (10)
    │
    └── appears in ──> Game Modes (5)
                          │
                          ├── has synergies (9)
                          └── has field buffs (36)
```

## Texture Resources Available

| Type | Count |
|---|---|
| Texture2D (PNG) | 2,785 |
| Sprites (PNG) | 4,222 |
| Hero portraits | ~300+ |
| UI/icon assets | ~2,000+ |

## Missing Data

- **Skill descriptions** — referenced by ID in unit data; descriptions are in localization CSV (`unit_skill_name_*`)
- **Equipment stat values** — the `levels` array has the actual numbers but we need to inspect the structure
- **Full stat values per unit level** — `levelCombatPower` has power values per level but not detailed stats like HP, ATK, etc. Those might be in the raw unit config files
