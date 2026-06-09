# Layout Guide — War Inc: Rising Wiki

## Design Principles

- **Data-first**: Stats tables are the hero. Every stat gets visual priority.
- **Clean and fast**: Minimal CSS, no JS frameworks for pages (just Astro static output).
- **Mobile-first**: All layouts must work on mobile (most game wiki traffic is mobile).
- **SEO-driven heading hierarchy**: H1 → H2 → H3, no skipping levels.
- **Content density**: Show data efficiently — tables over paragraphs.

---

## Hero Detail Page Layout

```
┌────────────────────────────────────────────────────────────┐
│ [Home] > [Heroes] > [Hero Name]                [Search]   │  ← Breadcrumb + search
├────────────────────────────────────────────────────────────┤
│ ┌──────────┐  H1: Archer                                   │
│ │          │                                                │
│ │  Portrait│  ⭐⭐⭐⭐⭐ Rarity 1 Warrior                    │
│ │  200×200 │                                                │
│ │          │  Cost: 2  |  HP: 636  |  ATK: 42  |  DEF: 1  │  ← Infobox bar
│ │          │                                                │
│ └──────────┘  "Archer is a Common Warrior unit in           │
│                War Inc: Rising, costing 2 to deploy."       │
├────────────────────────────────────────────────────────────┤
│  H2: Stats by Level                                         │
│                                                             │
│  ┌──────┬───────┬───────┬──────┬──────┬──────┬──────────┐  │
│  │Level │  HP   │  ATK  │ DEF  │ ATK  │ Move │  Combat  │  │
│  │      │       │       │      │Speed │ Speed│  Power   │  │
│  ├──────┼───────┼───────┼──────┼──────┼──────┼──────────┤  │
│  │  1   │  636  │  42   │  1   │  1   │  2   │    97    │  │
│  │  2   │  760  │  50   │  1   │  1   │  2   │   150    │  │
│  │  3   │  910  │  60   │  1   │  1   │  2   │   226    │  │
│  │  4   │ 1180  │  70   │  1   │  1   │  2   │   327    │  │
│  │  5   │ 1530  │  80   │  1   │  1   │  2   │   458    │  │
│  │  6   │ 1990  │ 100   │  1   │  1   │  2   │   641    │  │
│  │  7   │ 2590  │ 130   │  1   │  1   │  2   │   897    │  │
│  │  8   │ 3370  │ 170   │  1   │  1   │  2   │  1211    │  │
│  │  9   │ 4380  │ 220   │  1   │  1   │  2   │  1575    │  │
│  │  10  │ 5690  │ 290   │  1   │  1   │  2   │  2047    │  │
│  │  11  │ 7400  │ 380   │  1   │  1   │  2   │  2661    │  │
│  │  12  │ 9620  │ 490   │  1   │  1   │  2   │  3460    │  │
│  └──────┴───────┴───────┴──────┴──────┴──────┴──────────┘  │
│                                                             │
│  [Show growth chart ▾]  ← optional chart toggle             │
├────────────────────────────────────────────────────────────┤
│  H2: Skills                                                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  H3: Arrow Shot                        ⚡ 2 charges  │   │
│  │  ───────────────────────────────────────────────────  │   │
│  │  A precise arrow shot dealing X damage to the         │   │
│  │  nearest enemy.                                       │   │
│  │                                                       │   │
│  │  Cooldown: 5s  |  Duration: 0s  |  Range: 3          │   │
│  │                                                       │   │
│  │  ┌──────┬────────┬────────┬────────┬─────────┐        │   │
│  │  │Level │Damage  │CD      │Charges │Effect   │        │   │
│  │  ├──────┼────────┼────────┼────────┼─────────┤        │   │
│  │  │  1   │  150   │  5s    │   2    │   -     │        │   │
│  │  │  2   │  180   │  4.5s  │   2    │   -     │        │   │
│  │  │  3   │  210   │  4s    │   2    │   -     │        │   │
│  │  │  4   │  250   │  4s    │   3    │   -     │        │   │
│  │  │  5   │  300   │  3.5s  │   3    │   -     │        │   │
│  │  └──────┴────────┴────────┴────────┴─────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  H3: Volley                            ⚡ 1 charge   │   │
│  │  ...                                                  │   │
│  └──────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────┤
│  H2: How to Use Archer                                      │
│                                                             │
│  Archer is a cheap ranged unit effective in the early       │
│  game. Best used behind tanks like [Paladin] or             │
│  [WoodenShieldGuard].                                       │
│                                                             │
│  ✅ Best in: Campaign, Arena                                │
│  ❌ Weak in: Co-op (low HP makes it vulnerable)              │
├────────────────────────────────────────────────────────────┤
│  H2: Synergies & Counters                                   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────── ─┐        │
│  │ Works Well  │  │  Counters   │  │ Countered By │        │
│  ├─────────────┤  ├─────────────┤  ├──────────────┤        │
│  │Paladin      │  │Skeleton     │  │Assassin      │        │
│  │WoodenGuard  │  │Mage         │  │ShadowNinja   │        │
│  │Priest       │  │FrostSkeleton│  │FlameMage     │        │
│  └─────────────┘  └─────────────┘  └──────────────┘        │
├────────────────────────────────────────────────────────────┤
│  H2: Related Heroes                                         │
│                                                             │
│  [Hero Card] [Hero Card] [Hero Card] [Hero Card]            │
│  [Hero Card] [Hero Card] [Hero Card] [Hero Card]            │
│  ── Same Rarity: Common ──                                  │
│  ── Same Profession: Warrior ──                             │
├────────────────────────────────────────────────────────────┤
│  Footer: Home | Heroes | Equipment | Modes | Privacy     │
│  © 2026 War Inc: Rising Wiki                                │
└────────────────────────────────────────────────────────────┘
```

---

## Index / List Page Layout

```
┌────────────────────────────────────────────────────────────┐
│  [Home] > [Heroes]                                          │
├────────────────────────────────────────────────────────────┤
│  H1: All Heroes — 179 Units                                 │
│                                                             │
│  Filter: [🔍 Search...]                                     │
│  Rarity: [All] [Common] [Rare] [Epic] [Legend] [Mythic]    │
│  Profession: [All] [Warrior] [Tank] [Assassin] [Mage] ...  │
│  Sort: [Name ▼]                                             │
│                                                             │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │Archer│  │Berserk│  │Demoman│  │Flame │  │Gunner│         │
│  │Common│  │ Rare │  │Common│  │Mage  │  │Common│         │
│  │Warrior│  │Warrior│  │Warrior│  │ Epic │  │Warrior│         │
│  │Cost:2 │  │Cost:3 │  │Cost:4 │  │Cost:5│  │Cost:3 │         │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘         │
│                                                             │
│  [Pag 1] [2] [3] ... [15]                                   │
├────────────────────────────────────────────────────────────┤
│  SEO-friendly content block describing the category         │
│  and its role in the game.                                  │
├────────────────────────────────────────────────────────────┤
│  Footer                                                    │
└────────────────────────────────────────────────────────────┘
```

### Hero Card Component

```
┌────────────────────────┐
│  [Icon 64×64]  Archer   │ ← Small portrait + name
│  ⭐ Common              │ ← Rarity tag
│  ⚔️ Warrior  💧2       │ ← Profession + cost
│                         │
│  HP 636  ATK 42  DEF 1  │ ← Key stats (Lv1)
└────────────────────────┘
```

---

## Equipment Detail Page Layout

```
┌────────────────────────────────────────────────────────────┐
│  [Home] > [Equipment] > [Equipment Name]                    │
├────────────────────────────────────────────────────────────┤
│  H1: Flaming Sword                                          │
│                                                             │
│  Type: Weapon  |  Target: Warrior  |  Max Tier: 5          │
├────────────────────────────────────────────────────────────┤
│  H2: Stats by Tier                                          │
│                                                             │
│  ┌──────┬──────────┬──────────┬──────────┬──────────┐      │
│  │ Tier │   ATK+   │   HP+    │  DEF+    │ Upgrade  │      │
│  │      │          │          │          │  Cost    │      │
│  ├──────┼──────────┼──────────┼──────────┼──────────┤      │
│  │  1   │   +15    │   +50    │   +5     │   100g   │      │
│  │  2   │   +30    │  +100    │  +10     │   250g   │      │
│  │  3   │   +50    │  +200    │  +20     │   500g   │      │
│  │  4   │   +80    │  +350    │  +35     │  1000g   │      │
│  │  5   │  +120    │  +500    │  +50     │  2000g   │      │
│  └──────┴──────────┴──────────┴──────────┴──────────┘      │
├────────────────────────────────────────────────────────────┤
│  H2: Best Heroes for this Equipment                        │
│                                                             │
│  [Hero Card] [Hero Card] [Hero Card]                        │
├────────────────────────────────────────────────────────────┤
│  H2: Related Equipment                                      │
│  [Equip Card] [Equip Card] [Equip Card]                     │
└────────────────────────────────────────────────────────────┘
```

---

## Game Mode Page Layout

```
┌────────────────────────────────────────────────────────────┐
│  [Home] > [Modes] > [Mode Name]                             │
├────────────────────────────────────────────────────────────┤
│  H1: Arena                                                  │
│                                                             │
│  Layout: 1003  |  Max Enemies: 90  |  Duration: 60 min     │
├────────────────────────────────────────────────────────────┤
│  H2: Rules                                                  │
│  Description of how this mode works.                        │
│                                                             │
│  ● Win condition: survive X waves                           │
│  ● Card pool includes Y units                               │
│  ● Special rules...                                         │
├────────────────────────────────────────────────────────────┤
│  H2: Rewards                                                │
│  ┌─────────┬───────────────────────────────────────┐        │
│  │ Wave X  │  Rewards...                           │        │
│  │ Wave Y  │  Rewards...                           │        │
│  └─────────┴───────────────────────────────────────┘        │
├────────────────────────────────────────────────────────────┤
│  H2: Best Units for Arena                                   │
│  [Hero Card] [Hero Card] [Hero Card] [Hero Card]            │
├────────────────────────────────────────────────────────────┤
│  H2: Related Modes                                          │
└────────────────────────────────────────────────────────────┘
```

---

## Visual Design Specifications

### Colors (dark theme)

```
--bg-primary:    #0f1117    /* Page background */
--bg-card:       #1a1d27    /* Card backgrounds */
--bg-table-alt:  #1e2233    /* Table row alternate */
--text-primary:  #e4e6eb    /* Main text */
--text-secondary:#8b8fa3    /* Subdued text */
--accent:        #4f8cff    /* Links, highlights */
--rarity-1:      #9d9d9d    /* Common - grey */
--rarity-2:      #2ecc71    /* Rare - green */
--rarity-3:      #9b59b6    /* Epic - purple */
--rarity-4:      #f39c12    /* Legendary - orange/gold */
--rarity-5:      #e74c3c    /* Mythic - red */
--border:        #2a2d3a    /* Borders */
--hover:         #252836    /* Hover state */
```

### Typography

```
--font-heading:  'Inter', sans-serif  (bold 700)
--font-body:     'Inter', sans-serif  (regular 400)
--font-mono:     'JetBrains Mono', monospace  (for stat numbers)

Sizes:
--text-xs:  0.75rem  (12px)  — table cells, captions
--text-sm:  0.875rem (14px)  — labels, meta info
--text-base: 1rem    (16px)  — body text
--text-lg:  1.125rem (18px)  — H3, section headers
--text-xl:  1.5rem   (24px)  — H2
--text-2xl: 2rem     (32px)  — H1
```

### Components

| Component | Description |
|---|---|
| `HeroCard.astro` | Card for index pages: icon, name, rarity, profession, cost, key stats |
| `EquipCard.astro` | Card for equipment: icon, name, tier, bonuses |
| `StatTable.astro` | Full stat table (12 levels × 6+ stats) |
| `SkillCard.astro` | Skill detail with per-level effect table |
| `Infobox.astro` | Top section: portrait, name, rarity, profession, cost, quick stats |
| `Breadcrumb.astro` | SEO breadcrumb with schema |
| `RelatedGrid.astro` | Grid of related entity cards |
| `SynergyBox.astro` | Three-column layout: works with / counters / countered by |
| `FilterBar.astro` | Filter controls for index pages |
| `GrowthChart.astro` | Optional chart of stat growth across levels |
| `SchemaHead.astro` | JSON-LD structured data injection component |

### Responsive Breakpoints

```
sm: 640px    — mobile (1 column)
md: 768px    — tablet (2 columns)
lg: 1024px   — desktop (3 columns for grids)
xl: 1280px   — wide (4 columns)
```

### Stat Table Behavior

- On mobile: stat table scrolls horizontally (overflow-x: auto)
- On desktop: full table visible
- Level 1 and Level 12 columns highlighted (first and last)
- Combat Power column optionally collapsible
- Touch-friendly row heights (min 44px tap targets)

### Accessibility

- All stat tables use proper `<th>` scope attributes
- Color is never the sole indicator (rarity has text label + color dot)
- Interactive elements have visible focus states
- Alt text on all portrait images: `"{Hero Name} portrait from War Inc: Rising"`
- Skip-to-content link for keyboard users

---

## Comparison Page Layout (`/compare/{a}-vs-{b}`)

```
┌────────────────────────────────────────────────────────────┐
│  [Home] > [Compare] > [Hero A] vs [Hero B]                  │
├────────────────────────────────────────────────────────────┤
│  H1: Caesar vs Arthur — Which Hero is Better?               │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Caesar     │  │   Arthur     │                         │
│  │  (Legendary) │  │  (Legendary) │                         │
│  │  Warrior     │  │  Tank        │                         │
│  │  Cost: 5     │  │  Cost: 6     │                         │
│  │  HP: 3200    │  │  HP: 4500    │                         │
│  │  ATK: 250    │  │  ATK: 180    │                         │
│  └──────────────┘  └──────────────┘                         │
├────────────────────────────────────────────────────────────┤
│  H2: Stat Comparison                                         │
│  ┌────────────┬────────┬────────┬─────────┐                │
│  │   Stat     │ Caesar │ Arthur │  Winner │                │
│  ├────────────┼────────┼────────┼─────────┤                │
│  │ HP (Lv12)  │ 13,500 │ 15,800 │ Arthur  │                │
│  │ ATK (Lv12) │  1,240 │    850 │ Caesar  │                │
│  │ DEF (Lv12) │    320 │    480 │ Arthur  │                │
│  │ Cost       │   5    │   6    │ Caesar  │                │
│  └────────────┴────────┴────────┴─────────┘                │
├────────────────────────────────────────────────────────────┤
│  H2: Skill Comparison                                        │
│  H3: Caesar's Skills vs Arthur's Skills                      │
├────────────────────────────────────────────────────────────┤
│  H2: Game Mode Performance                                   │
│  Caesar excels in Arena, Arthur excels in Campaign           │
├────────────────────────────────────────────────────────────┤
│  H2: Verdict                                                 │
│  Choose Caesar for offensive play, Arthur for defense.       │
└────────────────────────────────────────────────────────────┘
```
