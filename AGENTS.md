# War Rising Stats Blog

## Project Goal

PSEO (Programmatic SEO) blog indexing all characters, cards, entities, modes, and stats for **War Rising** (com.i89trillion.strategy.rising). Generate wiki-style onboard pages from extracted game data to drive search traffic and ad revenue. Eventually publish guides. Strive to be the most up-to-date data source for the game.

## Data Source & Extraction

- Primary source: APK (`com.i89trillion.strategy.rising`). Download the APK and extract assets/data files (JSON, protobuf, SQLite, Lua, Unity AssetBundles, etc.) to scrape character/card/entity/stats info.
- No public API is assumed. All content comes from reverse-engineering the game binary.
- Future: scrape wikis, patch notes, or community sources to supplement.

## Stack

- **Package manager**: pnpm ^11.0.8
- **Module system**: ESM (`"type": "module"`)
- **Framework**: Undecided. Choose based on PSEO needs (static generation at scale, e.g. Next.js static export or Astro).
- **Hosting**: Likely Vercel or static hosting.

## Developer Commands

```bash
pnpm install        # Install deps
pnpm add <pkg>      # Add dependency
pnpm run <script>   # Run script (check package.json)

# Full extraction pipeline (one command)
./scripts/extract.sh [version]   # APK download → Il2Cpp dump → configs → localization → Unity assets
python3 scripts/extract_all.py   # Same as above but skips APK/Il2Cpp steps
```

## Data Files

All extracted data lives in `data/processed/`. These are the canonical files for page generation:

### Core Data (`data/processed/`)

| File | Contents | Key Fields |
|---|---|---|
| `config/card_growth.json` | 316 battle units + 10 followers + growth curves | `battleUnits`, `followers`, `battleGrowth`, `merge`, `skillUpgradeCost`, `unitSkillUnlock`, `combatPowerGrowth` |
| `config/equip_battle.json` | 160 equipment items, 5 tiers each | `equips` { `id`, `targetCamp`, `levels[]` } |
| `config/battle_conf_lib.json` | 5 game mode configs | Layout, enemy pools, card pools, rewards, synergies |
| `config/battle_config.json` | Core battle settings | `battle_config`, `formation` |
| `config/battle_synergy.json` | 9 synergy/lib definitions | `periods`, `libs` |
| `config/field_buff.json` | 36 field buffs | `libs` |
| `config/lay_map_lib.json` | 14 map layouts | Grid layouts with positions |
| `config/layout_strategy.json` | AI deployment strategies | `strategies`, `modeStrategyLibs` |
| `config/card_show_config.json` | **Unit stats + skill data** | `attrConfig` (TSV with HP/ATK/DEF/speed), `skillDescCsv` (5,761), `skillAttrCsv` (5,545) |
| `config/card_attr_config.json` | 179 unit attribute definitions | `basic` { `id`, `kind`, `threat`, `hpHeight`, `remark` } |
| `config/avatar_config.json` | Avatar/avatar frame config | `avatar`, `avatarFrame` |

### Processed Data (`data/processed/`)

| File | Contents | Count |
|---|---|---|
| `unit_database.json` | **Complete unit DB** — stats + names + skills merged | 251 units with per-level stats |
| `unit_stats.json` | Per-level unit stats (HP, ATK, DEF, speed, range, cost) | 251 units × 12 levels |
| `unit_name_map.json` | Unit ID → English display name | 389 entries |
| `hero_name_map.json` | Hero ID → full name (Caesar, Arthur, etc.) | 4 entries |
| `skill_data.json` | Unit → Skill → Level → Effect values | 441 combos across 183 units |
| `localization/en.csv` | All English UI strings (8,955 keys) | Skill names, descriptions, UI text |

### Stats Per Unit

From `card_growth.json` (per unit):
- `id`, `unitType` (1=hero, 4=building/tower, 5=special), `rarity` (1-5), `profession` (2-7)
- `combatPower`, `cost`, `atkRange` (grid coords), `levelCombatPower` (12 levels)
- `skills`, `skillsForMode`, `unlockCond`, `source`

From `card_show_config.json` `attrConfig.showAttrsLib.2` (per level, TSV):
- `1050`: HP (血量)
- `1070`: ATK (攻击)  
- `1080`: DEF (防御)
- `1090`: Attack Speed (攻速)
- `1100`: Move Speed (移速)
- `1110`: Attack Range (攻击距离)
- `35`: Weakness (自身弱点)
- `36`: Cost (水费)
- `10001`-`10003`: Tags (标签)

### Skill Data (per skill per level)

From `skillAttrCsv`:
- `1`: Charges (充能次数)
- `2`: Cooldown (冷却)
- `3`: Duration (持续时间)
- `4`: Trigger probability (触发概率)
- `5`: Skill range (技能范围)
- `8`: Skill damage (技能伤害)
- `9`: Move speed mod (移速调整)
- `10`: Attack speed mod (攻速调整)
- `11`: ATK mod (攻击力调整)
- `12`: Heal fixed (治疗固定值)
- `13`: Heal % (治疗百分比)
- `14`: Shield % (护盾比例)
- `16`: Crowd control (控制)
- `17`: Damage element (伤害属性)
- `27`: Shield value (护盾值)

### Type Mappings

```
unitType: 1=Hero/Unit, 4=Building/Tower, 5=Special
profession: 2=Warrior, 3=Tank, 4=Assassin, 5=Mage, 6=Support, 7=Ranger
rarity: 1=Common, 2=Rare, 3=Epic, 4=Legendary, 5=Mythic
```

### Page Potential (~500+ pages)

- **179 hero pages**: Name, rarity, profession, cost, per-level HP/ATK/DEF/speed, skills, combat power growth
- **55 building/tower pages**: Same stats but `unitType=4`
- **59 special pages**: Resources, mines, barracks (unitType=5)
- **10 follower pages**: Pet/troop units
- **160 equipment pages**: 5 upgrade tiers per item
- **5 game mode pages**: Rules, enemy pools, rewards
- **9 synergy pages**: Team bonus effects
- **36 buff pages**: Field modifier effects

## Developer Commands

```bash
pnpm install        # Install deps
pnpm add <pkg>      # Add dependency
pnpm run <script>   # Run script (check package.json)

# Full extraction pipeline (one command)
./scripts/extract.sh [version]   # APK download → Il2Cpp dump → configs → localization → Unity assets
python3 scripts/extract_all.py   # Same as above but skips APK/Il2Cpp steps
```

## Quirks & Conventions

- No testing framework configured yet. Add one before writing tests.
- This is a solo project; no CI/CD, linting, or formatting conventions established yet.
- Prefer static generation over SSR for SEO and hosting simplicity (Astro recommended).
- Keep the extraction pipeline scripted and reproducible (so updates are just re-running extraction).
- Unit stats come from `card_show_config.json` `attrConfig.showAttrsLib` as TSV embedded in JSON.
- Skill data from `skillAttrCsv` and `skillDescCsv` in the same file.
