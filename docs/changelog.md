# Changelog

## 2026-06-17 — Hero page title rewrites for CTR; GTM/GA investigation

- **Updated** hero page meta titles across all 95 heroes: `{Name} - Hero Stats and Skills` → `{Name} Stats & Guide` — shorter, more scan-friendly, targets "X stats" and "X guide" search intents
- **Why**: GSC data showed hero pages ranking at positions 2–4 getting 0 clicks. Old titles were generic and indistinguishable in SERP. New format is 10 chars shorter per title, drops the hyphens for visual scanning, and uses "& Guide" to signal actionable content.
- **Expected impact**: Improved CTR from hero page SERP listings, especially mobile where display space is tighter. Desktop may remain low due to SERP feature competition (knowledge panels).
- **Source**: GSC export `war-inc-rising.codex-atlas.com_-Performance-on-Search-2026-06-17.zip` — 23 clicks, 301 impressions, 7.64% overall CTR. Hero pages at positions 2–4 with 0 clicks: goblin-warrior (pos 1.5), iron-bulwark (2.6), gaia (2.3), frost-wizard (2.8), royal-archer (3.2), swordsman (3.0), and 12 others.
- **Note**: GTM/GA confirmed live on site. June 14 impression drop to 7 likely weekend effect / early-site volatility, not meta rewrite related.

## 2026-06-17 — 3 troop guide videos indexed into blog guides + hero video sections

- **Added** `war-inc-rising-common-troops-guide` — Beginner tips for common troops: level 7 power spike, Swordsman vs Demoman, Archer vs Gunner, when to use commons
- **Added** `war-inc-rising-rare-troops-guide` — Rare troop evaluations: Forest Scout priority, Flail Warden vs Goblin Warrior, Goblin Chef (beats level 6 mythic), Paladin + Radiant Warrior combo, Bomber and Frost Skeleton utility
- **Added** `war-inc-rising-epic-troops-guide` — Epic troop playability thresholds, Oracle priority #1, Poison Master Infinite War carry, Bone Warlock + Bone Gunner synergy, Rockthrower niche vs Frost Queen, Woodland Wizard healer
- **Added** `video_guides` section to 26 hero pages — Each relevant hero (Swordsman, Archer, Oracle, Bone Warlock, etc.) now shows a Video Guide section with embedded YouTube advice from the transcripts
- **Updated** `src/pages/heroes/[slug].astro` — Added Video Guide section rendering with play_circle icon, linked YouTube titles, and transcribed advice
- **Updated** `docs/klown-kollege/00-index.md` — Added 3 external videos (#63-65) to index, updated transcript count
- **Updated** `docs/klown-kollege/04-troop-guides.md` — Added Epic Troop Guide section with playability thresholds and per-troop evaluations
- **Saved transcripts** — Raw transcripts saved to `docs/klown-kollege/transcripts/Epic_Troop_Guide.md`, `Rare_Troop_Guide.md`, `Common_Troops_Beginner_Tips.md`
- **Source**: 3 YouTube videos (external channel) — Epic Troop Guide, Rare Troop Guide, Beginner Tips: Common Troops
- **Why**: These are the most comprehensive troop-specific guides available, covering playability thresholds, forge stone priorities, multi-unit vs single-unit mechanics, and per-troop evaluations
- **Expected impact**: New blog guides target "common troops guide," "rare troops War Inc," and "epic troop guide" keywords. Hero page video sections increase time-on-page and provide actionable advice alongside stat data.

## 2026-06-14 — Beginner guide expanded; 3 new blog guides

- **Updated** `war-inc-rising-beginner-guide` — Added 5 new sections: Account Setup (linking, invite codes), Auto-Display team builder, Castle/Command Center explanation (grid expansion 3×3→7×6), Wood management (co-op farming priority), and Understanding RNG (skill proc probabilities). Fixed fusion advice to distinguish low-tier (gold only) vs mystic-tier (450 gems efficient). Updated FAQ with 5 new questions. Word count 2,630→3,380.
- **Added** `war-inc-rising-gem-farming-guide` — Complete breakdown of daily, weekly, and bi-weekly gem sources with F2P and P2P monthly totals
- **Added** `war-inc-rising-fusion-system-guide` — Fusion mechanics, exact costs per tier, the 7 fusion mystics ranked, level-up math, bulk vs individual fusion strategy
- **Added** `war-inc-rising-roulette-vs-fusion-guide` — Breakpoint-by-breakpoint cost analysis of the Roulette, comparison vs fusion at every spending level, stage-by-stage progression path
- **Source**: Transcripts from Gulhdan YouTube channel (@Gulhdan-warinc) — 5 Spanish-language guides covering gem economy, fusion, roulette, co-op, and beginner progression
- **Why**: Filled beginner guide gaps in account setup, team building, and game mechanics. Added gem farming guide (no existing coverage of earning side). Added fusion system guide (existing merge guide advises against gem fusion — different meta context).
- **Expected impact**: Improved beginner guide comprehensiveness reduces bounce rate. New guides target "how to get gems," "fusion guide," and "roulette vs fusion" keywords.
