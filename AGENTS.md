# War Rising Stats Blog

## Project Goal

PSEO (Programmatic SEO) blog indexing all characters, cards, entities, modes, and stats for **War Rising** (com.i89trillion.strategy.rising). Generate wiki-style onboard pages from extracted game data to drive search traffic and ad revenue. Eventually publish guides. Strive to be the most up-to-date data source for the game.

## Data Source & Extraction

- Primary source: APK (`com.i89trillion.strategy.rising`). Download the APK and extract assets/data files (JSON, protobuf, SQLite, Lua, Unity AssetBundles, etc.) to scrape character/card/entity/stats info.
- No public API is assumed. All content comes from reverse-engineering the game binary.
- Future: scrape wikis, patch notes, or community sources to supplement.
- **See `docs/game-data.md`** for data file reference and format documentation.
- **See `docs/asset-extraction.md`** for extraction pipeline, image sources, tools, and roadmap.
- **See `docs/game-server.md`** for server infrastructure, CDN, API, and auth token info.

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

# Regenerate all pages after data changes
python3 scripts/map_images.py && python3 scripts/generate_pages.py && npm run build
```

## Content Structure

### URL Patterns

```
/heroes/{slug}           — Hero detail page
/buildings/{slug}        — Building detail
/special/{slug}          — Special entity
/followers/{slug}        — Follower detail
/modes/{slug}            — Game mode detail
/synergies/{slug}        — Synergy detail
/buffs/{slug}            — Field buff detail
/compare/{a}-vs-{b}     — Comparison page (auto-gen)
```

### Hierarchical Heading Structure per Entity Page

### Hero Page

```
H1: {Name}                              ← Unit display name
├── H2: Stats by Level                  ← Stat table (levels 1-12)
│   └── H3: Base Stats (Level 1)         ← Highlight row
├── H2: Skills                          ← Skill breakdown
│   └── H3: {Skill Name}                ← Per skill: desc, cd, charges, scaling
├── H2: How to Use {Name}               ← Game mode assessment
├── H2: Synergies                       ← Works well with / Counters / Countered by
└── H2: Related {Category}              ← Same rarity / profession links
```

### Content Patterns

| Pattern | Example | Value |
|---|---|---|
| `{Name} stats` | `Archer stats` | Stat table drives this query |
| `is {Name} good` | `Is Archer good War Inc` | Usage guide answers this |
| `best {profession}` | `best Warrior War Inc` | Filtered list page |
| `{Name} skills` | `Archer skills` | Skills section |
| `{Name} build` | `Archer build` | Equipment recommendations |
| `{Name} vs {Name}` | `Archer vs Berserker` | Auto-generated compare pages |

### Title Tag Templates (aim <60 chars)

- Hero: `{Name} - Hero Stats and Skills | War Inc: Rising Wiki`
- Building: `{Name} - Building Stats and Upgrades | War Inc: Rising Wiki`
- Equipment: `{Name} - Equipment Stats and Tiers | War Inc: Rising Wiki`
- List: `All {Category} - Stats and Analysis | War Inc: Rising Wiki`

### Structured Data per Entity Page

```jsonld
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{Name}",
  "description": "{Summary}",
  "about": {
    "@type": "Thing",
    "additionalProperty": [
      {"@type": "PropertyValue", "name": "Rarity", "value": "{rarity}"},
      {"@type": "PropertyValue", "name": "Profession", "value": "{profession}"}
    ]
  }
}
```

### Page Potential (~340+ pages)

- **179 hero pages**: Name, rarity, profession, cost, per-level HP/ATK/DEF/speed, skills, combat power growth
- **55 building/tower pages**: Same stats but `unitType=4`
- **59 special pages**: Resources, mines, barracks (unitType=5)
- **10 follower pages**: Pet/troop units

- **5 game mode pages**: Rules, enemy pools, rewards
- **9 synergy pages**: Team bonus effects
- **36 buff pages**: Field modifier effects

## Brand Strategy

### Positioning
- **Site**: `War Inc: Rising Wiki` — explicitly labelled as a fan wiki to avoid impersonation risk
- **Domain**: `war-inc-rising.codex-atlas.com` — subdomain under Codex Atlas master domain
- **Publisher**: `Codex Atlas` — the network/parent brand, shown only in footer + URL, not competing with page titles
- **Footer**: `War Inc: Rising Wiki — part of Codex Atlas. Unofficial fan site.`

### Rationale
- Page titles use "Wiki" qualifier so Google clearly understands this is a fan resource, not the official game
- Codex Atlas is the **publisher/network**, not the content subject — users know immediately they're on a fan wiki
- Subdomain pattern (`game-name.codex-atlas.com`) is designed to scale: future sites (other games, other wikis) get their own subdomain with the same footer pattern
- Master brand builds passively through footer + domain without diluting per-site SEO

### Implementation
- `og:site_name`: `War Inc: Rising Wiki`
- JSON-LD WebSite name: `War Inc: Rising Wiki`
- Page titles suffix: `| War Inc: Rising Wiki`
- Topbar logo: `War Inc: Rising Wiki`
- See `src/layouts/BaseLayout.astro` and `src/pages/index.astro`

## Quirks & Conventions

- No testing framework configured yet. Add one before writing tests.
- This is a solo project; no CI/CD, linting, or formatting conventions established yet.
- Prefer static generation over SSR for SEO and hosting simplicity (Astro recommended).
- Keep the extraction pipeline scripted and reproducible (so updates are just re-running extraction).
- Unit stats come from `card_show_config.json` `attrConfig.showAttrsLib` as TSV embedded in JSON.
- Skill data from `skillAttrCsv` and `skillDescCsv` in the same file.
- Equipment (`equip_battle.json`) is **not** a real game feature — leftover Unity assets, ignore.
