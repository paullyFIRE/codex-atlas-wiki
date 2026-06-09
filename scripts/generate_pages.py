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

TYPE_MAP = {1: "heroes", 4: "bosses", 5: "special"}
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

    # Schema.org — VideoGame with characterAttribute for LLM extraction
    char_attrs = [
        {"@type": "PropertyValue", "name": "Rarity", "value": rarity_name},
        {"@type": "PropertyValue", "name": "Profession", "value": prof_name},
        {"@type": "PropertyValue", "name": "Cost", "value": str(cost)},
        {"@type": "PropertyValue", "name": "Combat Power", "value": str(combat_power)},
    ]
    lv1 = stats.get("1", {})
    if lv1.get("1050"):
        char_attrs.append({"@type": "PropertyValue", "name": "HP (Lv1)", "value": str(lv1["1050"])})
    if lv1.get("1070"):
        char_attrs.append({"@type": "PropertyValue", "name": "ATK (Lv1)", "value": str(lv1["1070"])})
    if lv1.get("1080"):
        char_attrs.append({"@type": "PropertyValue", "name": "DEF (Lv1)", "value": str(lv1["1080"])})

    schema = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": name,
        "description": f"{name} is a {rarity_name} {prof_name} in War Inc: Rising.",
        "characterAttribute": char_attrs,
        "applicationCategory": "Game",
        "operatingSystem": "Android",
        "author": {"@type": "Organization", "name": "Fastone Games"},
    }

    # Breadcrumb schema
    bc_type = TYPE_MAP.get(unit_type, "special")
    bc_label = {"heroes": "Heroes", "bosses": "Bosses", "special": "Special"}.get(bc_type, bc_type.capitalize())
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://war-inc-rising.codex-atlas.com/"},
            {"@type": "ListItem", "position": 2, "name": bc_label, "item": f"https://war-inc-rising.codex-atlas.com/{bc_type}/"},
            {"@type": "ListItem", "position": 3, "name": name},
        ],
    }

    # Auto-generated strategy tips
    strategy_tips = []
    if prof_name == "Tank":
        strategy_tips.append(f"{name} is a durable front-line unit with high HP and DEF, ideal for absorbing damage.")
        strategy_tips.append(f"Position {name} in choke points to maximize their tanking potential.")
    elif prof_name == "Warrior":
        strategy_tips.append(f"{name} is a balanced melee unit, effective in both offense and defense.")
        strategy_tips.append(f"Use {name} in the front line to deal consistent damage while holding position.")
    elif prof_name == "Assassin":
        strategy_tips.append(f"{name} excels at single-target burst damage, making them ideal for eliminating key threats.")
        strategy_tips.append(f"Deploy {name} behind tanks to protect them while they deal damage.")
    elif prof_name == "Mage":
        strategy_tips.append(f"{name} deals area magic damage, effective against groups of enemies.")
        strategy_tips.append(f"Protect {name} with front-line tanks to maximize their damage output.")
    elif prof_name == "Support":
        strategy_tips.append(f"{name} provides healing and buffs to allied units, extending their survivability.")
        strategy_tips.append(f"Keep {name} behind the front line to ensure they survive and support the team.")
    elif prof_name == "Ranger":
        strategy_tips.append(f"{name} attacks from range, dealing physical damage from a safe distance.")
        strategy_tips.append(f"Position {name} on high ground or behind walls for maximum effectiveness.")
    elif prof_name == "Special":
        strategy_tips.append(f"{name} has unique abilities that can turn the tide of battle when used correctly.")
    else:
        strategy_tips.append(f"{name} can be effective in various battle situations depending on team composition.")

    if cost and cost <= 2:
        strategy_tips.append(f"Low cost ({cost}) makes {name} easy to deploy early in battle.")
    elif cost and cost >= 5:
        strategy_tips.append(f"High cost ({cost}) means {name} should be deployed strategically when the timing is right.")

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
        "breadcrumb_schema": breadcrumb_schema,
        "strategy_tips": strategy_tips,
    }

    return page


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


# ─── Compare pages ─────────────────────────────────────────────────

def build_compare_pages(db: dict, name_map: dict, slug_map: dict) -> list:
    pages = []
    # Build list of type-1 units with names
    units = []
    for uid, u in db.items():
        if u.get("unit_type") != 1:
            continue
        name = name_map.get(str(uid)) or u.get("name_en")
        if not name:
            continue
        units.append({
            "id": u["id"],
            "name": name,
            "slug": slug_map.get(str(uid), slugify(name)),
            "rarity": u.get("rarity"),
            "profession": u.get("profession"),
            "cost": u.get("cost", 0),
            "combat_power": u.get("combat_power", 0),
            "stats": u.get("stats", {}),
        })

    # Generate top compare pages: same profession or same cost
    compared = set()
    for i, a in enumerate(units):
        for j, b in enumerate(units):
            if i >= j:
                continue
            key = tuple(sorted([a["id"], b["id"]]))
            if key in compared:
                continue
            compared.add(key)

            # Only compare same profession (targeted search queries)
            if a["profession"] != b["profession"]:
                continue

            slug = f"{a['slug']}-vs-{b['slug']}"
            name = f"{a['name']} vs {b['name']}"
            title = f"{a['name']} vs {b['name']} - Which Hero is Better? | War Inc: Rising Wiki"
            meta_desc = f"Compare {a['name']} vs {b['name']} in War Inc: Rising. Side-by-side stats, skills, and combat power analysis."

            lv1_a = a["stats"].get("1", {})
            lv12_a = a["stats"].get("12", {})
            lv1_b = b["stats"].get("1", {})
            lv12_b = b["stats"].get("12", {})

            comparison = {
                "a": {"name": a["name"], "slug": a["slug"], "hp": lv1_a.get("1050"), "atk": lv1_a.get("1070"),
                      "def": lv1_a.get("1080"), "cost": a["cost"], "power": a["combat_power"]},
                "b": {"name": b["name"], "slug": b["slug"], "hp": lv1_b.get("1050"), "atk": lv1_b.get("1070"),
                      "def": lv1_b.get("1080"), "cost": b["cost"], "power": b["combat_power"]},
            }

            pages.append({
                "slug": slug,
                "name": name,
                "title": title,
                "meta_description": meta_desc,
                "type": "compare",
                "hero_a": a,
                "hero_b": b,
                "comparison": comparison,
        })

    return pages


# ─── Cost bracket guides ───────────────────────────────────────────

def build_cost_guides(db: dict, name_map: dict, slug_map: dict) -> list:
    pages = []
    cost_brackets = [
        ("low-cost", 0, 2, "Low Cost"),
        ("mid-cost", 3, 4, "Mid Cost"),
        ("high-cost", 5, 100, "High Cost"),
    ]

    for slug_suffix, cmin, cmax, clabel in cost_brackets:
        units = []
        for uid, u in db.items():
            if u.get("unit_type") != 1:
                continue
            cost = u.get("cost", 0)
            if cost < cmin or cost > cmax:
                continue
            name = name_map.get(str(uid)) or u.get("name_en")
            if not name:
                continue
            units.append({
                "name": name,
                "slug": slug_map.get(str(uid), slugify(name)),
                "rarity_name": RARITY_MAP.get(u.get("rarity"), "Unknown"),
                "profession_name": PROFESSION_MAP.get(u.get("profession"), "Unknown"),
                "cost": cost,
                "combat_power": u.get("combat_power", 0),
            })

        units.sort(key=lambda u: -u["combat_power"])
        label = f"Best {clabel} Units"
        slug = f"best-{slug_suffix}-units"
        title = f"{label} | War Inc: Rising Wiki"
        meta_desc = f"Browse the best {clabel.lower()} units in War Inc: Rising. Top heroes costing {'-'.join(str(x) for x in [cmin, cmax])} ranked by combat power."

        pages.append({
            "slug": slug,
            "name": label,
            "title": title,
            "meta_description": meta_desc,
            "type": "guides",
            "units": units,
            "cost_min": cmin,
            "cost_max": cmax if cmax < 100 else None,
            "cost_label": clabel,
        })

    return pages


# ─── Mode hero recommendations ─────────────────────────────────────

def build_mode_guides(db: dict, name_map: dict, slug_map: dict, loc: dict) -> list:
    pages = []
    mode_data = load_json(DATA_DIR / "config" / "battle_conf_lib.json")

    for mid, mode in mode_data.items():
        mode_name = loc.get(f"game_mode_name_{mid}", f"Mode {mid}")
        slug = slugify(f"best-heroes-for-{mode_name}")

        units = []
        for uid, u in db.items():
            if u.get("unit_type") != 1:
                continue
            name = name_map.get(str(uid)) or u.get("name_en")
            if not name:
                continue
            units.append({
                "name": name,
                "slug": slug_map.get(str(uid), slugify(name)),
                "rarity_name": RARITY_MAP.get(u.get("rarity"), "Unknown"),
                "profession_name": PROFESSION_MAP.get(u.get("profession"), "Unknown"),
                "cost": u.get("cost", 0),
                "combat_power": u.get("combat_power", 0),
            })

        units.sort(key=lambda u: -u["combat_power"])

        title = f"Best Heroes for {mode_name} | War Inc: Rising Wiki"
        meta_desc = f"Top heroes for {mode_name} in War Inc: Rising. Ranked by combat power."

        pages.append({
            "slug": slug,
            "name": f"Best Heroes for {mode_name}",
            "title": title,
            "meta_description": meta_desc,
            "type": "guides",
            "mode_id": int(mid),
            "mode_name": mode_name,
            "units": units[:30],
        })

    return pages

# ─── Profession guide pages ────────────────────────────────────────

PROFESSION_MAP_GUIDES = {2: "Warrior", 3: "Tank", 4: "Assassin", 5: "Mage", 6: "Support", 7: "Ranger", 8: "Special"}

def build_profession_pages(db: dict, name_map: dict, slug_map: dict) -> list:
    pages = []
    prof_units = {p: [] for p in PROFESSION_MAP_GUIDES}

    for uid, u in db.items():
        p = u.get("profession")
        if p not in prof_units:
            continue
        name = name_map.get(str(uid)) or u.get("name_en")
        if not name:
            continue
        prof_units[p].append({
            "id": u["id"],
            "name": name,
            "slug": slug_map.get(str(uid), slugify(name)),
            "rarity": u.get("rarity"),
            "cost": u.get("cost", 0),
            "combat_power": u.get("combat_power", 0),
        })

    for p_id, units in prof_units.items():
        if not units:
            continue
        p_name = PROFESSION_MAP_GUIDES[p_id]
        slug = slugify(p_name)
        title = f"All {p_name}s - Stats and Analysis | War Inc: Rising Wiki"
        meta_desc = f"Browse all {len(units)} {p_name} units in War Inc: Rising. Compare stats, costs, and combat power rankings."

        units.sort(key=lambda u: -u["combat_power"])

        pages.append({
            "slug": slug,
            "name": f"All {p_name}s",
            "title": title,
            "meta_description": meta_desc,
            "type": "professions",
            "profession_id": p_id,
            "profession_name": p_name,
            "units": units,
        })

    return pages


# ─── Rarity tier list pages ────────────────────────────────────────

RARITY_MAP_GUIDES = {1: "Common", 2: "Rare", 3: "Epic", 4: "Legendary", 5: "Mythic"}

def build_rarity_pages(db: dict, name_map: dict, slug_map: dict) -> list:
    pages = []
    rarity_units = {r: [] for r in RARITY_MAP_GUIDES}

    for uid, u in db.items():
        r = u.get("rarity")
        if r not in rarity_units:
            continue
        name = name_map.get(str(uid)) or u.get("name_en")
        if not name:
            continue
        rarity_units[r].append({
            "id": u["id"],
            "name": name,
            "slug": slug_map.get(str(uid), slugify(name)),
            "profession": u.get("profession"),
            "cost": u.get("cost", 0),
            "combat_power": u.get("combat_power", 0),
        })

    for r_id, units in rarity_units.items():
        if not units:
            continue
        r_name = RARITY_MAP_GUIDES[r_id]
        slug = f"{slugify(r_name)}-units"
        title = f"All {r_name} Units - Stats and Tier List | War Inc: Rising Wiki"
        meta_desc = f"Browse all {len(units)} {r_name} units in War Inc: Rising. Ranked by combat power."

        units.sort(key=lambda u: -u["combat_power"])

        pages.append({
            "slug": slug,
            "name": f"All {r_name} Units",
            "title": title,
            "meta_description": meta_desc,
            "type": "rarities",
            "rarity_id": r_id,
            "rarity_name": r_name,
            "units": units,
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

    # Load card_growth to filter playable units
    cg = load_json(DATA_DIR / "config" / "card_growth.json")
    battle_units = cg.get("battleUnits", {})
    # Build set of unit IDs that are actually shown in game (canShow=True)
    shown_ids = set()
    for uid, u in battle_units.items():
        if isinstance(u, dict) and u.get("canShow") == True:
            shown_ids.add(str(u.get("id", uid)))

    print(f"Generating pages for {len(db)} units ({len(shown_ids)} playable heroes)...")

    # Filter db to only shown units (type-1) + all non-type-1
    filtered_db = {
        uid: u for uid, u in db.items()
        if u.get("unit_type") != 1 or str(uid) in shown_ids
    }
    print(f"  After filtering: {len(filtered_db)} units")

    # First pass: compute names and initial slugs for all units
    unit_names = {}
    unit_slugs = {}
    for unit_id, unit in filtered_db.items():
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
    for unit_id, unit in filtered_db.items():
        page = build_page_data(unit_id, unit, name_map, loc, skill_attrs, skill_descs, filtered_db, slug_map)
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
    print("Building equipment pages... (disabled — equipment not usable in game)")
    # Equipment page generation disabled per user request
    # for page in build_equipment_pages(loc):
    #     all_pages.append(page)

    print("Building field buff pages...")
    for page in build_buff_pages(name_map):
        all_pages.append(page)

    print("Building synergy pages...")
    for page in build_synergy_pages():
        all_pages.append(page)

    print("Building game mode pages...")
    for page in build_mode_pages(loc):
        all_pages.append(page)

    print("Building compare pages...")
    for page in build_compare_pages(filtered_db, name_map, slug_map):
        all_pages.append(page)

    print("Building profession guide pages...")
    for page in build_profession_pages(filtered_db, name_map, slug_map):
        all_pages.append(page)

    print("Building rarity tier list pages...")
    for page in build_rarity_pages(filtered_db, name_map, slug_map):
        all_pages.append(page)

    print("Building cost bracket guides...")
    for page in build_cost_guides(filtered_db, name_map, slug_map):
        all_pages.append(page)

    print("Building mode hero guides...")
    for page in build_mode_guides(filtered_db, name_map, slug_map, loc):
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
