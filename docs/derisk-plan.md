# Derisk Plan — War Inc: Rising Wiki (codex-atlas.com)

## Goal

Build a PSEO (Programmatic SEO) wiki indexing all characters, cards, entities, modes, and stats for War Inc: Rising (com.i89trillion.strategy.rising). Generate wiki-style onboard pages from extracted game data to drive search traffic.

## Stack Decisions

| Concern         | Decision                          |
|-----------------|-----------------------------------|
| Domain          | `war-inc-rising.codex-atlas.com`  |
| Framework       | Astro v6 (static output)          |
| Hosting         | Cloudflare Pages                  |
| Package manager | npm ^11.8.0                       |
| Module system   | ESM                               |
| APK source      | APKPure (no device)               |

---

## Phase 0 — APK Feasibility

**Goal**: Answer "can we get usable data out of the APK?" before any architecture decisions.

- Download APK from APKPure (~720 MB XAPK)
- Decompile with `apktool`
- Confirm Unity + Il2Cpp engine
- Dump Il2Cpp metadata with `Il2CppDumper`
- Extract all assets with `AssetRipper`
- Catalog data formats found (JSON, ScriptableObject, SQLite, protobuf, Lua)
- Count entities per type (heroes, towers, troops, modes, items)
- Go/no-go decision

**Deliverable**: Feasibility summary with extracted entity counts and data format assessment.

---

## Phase 1 — Data Pipeline ✅

**Goal**: Scripted, reproducible extraction from APK to clean structured data.

- `scripts/extract_all.py` — Python extraction pipeline (replaces initial `.js` plan)
- `scripts/extract_data.py` / `scripts/extract_data_v2.py` — UnityPy asset extraction
- `scripts/generate_pages.py` — Merges raw configs → `data/pages/{type}/{slug}.json`
- Entity inventory: **250 units** (161 heroes, 20 buildings, 69 special entities)

**Deliverable**: Clean JSON data files in `data/processed/` + page-ready JSON in `data/pages/`.

---

## Phase 2 — Content Prototype ✅

**Goal**: Deployable prototype with real entity data.

- Astro v6 scaffolded (static output, `npm run build` → `dist/`)
- Dynamic routes: `[slug].astro` for heroes, buildings, special entities
- Each page: breadcrumb, H1, rarity/profession, per-level stats table (12 levels), skills (with effects where available), related units, JSON-LD schema
- **259 pages generated** (161 hero + 20 building + 69 special + 9 index/home pages)
- Build time: ~600ms, output: ~1.7MB
- `wrangler.toml` configured for Cloudflare Pages

**Deliverable**: Live prototype on Cloudflare Pages with all entity types rendered.

---

## Phase 3 — Scale ✅

**Goal**: Full site with all entities indexed. Domain live on Cloudflare Pages.

- [x] Generate all entity pages (469 pages from unit_database + config files)
- [x] Category landing pages per entity type (heroes, buildings, special, equipment, buffs, synergies, modes)
- [x] Deploy to Cloudflare Pages (`wrangler pages deploy dist/`)
- [x] Custom domain `war-inc-rising.codex-atlas.com` added via Cloudflare Pages API
- [x] Add remaining entity types: equipment (160), field buffs (36), synergies (9), game modes (5)
- [x] Move followers (10 units) from /special/ to /followers/
- [x] SEO audit — key findings resolved:
  - [x] robots.txt + sitemap.xml (469 URLs) via @astrojs/sitemap
  - [x] Canonical URLs on all pages (`<link rel="canonical">`)
  - [x] Equipment stats display named values instead of raw IDs
  - [x] Related units filtered by page type (no cross-type links)
  - [x] Breadcrumb JSON-LD schema on all entity pages
  - [x] Auto-generated strategy tips (replaces "coming soon" placeholder)
  - [x] Minimal inline CSS for basic readability (tables, nav, typography)
- [x] Submit sitemap to Google Search Console (verified: resource `war-inc-rising.codex-atlas.com`)
- [x] Monitor SSL certificate provisioning for custom domain (still pending)

**Deliverable**: Live site at `war-inc-rising.codex-atlas.com` covering all game entities.

### Deploy Approach

**Current** (quick deploy via CLI):
```bash
npm run build
npx wrangler pages deploy dist/ --project-name=war-inc-rising-wiki
```
Site: `https://war-inc-rising-wiki.pages.dev`

**Future** (GitHub → Cloudflare Pages auto-deploy ✅):
1. ✅ Create GitHub repo and push: `git@github.com:paullyFIRE/codex-atlas-wiki.git`
2. ✅ `.github/workflows/deploy.yml` with cloudflare/wrangler-action
3. ✅ `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` added as GitHub secrets
4. ✅ Auto-deploy verified: every push to `main` builds + deploys via GitHub Actions

---

## Phase 4 — Ongoing

**Goal**: Stay up-to-date with game releases. Improve content depth and community integration.

- [x] **Compare pages** — 2,580 auto-generated hero matchups (`/compare/{a}-vs-{b}`)
- [x] **Profession guides** — 7 pages ranking all units by class (`/professions/warrior/`)
- [x] **Rarity tier lists** — 5 pages ranking units by rarity (`/rarities/legendary-units/`)
- [x] **External resources** — `/resources/` with Discord, YouTube, APKPure, Facebook links
- [ ] **Localize buffs/synergies/equipment**: translate 36 buffs + 9 synergies from Chinese, name 144 unnamed equipment items
- [ ] **Strategy guides**: deep-dive articles (tier lists, team comps, counters)
- [ ] **Re-extraction script**: automate version detection + re-extraction on APK update
- [ ] **Traffic + ad monitoring**: track Search Console impressions, plan ad integration

### AI Search (AEO/LLMO) Actions

| Action | Status | Impact |
|---|---|---|
| Allow AI crawlers (GPTBot, Claude-Web, CCBot) in robots.txt | ✅ Done | Citation eligibility |
| Block Google-Extended from training (still allows AI Overviews) | ✅ Done | Training opt-out |
| Upgrade hero schema: CreativeWork → VideoGame + characterAttribute | ✅ Done | Machine-readable facts for LLMs |
| Dataset schema page at `/data/` with JSON distribution links | ✅ Done | Position as canonical data source |
| Q&A-format H2 headings for AI Overview snippet capture | ✅ Done | Increases citation by AI Overviews |
| Breadcrumb JSON-LD on all pages | ✅ Done | Internal linking graph for query fan-out |
| Unique APK-extracted stats (not republished from other wikis) | ✅ Built-in | Non-commodity content LLMs prefer to cite |

---

## Key Risks

| Risk | Mitigation |
|---|---|
| Data encrypted/obfuscated | Frida runtime injection to intercept decrypted data |
| < 50 entities for PSEO | Supplement with guides, mode breakdowns, update posts |
| APK too large for frequent re-downloads | Checksum diffing; only re-extract on version change |
| Il2Cpp obfuscation | Zygisk-Il2CppDumper for runtime dump if static fails |
