# Derisk Plan — War Inc: Rising Stats Blog

## Goal

Build a PSEO (Programmatic SEO) blog indexing all characters, cards, entities, modes, and stats for War Inc: Rising (com.i89trillion.strategy.rising). Generate wiki-style onboard pages from extracted game data.

## Stack Decisions

| Concern         | Decision               |
|-----------------|------------------------|
| Framework       | Astro                  |
| Hosting         | Cloudflare Pages       |
| Package manager | pnpm ^11.0.8           |
| Module system   | ESM                    |
| APK source      | APKPure (no device)    |

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

## Phase 1 — Data Pipeline

**Goal**: Scripted, reproducible extraction from APK to clean structured data.

- `scripts/extract.js` — automate APK download + extraction
- `scripts/transform.js` — normalize raw exports into clean JSON
- Entity inventory (count by type, assess page potential)

**Deliverable**: Clean JSON data files in `data/processed/` + entity inventory.

---

## Phase 2 — Content Prototype

**Goal**: Deployable prototype with real entity data.

- Scaffold Astro project (`pnpm create astro`)
- One template per entity type
- SEO foundation:
  - Flat slug structure
  - Per-page meta tags + canonical URLs
  - Schema.org structured data (Game, Character, Item)
  - Auto-generated sitemap + robots.txt
- Measure build time vs projected entity count

**Deliverable**: Live prototype on Cloudflare Pages with 1-2 entity types rendered.

---

## Phase 3 — Scale

**Goal**: Full site with all entities indexed.

- Generate all entity pages
- Category landing pages per entity type
- Deploy to Cloudflare Pages (build config, caching, redirects)
- SEO audit (validators, Core Web Vitals, indexability)

**Deliverable**: Live site covering all current game entities.

---

## Phase 4 — Ongoing

**Goal**: Stay up-to-date with game releases.

- Re-extraction script with APK version change detection
- Strategy guides layered on stat data
- Google Search Console + traffic + ad monitoring

---

## Key Risks

| Risk | Mitigation |
|---|---|
| Data encrypted/obfuscated | Frida runtime injection to intercept decrypted data |
| < 50 entities for PSEO | Supplement with guides, mode breakdowns, update posts |
| APK too large for frequent re-downloads | Checksum diffing; only re-extract on version change |
| Il2Cpp obfuscation | Zygisk-Il2CppDumper for runtime dump if static fails |
