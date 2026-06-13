# Asset Extraction Pipeline

## Current Portrait Status

- **21 mythic portraits** scraped from `warincrising.com` — confirmed correct, highest quality (1024×1536, transparent bg)
- **71 battleunit FBX renders** from APK's `artofwar-ii_art/fbx/battleunit/` — 512×512 3D model renders with dark green opaque bg, used as card art in game's hero collection UI
- **3 heroes still missing**: Oracle (id=643), Scarlet Spark (id=663), Bone Warlock (id=659) — no texture exists in current APK
- **19 heroes have no asset at all**: Blacksmith Warrior, Bounty Hunter, Butterfly Mage, Crystal Cat, Dark Knight, Deadly Blade, Elemental Dragon, Energy Striker, Flame Prisoner, Frost Wizard, Gaia, Guard Chario, Mech Artisan, Pharmacist, Stasis Guard, Steam Robot, Wandering Swordsman, Weakened One, Weapon Sage

## Image Sources Summary

| Source | Format | Resolution | Heroes Covered | Quality |
|---|---|---|---|---|
| Official site (`warincrising.com`) | PNG with transparent bg | 1024×1536 | 21 (mythics only) | ⭐⭐⭐⭐⭐ |
| Battleunit FBX renders (`fbx/battleunit/`) | PNG with dark green opaque bg | 512×512 | 71 | ⭐⭐⭐ |
| Texture2D `_C.png` named portraits | PNG (often sprite atlas) | varies | — | ⭐⭐ |
| Texture2D `Card_{id}.png` | PNG (card art) | varies | — | ⭐⭐ |
| Texture2D `{id}.png` raw texture | PNG (sprite sheets) | varies | — | ⭐ (wrong) |

## Battleunit Portrait Directory Structure

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

## Installed Tools & Locations

| Tool | Location | Purpose |
|---|---|---|
| mitmproxy | `brew install mitmproxy` | HTTP/HTTPS traffic interception |
| ADB | `~/Android/platform-tools/adb` (+ Homebrew) | Android Debug Bridge |
| scrcpy | `brew install scrcpy` | Screen mirroring |
| OpenCV | `pip3 install opencv-python` (4.13.0) | Image processing |
| Frida | `pip3 install frida-tools` (17.12.0) | Dynamic instrumentation |
| objection | `pip3 install objection` (1.12.5) | APK patching for SSL bypass |
| UnityPy | `pip3 install UnityPy` (1.25.0) | Unity asset extraction |
| Pillow | `pip3 install Pillow` (12.2.0) | Image processing |
| Android SDK | `~/Android/` | SDK manager, emulator, build tools |
| Android emulator | `~/Android/emulator/emulator` | API 34 Google Play AVD (`warinc_test`) |
| BlueStacks | `/Applications/BlueStacks.app` | Android emulator (Mac, Apple Silicon) |
| apktool | `brew install apktool` | APK decompilation |
| apkeep | N/A (downloaded by extract.sh) | APK download from APKPure |
| tcpdump | `/usr/sbin/tcpdump` | Packet capture |

## MITM + Frida Investigation Results

Each approach failed for fundamental reasons:

| Approach | Tested On | Result | Root Cause |
|---|---|---|---|
| System proxy + mitmproxy | Android Emulator / BlueStacks | ❌ No traffic | Game ignores system proxy (Unity native networking) |
| Frida attach | Android Emulator | ❌ `unable to access process` | Non-rooted emulator blocks ptrace |
| Frida attach | BlueStacks | ❌ `unable to access process` | Game anti-tamper protection |
| Frida spawn | BlueStacks | ❌ `InvocationTargetException` | Unity IL2CPP + anti-tamper crashes on inject |
| objection patchapk | Stock APK | ❌ Split APK signature mismatch | Game uses split APKs |
| CA cert push + `adb root` | Android Emulator | ❌ Production build | No root |
| CA cert push via `su` | BlueStacks | ❌ `su: inaccessible` | No root shell |
| tcpdump on emulator | Android Emulator | ❌ No tcpdump binary | Not available |
| `adb exec-out` raw capture | Both | ❌ Protocol fault | ADB version mismatch |

**Key insight**: Unity IL2CPP games compile C# networking to native code. Java-level Frida hooks for SSL won't work. Need native hooks (`SSL_read`/`SSL_write` in `libssl.so`). Frida needs root to attach.

## Extraction Pipeline Scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/map_images.py` | Map unit IDs to portrait images | `python3 scripts/map_images.py` |
| `scripts/generate_pages.py` | Generate page-ready JSON blobs | `python3 scripts/generate_pages.py` |
| `scripts/download_portraits.py` | Download from official site, check APK version, placeholders | `--check-version`, `--scrape`, `--placeholder` |
| `scripts/mitm_capture.py` | MITM proxy capture + analysis | `python3 scripts/mitm_capture.py --duration 300` |
| `scripts/extract.sh` | Full APK extraction (download → Il2Cpp → configs) | `./scripts/extract.sh [version]` |
| `scripts/extract_all.py` | Python extraction (configs, localization, Unity assets) | `python3 scripts/extract_all.py` |

## Asset Extraction Roadmap

### Phase 1: Native SSL Hooking + CDN Access
**Goal**: Capture the exact HTTP request headers the game sends when downloading from CDN.

**Needed**: Rooted BlueStacks instance or rooted Android emulator with Google Play Services.

1. Create rooted BlueStacks 5 Nougat instance (has root) — NOT possible on BlueStacks Air (Mac)
2. Install game, push frida-server, hook `SSL_read`/`SSL_write` in `libssl.so`
3. Capture CDN request headers → replicate in curl to download all assets

**Why native hooks**: Unity IL2CPP compiles C# to native ARM64. `UnityWebRequest` uses `libcurl` → `libssl.so`. Hooking at SSL layer catches ALL traffic.

**Estimated time**: 1-2 hours (with rooted instance)

### Phase 2: API Discovery
**Goal**: Find the game's real backend API endpoint.

Hook `connect()` in `libc.so` and `getaddrinfo` to log all outbound connections from the game. Current API at `rising.89trillion.com` returns an SPA — real API is elsewhere.

**Estimated time**: 1-2 hours

### Phase 3: Full Asset Extraction Pipeline
Automate CDN downloader, extract sprites from Unity bundles, map to unit IDs.

**Estimated time**: 2-3 hours

### Phase 4: Screenshot Automation (Fallback)
Build ADB + OpenCV script to screenshot hero detail pages from running emulator.

**Estimated time**: 2-3 hours, ~8 min per run

### Phase 5: Skill Icon Extraction
Search `_auto_extracted/Sprite/` for `Skill_Icon_*.png`, match to skill IDs from `skill_data.json`. HttpPicCache has cached 172×172 PNGs that may be skill icons.

**Estimated time**: 1 hour

### Phase 6: Spine Extraction
Extract character frames from Spine `.skel` files. Currently only UI effect skeletons found. Character skeletons may be in different bundle locations.

**Estimated time**: 3-4 hours

### Phase 7: Emulator Alternatives
| Solution | Cost | Setup | Notes |
|---|---|---|---|
| Genymotion | Free tier | 30 min | Root by default |
| Android x86 | Free | 1 hr | VM install, root by default |
| Custom AOSP build | Free | 2-3 hrs | Full control |

## Quick Reference Commands

```bash
# Start BlueStacks
open -a BlueStacks

# Connect ADB
adb connect 127.0.0.1:5555

# Frida on BlueStacks
adb -s 127.0.0.1:5555 shell /data/local/tmp/frida-server -D &
adb -s 127.0.0.1:5555 forward tcp:27042 tcp:27042
frida-ps -R

# mitmproxy
mitmweb --listen-host 0.0.0.0 --listen-port 8080 --web-port 8081

# Proxy on BlueStacks
adb -s 127.0.0.1:5555 shell settings put global http_proxy "10.0.2.2:8080"
adb -s 127.0.0.1:5555 shell settings put global http_proxy ":0"

# Install game APK with splits
adb install-multiple base.apk config.arm64_v8a.apk UnityDataAssetPack.apk

# Check game network connections
adb shell cat /proc/net/tcp | grep $(adb shell ps | grep strategy | awk '{print $2}')

# Decode hex IP (little endian)
# 0F02000A → 10.0.2.15, 40195534 → 52.85.25.64
python3 -c "ip='.'.join(str(int(h[i:i+2],16)) for i in range(6,-1,-2)); print(ip)"

# Check CloudFront reverse DNS
dig +short -x 52.85.25.64

# Regenerate all pages
python3 scripts/map_images.py && python3 scripts/generate_pages.py && npm run build
```
