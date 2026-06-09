"""
Generate page-ready JSON blobs from processed game data.

Reads:  unit_database.json, unit_name_map.json, skill_data.json,
        card_show_config.json (skillAttrCsv, skillDescCsv),
        localization/en.csv

Writes: data/pages/{heroes,buildings,special,followers}/{slug}.json
        data/pages/index/{type}.json  (index page data)
"""

import json
import csv
import re
import os
import math
from pathlib import Path

DATA_DIR = Path("data/processed")
OUT_DIR = Path("data/pages")

TYPE_MAP = {1: "heroes", 4: "buildings", 5: "special"}
PROFESSION_MAP = {2: "Warrior", 3: "Tank", 4: "Assassin", 5: "Mage", 6: "Support", 7: "Ranger", 8: "Special"}
RARITY_MAP = {1: "Common", 2: "Rare", 3: "Epic", 4: "Legendary", 5: "Mythic"}
STAT_NAMES = {1050: "HP", 1070: "ATK", 1080: "DEF", 1090: "Attack Speed", 1100: "Move Speed", 1110: "Attack Range", 36: "Cost"}

# Keys in skillAttrCsv header -> semantic keys
SKILL_EFFECT_KEYS = {
    4: "charges", 5: "cooldown", 6: "duration", 7: "trigger_chance",
    8: "skill_range", 9: "attack_range", 10: "split_bullets",
    11: "damage", 12: "move_speed_mod", 13: "attack_speed_mod",
    14: "atk_mod", 15: "heal_fixed", 16: "heal_pct", 17: "shield_pct",
    18: "attribute_weaken", 19: "crowd_control", 20: "damage_element",
    21: "all_def", 22: "phys_def", 23: "wood_def", 24: "water_def",
    25: "fire_def", 26: "earth_def", 27: "wind_def",
    28: "targeting", 29: "displacement", 30: "shield_value",
}


def slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"[\s-]+", "-", name)
    return name[:50].strip("-")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def parse_skill_attrs(path: Path) -> dict:
    """Parse skillAttrCsv TSV into {(unitId, skillId, skillLv): {effect_key: value}}."""
    config = load_json(path)
    tsv = config["skillAttrCsv"]
    lines = tsv.strip().split("\n")
    if not lines:
        return {}
    result = {}
    for line in lines[1:]:
        cols = line.split("\t")
        if len(cols) < 31:
            continue
        unit_id = cols[0].strip()
        skill_id = cols[1].strip()
        skill_lv = cols[3].strip()
        key = (unit_id, skill_id, skill_lv)
        effects = {}
        for col_idx, effect_key in SKILL_EFFECT_KEYS.items():
            val = cols[col_idx].strip() if col_idx < len(cols) else "-"
            if val != "-" and val != "" and val != ".":
                effects[effect_key] = parse_num(val)
        if effects:
            result[key] = effects
    return result


def parse_num(val: str):
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


def load_localization(path: Path) -> dict:
    """Load en.csv into {key: value} dict."""
    result = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                result[row[0].strip()] = row[1].strip()
    return result


def parse_skill_descs(path: Path) -> dict:
    """Parse skillDescCsv into {(unitId, skillId, skillLv): {"tags":..., "params":...}}."""
    config = load_json(path)
    csv_text = config["skillDescCsv"]
    lines = csv_text.strip().split("\n")
    if not lines:
        return {}
    result = {}
    for line in lines[1:]:
        parts = line.split(",", 4)
        if len(parts) < 5:
            continue
        unit_id = parts[0].strip()
        skill_lv = parts[2].strip()
        skill_num = parts[1].strip()
        tags = parts[3].strip()
        params = parts[4].strip()
        result[(unit_id, skill_num, skill_lv)] = {"tags": tags, "params": params}
    return result


def build_page_data(unit_id: str, unit: dict, name_map: dict, loc: dict,
                    skill_attrs: dict, skill_descs: dict, db: dict,
                    slug_map: dict | None = None) -> dict | None:
    name = name_map.get(str(unit_id))
    if not name:
        name = unit.get("name_en")
    if not name:
        return None

    unit_type = unit.get("unit_type")
    page_type = TYPE_MAP.get(unit_type, "special")
    profession = unit.get("profession")
    rarity = unit.get("rarity")
    cost = unit.get("cost", 0)
    combat_power = unit.get("combat_power", 0)
    stats = unit.get("stats") or {}
    level_power = unit.get("level_combat_power") or {}

    slug = (slug_map or {}).get(str(unit["id"]), slugify(name))
    rarity_name = RARITY_MAP.get(rarity, "Unknown")
    prof_name = PROFESSION_MAP.get(profession, "Unknown")

    # Base stats (level 1)
    lv1 = stats.get("1", {})
    hp = lv1.get("1050", "-")
    atk = lv1.get("1070", "-")
    defense = lv1.get("1080", "-")
    speed = lv1.get("1100", "-")

    # Meta description
    meta_desc = (
        f"Learn about {name} in War Inc: Rising. "
        f"{rarity_name} {prof_name} unit costing {cost}. "
        f"HP {hp}, ATK {atk}, DEF {defense} per level, skills, and best game modes."
    )

    # Title
    title_suffix = {
        1: "Hero Stats and Skills",
        4: "Building Stats and Upgrades",
        5: "Special Entity Stats",
    }.get(unit_type, "Stats")
    title = f"{name} - {title_suffix} | War Inc: Rising Wiki"

    # Stats table
    stats_table = []
    levels = sorted(stats.keys(), key=int)
    for lv in levels:
        s = stats[lv]
        row = {
            "level": int(lv),
            "hp": s.get("1050"),
            "atk": s.get("1070"),
            "def": s.get("1080"),
            "attack_speed": s.get("1090"),
            "move_speed": s.get("1100"),
            "attack_range": s.get("1110"),
            "combat_power": level_power.get(lv, level_power.get(str(int(lv)))),
        }
        stats_table.append(row)

    # Skills
    skills_list = []
    unit_skills = unit.get("skills") or {}
    for skill_num_str, skill_ids in unit_skills.items():
        for skill_id in skill_ids:
            if not skill_id:
                continue
            skill_id_str = str(skill_id)
            # Get name and description from localization
            skill_name_key = f"unit_skill_name_{unit_id}_{skill_num_str}"
            skill_desc_key = f"unit_skill_desc_{unit_id}_{skill_num_str}"
            skill_name = loc.get(skill_name_key, f"Skill {skill_id}")
            skill_desc = loc.get(skill_desc_key, "")

            # Per-level effects
            level_effects = {}
            for lv in range(1, 13):
                lv_str = str(lv)
                effect = skill_attrs.get((str(unit_id), skill_id_str, lv_str), {})
                if effect:
                    level_effects[lv_str] = effect
                else:
                    effect = skill_attrs.get((str(unit_id), skill_id_str, lv_str), {})
                    if effect:
                        level_effects[lv_str] = effect

            # Get base level-1 effects summary
            base_effect = level_effects.get("1", {})
            max_effect = level_effects.get("12", level_effects.get(str(max([int(k) for k in level_effects.keys()] + [1])))) if level_effects else {}

            # Build skill description from effects
            effect_lines = []
            for ek, ev in base_effect.items():
                effect_lines.append(f"{ek}: {ev}")

            skills_list.append({
                "skill_id": skill_id,
                "skill_number": int(skill_num_str),
                "name": skill_name,
                "description": skill_desc,
                "level_effects": level_effects,
            })

    # Sort skills by skill_number
    skills_list.sort(key=lambda s: s["skill_number"])

    # Related units (same page type + same rarity or profession)
    related = []
    if rarity or profession:
        for other_id, other in db.items():
            if other_id == unit_id:
                continue
            # Only relate same page type (hero↔hero, building↔building, etc.)
            other_type = other.get("unit_type")
            if other_type != unit_type:
                continue
            score = 0
            if rarity and other.get("rarity") == rarity:
                score += 1
            if profession and other.get("profession") == profession:
                score += 1
            if score > 0:
                other_name = name_map.get(str(other_id)) or other.get("name_en", "")
                if other_name:
                    related.append({
                        "id": other["id"],
                        "name": other_name,
                        "slug": (slug_map or {}).get(str(other["id"]), slugify(other_name)),
                        "rarity": other.get("rarity"),
                        "profession": other.get("profession"),
                        "unit_type": other.get("unit_type"),
                        "combat_power": other.get("combat_power", 0),
                        "relevance": score,
                    })
        related.sort(key=lambda r: (-r["relevance"], -r["combat_power"]))
        related = related[:12]

    # Schema.org
    schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": name,
        "description": f"{name} is a {rarity_name} {prof_name} in War Inc: Rising.",
        "about": {
            "@type": "Thing",
            "name": f"{name} - War Inc: Rising Unit",
            "additionalProperty": [
                {"@type": "PropertyValue", "name": "Rarity", "value": rarity_name},
                {"@type": "PropertyValue", "name": "Profession", "value": prof_name},
                {"@type": "PropertyValue", "name": "Cost", "value": str(cost)},
            ],
        },
    }

    page = {
        "id": unit["id"],
        "slug": slug,
        "name": name,
        "title": title,
        "meta_description": meta_desc,
        "type": page_type,
        "unit_type": unit_type,
        "rarity": rarity,
        "rarity_name": rarity_name,
        "profession": profession,
        "profession_name": prof_name,
        "cost": cost,
        "combat_power": combat_power,
        "atk_range": unit.get("atk_range", []),
        "stats_table": stats_table,
        "skills": skills_list,
        "related": related,
        "schema": schema,
    }

    return page


def main():
    print("Loading data sources...")
    db = load_json(DATA_DIR / "unit_database.json")
    name_map = load_json(DATA_DIR / "unit_name_map.json")
    loc = load_localization(DATA_DIR / "localization" / "en.csv")

    print("Parsing skill attributes...")
    skill_attrs = parse_skill_attrs(DATA_DIR / "config" / "card_show_config.json")

    print("Parsing skill descriptions...")
    skill_descs = parse_skill_descs(DATA_DIR / "config" / "card_show_config.json")

    # Track pages per type for index data
    index_data = {t: [] for t in ["heroes", "buildings", "special", "followers"]}
    # Track followers separately (unit_type null with profession null or special handling)
    follower_ids = set()

    print(f"Generating pages for {len(db)} units...")

    # First pass: compute names and initial slugs for all units
    unit_names = {}
    unit_slugs = {}
    for unit_id, unit in db.items():
        name = name_map.get(str(unit_id)) or unit.get("name_en")
        if not name:
            continue
        unit_names[str(unit_id)] = name
        unit_slugs[str(unit_id)] = slugify(name)

    # Deduplicate slugs
    slug_counts = {}
    for uid, slug in unit_slugs.items():
        slug_counts[slug] = slug_counts.get(slug, 0) + 1

    slug_counters = {}
    slug_map = {}
    for uid, slug in unit_slugs.items():
        final_slug = slug
        if slug_counts[slug] > 1:
            slug_counters[slug] = slug_counters.get(slug, 0) + 1
            final_slug = f"{slug}-{slug_counters[slug]}"
        slug_map[uid] = final_slug

    # Second pass: build all pages with resolved slug map
    all_pages = []
    for unit_id, unit in db.items():
        page = build_page_data(unit_id, unit, name_map, loc, skill_attrs, skill_descs, db, slug_map)
        if not page:
            continue

        # Override slug with deduplicated version
        page["slug"] = slug_map.get(str(unit["id"]), page["slug"])

        # Normalize type for null unit_type
        if unit.get("unit_type") is None:
            uid_int = unit.get("id") or (int(unit_id) if str(unit_id).isdigit() else 0)
            if 2001 <= uid_int <= 2010:
                page["type"] = "followers"
            else:
                page["type"] = "special"

        all_pages.append(page)

    # Write pages
    count = 0
    index_data = {}
    for page in all_pages:
        page_type = page["type"]
        page_dir = OUT_DIR / page_type
        page_dir.mkdir(parents=True, exist_ok=True)

        with open(page_dir / f"{page['slug']}.json", "w") as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
        count += 1

        if page_type not in index_data:
            index_data[page_type] = []
        index_data[page_type].append({
            "id": page["id"],
            "name": page["name"],
            "slug": page["slug"],
            "rarity": page["rarity"],
            "rarity_name": page["rarity_name"],
            "profession": page["profession"],
            "profession_name": page["profession_name"],
            "cost": page["cost"],
            "combat_power": page["combat_power"],
            "unit_type": page["unit_type"],
        })

    # Write index files
    for page_type, items in index_data.items():
        index_dir = OUT_DIR / page_type
        index_dir.mkdir(parents=True, exist_ok=True)
        with open(index_dir / "_index.json", "w") as f:
            json.dump({"type": page_type, "count": len(items), "items": items}, f, indent=2, ensure_ascii=False)

    # Build the count summary
    summary = {t: len(index_data[t]) for t in index_data if index_data[t]}
    print(f"\nDone! {count} pages generated:")
    for t, c in summary.items():
        print(f"  {t}: {c}")


# ─── Equipment pages ───────────────────────────────────────────────

def build_equipment_pages(loc: dict) -> list:
    equip_data = load_json(DATA_DIR / "config" / "equip_battle.json")
    equips = equip_data.get("equips", {})
    pages = []

    for eid, equip in equips.items():
        eid_str = str(eid)
        name = loc.get(f"equip_name_{eid_str}", f"Equipment {eid}")
        slug = slugify(name)

        # Dedup equipment slugs
        # (handled by caller)

        levels = equip.get("levels", [])
        stats_by_tier = []
        for lv_data in levels:
            buffs = []
            for buff in lv_data.get("buffs", []):
                buffs.append({
                    "stat": buff.get("buffId"),
                    "value": buff.get("buffVal"),
                })
            stats_by_tier.append({
                "tier": lv_data.get("lv"),
                "buffs": buffs,
            })

        target_camp = equip.get("targetCamp", 0)
        camp_name = {0: "Neutral", 1: "Camp 1", 2: "Camp 2", 3: "Camp 3"}.get(target_camp, f"Camp {target_camp}")

        meta_desc = f"{name} is a {camp_name} equipment in War Inc: Rising with {len(stats_by_tier)} upgrade tiers."
        title = f"{name} - Equipment Stats and Tiers | War Inc: Rising Wiki"

        # Schema
        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": name,
            "description": f"{name} equipment for War Inc: Rising.",
            "about": {
                "@type": "Thing",
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Tiers", "value": str(len(stats_by_tier))},
                    {"@type": "PropertyValue", "name": "Target Camp", "value": camp_name},
                ],
            },
        }

        pages.append({
            "id": int(eid) if isinstance(eid, (int, float)) else hash(str(eid)),
            "slug": slug,
            "name": name,
            "title": title,
            "meta_description": meta_desc,
            "type": "equipment",
            "equip_id": eid_str,
            "target_camp": target_camp,
            "camp_name": camp_name,
            "stats_by_tier": stats_by_tier,
            "schema": schema,
        })

    return pages


# ─── Field Buff pages ──────────────────────────────────────────────

BUFF_STAT_NAMES = {
    1050: "HP", 1070: "ATK", 1080: "DEF", 1090: "Attack Spd",
    1100: "Move Spd", 1110: "Range",
}


def build_buff_pages(name_map: dict) -> list:
    fb_data = load_json(DATA_DIR / "config" / "field_buff.json")
    libs = fb_data.get("libs", {})
    pages = []

    for bid, buff_entry in libs.items():
        remark = buff_entry.get("remark", "")
        # Extract English name from remark or use ID-based name
        # The remark is Chinese; use unit names from referenced buffs for description
        name = f"Field Buff {bid}"
        slug = slugify(f"field-buff-{bid}")

        buff_units = []
        for b in buff_entry.get("buffs", []):
            uid = str(b.get("unitId", ""))
            unit_name = name_map.get(uid, f"Unit {uid}")
            buff_units.append({
                "unit_id": uid,
                "unit_name": unit_name,
                "unit_level": b.get("unitLv", 1),
            })

        meta_desc = f"Field buff {bid} in War Inc: Rising. {remark}"
        title = f"Field Buff {bid} - Battle Modifier | War Inc: Rising Wiki"

        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": name,
            "description": f"Field buff {bid} in War Inc: Rising.",
        }

        pages.append({
            "id": int(bid),
            "slug": slug,
            "name": name,
            "title": title,
            "meta_description": meta_desc,
            "type": "buffs",
            "buff_id": int(bid),
            "remark": remark,
            "style": buff_entry.get("style"),
            "affected_units": buff_units,
            "schema": schema,
        })

    return pages


# ─── Synergy pages ─────────────────────────────────────────────────

def build_synergy_pages() -> list:
    syn_data = load_json(DATA_DIR / "config" / "battle_synergy.json")
    libs = syn_data.get("libs", {})
    pages = []

    for sid, lib in libs.items():
        remark = lib.get("remark", "")
        name = f"Synergy {sid}"
        slug = slugify(f"synergy-{sid}")

        # Extract layBuffs for affected units/effects
        lay_buffs = lib.get("layBuffs", [])
        effects = []
        for lb in lay_buffs:
            lv_configs = lb.get("lvConfig", [])
            for lv_cfg in lv_configs:
                conds = lv_cfg.get("conds", [])
                effects.append({
                    "cond_type": conds[0].get("condType") if conds else None,
                    "options": conds[0].get("options", []) if conds else [],
                })

        meta_desc = f"Synergy {sid} in War Inc: Rising. {remark}"
        title = f"Synergy {sid} - Team Bonus Effect | War Inc: Rising Wiki"

        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": name,
            "description": f"Synergy {sid} in War Inc: Rising.",
        }

        pages.append({
            "id": int(sid),
            "slug": slug,
            "name": name,
            "title": title,
            "meta_description": meta_desc,
            "type": "synergies",
            "synergy_id": int(sid),
            "remark": remark,
            "effects": effects,
            "schema": schema,
        })

    return pages


# ─── Game Mode pages ───────────────────────────────────────────────

def build_mode_pages(loc: dict) -> list:
    mode_data = load_json(DATA_DIR / "config" / "battle_conf_lib.json")
    pages = []

    for mid, mode in mode_data.items():
        name = loc.get(f"game_mode_name_{mid}", f"Game Mode {mid}")
        slug = slugify(name)

        mini_rule = mode.get("miniGameRule", {})
        loot = mode.get("lootChest", {})
        drops = mode.get("dropRewards", [])

        meta_desc = f"{name} is a game mode in War Inc: Rising. Learn the rules, rewards, and strategies."
        title = f"{name} - Rules, Rewards, and Strategy | War Inc: Rising Wiki"

        # Extract rewards summary
        reward_summary = []
        for drop in (drops or []):
            reward_summary.append({
                "type": drop.get("dropType"),
                "id": drop.get("dropId"),
                "count": drop.get("dropNum"),
            })

        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": name,
            "description": f"{name} game mode in War Inc: Rising.",
        }

        pages.append({
            "id": int(mid),
            "slug": slug,
            "name": name,
            "title": title,
            "meta_description": meta_desc,
            "type": "modes",
            "mode_id": int(mid),
            "layout_id": mode.get("layoutId"),
            "mini_game_rule": mini_rule,
            "rewards": reward_summary,
            "schema": schema,
        })

    return pages


def main():
    print("Loading data sources...")
    db = load_json(DATA_DIR / "unit_database.json")
    name_map = load_json(DATA_DIR / "unit_name_map.json")
    loc = load_localization(DATA_DIR / "localization" / "en.csv")

    print("Parsing skill attributes...")
    skill_attrs = parse_skill_attrs(DATA_DIR / "config" / "card_show_config.json")

    print("Parsing skill descriptions...")
    skill_descs = parse_skill_descs(DATA_DIR / "config" / "card_show_config.json")

    print(f"Generating pages for {len(db)} units...")

    # First pass: compute names and initial slugs for all units
    unit_names = {}
    unit_slugs = {}
    for unit_id, unit in db.items():
        name = name_map.get(str(unit_id)) or unit.get("name_en")
        if not name:
            continue
        unit_names[str(unit_id)] = name
        unit_slugs[str(unit_id)] = slugify(name)

    # Deduplicate slugs
    slug_counts = {}
    for uid, slug in unit_slugs.items():
        slug_counts[slug] = slug_counts.get(slug, 0) + 1

    slug_counters = {}
    slug_map = {}
    for uid, slug in unit_slugs.items():
        final_slug = slug
        if slug_counts[slug] > 1:
            slug_counters[slug] = slug_counters.get(slug, 0) + 1
            final_slug = f"{slug}-{slug_counters[slug]}"
        slug_map[uid] = final_slug

    # Second pass: build all unit pages with resolved slug map
    all_pages = []
    for unit_id, unit in db.items():
        page = build_page_data(unit_id, unit, name_map, loc, skill_attrs, skill_descs, db, slug_map)
        if not page:
            continue

        page["slug"] = slug_map.get(str(unit["id"]), page["slug"])

        if unit.get("unit_type") is None:
            uid_int = unit.get("id") or (int(unit_id) if str(unit_id).isdigit() else 0)
            if 2001 <= uid_int <= 2010:
                page["type"] = "followers"
            else:
                page["type"] = "special"

        all_pages.append(page)

    # Build new entity type pages
    print("Building equipment pages...")
    for page in build_equipment_pages(loc):
        all_pages.append(page)

    print("Building field buff pages...")
    for page in build_buff_pages(name_map):
        all_pages.append(page)

    print("Building synergy pages...")
    for page in build_synergy_pages():
        all_pages.append(page)

    print("Building game mode pages...")
    for page in build_mode_pages(loc):
        all_pages.append(page)

    # Write pages
    count = 0
    index_data = {}
    for page in all_pages:
        page_type = page["type"]
        page_dir = OUT_DIR / page_type
        page_dir.mkdir(parents=True, exist_ok=True)

        with open(page_dir / f"{page['slug']}.json", "w") as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
        count += 1

        if page_type not in index_data:
            index_data[page_type] = []
        index_data[page_type].append({
            "id": page.get("id", 0),
            "name": page["name"],
            "slug": page["slug"],
        })

    # Write index files
    for page_type, items in index_data.items():
        index_dir = OUT_DIR / page_type
        index_dir.mkdir(parents=True, exist_ok=True)
        with open(index_dir / "_index.json", "w") as f:
            json.dump({"type": page_type, "count": len(items), "items": items}, f, indent=2, ensure_ascii=False)

    summary = {t: len(index_data[t]) for t in index_data if index_data[t]}
    print(f"\nDone! {count} pages generated:")
    for t, c in summary.items():
        print(f"  {t}: {c}")
    print(f"  Total: {count}")


if __name__ == "__main__":
    main()
