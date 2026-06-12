# Hero Page Blueprint — Metaprompt

Every hero at `war-inc-rising.codex-atlas.com/heroes/{slug}/` is a 7-section vertical-scroll entity detail page targeting the keyword pattern `"{Name} stats", "is {Name} good", "best {profession}"`. Below is the complete page blueprint: what a visitor sees, the data backing it, the cross-links served, and content ideas that can be added per section.

---

## Page Overview

| Property | Value |
|---|---|
| URL pattern | `/heroes/{slug}/` |
| SEO title | `{Name} - Hero Stats and Skills | War Inc: Rising Wiki` |
| Meta description | `Learn about {Name} in War Inc: Rising. {Rarity} {Profession} unit costing {cost}. HP {hp}, ATK {atk}, DEF {def} per level, skills, and best game modes.` |
| Schema | `CreativeWork` (page) + `VideoGame` (entity) + `FAQPage` (Q&A) + `BreadcrumbList` |
| Layout | BaseLayout with topbar navigation, breadcrumb, sticky section nav, footer |
| Target queries | `{name} war inc rising`, `{name} stats`, `is {name} good war inc rising`, `{name} skills` |

---

## Section 1 — Entity Header (always visible)

**What the visitor sees:**
- Large hero name as H1 heading
- Rarity badge (colored: Common → Mythic)
- Profession badge (Warrior / Tank / Assassin / Mage / Support / Ranger / Special)
- Combat power star rating
- Cost pips (8 pips max)

**Data source:** `data/pages/heroes/{slug}.json` `→ name, rarity_name, profession_name, combat_power, cost`

**Content ideas:**
- Hero portrait/icon if extracted from APK assets
- Flavor text or lore snippet for flavor (future community contributions)

---

## Section 2 — Community Rank Badge (conditional)

**Shown only if** the hero has a ranking in `data/pages/community_rankings.json`.

**What the visitor sees:**
- Colored badge: S+ (gold glow), S (green), A (blue), B (yellow), C (orange), D (red), F (dark red)
- Tier label: "S+ Tier — Game-Breaking", "S Tier — Excellent", etc.
- Mode tags as small pills: `pvp`, `clan-war`, `infinite-war`, `hunting`, `co-op`, `pve`

**Data source:** `data/pages/community_rankings.json` `→ heroes[slug].tier, heroes[slug].tags`

**Content ideas:**
- Show rank number (#1, #2, etc.) next to tier letter
- Add "moved up/down from last month" indicator for meta shift tracking
- Link to the full tier list comparison page at `/tier-lists/overall/`

---

## Section 3 — Stats Section (#stats)

**What the visitor sees:**
- A 7-column stat grid showing Level 1 values:
  HP · ATK · DEF · Speed · Range · Power · Cost · (Move speed if present)
- Full 12-level stat table with columns:
  Level | HP | ATK | DEF | ATK Speed | Move Speed | Range | Power
- Data cells are right-aligned numbers; alternate row backgrounds for readability
- Scrollable horizontally on mobile via `.table-wrap`

**Exact HTML pattern:**
```html
<div class="table-wrap">
  <table class="wiki-table">
    <thead><tr><th>Level</th><th>HP</th><th data-align="right">ATK</th>...</tr></thead>
    <tbody>
      <tr><td><strong>1</strong></td><td>9840</td><td data-type="number">144</td>...</tr>
    </tbody>
  </table>
</div>
```

**Data source:** `pageData.stats_table[]` (array of 12 objects with `level, hp, atk, def, attack_speed, move_speed, attack_range, combat_power`)

**Content ideas:**
- Highlight the jump from level 3→4 or level 6→7 (key breakpoints)
- Show a % growth column (e.g., "+58% HP from Lv1→Lv2")
- Compare stat totals vs. same-rarity average (e.g., "HP is 40% above Mythic average")
- Show attack range as a visual grid overlay (from `atk_range` coordinate data)
- Add a "stats card" summary: tanky fighter, glass cannon, balanced support

**Target keyword:** `{name} stats`

---

## Section 4 — Skills Section (#skills, conditional)

**Shown only if** the hero has skills defined.

**What the visitor sees:**
- One card per skill, each with:
  - Skill name as H3 heading
  - Skill description (from game data)
  - Level effects table: Level | Charges | Cooldown | Duration | Damage | Heal | Shield | etc.
- Dynamically generated column headers from the effect keys (e.g., `charges`, `cd`, `duration`, `skill_damage`, `atk_mod`, `heal_fixed`)

**Data source:** `pageData.skills[]` each with `name, description, level_effects: { "1": { charges: 3, cd: 15 }, "2": {...} }`

**Content ideas:**
- Callout the skill unlock level (e.g., level 4 unlock often adds a powerful passive)
- Compare this hero's skills to similar-profession heroes
- Flag if a skill is bugged or has hidden mechanics (from community KB)
- Note which game modes the skill shines in

**Target keyword:** `{name} skills`

---

## Section 5 — Community Verdict (#community-rank, conditional)

**Shown only if** community ranking data exists.

**What the visitor sees:**
- Callout box (styled by tier: green for S+/S, yellow for C/B, red for D/F)
- "Is {Name} good?" as the H2 heading (direct keyword match for "is X good" queries)
- Tier description: "S+ Tier — Game-Breaking"
- Good-for summary: brief 1-sentence explanation of where they excel
- Recommended minimum level for new players and mid-game players
- Strategy card: "How to use {Name}" with deployment tips, merge advice, pairing suggestions
- "Learn more" link to a relevant blog/guide post if available

**Data source:** `data/pages/community_rankings.json`
```json
{
  "radiant-warrior": {
    "tier": "S+",
    "tags": ["pvp", "clan-war", "infinite-war", "hunting", "co-op"],
    "min_level": 3,
    "min_level_mid": 4,
    "good_for": "Every single game mode.",
    "strategy": "Never merge your last 2 copies...",
    "must_read": "Related Guide Title",
    "must_read_slug": "guide-slug"
  }
}
```

**Content ideas:**
- Add a "good against / weak against" list (counters)
- Show which top-10 arena players use this hero (screenshot evidence from KB)
- Add a "verdict last updated" date
- Show formation placement recommendation (front row, back row, mid)
- Fuse-to-get ratio (how many copies needed for level 4/6/8)
- Add a "Community Rating" star slider (1-5) from multiple sources

**Target keyword:** `is {name} good war inc rising`

---

## Section 6 — Strategy (#strategy)

**What the visitor sees:**
- Info callout box: "Strategy Overview" with primary tip
- Bullet list of additional strategy tips (if any exist)
- Generic fallback: "Adapt this unit to your strategy based on their stats and role."

**Data source:** `pageData.strategy_tips[]` (array of strings)

**Content ideas:**
- Mode-specific strategy: one tip for PvP, one for Co-op, one for Infinite War
- Synergy pairings: "Works great with Paladin because..."
- Upgrade priority: "Invest forge stones here before other units of this rarity"
- Formation position recommendation
- When to skip / when to invest

---

## Section 7 — Related Heroes (#related, conditional)

**What the visitor sees:**
- Card grid of 3-6 related heroes
- Each card shows: hero name + rarity + profession
- Links to `/heroes/{slug}/`

**Data source:** `pageData.related[]` with `name, slug, rarity_name, profession_name`

**Content ideas:**
- Show relationship type: "Same profession", "Same rarity", "Common strategy pair"
- Sort by relevance: most similar cost first
- Show a mini tier badge next to related hero names (if they have community ranking)

---

## Section 8 — Quick Links (#resources, always visible)

**What the visitor sees:**
- All `{profession_name}s` link → `/professions/{profession}/`
- Best `{cost_label} Cost Units` → `/guides/best-{low|mid|high}-cost-units/`
- Browse All Heroes → `/heroes/`
- `{Name} vs {Related.Name}` (compare link, auto-generated) → `/compare/{slug}-vs-{related-slug}/`
- Best Heroes for General Lineup → `/guides/best-heroes-for-general-lineup/`
- All `{Rarity} Units` → `/rarities/{rarity}-units/`
- Tools & Calculators → `/tools/`

**Data source:** Computed from `pageData.profession_name, cost, slug, related[0], rarity_name`

**Content ideas:**
- Link to the tier list page: `/tier-lists/overall/`
- Link to mode-specific tier lists if hero has mode tags
- Link to YouTube guide (via Klown Kollege if available)
- "Report incorrect data" link for community QA

---

## JSON-LD Schema (injected)

### FAQPage schema (conditional on FAQ data)

Each hero page can carry FAQPage structured data with questions matched to the most common search queries:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is {Name} good in War Inc: Rising?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{S+ Tier} — Game-Breaking. {good_for summary}"
      }
    },
    {
      "@type": "Question",
      "name": "What are {Name}'s stats?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "At level 1, {Name} has {hp} HP, {atk} ATK, {def} DEF, and {combat_power} combat power."
      }
    },
    {
      "@type": "Question",
      "name": "How much does {Name} cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{Name} costs {cost} deployment slots."
      }
    }
  ]
}
```

### BreadcrumbList schema
```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"position": 1, "name": "Home", "item": "https://..."},
    {"position": 2, "name": "Heroes", "item": "https://.../heroes/"},
    {"position": 3, "name": "{Name}"}
  ]
}
```

### CreativeWork schema (page metadata)
```json
{
  "@type": "CreativeWork",
  "name": "{Name}",
  "description": "{meta_description}",
  "about": {
    "@type": "Thing",
    "additionalProperty": [
      {"name": "Rarity", "value": "{rarity}"},
      {"name": "Profession", "value": "{profession}"}
    ]
  }
}
```

---

## Internal Linking Map

Each hero page is a **link hub** connecting to:

| Link | Target | Purpose |
|---|---|---|
| Breadcrumb Home | `/` | Site root |
| Breadcrumb Heroes | `/heroes/` | Category index |
| Stats table rows → other heroes | *(same page)* | *(no links within table)* |
| Community Rank → guide link | `/blog/{slug}/` | Cross-sell guides |
| Related heroes × 3-6 | `/heroes/{slug}/` | Internal linking depth |
| All {profession}s | `/professions/{profession}/` | Category cross-link |
| Best {cost} Cost Units | `/guides/best-{cost}-units/` | Guide cross-link |
| Browse All Heroes | `/heroes/` | Category index repeat |
| {Name} vs {Related} | `/compare/{a}-vs-{b}/` | Tool cross-link |
| Best Heroes for General Lineup | `/guides/best-heroes-for-general-lineup/` | Guide cross-link |
| All {rarity} Units | `/rarities/{rarity}-units/` | Category cross-link |
| Tools & Calculators | `/tools/` | Tool cross-link |

**Total outbound internal links:** 10-15 per page.

---

## Content Ideas Not Yet Built

- **Stat radar/spider chart**: Visual HP/ATK/DEF/Speed/Range comparison against profession average
- **Formation position viewer**: Show recommended grid placement from `lay_map_lib.json` data
- **"Best for which mode?" selector**: Tabbed view switching between PvP/Co-op/Infinite War/Hunting stats
- **Upgrade cost calculator**: Forge stones + gold needed to reach target level (links to `/tools/evolution/`)
- **Community builds**: User-submitted formation loadouts featuring this hero
- **Video embed**: Pull Klown Kollege YouTube video if hero has a dedicated spotlight
- **Change log**: Last data update date + what changed (new skill values, stat adjustments)
- **Print-friendly stat card**: Single-column printable reference sheet
