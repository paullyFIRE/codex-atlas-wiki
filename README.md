# War Inc: Rising Wiki

Live at [war-inc-rising.codex-atlas.com](https://war-inc-rising.codex-atlas.com)

Programmatic SEO blog indexing all characters, cards, entities, modes, and stats for **War Inc: Rising** (com.i89trillion.strategy.rising), a tower defense/strategy game by Fastone Games / 89Trillion.

---

## Data Source

| Field | Value |
|---|---|
| Game | War Inc: Rising |
| Package | `com.i89trillion.strategy.rising` |
| Engine | Unity 6000.0.59f2 + Il2Cpp |
| APK source | [APKPure](https://apkpure.com/war-inc-rising/com.i89trillion.strategy.rising) |
| Current version | **1.0.7** (code 1070) |
| Published | **2026-05-27** |
| XAPK size | ~727 MB |
| Split APKs | base + config.arm64_v8a + UnityDataAssetPack + UnityStreamingAssetsPack |

### Version Tracking

Data versions are tracked as `MAJOR.MINOR.PATCH` matching the game's version name (e.g. `1.0.7`). Each APK release gets its own extraction snapshot.

When a new version drops:
1. Download the new APK via `apkeep`
2. Re-run the extraction pipeline
3. Compare `data/processed/` against the previous version to detect entity changes
4. Regenerate the static site

---

## Extraction Pipeline

```
APKPure                        # 1. Download XAPK
  → apkeep
  → data/raw/_apk_source/

unzip                          # 2. Extract XAPK → split APKs
  → data/raw/_apk_extracted/

apktool d                      # 3. Decompile APK
  → data/raw/_apk_decompiled_*/

Il2CppDumper                   # 4. Dump game assemblies
  → data/raw/_il2cpp_output/
  → DummyDll/ (240 assemblies)
  → dump.cs (25K+ classes)
  → script.json (type definitions)

AssetRipper GUI                # 5. Export Unity assets
  → data/raw/unity/            (Unity project format)
  → data/raw/other-raw/        (primary content)

battle_pack_bundle.zip         # 6. Extract config JSON
  → Common/Config/*.bytes
  → parse embedded JSON
  → data/processed/config/

Unity AssetBundles             # 7. Extract localization CSV
  → localconfig_language_conf/
  → en.csv, zh.csv, etc. (16 langs)
  → data/processed/localization/

scripts/extract.sh             # 8. One-command pipeline for steps 1-4
```

### Step-by-Step

#### 1. Download APK

```bash
apkeep -a "com.i89trillion.strategy.rising@1.0.7" -d apk-pure data/raw/_apk_source/
```

#### 2. Extract XAPK

```bash
unzip data/raw/_apk_source/com.i89trillion.strategy.rising@1.0.7.xapk \
  -d data/raw/_apk_extracted/
```

#### 3. Decompile with apktool

```bash
apktool d data/raw/_apk_extracted/com.i89trillion.strategy.rising.apk \
  -o data/raw/_apk_decompiled_base/
apktool d data/raw/_apk_extracted/config.arm64_v8a.apk \
  -o data/raw/_apk_decompiled_config/
```

#### 4. Il2CppDumper (class structures)

```bash
DOTNET_ROLL_FORWARD=LatestMajor dotnet /tmp/il2cppdumper/Il2CppDumper.dll \
  data/raw/_apk_decompiled_config/lib/arm64-v8a/libil2cpp.so \
  data/raw/_apk_decompiled_base/assets/bin/Data/Managed/Metadata/global-metadata.dat \
  data/raw/_il2cpp_output/
```

#### 5. AssetRipper (Unity assets)

```bash
# Starts web UI at http://127.0.0.1:PORT
/tmp/assetripper_extracted/AssetRipper.GUI.Free --headless

# In browser:
#   1. File → Load Folder → data/raw/_apk_extracted/
#   2. Export → Unity Project → data/raw/unity/
#   3. Export → Primary Content → data/raw/other-raw/
```

#### 6. Game config JSON (battle bundle)

```bash
unzip data/raw/_apk_decompiled_assets/assets/battle_pack_bundle.zip \
  -d data/raw/_battle_bundle/
```

Then run a parser to strip prefix bytes and extract JSON from each `.bytes` file in `Common/Config/`.

#### 7. Localization CSV

```bash
# Python: open the language_conf AssetBundle as a ZIP,
# find the CSV at offset of PK\x03\x04 signature, extract all .csv files.
```

---

## Data Layout

```
data/
├── raw/                          # 3+ GB — reproducible from APK (gitignored)
│   ├── _apk_source/              # Original XAPK downloads
│   ├── _apk_extracted/           # Extracted split APKs
│   ├── _apk_decompiled_base/     # apktool output (base)
│   ├── _apk_decompiled_config/   # apktool output (config)
│   ├── _apk_decompiled_assets/   # apktool output (UnityDataAssetPack)
│   ├── _il2cpp_output/          # Il2CppDumper output (DummyDll, dump.cs, script.json)
│   ├── _battle_bundle/          # Extracted battle_pack_bundle.zip
│   ├── _assetripper_export/     # UnityPy extraction (deprecated)
│   └── unity/                    # AssetRipper Unity project export
│
└── processed/                    # 10 MB — version-controlled, canonical
    ├── config/                   # Game config JSON from battle bundle
    │   ├── card_growth_config.json   # 316 units, 10 followers, skills, upgrades
    │   ├── equip_battle_config.json  # 160 equipment with 5 tiers
    │   ├── battle_conf_lib.json      # 5+ game modes
    │   ├── battle_config.json
    │   ├── battle_synergy_config.json
    │   ├── field_buff_config.json
    │   ├── lay_map_lib.json
    │   └── layout_strategy_config.json
    ├── localization/             # 16 language CSVs
    │   ├── en.csv                # English (~8,900 keys)
    │   ├── zh.csv                # Chinese
    │   └── ...
    ├── unit_name_map.json        # 389 unit IDs → display names
    ├── hero_name_map.json        # 4 hero entries
    └── hero_names.json           # 194 cleaned display names from Avatar assets
```

---

## Entity Counts

| Entity | Count | Source |
|--------|-------|--------|
| Battle units | 316 | `card_growth_config.battleUnits` |
| Followers | 10 | `card_growth_config.followers` |
| Equipment | 160 | `equip_battle_config.equips` |
| Game modes | 5+ | `battle_conf_lib` |
| Maps | 14 | `lay_map_lib` |
| Unit names | 389 | `en.csv` (`unit_name_*` keys) |
| Localization keys | ~8,900 | `en.csv` (all strings) |
| Languages | 16 | en, zh, jp, kr, de, es, tw, ru, pt, fr, ar, th, tr, it, vi, id |

---

## Re-extraction Checklist

When a new game version is released:

```bash
# 1. Download new version
apkeep -a "com.i89trillion.strategy.rising@NEW.VERSION" -d apk-pure data/raw/_apk_source/

# 2. Determine version name/code
unzip -p data/raw/_apk_source/com.i89trillion.strategy.rising@NEW.VERSION.xapk \
  manifest.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['version_name'], d['version_code'])"

# 3. Run extraction
./scripts/extract.sh NEW.VERSION

# 4. Manual: AssetRipper export (GUI needed)
# 5. Manual: Run Python extraction for config JSONs and localization CSVs

# 6. Diff against previous version
diff -r data/processed/config/ previous_data/processed/config/
diff data/processed/unit_name_map.json previous_data/processed/unit_name_map.json
```

---

## Tools Required

| Tool | Install | Purpose |
|------|---------|---------|
| apktool | `brew install apktool` | APK decompilation |
| jadx | `brew install jadx` | DEX → Java decompilation |
| apkeep | `brew install apkeep` | APK download from APKPure |
| dotnet SDK | `dot.net/v1/dotnet-install.sh` | Runtime for Il2CppDumper |
| Il2CppDumper | GitHub release (Perfare) | C# assembly reconstruction |
| AssetRipper | GitHub release (AssetRipper/AssetRipper) | Unity asset extraction (GUI) |
| UnityPy | `pip install UnityPy` | Python Unity asset reader |
| 7zip/unzip | built-in | XAPK and ZIP extraction |

---

## Developer Commands

```bash
pnpm install          # Install dependencies
pnpm run <script>     # Run a script
./scripts/extract.sh  # Automated APK download + Il2Cpp dump
```
