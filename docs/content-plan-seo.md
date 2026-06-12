# War Inc: Rising — Content Plan & SEO Strategy

> Generated 2026-06-12 from Klown Kollege knowledge base (62 videos)

---

## 1. Current Site Audit

### What's Already Built (1,158 pages)

| Category | Pages | Status |
|---|---|---|
| Heroes | 95 | ✅ Built |
| Buildings | 36 | ✅ Built |
| Special entities | 23 | ✅ Built |
| Followers | 10 | ✅ Built |
| Hunting bosses | 20 | ✅ Built |
| Compare pages | 857 | ✅ Built |
| Buffs | 36 | ✅ Built |
| Synergies | 9 | ✅ Built |
| Modes | 5 | ✅ Built |
| Tier lists | 12 | ✅ Built |
| Guides | 8 | ✅ Built |
| Professions | 7 | ✅ Built |
| Rarities | 5 | ✅ Built |
| Blog posts | 16 | ✅ Built |
| Tools | 3 | ✅ Built |

### Note: Equipment Ignored

The `equip_battle.json` file in `data/processed/config/` contains leftover Unity assets — **equipment is not a feature in War Inc: Rising**. Do not build `/equipment/` pages. Remove the broken `/equipment/` link from the resources page.

### Data Gap: Missing Heroes

Only 95 heroes published vs ~179 expected. Check `card_growth.json` for more `unitType=1` entries not yet extracted.

---

## 2. SEO Opportunity Analysis

### Current Performance (from GSC data)
- 2 clicks, 21 impressions in first 3 days
- Only 1 page ranking: `/tier-lists/overall/` at position 3.52
- Traffic from Japan + US (mobile only)

### Keyword Opportunity Space

Using the knowledge base, here are high-value keyword clusters:

#### Cluster 1: Troop Rankings (Highest Intent)
```
war inc rising tier list              ← already ranking
war inc rising best troops
war inc rising troop rankings 2026
war inc rising S tier units
war inc rising best mythic priority
war inc rising radiant warrior vs frost queen
war inc rising necromancer review
war inc rising bone marksman build
war inc rising oracles worth it
war inc rising best epic troops
war inc rising best rare troops
war inc rising best common troops
```

**Strategy**: Publish weekly-updated tier list pages. Add per-troop "is this unit good?" sections on hero pages that incorporate Klown Kollege rankings.

#### Cluster 2: Gem Spending (Commercial Intent)
```
war inc rising gem guide
war inc rising what to spend gems on
war inc rising wheel vs card master
war inc rising card master strategy
war inc rising wheel guide
war inc rising best value purchases
war inc rising fusion guide
war inc rising how to get bombs
```

**Strategy**: Dedicated gem guide page + individual articles for each spending method.

#### Cluster 3: Clan War (Informational + Commercial)
```
war inc rising clan war guide
war inc rising clan war strategy
war inc rising dragon strategy
war inc rising ruler guide
war inc rising rope a dope technique
war inc rising clan war trials
war inc rising clan war formation
```

**Strategy**: Complete clan war guide series (8-10 articles).

#### Cluster 4: Beginner Guides (Top of Funnel)
```
war inc rising beginner guide
war inc rising what to do first
war inc rising best formation
war inc rising how to get gold fast
war inc rising co op strategy
war inc rising building guide
war inc rising castle upgrade priority
war inc rising forge stone guide
```

**Strategy**: Ultimate beginner guide (pillar page) + supporting articles.

#### Cluster 5: Game Modes
```
war inc rising infinite war guide
war inc rising hunting guide
war inc rising dragon clash guide
war inc rising pvp guide
war inc rising lucky dice strategy
war inc rising exchange shop guide
```

**Strategy**: Individual guides for each game mode.

#### Cluster 6: News & Updates (Freshness Signals)
```
war inc rising weekly update
war inc rising new troops
war inc rising forge stone discount
war inc rising event calendar
```

**Strategy**: Regular update posts timed with game events.

#### Cluster 7: Specific Troop Guides
```
war inc rising light seeker build
war inc rising necromancer build
war inc rising ripple wizard guide
war inc rising woodland guardian guide
war inc rising best heroes for PvP
war inc rising best heroes for clan war
war inc rising best heroes for infinite war
war inc rising best heroes for hunting
```

**Strategy**: Add "best for [mode]" sections to existing hero pages + mode-specific tier lists.

---

## 3. Content Plan (Prioritized)

### Phase 1: Quick Wins (This Week) — ✅ DONE

| Priority | Action | Status |
|---|---|---|
| 🔴 P0 | **Publish Ultimate Gem Guide** — synthesize Klown Kollege gem advice into canonical guide | ✅ Done (850 words) |
| 🔴 P0 | **Publish Full Troop Tier List 2026** — expand existing tier list with community rankings | ✅ Done (950 words) |
| 🟡 P1 | **Publish Complete Beginner Guide** — pillar page covering first 30 days | ✅ Done (1,150 words) |
| 🟡 P1 | **Add "is X good?" snippets** to top 20 hero pages using Klown Kollege rankings | ✅ Done (43 hero pages) |
| 🟡 P1 | **Fix broken `/equipment/` link** on resources page | ✅ Done |

### Phase 2: Depth (Next 2 Weeks) — ✅ DONE

| Priority | Action | Status |
|---|---|---|
| 🟡 P1 | **Clan War Guide Series** (5 articles): pillar guide + Dragon, Ruler, Formations, Recruitment | ✅ Done (3,680 words total) |
| 🟡 P1 | **Mode-Specific Tier Lists**: Best troops for Infinite War, Hunting, PvP | ✅ Done (3 articles) |

### Troop Spotlight Series (Month 2-3)

Deep-dive articles on specific top-tier troops. Each covers: stats, skill breakdown, optimal level, best game modes, synergies, formation placement, forge stone priority, and community verdict.

| Priority | Spotlight | Target Keyword |
|---|---|---|
| 🟡 P1 | **Necromancer Deep Dive** | `war inc rising necromancer guide` |
| 🟡 P1 | **Light Seeker / Pretty Boy Guide** | `war inc rising light seeker` |
| 🟡 P1 | **Bone Marksman Guide** | `war inc rising bone marksman` |
| 🟡 P1 | **Radiant Warrior Guide** | `war inc rising radiant warrior` |
| 🟡 P1 | **Oracles Guide** | `war inc rising oracles` |
| 🟢 P2 | **Ripple Wizard Guide** | `war inc rising ripple wizard` |
| 🟢 P2 | **Frost Queen Guide** | `war inc rising frost queen` |
| 🟢 P2 | **Goddess of War Guide** | `war inc rising goddess of war` |
| 🟢 P2 | **Bomber Guide** | `war inc rising bomber guide` |
| 🟢 P2 | **Poison Master Guide** | `war inc rising poison master` |

Each spotlight targets a specific troop name search with commercial intent (how to get, should I invest). Use the existing `community_rankings.json` data and KB transcripts as source material.

### Phase 3: Scale (Month 2)

| Priority | Action | Expected Impact |
|---|---|---|
| 🟡 P1 | **Weekly update blog posts** — recap game changes, new troops, events | Freshness signals for Google, returning visitor capture |
| 🟢 P2 | **Tool pages**: Forge stone calculator, Fusion checker, Wheel/Card Master ROl calculator | High-value interactive content, backlink bait |
| 🟢 P2 | **Hero ranking updates** — monthly re-ranking reflecting game balance changes | Topical authority, repeat visitors |

---

## 4. Programmatic SEO Recommendations

### 4.1 Hero Page Enhancements

Current hero pages have stats + skills but lack community knowledge. Add:

- **"Is X Good?" section** with Klown Kollege ranking (S/A/B/C/D/F)
- **"Best For" tags** — mark which modes this hero excels in
- **"Synergy With"** — suggest heroes that combo well
- **"How To Get"** — wheel, card master, fusion, recruitment
- **"Recommended Level"** — minimum viable level from community wisdom
- **"Skip or Invest"** verdict

This can be done programmatically by adding a `community_rankings.json` data file that maps hero IDs to rankings, then rendering it on each hero page.

### 4.2 Compare Pages Enhancement

857 compare pages exist but are purely stat-based. Enhance with:
- Community verdict on which is better
- Head-to-head in different game modes
- Auto-generated "X vs Y: Which Should You Build?" content

### 4.4 Auto-Generated Blog Content

Use the data pipeline to auto-generate:
- "Top 10 {Profession} Heroes for {Month} {Year}"
- "Best {Rarity} Units Ranked"
- "War Inc Rising {Month} Meta Report"

### 4.5 New Page Templates

| Template | Data Source | Est. Pages | Priority |
|---|---|---|---|
| `/guides/gem-spending/` | Knowledge base | 1 | 🔴 P0 |
| `/guides/beginners/` | Knowledge base | 1 | 🟡 P1 |
| `/guides/clan-war/` | Knowledge base | 8 | 🟡 P1 |
| `/guides/troop-spotlights/` | Knowledge base + data | 10+ | 🟢 P2 |
| `/meta/monthly-rankings/` | Scripted from data | Monthly | 🟢 P2 |
| `/tools/forge-calc/` | Custom build | 1 | 🟢 P2 |

### 4.6 Internal Linking Strategy

```
Current: Hero page → Profession page → Rarity page
Add:     Hero page → Guide page (gem, beginner, clan war)
Add:     Hero page → Tier list page
Add:     Guide page → Related hero pages (linked in text)
Add:     Guide page → Tool pages
Add:     Tier list → Individual troop guide → Hero page
```

The goal is a **topic cluster** model where:
- Pillar page (e.g., "Gem Guide") links to cluster content (e.g., "Wheel vs Card Master")
- Cluster content links back to pillar page
- Hero pages link to relevant guides
- Guides link to relevant hero pages

### 4.7 Structured Data Enhancements

Current: VideoGame + FAQPage + BreadcrumbList schemas per page.

Add:
- **Article schema** for guides and blog posts
- **HowTo schema** for guides with steps
- **Product schema** for in-game items (with `offers` for gem cost)
- **ItemList schema** for tier lists and rankings
- **FAQPage** expansion on hero pages (current: 3-4 questions → add "What level should I upgrade X?", "Is X good for PvP?", "Is X good for clan war?")

### 4.8 Image SEO

Current: Fixed `og-default.svg` for all pages.
- Generate unique OG images per hero/entity showing name, rarity, profession
- Add descriptive `alt` text to all troop images from `unit_name_map.json`
- Generate tier list images with actual troop icons arranged by tier

---

## 5. Technical SEO Checklist

| Item | Status | Action |
|---|---|---|
| Sitemap | ✅ Auto-generated | Verify it includes all new pages |
| robots.txt | ✅ Good | Review monthly |
| Canonical URLs | ✅ Per-page | Verify on new templates |
| Meta descriptions | ✅ Dynamic | Add mode-specific templates for guides |
| OG images | ⚠️ Static fallback | Generate per-entity OG images |
| Page speed | ❓ Not measured | Run Lighthouse after next build |
| Mobile optimized | ✅ Responsive design | Verify new templates |
| Core Web Vitals | ❓ Not measured | Add monitoring |
| Analytics | ⚠️ Placeholder only | Connect GTM/GA |
| Search Console | ✅ Verified | Add new sitemaps after new sections |

---

## 6. Measurement & KPIs

### Month 1 Targets
- Index 200+ pages in Google (from current ~1)
- 50+ organic clicks/month
- Top 10 ranking for 5+ keywords
- Zero broken internal links

### Month 3 Targets
- 500+ pages indexed
- 500+ organic clicks/month
- Top 5 ranking for "war inc rising tier list"
- Top 10 ranking for "war inc rising gem guide"
- Equipment pages fully indexed

---

## 8. SEO Research — Keywords & Content Opportunities

### Methodology
Google autocomplete scraped (30 prefixes), DuckDuckGo SERPs checked for 6 head queries, competitive landscape analyzed (warinc-tools.vercel.app, writerparty.com, warincrising.com, clashiverse.com, bluestacks.com, gamingonphone.com).

### Top Keywords by Search Demand

| Prefix | Autocomplete Signals (count) | High-Intent Queries |
|---|---|---|
| `best` | 15 | best units, best lineup, best use of gems, best mythical, best troops |
| `how` | 15 | how to get forge stones, how to get stamps, how to transcend, how to upgrade command center, how to join a clan, how to spend gems |
| `tier` | 13 | tier list 2026, co-op tier list, troop tier list, mythical tier list, arena tier list |
| `guide` | 15 | fusion guide, strategy guide, arena guide, formation guide, co-op guide, pvp guide, beginner guide |
| `co-op` | 15 | co-op guide, co-op strategy, co-op tips, co-op transcend, co-op wheel, co-op tier list |
| `fusion` | 8 | fusion guide (strong), fusion guide pdf, fusion guide reddit |
| `arena` | 10 | arena tier list, arena guide, arena formation, arena strategy, arena rewards |
| `reddit` | 15 | review, codes, cheats, tips, strategy, tier list, forge stones, fusion guide |
| `battle drills` | 14 | battle drills level 2/3/6/7/8, battle drills guide, battle drills walkthrough |
| `formation` | 9 | formation guide, best formation strategy, arena formation, sturdy formation |
| `hero` | 6 | hero tier list, best hero |
| `mythic` | 5 | mythical tier list, best mythical |
| `dragon` | 3 | dragon raid, dragon clash |
| `clan war` | 4 | clan war map |
| `hunting` | 2 | clan hunt |
| `transcend` | 6 | co-op transcend, unlock transcend, how to transcend |
| `spells` | 2 | how to use spells |
| `summon` | 3 | limited summon, limited vs permanent summon |
| `upgrade` | 3 | upgrade command center, upgrade guide |

### Content Gap Analysis (Opportunities by Difficulty)

#### 🟢 Easy Wins (no SERP competition, 0-2 thin results)

| Keyword | Why It's a Gap | Existing Content |
|---|---|---|
| `war inc rising battle drills level 2/3/6/7/8` | Multiple level-specific searches, zero guides | ❌ None |
| `war inc rising how to transcend` | Strong autocomplete signal, no dedicated guide | ❌ None (mentioned in beginner guide) |
| `war inc rising how to use spells` | People searching, no standalone guide | ❌ None |
| `war inc rising fusion guide` | Strong signal + "pdf" modifier = high intent | ❌ None (mentioned in beginner guide) |
| `war inc rising limited vs permanent summon` | Direct comparison query, no content | ❌ None |
| `war inc rising upgrade command center` | Specific how-to, zero guides | ❌ None |
| `war inc rising how to join a clan` | Basic info need, no dedicated page | ❌ None (clan war guide exists but not this) |
| `war inc rising arena rewards` | People want to know what they get | ❌ None |
| `war inc rising sturdy formation` | Specific formation name search | ❌ None |
| `war inc rising co-op wheel` | Game mechanic specific query | ❌ None |

#### 🟡 Medium Opportunity (some competition, but fragmented)

| Keyword | Existing competitors | Our Angle |
|---|---|---|
| `war inc rising arena guide` | writerparty.com (thin), YouTube | Data-driven formation analysis + tier list |
| `war inc rising best lineup` | YouTube videos, clashiverse | Combo of mode-specific + data-backed |
| `war inc rising how to spend gems` | writerparty.com (section), YouTube | Already have gem guide — optimize for this exact query |
| `war inc rising formation guide` | warincrising.com (thin), YouTube | Use KB formations + lay_map data |
| `war inc rising co-op guide` | warincrising.com (thin page), YouTube | Already have co-op guide — expand + optimize |
| `war inc rising arena tier list` | warinc-tools (interactive), BlueStacks | Unique: mode-specific + KB community rankings |
| `war inc rising best mythical` | YouTube, writersparty | Data-driven ranking with community verdict |
| `war inc rising best troops` | BlueStacks tier list, clashiverse | Our site specifically targets "troops" language |
| `war inc rising mythical tier list` | warinc-tools, YouTube | Same as above |

#### 🔴 Hard (established competitors)

| Keyword | Dominant competitor | Our strategy |
|---|---|---|
| `war inc rising guide` | writerparty.com (strong all-in-one) | Niche down — win specific sub-topics |
| `war inc rising tier list` | warinc-tools.vercel.app (interactive tools + calculators) | Differentiate with KB community data, mode-specific lists, hero pages |
| `war inc rising beginner guide` | clashiverse.com, bluestacks.com, gamingonphone.com | Already published — needs optimization |

### Competitive Landscape

| Competitor | Strengths | Weaknesses | Pages Indexed |
|---|---|---|---|
| **warinc-tools.vercel.app** | Interactive tools (calculator, tier list maker), modern UI | No prose content, no hero pages, thin on SEO | ~10 |
| **writerparty.com** | Strong all-in-one guide, early mover (Nov 2025), good keyword coverage | Single page, no entity pages, stale | ~5 |
| **warincrising.com** | Official game domain, guide sections | Thin content, low effort, few pages | ~15 |
| **clashiverse.com** | Modern site, beginner guide, team building guide | 2 articles only, narrow scope | ~5 |
| **bluestacks.com** | High domain authority | Generic content, not game-specific depth | ~2 |
| **gamingonphone.com** | Decent domain | Thin beginner guide only | ~2 |

### Recommended Priority Content (New)

Based on gap analysis, build these next (ordered by effort vs. impact):

| Priority | Page | Target Keyword | Why Now |
|---|---|---|---|
| 🔴 P0 | **Battle Drills Walkthrough (all levels)** | `war inc rising battle drills level 6` (repeat per level) | **Zero competition**, multiple level-specific searches, easy to produce |
| 🔴 P0 | **How to Transcend Guide** | `war inc rising how to transcend` | Strong signal, no dedicated content, KB has info |
| 🟡 P1 | **Fusion Guide** | `war inc rising fusion guide` | High intent (searching for PDF!), already have partial content |
| 🟡 P1 | **Limited vs Permanent Summon Comparison** | `war inc rising limited vs permanent summon` | Direct comparison query, zero competition |
| 🟡 P1 | **How to Use Spells Guide** | `war inc rising how to use spells` | Clear info need, zero guides |
| 🟡 P1 | **Arena Guide (rewards + strategy)** | `war inc rising arena guide` | Multiple related autocomplete signals |
| 🟢 P2 | **Best Mythical Heroes (expanded)** | `war inc rising best mythical` | Already have data, expand into dedicated page |
| 🟢 P2 | **Upgrade Command Center Guide** | `war inc rising upgrade command center` | Specific how-to, no competition |
| 🟢 P2 | **How to Join a Clan** | `war inc rising how to join a clan` | Basic info need, easy win |
| 🟢 P2 | **Sturdy Formation Guide** | `war inc rising sturdy formation` | Specific formation, easy with KB data |

### SEO Quick Wins (Minimal Effort)

1. **Title tag optimization**: Page titles currently use "War Inc: Rising Wiki" — change to "War Inc: Rising" (removing "Wiki") to match exact brand search
2. **H1 audit**: Ensure each hero page H1 matches the unit name verbatim (Google uses H1 for snippets)
3. **FAQ schema on existing guides**: Add FAQ structured data to beginner/gem/clan war guides for People Also Ask eligibility
4. **Internal linking**: Add "Related Guides" section to blog posts linking to relevant hero pages
5. **Battle drills keywords**: Even without dedicated pages, add "battle drills" mentions to existing progression/co-op guides to capture partial traffic

### Unique Differentiators vs Competitors

- **Data-driven**: Only site with per-level unit stats from APK extraction
- **Community-sourced**: KB rankings give us authenticity no other site has
- **Entity depth**: 96 hero pages (soon 100+) — no competitor has individual hero pages
- **Topic clusters**: Clan war series (5 articles) with pillar + cluster model

### Month 6 Targets (Updated)
- All data-driven pages indexed (1,300+)
- 2,000+ organic clicks/month
- Top 5 ranking for 20+ keywords
- 10+ referring domains (backlinks)
- Regular weekly update posts

---

## 7. Files to Create

### Data Files
```
data/pages/community_rankings.json       ← Hero → Tier mapping from KB
data/pages/guide-content.json            ← Guide page content from KB
```

### New Page Templates
```
src/pages/equipment/[slug].astro          ← 160 equipment pages
src/pages/guides/gem-spending.astro       ← Gem guide
src/pages/guides/beginners.astro          ← Beginner guide
src/pages/guides/clan-war/[slug].astro    ← Clan war series (8 pages)
src/pages/guides/troop-spotlights/[slug].astro ← Troop spotlight series
```

### Enhanced Templates
```
src/pages/heroes/[slug].astro             ← Add community ranking + mode tags
src/pages/tier-lists/[slug].astro         ← Expand with mode-specific variants
src/pages/compare/[slug].astro            ← Add community verdict
```
