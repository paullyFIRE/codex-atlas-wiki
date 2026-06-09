# Content Guide — War Inc: Rising Wiki

## Page Types

### 1. Hero/Unit Page (`/heroes/{slug}`) — 179 pages

**High-value queries**: `{name} stats`, `{name} skills`, `is {name} good`, `{name} build`, `best {profession}`

**Page structure** (top to bottom):

```
┌─────────────────────────────────────────────────────┐
│  Breadcrumb: Home > Heroes > {Name}                  │
├─────────────────────────────────────────────────────┤
│  ┌──────┐  H1: {Hero Name}                          │
│  │portrait│  Rarity stars | Profession tag | Cost    │
│  │       │  "Rarity {n} {Profession} unit costing   │
│  └──────┘   {cost} to deploy."                      │
│  ────────  ──────────────────────────────────────   │
│  Quick Stats: HP 636 | ATK 42 | DEF 1 | Spd 2       │
│  (Level 1 values above the fold)                     │
├─────────────────────────────────────────────────────┤
│  H2: Stats by Level                                  │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐ │
│  │Level │ HP   │ ATK  │ DEF  │ Spd  │ Range│ Power│ │
│  ├──────┼──────┼──────┼──────┼──────┼──────┼──────┤ │
│  │  1   │ 636  │  42  │  1   │  2   │  3   │  97  │ │
│  │  2   │ 760  │  50  │  1   │  2   │  3   │ 150  │ │
│  │ ...  │ ...  │ ...  │ ...  │ ...  │ ...  │ ...  │ │
│  │  12  │ 9620 │ 490  │  1   │  2   │  3   │ 3460 │ │
│  └──────┴──────┴──────┴──────┴──────┴──────┴──────┘ │
├─────────────────────────────────────────────────────┤
│  H2: Skills                                           │
│                                                       │
│  H3: {Skill 1 Name}                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ Skill description text from localization      │    │
│  │ Charges: 2 | Cooldown: 8s | Duration: 3s     │    │
│  │ Damage: 150 (level 1) → 450 (level 12)       │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  H3: {Skill 2 Name}                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ ...                                            │    │
│  └──────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────┤
│  H2: How to Use {Name}                                │
│  Best in: [Campaign] [Arena] [Co-op] [Events]         │
│  Strategy tips based on profession and stats          │
├─────────────────────────────────────────────────────┤
│  H2: Synergies                                        │
│  Works well with: [Hero A] [Hero B] [Hero C]          │
│  Counters: [Hero X] [Hero Y]                          │
│  Countered by: [Hero Z]                               │
├─────────────────────────────────────────────────────┤
│  H2: Related Heroes                                   │
│  [Same Rarity] [Same Profession] [Same Type]          │
│  Grid of 6-12 related unit cards                      │
└─────────────────────────────────────────────────────┘
```

**Hero page template** (`src/templates/HeroPage.astro`):

```astro
---
// Props: unitId, unitData, stats, skills, relatedUnits
---
<Breadcrumb path={["Heroes", name]} />
<HeroInfobox portrait={...} rarity={...} profession={...} cost={...} />
<StatTable levels={stats.levels} />
<SkillsSection skills={skills} />
<UsageGuide unit={unitData} />
<SynergiesSection unitId={unitId} relations={relations} />
<RelatedUnits units={relatedUnits} category="heroes" />
```

---

### 2. Building/Tower Page (`/buildings/{slug}`) — 55 pages

Same template as hero page but:
- Title: `{Name} - Building Stats and Upgrades | War Inc: Rising Wiki`
- Skills section → "Abilities" (some buildings have special abilities)
- Added section: **H2: Upgrade Path** (what it upgrades into, level requirements)
- No synergies section (buildings don't have team synergies)

---

### 3. Special Entity Page (`/special/{slug}`) — 59 pages

For resources, mines, barracks, command center, etc.
- Title: `{Name} - Special Entity Stats | War Inc: Rising Wiki`
- Simplified stat table (fewer stats)
- Added section: **H2: Function** (what this entity does in battle)
- Added section: **H2: Production** (for resource-generating entities)

---

### 4. Follower Page (`/followers/{slug}`) — 10 pages

For troop/pet units (Frieda, Toasty, Flory, etc.)
- Title: `{Name} - Follower Stats and Abilities | War Inc: Rising Wiki`
- Same stat table as heroes (HP, ATK, speed, range)
- Skills section (each follower has 1 ability)
- Added section: **H2: How to Acquire** (which heroes use this follower)

---

### 5. Equipment Page (`/equipment/{slug}`) — 160 pages

**High-value queries**: `{equip name} stats`, `{equip name} tier`, `best equipment for {hero}`

```
H1: {Equipment Name}
  H2: Overview — type, target camp, base stats
  H2: Stats by Tier (5 tiers)
    ┌──────┬──────┬──────┬──────┬──────┐
    │ Tier │ Stat1│ Stat2│ Stat3│ Cost │
    ├──────┼──────┼──────┼──────┼──────┤
    │  1   │ ...  │ ...  │ ...  │ ...  │
    │  ... │ ...  │ ...  │ ...  │ ...  │
    │  5   │ ...  │ ...  │ ...  │ ...  │
    └──────┴──────┴──────┴──────┴──────┘
  H2: Upgrade Costs (materials per tier upgrade)
  H2: Best Heroes for this Equipment
  H2: Related Equipment
```

---

### 6. Game Mode Page (`/modes/{slug}`) — 5 pages

```
H1: {Mode Name}
  H2: Overview — objective, layout, duration
  H2: Rules — win conditions, enemy types
  H2: Rewards — chests, drops per build level
  H2: Card Pool — available units and rarities
  H2: Best Units for {Mode}
  H2: Strategy Tips
  H2: Related Modes
```

---

### 7. Synergy Page (`/synergies/{slug}`) — 9 pages

```
H1: {Synergy Name}
  H2: Effect Description
  H2: Affected Units (units that belong to this synergy group)
  H2: Best Team Compositions
  H2: Strategy Tips
```

---

### 8. Field Buff Page (`/buffs/{slug}`) — 36 pages

```
H1: {Buff Name}
  H2: Effect
  H2: Duration / Trigger Conditions
  H2: Best Units to Use With This Buff
  H2: Strategy
```

---

## List / Index Pages

| Page | URL | Content |
|---|---|---|
| All Heroes | `/heroes/` | Filterable grid of all 179 heroes |
| All Buildings | `/buildings/` | Grid of all 55 buildings |
| All Equipment | `/equipment/` | Filterable list of 160 equipment |
| All Followers | `/followers/` | Grid of 10 followers |
| All Modes | `/modes/` | Cards for 5 game modes |
| All Synergies | `/synergies/` | Cards for 9 synergies |
| All Buffs | `/buffs/` | Cards for 36 buffs |

### Index Page Layout

```
H1: All Heroes
  [Filter bar: Rarity | Profession | Unit Type | Cost range]
  
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │      │ │      │ │      │ │      │ │      │ │      │
  │Hero 1│ │Hero 2│ │Hero 3│ │Hero 4│ │Hero 5│ │Hero 6│
  │      │ │      │ │      │ │      │ │      │ │      │
  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
  (X of 179 shown)
```

### Index Page Templates

| Template | Variables | Filter Options |
|---|---|---|
| `HeroList` | `units[]` | rarity, profession, unitType, cost |
| `BuildingList` | `units[]` | rarity, subcategory |
| `EquipmentList` | `items[]` | targetCamp, tier |
| `FollowerList` | `items[]` | rarity |

---

## URL Structure

```
/                          ← Homepage (VideoGame schema)
/heroes/                   ← Hero index (filterable)
/heroes/{hero-slug}        ← Hero detail
/buildings/                ← Building index
/buildings/{building-slug} ← Building detail
/special/{special-slug}    ← Special entity detail
/followers/                ← Follower index
/followers/{follower-slug} ← Follower detail
/equipment/                ← Equipment index
/equipment/{equip-slug}    ← Equipment detail
/modes/{mode-slug}         ← Game mode detail
/synergies/{synergy-slug}  ← Synergy detail
/buffs/{buff-slug}         ← Field buff detail
/compare/{heroA}-vs-{heroB}  ← Hero comparison (auto-generated)
```

**Slug rules:**
- Lowercase only
- Hyphens for spaces (not underscores)
- Max 50 chars
- Strip special characters
- Examples: `caesar`, `sakura-ronin`, `goblin-shaman`

---

## Title and Meta Patterns

### Title Tags (aim for <60 chars)

| Page Type | Pattern | Example |
|---|---|---|
| Hero | `{Name} - Hero Stats and Skills | War Inc: Rising Wiki` | `Archer - Hero Stats and Skills | War Inc: Rising Wiki` |
| Building | `{Name} - Building Stats and Upgrades | War Inc: Rising Wiki` | `Arrow Tower - Building Stats and Upgrades` |
| Special | `{Name} - {Type} Stats | War Inc: Rising Wiki` | `Gold Mine - Resource Building Stats` |
| Follower | `{Name} - Follower Stats and Abilities | War Inc: Rising Wiki` | `Frieda - Follower Stats and Abilities` |
| Equipment | `{Name} - Equipment Stats and Tiers | War Inc: Rising Wiki` | `Flaming Sword - Equipment Stats and Tiers` |
| Game Mode | `{Mode Name} - Rules, Rewards, and Strategy` | `Arena - Rules, Rewards, and Strategy` |
| List page | `All {Category} - Stats and Analysis` | `All Heroes - Stats and Analysis` |
| Comparison | `{A} vs {B} - Which Hero is Better?` | `Caesar vs Arthur - Which Hero is Better?` |

### Meta Descriptions (aim for <160 chars)

| Page Type | Pattern |
|---|---|
| Hero | `Learn about {Name} in War Inc: Rising. {Rarity} {Profession} unit costing {cost}. HP {hp}, ATK {atk}, DEF {def} per level, skills, and best game modes.` |
| Equipment | `{Name} is a level {tier} equipment in War Inc: Rising. View stats for all {tierCount} tiers, upgrade costs, and which heroes use it.` |
| Game Mode | `{Mode Name} is a game mode in War Inc: Rising. Learn the rules, rewards, best units, and strategies to win.` |
| List | `Browse all {count} {category} in War Inc: Rising. Filter by rarity, profession, and stats to find the best units.` |

---

## Structured Data (Schema.org)

### Hero/Unit Page

```jsonld
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{Name}",
  "description": "{Name} is a {rarity} {profession} in War Inc: Rising. HP {hp}, ATK {atk}, DEF {def} at level 1.",
  "about": {
    "@type": "Thing",
    "name": "{Name} - War Inc: Rising Unit",
    "additionalProperty": [
      {"@type": "PropertyValue", "name": "Rarity", "value": "{rarity}"},
      {"@type": "PropertyValue", "name": "Profession", "value": "{profession}"},
      {"@type": "PropertyValue", "name": "Cost", "value": "{cost}"},
      {"@type": "PropertyValue", "name": "HP", "value": "{hp_lv1}"},
      {"@type": "PropertyValue", "name": "ATK", "value": "{atk_lv1}"},
      {"@type": "PropertyValue", "name": "DEF", "value": "{def_lv1}"},
      {"@type": "PropertyValue", "name": "Combat Power", "value": "{power}"}
    ]
  }
}
```

### Homepage

```jsonld
{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "War Inc: Rising",
  "applicationCategory": "Game",
  "operatingSystem": "Android",
  "author": { "@type": "Organization", "name": "Fastone Games" },
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
}
```

---

## Internal Linking Rules

Every entity page should automatically generate links:

| Source | Target | Condition |
|---|---|---|
| Hero page | `/heroes/?rarity={rarity}` | Always |
| Hero page | `/heroes/?profession={profession}` | Always |
| Hero page | Equipment pages | If unit uses equipment |
| Hero page | Followers | If unit has followers |
| Equipment page | Heroes of target camp | Always |
| Game mode page | Top units for this mode | By combat power |
| Hero page | Related heroes (same rarity) | Top 6 by ID |
| Hero page | Related heroes (same profession) | Top 6 by combat power |
| All pages | Homepage, category index | Breadcrumb |

---

## Sitemap Strategy

- One sitemap per entity type (modular, easier to update)
- Priority: Hero pages = 0.8, Equipment = 0.7, Index pages = 0.9
- Changefreq: weekly for entity pages, daily for homepage
- Max 50,000 URLs per sitemap (we'll have <5,000 total)

```
sitemap-heroes.xml (179 URLs)
sitemap-buildings.xml (55 URLs)
sitemap-special.xml (59 URLs)
sitemap-followers.xml (10 URLs)
sitemap-equipment.xml (160 URLs)
sitemap-modes.xml (5 URLs)
sitemap-synergies.xml (9 URLs)
sitemap-buffs.xml (36 URLs)
sitemap-compare.xml (500+ URLs, optional)
sitemap-main.xml (index pages, homepage)
```

---

## Data Transformations Needed

Before building templates, we need transforms that merge the raw configs into page-ready JSON:

```python
# pseudo-code for page generation
def build_hero_page(unit_id):
    unit = unit_database[unit_id]
    stats = unit_stats[unit_id]
    skills = skill_data.get(unit_id, {})
    name = unit_name_map[unit_id]
    
    return {
        "slug": slugify(name),
        "title": f"{name} - Hero Stats and Skills | War Inc: Rising Wiki",
        "meta_description": f"Learn about {name} in War Inc: Rising...",
        "h1": name,
        "breadcrumb": ["Home", "Heroes", name],
        "infobox": {
            "portrait": f"/images/heroes/{unit_id}.png",
            "rarity": rarity_map[unit.rarity],
            "profession": profession_map[unit.profession],
            "cost": unit.cost,
            "base_stats": stats["1"],
            "max_stats": stats["12"],
        },
        "stats_table": generate_stat_table(stats),
        "skills": parse_skills(skills, skill_names, unit.skills),
        "related": find_related(unit_id, unit_database),
        "schema": generate_schema(name, unit, stats),
    }
```

This transformation logic goes in `scripts/generate_pages.py` — to be written when we scaffold the Astro site.
