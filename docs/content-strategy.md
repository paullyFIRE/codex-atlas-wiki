# Content Strategy — War Inc: Rising Wiki

## Overview

3,075 static pages across 12 content types, targeting high-volume PSEO queries for War Inc: Rising. All content is generated from APK-extracted game data, providing unique factual data no other site has.

---

## 1. Entity Pages (469)

The foundation. Every game entity gets its own detail page with stats, skills, and schema markup.

| Type | Pages | URL Pattern | Example |
|---|---|---|---|
| Heroes | 161 | `/heroes/{slug}` | `/heroes/archer/` |
| Buildings | 20 | `/buildings/{slug}` | `/buildings/arrow-tower/` |
| Special | 59 | `/special/{slug}` | `/special/gold-mine/` |
| Followers | 10 | `/followers/{slug}` | `/followers/frieda/` |
| Equipment | 160 | `/equipment/{slug}` | `/equipment/conqueror/` |
| Field Buffs | 36 | `/buffs/{slug}` | `/buffs/field-buff-1/` |
| Synergies | 9 | `/synergies/{slug}` | `/synergies/synergy-1/` |
| Game Modes | 5 | `/modes/{slug}` | `/modes/general-lineup/` |

**Query targets**: `{name} stats`, `{name} skills`, `{name} build`, `is {name} good`

---

## 2. Compare Pages (2,580)

Auto-generated hero-vs-hero stat comparisons for all same-profession pairings.

| Feature | Value |
|---|---|
| Pages | 2,580 |
| URL | `/compare/{heroA}-vs-{heroB}` |
| Query targets | `{a} vs {b} War Inc`, `which is better {a} or {b}` |
| Data | HP, ATK, DEF, cost, combat power side-by-side |

**Example**: `/compare/archer-vs-gunner/`

---

## 3. Strategy Guides (8)

Data-driven rankings by cost bracket and game mode.

| Guide | Units | URL |
|---|---|---|
| Best Low Cost (0-2) | 12 | `/guides/best-low-cost-units/` |
| Best Mid Cost (3-4) | 12 | `/guides/best-mid-cost-units/` |
| Best High Cost (5+) | 137 | `/guides/best-high-cost-units/` |
| Best Heroes per Mode | 30 each | `/guides/best-heroes-for-{mode}/` |

---

## 4. Profession Guides (7)

All units ranked by combat power within each profession class.

| Profession | Units | URL |
|---|---|---|
| Warrior | 40 | `/professions/warrior/` |
| Tank | 47 | `/professions/tank/` |
| Assassin | 52 | `/professions/assassin/` |
| Mage | 31 | `/professions/mage/` |
| Support | 5 | `/professions/support/` |
| Ranger | 25 | `/professions/ranger/` |
| Special | 23 | `/professions/special/` |

---

## 5. Rarity Tier Lists (5)

All units ranked by combat power within each rarity tier.

| Rarity | Units | URL |
|---|---|---|
| Common | 21 | `/rarities/common-units/` |
| Rare | 58 | `/rarities/rare-units/` |
| Epic | 14 | `/rarities/epic-units/` |
| Legendary | 39 | `/rarities/legendary-units/` |
| Mythic | 95 | `/rarities/mythic-units/` |

---

## 6. Interactive Tools (5)

Client-side tools built on game data.

| Tool | URL | Description |
|---|---|---|
| Team Builder | `/build-team/` | Search/filter 162 heroes, build 8-slot formations, see synergies |
| Mode Loot Explorer | `/tools/mode-loot/` | Drop tiers, boss spawns, monster pools per mode |
| Boss Wave Calculator | `/tools/boss-waves/` | Boss power scaling across 12 levels |
| Spell Calculator | `/tools/spell-calc/` | Training times, cooldowns, capacity |
| Evolution & Merge | `/tools/evolution/` | Unit upgrade costs and merge requirements |

---

## 7. Landing & Resource Pages (5)

| Page | URL | Purpose |
|---|---|---|
| Homepage | `/` | Category navigation, VideoGame schema |
| Professions Index | `/professions/` | Links to all profession guides |
| Tools Index | `/tools/` | Links to all interactive tools |
| Community Resources | `/resources/` | Discord, YouTube, APKPure, Facebook |
| Game Data API | `/data/` | Dataset schema + downloadable JSON |

---

## 8. AI Search Optimization

| Feature | Status |
|---|---|
| VideoGame schema with characterAttribute | ✅ All entity pages |
| Dataset schema with JSON distribution | ✅ `/data/` page |
| BreadcrumbList schema | ✅ All entity pages |
| Q&A-format H2 headings | ✅ 161 hero pages |
| AI crawlers allowed (GPTBot, Claude-Web, CCBot) | ✅ robots.txt |
| Google-Extended blocked (training opt-out) | ✅ robots.txt |
| Google Search Console verified | ✅ `war-inc-rising.codex-atlas.com` |

---

## 9. Technical SEO

| Feature | Status |
|---|---|
| robots.txt | ✅ Sitemap referenced |
| XML Sitemap | ✅ 3,075 URLs via @astrojs/sitemap |
| Canonical URLs | ✅ All pages |
| Responsive viewport | ✅ |
| Inline CSS | ✅ Basic readability |
| Static build time | ~4.5s |
| Deploy | GitHub Actions → Cloudflare Pages |

---

## 10. Content Opportunities (Not Yet Built)

| Opportunity | Data Source | Difficulty | Query Targets |
|---|---|---|---|
| Equipment-by-hero mapping | equip_battle.json targetCamp | Easy | `best equipment for {hero}` |
| Follower-to-hero matching | card_growth.json followers.unlockCond | Medium | `best follower for {hero}` |
| Unit stat visualizer (charts) | unit_database.json stats | Medium | `{hero} stat chart` |
| Boss unit profiles | battle_conf_lib boss spawns | Easy | `{boss name} War Inc` |
| Patch notes archive | Manual per APK release | High | `War Inc patch notes 1.0.x` |
| Spell names translation | Manual | Easy | (spells are currently Chinese only) |
| Item ID name mapping | localization en.csv | Easy | (many item IDs are unmapped) |

---

## 11. Traffic & Monetization

- **Hosting**: Cloudflare Pages (free tier, unlimited bandwidth)
- **Domain**: `war-inc-rising.codex-atlas.com` (SSL pending)
- **Analytics**: Google Search Console connected
- **Ad potential**: 3,075 pages × PSEO gaming keywords → display ads (AdSense, Ezoic, Mediavine)
- **Custom domain SSL**: Still provisioning (Cloudflare)
