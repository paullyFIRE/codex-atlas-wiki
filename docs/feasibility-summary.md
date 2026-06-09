# Phase 0 — Feasibility Summary

## Status: ✅ GO — Data is extractable

---

## What We Did

| Step | Status | Details |
|------|--------|---------|
| Download APK | ✅ | 727 MB XAPK from APKPure via `apkeep` |
| APK decompilation | ✅ | apktool — confirmed Unity + Il2Cpp |
| Il2Cpp dump | ✅ | 240 dummy DLLs, 25K classes, full C# struct dump |
| Asset exploration | ✅ | Found 1,241+ unit entities, config tables, battle data |
| AssetRipper export | ⚠️ | Needs browser interaction (see below) |

---

## What We Found

### Game Engine
- **Unity** with **Il2Cpp** code compilation
- Unity version: ~2022+ (based on metadata version 31)
- Split APK: base APK (42 MB) + config (188 MB) + Unity assets (497 MB)

### Entity Counts
| Entity Type | Count |
|-------------|-------|
| Units (game_mode_0) | 396 |
| Units (game_mode_4) | 401 |
| Units (game_mode_14) | 285 |
| Units (game_mode_26) | 159 |
| **Total units** | **1,241+** |

### Game Modes Found
- game_mode_0 — likely Campaign/World Road
- game_mode_4 — likely PvP/Arena
- game_mode_14 — likely Co-op
- game_mode_26 — likely Infinite War / special event

### Config Data Files (in Common/Config/)
| File | Contents |
|------|----------|
| `battle_config` | Core battle parameters |
| `battle_conf_lib` | Battle configuration library |
| `battle_synergy_config` | Synergy/bonus effects between units |
| `card_growth_config` | Card upgrade/evolution data |
| `equip_battle_config` | Equipment stats and battle effects |
| `field_buff_config` | Field buffs and modifiers |
| `lay_map_lib` | Map layout library |
| `layout_strategy_config` | AI/deployment strategies |

### Data Storage Pattern
- Stats stored in **Unity serialized ScriptableObjects** (`.bytes` files)
- Use **CSV-based table system** (`CsvTable.dll`) for data-driven content
- **protobuf** for network communication
- **SQLCipher** present (encrypted local storage, not needed for extraction)
- Data is NOT encrypted or obfuscated — standard Unity serialization

### Key Assemblies (from Il2Cpp dump)
| Assembly | Purpose |
|----------|---------|
| `Assembly-CSharp.dll` | Main game logic |
| `CsvTable.dll` | CSV data table system |
| `com.i89.sws.dll` | Custom framework |
| `battle.sim.logic.dll` | Battle simulation |
| `CardView.dll` | Card display system |

---

## AssetRipper Export (Manual Step)

AssetRipper runs as a **web UI** (browser-based). To export all assets:

```bash
# Start AssetRipper headless
/tmp/assetripper_extracted/AssetRipper.GUI.Free --headless

# Open the displayed URL in a browser
# Then: File > Load Folder > select data/raw/_apk_extracted/
# Then: Export > Export All Files > choose data/raw/_assetripper_export/
```

This step is only needed once per APK version — the exported data feeds the transformation scripts.

---

## Entity Inventory Summary

After AssetRipper export, the following entity types are expected:

1. **Heroes/Characters** — stat blocks with damage, health, abilities, skills
2. **Equipment** — weapon types, stat bonuses, upgrade paths
3. **Cards** — gacha card definitions, growth curves
4. **Units/Troops** — combat stats, type, faction, synergy
5. **Game Modes** — campaign, PvP, co-op, infinite war, etc.
6. **Field Buffs** — temporary modifiers and effects
7. **Battles** — wave configurations, enemy spawns
8. **Synergies** — team composition bonuses

---

## Go/No-Go: ✅ GO

**Reasons to proceed:**
- Data is structured, serialized via standard Unity format
- No encryption or obfuscation found
- Large entity count (1,241+) — sufficient for PSEO
- No existing wiki/fansite — first-mover opportunity
- Update-friendly: pipeline is APK diff + re-export
- 2.9M downloads, active community — real audience

**Reasons to be cautious:**
- AssetRipper extraction requires manual browser step (minor)
- Need to write custom transform scripts to parse Unity serialized data
- Game is relatively new (Dec 2024) — future content expansion likely

---

## Next Steps (Phase 1)

1. Run AssetRipper export manually (5 min browser session)
2. Write `scripts/extract.js` to automate APK download
3. Write `scripts/transform.js` to normalize exported data to JSON
4. Build entity inventory with page potential per type
