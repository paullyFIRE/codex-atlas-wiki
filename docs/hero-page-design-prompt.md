# Hero Page — Design Prompt

Design a hero detail page for **War Inc: Rising Wiki** (`war-inc-rising.codex-atlas.com`).

Each hero has a dedicated page at `/heroes/{slug}/`. The page is a single-column scrollable layout with 8 sections. Below is exactly what the page contains, what the visitor sees, and what links are presented.

---

## Section 1 — Entity Header

- H1: hero name (large heading)
- Rarity badge: colored pill — Common / Rare / Epic / Legendary / Mythic
- Profession badge: Warrior / Tank / Assassin / Mage / Support / Ranger / Special
- Combat power: star rating (1-5 stars)
- Deployment cost: pip display (1-8 pips)

---

## Section 2 — Community Rank (only shown if hero has a ranking)

A visually prominent colored rank badge:
- **S+** = gold glow, game-breaking
- **S** = green, excellent
- **A** = blue, strong
- **B** = yellow, situational
- **C** = orange, below average
- **D** = red, weak
- **F** = dark red, never use

Below the tier: small mode tag pills showing where this hero excels (`pvp`, `clan-war`, `infinite-war`, `hunting`, `co-op`, `pve`).

---

## Section 3 — Stats by Level

A stat summary grid at top showing Level 1 values: HP / ATK / DEF / Speed / Range / Power / Cost / Move Speed (if present).

Below it: a full 12-row data table:

| Level | HP | ATK | DEF | ATK Speed | Move Speed | Range | Power |
|---|---|---|---|---|---|---|---|

Each row = one level (1-12). Numbers are right-aligned. Alternating row colors. Scrollable horizontally on mobile.

---

## Section 4 — Skills (only if hero has skills)

One card per skill, each showing:
- Skill name (H3)
- Description text
- Level effects table — dynamic columns based on the skill's stats (charges, cooldown, duration, damage, heal, shield, modifiers, etc.)

---

## Section 5 — Community Verdict (only if hero has ranking)

- A callout box colored by tier (green for top tier, yellow for mid, red for low)
- Heading: "Is {Name} good? — Community Verdict"
- 1-2 sentence summary of where they excel
- Recommended minimum level for new and mid-game players if applicable
- Strategy card: "How to use {Name}" with deployment + merge advice
- Optional link to a related blog guide

---

## Section 6 — Strategy

- Info callout: "Strategy Overview" with primary tip
- Bullet list of additional strategy tips

---

## Section 7 — Related Heroes (if related heroes exist)

Card grid showing 3-6 related heroes. Each card shows: name, rarity, profession. Links to `/heroes/{slug}/`.

---

## Section 8 — Quick Links (always present)

| Link | Goes to |
|---|---|
| All {Profession}s | `/professions/{name}/` |
| Best {Cost} Cost Units | `/guides/best-{low|mid|high}-cost-units/` |
| Browse All Heroes | `/heroes/` |
| {Name} vs {Related Hero} | `/compare/{slug}-vs-{related}/` |
| Best Heroes for General Lineup | `/guides/best-heroes-for-general-lineup/` |
| All {Rarity} Units | `/rarities/{name}-units/` |
| Tools & Calculators | `/tools/` |

---

## Visual Notes

- Brand: **War Inc: Rising Wiki** (fan wiki, not official)
- Topbar navigation: Heroes | Buildings | Bosses | Tools | Guides | Resources | Search
- Breadcrumb: Home › Heroes › {Name}
- Sticky section nav below header: Stats | Skills | Community Rank | Strategy | Related | More
- Footer: "War Inc: Rising Wiki — part of Codex Atlas. Unofficial fan site."
- Font: Cinzel (headings), Inter (body), JetBrains Mono (numbers/data)
- Site uses a dark-gold war theme with muted surfaces

---

## Content Ideas for Design Exploration

- Stat radar/spider chart comparing hero to profession average
- Formation position grid showing recommended placement
- Mode selector tabs switching stat display for PvP vs Co-op vs Infinite War
- Mini tier badge on related hero cards
- Upgrade cost calculator inline
- "Good against / weak against" callout
- Video embed slot for hero spotlights

---

## Deliverables

Design the page layout (desktop + mobile) showing all sections in vertical scroll order. Use real data for **Radiant Warrior** as the example hero:

- Mythic · Special · 8 cost · 449 power
- S+ Tier · tags: pvp, clan-war, infinite-war, hunting, co-op
- HP 9840, ATK 144, DEF 2, Speed 2, Range 1, Move 2
- 1 skill: "Radiant Shield" (shield at start of battle, scales with level)
- Related: Paladin, Frost Queen, Bone Marksman
