# War Rising Stats Blog

## Project Goal

PSEO (Programmatic SEO) blog indexing all characters, cards, entities, modes, and stats for **War Rising** (com.i89trillion.strategy.rising). Generate wiki-style onboard pages from extracted game data to drive search traffic and ad revenue. Eventually publish guides. Strive to be the most up-to-date data source for the game.

## Data Source & Extraction

- Primary source: APK (`com.i89trillion.strategy.rising`). Download the APK and extract assets/data files (JSON, protobuf, SQLite, Lua, Unity AssetBundles, etc.) to scrape character/card/entity/stats info.
- No public API is assumed. All content comes from reverse-engineering the game binary.
- Future: scrape wikis, patch notes, or community sources to supplement.

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
```

## Content Architecture (intended)

- One page per entity (character, card, mode, etc.) — flat URL structure for SEO.
- Stats rendered from structured data files (JSON/YAML) derived from APK extraction.
- Data pipeline: `extract -> transform -> generate pages` — keep extract/transform scripts separate from the web app.

## Quirks & Conventions

- No testing framework configured yet. Add one before writing tests.
- This is a solo project; no CI/CD, linting, or formatting conventions established yet.
- Prefer static generation over SSR for SEO and hosting simplicity.
- Keep the extraction pipeline scripted and reproducible (so updates are just re-running extraction).
