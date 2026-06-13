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

## Data Files

All extracted data lives in `data/processed/`. These are the canonical files for page generation:

### Core Data (`data/processed/`)

| File | Contents | Key Fields |
|---|---|---|
| `config/card_growth.json` | 316 battle units + 10 followers + growth curves | `battleUnits`, `followers`, `battleGrowth`, `merge`, `skillUpgradeCost`, `unitSkillUnlock`, `combatPowerGrowth` |
| ~~`config/equip_battle.json`~~ | ~~160 equipment items, 5 tiers each~~ | ~~IGNORE — not a real game feature, leftover Unity assets~~ |
| `config/battle_conf_lib.json` | 5 game mode configs | Layout, enemy pools, card pools, rewards, synergies |
| `config/battle_config.json` | Core battle settings | `battle_config`, `formation` |
| `config/battle_synergy.json` | 9 synergy/lib definitions | `periods`, `libs` |
| `config/field_buff.json` | 36 field buffs | `libs` |
| `config/lay_map_lib.json` | 14 map layouts | Grid layouts with positions |
| `config/layout_strategy.json` | AI deployment strategies | `strategies`, `modeStrategyLibs` |
| `config/card_show_config.json` | **Unit stats + skill data** | `attrConfig` (TSV with HP/ATK/DEF/speed), `skillDescCsv` (5,761), `skillAttrCsv` (5,545) |
| `config/card_attr_config.json` | 179 unit attribute definitions | `basic` { `id`, `kind`, `threat`, `hpHeight`, `remark` } |
| `config/avatar_config.json` | Avatar/avatar frame config | `avatar`, `avatarFrame` |

### Processed Data (`data/processed/`)

| File | Contents | Count |
|---|---|---|
| `unit_database.json` | **Complete unit DB** — stats + names + skills merged | 251 units with per-level stats |
| `unit_stats.json` | Per-level unit stats (HP, ATK, DEF, speed, range, cost) | 251 units × 12 levels |
| `unit_name_map.json` | Unit ID → English display name | 389 entries |
| `hero_name_map.json` | Hero ID → full name (Caesar, Arthur, etc.) | 4 entries |
| `skill_data.json` | Unit → Skill → Level → Effect values | 441 combos across 183 units |
| `localization/en.csv` | All English UI strings (8,955 keys) | Skill names, descriptions, UI text |

### Stats Per Unit

From `card_growth.json` (per unit):
- `id`, `unitType` (1=hero, 4=building/tower, 5=special), `rarity` (1-5), `profession` (2-7)
- `combatPower`, `cost`, `atkRange` (grid coords), `levelCombatPower` (12 levels)
- `skills`, `skillsForMode`, `unlockCond`, `source`

From `card_show_config.json` `attrConfig.showAttrsLib.2` (per level, TSV):
- `1050`: HP (血量)
- `1070`: ATK (攻击)  
- `1080`: DEF (防御)
- `1090`: Attack Speed (攻速)
- `1100`: Move Speed (移速)
- `1110`: Attack Range (攻击距离)
- `35`: Weakness (自身弱点)
- `36`: Cost (水费)
- `10001`-`10003`: Tags (标签)

### Skill Data (per skill per level)

From `skillAttrCsv`:
- `1`: Charges (充能次数)
- `2`: Cooldown (冷却)
- `3`: Duration (持续时间)
- `4`: Trigger probability (触发概率)
- `5`: Skill range (技能范围)
- `8`: Skill damage (技能伤害)
- `9`: Move speed mod (移速调整)
- `10`: Attack speed mod (攻速调整)
- `11`: ATK mod (攻击力调整)
- `12`: Heal fixed (治疗固定值)
- `13`: Heal % (治疗百分比)
- `14`: Shield % (护盾比例)
- `16`: Crowd control (控制)
- `17`: Damage element (伤害属性)
- `27`: Shield value (护盾值)

### Type Mappings

```
unitType: 1=Hero/Unit, 4=Building/Tower, 5=Special
profession: 2=Warrior, 3=Tank, 4=Assassin, 5=Mage, 6=Support, 7=Ranger
rarity: 1=Common, 2=Rare, 3=Epic, 4=Legendary, 5=Mythic
```

### Page Potential (~340+ pages)

- **179 hero pages**: Name, rarity, profession, cost, per-level HP/ATK/DEF/speed, skills, combat power growth
- **55 building/tower pages**: Same stats but `unitType=4`
- **59 special pages**: Resources, mines, barracks (unitType=5)
- **10 follower pages**: Pet/troop units
- **5 game mode pages**: Rules, enemy pools, rewards
- **9 synergy pages**: Team bonus effects
- **36 buff pages**: Field modifier effects

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

## Developer Commands

```bash
pnpm install        # Install deps
pnpm add <pkg>      # Add dependency
pnpm run <script>   # Run script (check package.json)

# Full extraction pipeline (one command)
./scripts/extract.sh [version]   # APK download → Il2Cpp dump → configs → localization → Unity assets
python3 scripts/extract_all.py   # Same as above but skips APK/Il2Cpp steps
```

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

## Asset Extraction Pipeline

### Current Portrait Status
- **21 mythic portraits** scraped from `warincrising.com` — confirmed correct (21/95 heroes)
- **85 battleunit FBX renders** found in `artofwar-ii_art/fbx/battleunit/battleunit_{id}/` — these are 512×512 actual 3D model renders from the game's FBX assets. They're the character card art shown in the game's hero collection UI. They have opaque dark green backgrounds (not transparent) but are genuine character renders.
- Currently only the 21 official site images are used. The battleunit renders could provide portraits for 85 heroes but need verification first via `public/hero-images.html`.
- **19 heroes have no texture asset at all** in the current APK: Blacksmith Warrior, Bounty Hunter, Butterfly Mage, Crystal Cat, Dark Knight, Deadly Blade, Elemental Dragon, Energy Striker, Flame Prisoner, Frost Wizard, Gaia, Guard Chario, Mech Artisan, Pharmacist, Stasis Guard, Steam Robot, Wandering Swordsman, Weakened One, Weapon Sage.

### Installed Tools & Locations

| Tool | Location | Purpose | Status |
|---|---|---|---|
| mitmproxy | `brew install mitmproxy` | HTTP/HTTPS traffic interception for API/CDN discovery | ✅ Installed |
| ADB | `~/Android/platform-tools/adb` (+ Homebrew) | Android Debug Bridge for emulator/device communication | ✅ Installed |
| scrcpy | `brew install scrcpy` | Screen mirroring for Android devices | ✅ Installed |
| OpenCV | `pip3 install opencv-python` (4.13.0) | Image processing for screenshot automation | ✅ Installed |
| Frida | `pip3 install frida-tools` (17.12.0) | Dynamic instrumentation for SSL bypass, API hooking | ✅ Installed |
| objection | `pip3 install objection` (1.12.5) | APK patching for SSL pinning bypass | ✅ Installed |
| UnityPy | `pip3 install UnityPy` (1.25.0) | Python Unity asset extraction | ✅ Installed |
| Pillow | `pip3 install Pillow` (12.2.0) | Image processing | ✅ Installed |
| Android SDK | `~/Android/` | SDK manager, emulator, build tools for aapt | ✅ Installed |
| Android emulator | `~/Android/emulator/emulator` | API 34 Google Play arm64 image (`warinc_test` AVD) | ✅ Available |
| BlueStacks | `/Applications/BlueStacks.app` | Android emulator with native Google Play, runs on Mac | ✅ Installed |
| apktool | `brew install apktool` | APK decompilation and repackaging | ✅ Installed |
| apkeep | N/A (downloaded by extract.sh) | APK download from APKPure | ✅ Installed |
| tcpdump | `/usr/sbin/tcpdump` | Host-side packet capture | ✅ Installed |

### Game Server Infrastructure

Discovered via `/proc/net/tcp` analysis from the running game on the emulator:

| Service | Domain / IP | Purpose |
|---|---|---|
| Game API | `rising.89trillion.com` → `ingress.89tgame.com` → EC2 (us-west-2) | Game backend API. Returns HTTP 200 but requires auth tokens. |
| CDN | `server-*.cloudfront.net` IP range `52.85.25.x` | AWS CloudFront distribution serving game assets (portraits, configs, etc.) |
| Analytics | `1e100.net` (Google) | Firebase Analytics, Crashlytics |
| Google Services | `*.googleapis.com` | Firebase/Play Services |

API locked down — direct requests return nothing. Would need in-game session token to access.

### MITM + Frida Investigation Results

Each approach was tested and failed for fundamental reasons:

| Approach | Tested On | Result | Root Cause |
|---|---|---|---|
| System proxy + mitmproxy | Android Emulator | ❌ No traffic | Game ignores system proxy (Unity native networking stack) |
| System proxy + mitmproxy | BlueStacks | ❌ No traffic | Same — Unity bypasses system proxy |
| Frida attach (`frida -R PID`) | Android Emulator | ❌ `unable to access process` | Non-rooted emulator blocks ptrace |
| Frida attach (`frida -R PID`) | BlueStacks | ❌ `unable to access process` | Game process protected / anti-tamper |
| Frida spawn (`frida -R -f com...`) | BlueStacks | ❌ `InvocationTargetException` | Unity IL2CPP + anti-tamper crashes on inject |
| objection patchapk | Stock APK | ❌ Split APK signature mismatch | Game uses split APKs (config.arm64_v8a + UnityDataAssetPack) |
| CA cert push + `adb root` | Android Emulator | ❌ `not running in production builds` | Production build — no root |
| CA cert push via `su` | BlueStacks | ❌ `su: inaccessible` | BlueStacks also lacks root shell |
| tcpdump on emulator | Android Emulator | ❌ No tcpdump binary | Not available on device |
| `adb exec-out` raw capture | Both | ❌ Protocol fault | ADB version mismatch |

**Key insight**: Unity IL2CPP games compile C# networking code to native code. Java-level Frida hooks for SSL won't work because the game doesn't use Java SSL — it uses C# `UnityWebRequest` or `System.Net.Http.HttpClient` compiled to native ARM64 via IL2CPP. Frida would need to hook native functions (e.g., `SSL_read`/`SSL_write` in `libssl.so` or `libunity.so`), which was attempted via the `dns_hook.js` script but Frida couldn't attach to the process.

### Game CDN Investigation

The game connects to AWS CloudFront (IP range `52.85.25.x`, reverse DNS `server-*.cpt51.r.cloudfront.net`).

**CDN base URL discovered** (from `versions.json` on device):
```
https://file.89tgame.com/assets/298/Bundles/
```

Bundle manifests contain 860+ asset bundle names that are downloaded from this CDN:
- `builtin_v6_*.json` — 860 builtin asset bundles (audio, UI, art)
- `battle_v1_*.json` — 2041 battle asset bundles
- `season_v5_*.json` — 21 seasonal bundles
- `dlc_v3_*.json` — 155 DLC bundles

The CDN returns 403 without authentication. The game likely sends auth headers or uses signed URLs.

**Auth token discovered** (from app data):
```
/sdcard/Android/data/com.i89trillion.strategy.rising/files/UserInfo/UserInfo_Guest
```
JWT token: `{"alg":"HS256","typ":"JWT"}` with payload `{"uid":7841390,"iss":"gin-blog"}`

The game's API is at `ingress.89tgame.com` (the CNAME target of `rising.89trillion.com`), but returns 404 for all probed paths. The real API may use a different protocol (gRPC, WebSockets) or path.

### Scripts Reference

| Script | Purpose | Usage |
|---|---|---|
| `scripts/map_images.py` | Map unit IDs to portrait images. Currently only uses 21 official site scraped portraits. | `python3 scripts/map_images.py` |
| `scripts/generate_pages.py` | Generate page-ready JSON blobs from processed game data. Reads image map. | `python3 scripts/generate_pages.py` |
| `scripts/download_portraits.py` | Download from official site, scrape characters page for new images, check APK version, generate placeholders. | `--check-version`, `--scrape`, `--placeholder`, `--out public/images/heroes` |
| `scripts/mitm_capture.py` | MITM proxy capture + traffic analysis. Captures flows from mitmweb API, extracts domains, image URLs, API endpoints. | `python3 scripts/mitm_capture.py --duration 300` |
| `scripts/extract.sh` | Full APK extraction pipeline (download → Il2Cpp → configs → localization). | `./scripts/extract.sh [version]` |
| `scripts/extract_all.py` | Python-only extraction (configs, localization, UnityPy asset extraction). | `python3 scripts/extract_all.py` |

### Image Sources Summary

| Source | Format | Resolution | Heroes Covered | Quality |
|---|---|---|---|---|
| Official site (`warincrising.com`) | PNG with transparent bg | 1024×1536 | 21 (mythics only) | ⭐⭐⭐⭐⭐ |
| Battleunit FBX renders (`artofwar-ii_art/fbx/battleunit/`) | PNG with dark green opaque bg | 512×512 | 85 | ⭐⭐⭐ |
| Texture2D `_C.png` named portraits | PNG (often sprite atlas) | varies | 49 matched by name | ⭐⭐ |
| Texture2D `Card_{id}.png` | PNG (card art) | varies | 8 | ⭐⭐ |
| Texture2D `{id}.png` raw texture | PNG (sprite sheets) | varies | 50 | ⭐ (often wrong) |

### Battleunit Portrait Directory Structure

The most promising source for hero portraits is the FBX battleunit directory:

```
data/raw/unity/AssetRipper_export_20260609_105936/ExportedProject/Assets/
  artofwar-ii_art/fbx/
    battleunit/           ← In-game 3D model renders (512×512, opaque bg)
      battleunit_{id}/        ← Directory named by unit ID
        {Name}_C.png          ← Character portrait
        1/                    ← Variants (e.g., different skins)
          {Name}_C.png
    battleunit_ui/        ← UI card art (higher quality, 1024+)
      battleunit_{id}/
        {Name}_C.png
```

**To use battleunit portraits**: Modify `map_images.py` to scan these directories and prefer them over Texture2D _C.png files. Add a size-based quality check (battleunit images have 0% transparency with opaque bg, while sprite atlases have sparse pixel distributions).

## Asset Extraction Roadmap

### Completed Discovery
- **CDN base URL**: `https://file.89tgame.com/assets/298/Bundles/` (returns 403 without auth)
- **Auth token** (JWT): Found at `UserInfo/UserInfo_Guest` in game's app data
- **Bundle manifests**: 860+ builtin, 2041+ battle, 21 seasonal, 155 DLC bundle names
- **Battleunit portraits**: 85 hero renders in `artofwar-ii_art/fbx/battleunit/`
- **Official portraits**: 21 mythic from `warincrising.com`

### Phase 1: Native SSL Hooking + CDN Access
**Goal**: Capture the exact HTTP request headers the game sends when downloading assets from the CDN, then reuse them to download all assets directly.

**Approach**:
1. **Create a rooted BlueStacks instance** — BlueStacks 5 Nougat 64-bit with root (or BlueStacks Air if root available)
2. **Install game on rooted instance** — Install via ADB from our APK
3. **Push + run frida-server** — Frida can now attach because root bypasses anti-tamper
4. **Hook `SSL_read`/`SSL_write`** in `libssl.so` — native hook, catches ALL SSL traffic including Unity's native networking
5. **Log CDN request headers** — Capture the exact Authorization/Cookie/URL pattern
6. **Replicate headers in curl** — Download all assets from CDN directly

**Why native hooks work**: Unity IL2CPP compiles C# to native ARM64. Unity's `UnityWebRequest` uses `libcurl` which calls `libssl.so`'s `SSL_write`/`SSL_read`. Hooking at the SSL layer captures ALL traffic regardless of the game's scripting backend.

**Expected deliverables**:
- Complete asset bundle list from CDN (audio, UI, art)
- Hero portrait textures (high-res from atlas)
- Skill icons
- UI textures
- Game config updates (balance patches)

**Estimated time**: 1-2 hours

### Phase 2: API Discovery
**Goal**: Find and access the game's backend API to get live game data.

**Approach**:
1. Same rooted instance + Frida native hooks
2. Hook `connect()` in `libc.so` to log all connection attempts
3. Hook `getaddrinfo` to log all DNS lookups
4. Use captured API endpoints + JWT token to query live game data
5. Extract: hero stats, event schedules, shop items, leaderboards

**Why current API probing failed**: `rising.89trillion.com` returns an SPA (Vue.js). The real API is likely at a different path or uses a different protocol (gRPC, WebSockets, custom TCP). Frida native hooks will reveal the actual endpoints.

**Estimated time**: 1-2 hours

### Phase 3: Full Asset Extraction Pipeline
**Goal**: Automate the entire extraction pipeline from APK download → asset extraction.

**Approach**:
1. Script the CDN downloader using captured auth headers
2. Extract individual sprites from Unity atlases (UnityPy)
3. Map sprite names to unit IDs
4. Generate all hero portraits, skill icons, UI elements
5. Automate APK version detection + re-extraction on updates

**Estimated time**: 2-3 hours

### Phase 4: Screenshot Automation (Fallback)
**Goal**: If CDN/API access fails, capture portraits via screen scraping.

**Approach**:
1. Build `scripts/screenshot_capture.py` using ADB + OpenCV
2. Navigate to each hero's detail page programmatically
3. Capture portrait area using template matching
4. Save as `{unit_id}.png`
5. ~8 minutes per full scrape

**Estimated time**: 2-3 hours

### Phase 5: Skill Icon Extraction (Independent)
**Goal**: Extract skill icons from APK assets.

**Approach**:
1. Search `_auto_extracted/Sprite/` for `Skill_Icon_*.png`
2. Match filenames to skill IDs from `skill_data.json`
3. Map to hero skill pages on the wiki

Alternatively, the `HttpPicCache` on the device (at `/sdcard/.../HttpPicCache/`) has cached 172×172 PNGs that could be skill icons — need to match MD5 hashes to skill IDs.

**Estimated time**: 1 hour

### Phase 6: Spine Extraction (Optional)
**Goal**: Extract individual character frames from Spine skeletal animations.

**Approach**:
1. Find actual character `.skel` files (currently only UI effect skeletons found)
2. May be stored in different APK bundle locations
3. Use Spine runtime Python library to render specific poses
4. Extract ideal portrait frame from idle animation

**Estimated time**: 3-4 hours

### Phase 7: Emulator Alternatives (If needed)
If BlueStacks root doesn't work, these alternatives provide root out of the box:

| Solution | Cost | Setup Time | Notes |
|---|---|---|---|
| Genymotion | Free tier available | 30 min | Root by default, great for development |
| Android x86 | Free | 1 hr | Install in VM, root by default |
| Custom AOSP build | Free | 2-3 hrs | Full control, Android 14+ with root |

### Tools for Quick Reference

```bash
# Start BlueStacks
open -a BlueStacks

# Connect ADB to BlueStacks
adb connect 127.0.0.1:5555

# Start frida-server on device
adb -s 127.0.0.1:5555 shell /data/local/tmp/frida-server -D &

# Forward frida port
adb -s 127.0.0.1:5555 forward tcp:27042 tcp:27042

# Check Frida processes
frida-ps -R

# Start mitmproxy web interface
mitmweb --listen-host 0.0.0.0 --listen-port 8080 --web-port 8081

# Set/clear proxy on BlueStacks
adb -s 127.0.0.1:5555 shell settings put global http_proxy "IP:8080"
adb -s 127.0.0.1:5555 shell settings put global http_proxy ":0"

# Install game APK with splits
adb install-multiple base.apk config.arm64_v8a.apk UnityDataAssetPack.apk

# Check game network connections
adb shell cat /proc/net/tcp | grep $(adb shell ps | grep strategy | awk '{print $2}')

# Find emulator IP from hex (little endian)
# 0F02000A → 10.0.2.15
# 40195534 → 52.85.25.64
python3 -c "ip='.'.join(str(int(h[i:i+2],16)) for i in range(6,-1,-2)); print(ip)"

# Check CloudFront reverse DNS
dig +short -x 52.85.25.64

# Check game API
curl -s https://rising.89trillion.com/

# Run UnityPy extraction
python3 scripts/extract_all.py

# Regenerate all pages after data changes
python3 scripts/map_images.py && python3 scripts/generate_pages.py && npm run build
```

## Quirks & Conventions

- No testing framework configured yet. Add one before writing tests.
- This is a solo project; no CI/CD, linting, or formatting conventions established yet.
- Prefer static generation over SSR for SEO and hosting simplicity (Astro recommended).
- Keep the extraction pipeline scripted and reproducible (so updates are just re-running extraction).
- Unit stats come from `card_show_config.json` `attrConfig.showAttrsLib` as TSV embedded in JSON.
- Skill data from `skillAttrCsv` and `skillDescCsv` in the same file.
- Equipment (`equip_battle.json`) is **not** a real game feature — leftover Unity assets, ignore.
