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

TYPE_MAP = {1: "heroes", 4: "hunting-bosses", 5: "special"}
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


# IDs of units that are player-constructible buildings (type=5 special entities)
BUILDING_IDS = {101, 104, 201, 203, 601, 3010, 3011, 3012, 3023, 3024, 3025,
                3034, 3036, 3037, 3038, 3054, 3055, 3056, 3057, 3058, 3059,
                3060, 3061, 3062, 3068, 3021, 3022, 3026, 3027, 3028, 3029,
                3030, 3031, 3032, 3033, 3035}


def build_page_data(unit_id: str, unit: dict, name_map: dict, loc: dict,
                    skill_attrs: dict, skill_descs: dict, db: dict,
                    slug_map: dict | None = None,
                    image_map: dict | None = None) -> dict | None:
    name = name_map.get(str(unit_id))
    if not name:
        name = unit.get("name_en")
    if not name:
        return None

    unit_type = unit.get("unit_type")
    page_type = TYPE_MAP.get(unit_type, "special")
    profession = unit.get("profession")
    rarity = unit.get("rarity")
    if rarity is None:
        rarity = 0
    cost = unit.get("cost", 0)
    if cost is None:
        cost = 0
    combat_power = unit.get("combat_power", 0)
    if combat_power is None:
        combat_power = 0
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

    # Meta description - compelling hook to drive CTR
    hooks = {
        1: "stats per level, skills analysis and strategy guide for",
        4: "building stats, upgrade costs and strategy guide for",
        5: "special entity stats, mechanics and strategy guide for",
    }
    hook = hooks.get(unit_type, "guide for")
    power_str = f" Combat power {combat_power}." if isinstance(combat_power, (int, float)) and combat_power > 0 else ""
    meta_desc = (
        f"{name} is a {rarity_name.lower()} {prof_name.lower()} in War Inc: Rising. "
        f"Complete {hook} {name} — HP {hp}, ATK {atk}, DEF {defense}, {power_str}"
        f" skills, best formations and game mode performance."
    )
    if unit_type == 1 and rarity_name == "Common":
        meta_desc = (
            f"Is {name} worth using in War Inc: Rising? Complete guide for this "
            f"{rarity_name.lower()} {prof_name.lower()} — HP {hp}, ATK {atk}, DEF {defense},"
            f" skills and whether to invest resources."
        )
    if unit_type == 1 and rarity_name == "Rare":
        meta_desc = (
            f"{name} rare troop guide for War Inc: Rising. "
            f"HP {hp}, ATK {atk}, DEF {defense}, skills per level, best game modes "
            f"and forge stone investment analysis."
        )
    if unit_type == 1 and rarity_name in ("Epic", "Legendary", "Mythic"):
        meta_desc = (
            f"{name} — {rarity_name} {prof_name} guide for War Inc: Rising. "
            f"Complete stats, skills breakdown, best formations and "
            f"{'forge stone priority' if rarity_name in ('Epic', 'Legendary') else 'team synergies'}."
        )

    # Title — shortened suffix for better SERP CTR
    # Heroes use "Stats & Guide" replacing wordy "Hero Stats and Skills"
    if unit_type == 1:
        title = f"{name} Stats & Guide | War Inc: Rising Wiki"
    else:
        title_suffix = {
            4: "Building Stats and Upgrades",
            5: "Special Entity Stats",
        }.get(unit_type, "Stats")
        title = f"{name} — {title_suffix} | War Inc: Rising Wiki"

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

    # FAQPage schema — 3-4 common questions per hero (conversational tone)
    faq_items = [
        {
            "@type": "Question",
            "name": f"Is {name} good in War Inc: Rising?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Yes — {name} is a {rarity_name.lower()} {prof_name.lower()} with a cost of {cost} and {'impressive' if combat_power > 500 else 'solid' if combat_power > 200 else 'reasonable'} combat power. {'They excel in most game modes and team compositions.' if combat_power > 500 else 'They perform well in the right setup.' if combat_power > 200 else 'They\'re a solid choice for early to mid-game progression.'}"
            },
        },
        {
            "@type": "Question",
            "name": f"What does {name} do best?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{name} is a {prof_name.lower()} unit. {'Put them on the frontline to absorb damage and protect your team.' if prof_name == 'Tank' else 'Use them for melee damage and holding the front line.' if prof_name == 'Warrior' else 'They burst down high-priority targets like enemy mages and marksmen.' if prof_name == 'Assassin' else 'They deal area magic damage from a safe position — great against grouped enemies.' if prof_name == 'Mage' else 'They heal and buff your team, keeping everyone alive longer.' if prof_name == 'Support' else 'They attack from range, dealing physical damage safely.' if prof_name == 'Ranger' else 'They bring unique utility that can swing fights in your favor.'}"
            },
        },
        {
            "@type": "Question",
            "name": f"How much does {name} cost to deploy?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{name} costs {cost} Elixir. {'That\'s cheap — you can deploy them early to build pressure.' if cost <= 2 else 'That\'s a mid-range cost, fitting well into most team compositions.' if cost <= 4 else 'That\'s expensive — deploy them when the timing is right for maximum impact.'}"
            },
        },
    ]
    if rarity >= 4:
        faq_items.append({
            "@type": "Question",
            "name": f"How to get {name} in War Inc: Rising?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{name} is a {rarity_name.lower()} rarity unit. You can get them through summoning, events, and special banners. {'Save gems for limited summon events — they offer the best rates for Mythic heroes.' if rarity == 5 else 'Permanent summon is reliable for adding Legendary heroes over time.' if rarity == 4 else 'Keep an eye on event shops and special offers for this rarity.'}"
            },
        })
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_items,
    }

    # Breadcrumb schema
    bc_type = TYPE_MAP.get(unit_type, "special")
    bc_label = {"heroes": "Heroes", "buildings": "Buildings", "hunting-bosses": "Hunting Mode Bosses", "special": "Special"}.get(bc_type, bc_type.capitalize())
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://war-inc-rising.codex-atlas.com/"},
            {"@type": "ListItem", "position": 2, "name": bc_label, "item": f"https://war-inc-rising.codex-atlas.com/{bc_type}/"},
            {"@type": "ListItem", "position": 3, "name": name},
        ],
    }

    # Auto-generated strategy tips - player-first tone
    strategy_tips = []

    # Lead with the player's goal - what can this hero do for you?
    if prof_name == "Tank":
        if cost and cost >= 5:
            strategy_tips.append(f"Need someone to absorb big hits? {name} is your wall — high HP and DEF for holding the line against heavy attackers.")
        else:
            strategy_tips.append(f"Need a reliable frontline? {name} soaks up damage with high HP and DEF so your damage dealers can work safely.")
    elif prof_name == "Warrior":
        strategy_tips.append(f"Need a melee unit that can both deal damage and take hits? {name} balances offense and defense, making them flexible in any formation.")
    elif prof_name == "Assassin":
        strategy_tips.append(f"Need to delete a specific enemy fast? {name} focuses on single-target burst damage — great for taking out enemy backline carries.")
    elif prof_name == "Mage":
        strategy_tips.append(f"Need to clear groups of enemies? {name} deals area magic damage that shreds clustered units. Keep them protected behind your frontline.")
    elif prof_name == "Support":
        strategy_tips.append(f"Need your team to survive longer? {name} heals and buffs nearby allies, keeping your key units in the fight.")
    elif prof_name == "Ranger":
        strategy_tips.append(f"Need safe ranged damage? {name} attacks from distance, dealing physical damage without risking direct engagement.")
    elif prof_name == "Special":
        strategy_tips.append(f"Need a wildcard? {name} has unique abilities that can swing a fight when used at the right moment.")
    else:
        strategy_tips.append(f"{name} fits into various team compositions — experiment to find their best role.")

    # Positioning advice based on cost
    if cost and cost <= 2:
        strategy_tips.append(f"Low deployment cost ({cost}) means you can drop {name} early to start building pressure fast.")
    elif cost and cost >= 5:
        strategy_tips.append(f"High cost ({cost}) means timing matters — deploy {name} when they can make an immediate impact rather than rushing them out.")

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
        "faq_schema": faq_schema,
        "breadcrumb_schema": breadcrumb_schema,
        "strategy_tips": strategy_tips,
        "image": None,
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
            title = f"{a['name']} vs {b['name']} - Which Unit is Better? | War Inc: Rising Wiki"
            meta_desc = f"Compare {a['name']} vs {b['name']} in War Inc: Rising. Side-by-side unit stats, skills, and combat power analysis."

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


# ─── Building upgrade data ─────────────────────────────────────────

ITEM_NAMES = {102: "Gems", 103: "Coins", 121: "Wood", 205: "Timber I", 305: "Timber II", 405: "Timber III",
              705: "Rock I", 805: "Rock II", 905: "Rock III",
              1205: "Metal I", 1305: "Metal II", 1405: "Metal III"}


def load_building_upgrades() -> tuple:
    """Load buildings.json and resourceBd, return lookup maps keyed by building type ID."""
    try:
        bd = load_json(DATA_DIR / "config" / "buildings.json")
    except FileNotFoundError:
        return {}, {}

    bd_map = {}
    for b in bd.get("buildings", []):
        bd_map[b["type"]] = b

    rb_map = {}
    for rb in bd.get("resourceBd", []):
        rb_map[rb["type"]] = rb

    return bd_map, rb_map


def format_time(secs: int) -> str:
    if secs < 60: return f"{secs}s"
    if secs < 3600: return f"{secs // 60}m"
    if secs < 86400: return f"{secs // 3600}h"
    return f"{secs // 86400}d"


def inject_building_upgrades(page: dict, bd_map: dict, rb_map: dict, loc: dict):
    """Enrich building page with upgrade costs, production, and requirements."""
    uid = page.get("id")
    if not uid:
        return

    bd = bd_map.get(uid)
    if not bd:
        return

    levels = bd.get("levels", [])
    upgrade_table = []
    for lv in levels:
        costs = []
        for c in lv.get("costs", []):
            item_id = c.get("itemId", 0)
            name = ITEM_NAMES.get(item_id, loc.get(f"res_name_{item_id}", f"Item {item_id}"))
            costs.append({"item": name, "count": c.get("itemCnt", 0)})

        pre_reqs = []
        for pc in lv.get("preCond", []):
            btype = pc.get("type", 0)
            bname = loc.get(f"building_name_{btype}", f"Building {btype}")
            pre_reqs.append(f"{bname} Lv{pc.get('val', 0)}")

        unlocks = []
        for u in lv.get("unlock", []):
            utype = u.get("type", 0)
            if utype == 6:
                builds = {9: "Build Slot +1", 13: "Research Slot +1"}.get(u.get("val"))
                if builds: unlocks.append(builds)
            elif utype == 9:
                subtype = u.get("subtype", 0)
                sname = ITEM_NAMES.get(subtype, loc.get(f"res_name_{subtype}", f"Item {subtype}"))
                val = u.get("val", 0)
                if val >= 1000000:
                    unlocks.append(f"{sname} Cap: {val / 1000000:.2f}M")
                elif val >= 1000:
                    unlocks.append(f"{sname} Cap: {val / 1000:.1f}K")
                else:
                    unlocks.append(f"{sname} Cap: {val}")
            elif utype == 15:
                unlocks.append("New Building Available")

        upgrade_table.append({
            "level": lv.get("level", 0),
            "costs": costs,
            "time": format_time(lv.get("costTime", 0)),
            "pre_reqs": pre_reqs,
            "unlocks": unlocks,
        })

    # Resource production data
    resource_info = None
    rb = rb_map.get(uid)
    if rb:
        prod_levels = []
        for lc in rb.get("levelConfig", []):
            configs = lc.get("config", [])
            for cfg in configs:
                item_id = cfg.get("itemId", 0)
                prod_levels.append({
                    "level": lc.get("level", 0),
                    "production": cfg.get("productivity", 0),
                    "capacity": cfg.get("capacity", 0),
                    "speed": cfg.get("speedInterval", 0),
                    "item_id": item_id,
                    "item_name": ITEM_NAMES.get(item_id, ""),
                })
        resource_info = {
            "levels": prod_levels,
        }

    page["upgrade_table"] = upgrade_table
    page["resource_production"] = resource_info


# ─── Tier list pages ───────────────────────────────────────────────

TIER_RANGES = [
    (float('inf'), 500, "S"),
    (500, 400, "A"),
    (400, 250, "B"),
    (250, 100, "C"),
    (100, 30, "D"),
    (30, 0, "F"),
]


def assign_tier(combat_power: int) -> str:
    for high, low, tier in TIER_RANGES:
        if low <= combat_power < high:
            return tier
    return "F"


def build_tier_list_pages(db: dict, name_map: dict, slug_map: dict, loc: dict) -> list:
    pages = []
    mode_data = load_json(DATA_DIR / "config" / "battle_conf_lib.json")

    all_heroes = []
    for uid, u in db.items():
        if u.get("unit_type") != 1:
            continue
        name = name_map.get(str(uid)) or u.get("name_en")
        if not name:
            continue
        all_heroes.append({
            "id": u["id"],
            "name": name,
            "slug": slug_map.get(str(uid), slugify(name)),
            "rarity": u.get("rarity"),
            "rarity_name": RARITY_MAP.get(u.get("rarity"), "Unknown"),
            "profession": u.get("profession"),
            "profession_name": PROFESSION_MAP.get(u.get("profession"), "Unknown"),
            "cost": u.get("cost", 0),
            "combat_power": u.get("combat_power", 0),
        })

    # Global tier list (all heroes)
    all_sorted = sorted(all_heroes, key=lambda u: -u["combat_power"])
    tier_name = "Overall"
    tier_slug = "overall"
    tiered = {}
    for u in all_sorted:
        t = assign_tier(u["combat_power"])
        tiered.setdefault(t, []).append(u)
    tier_order = ["S", "A", "B", "C", "D", "F"]
    title = f"War Inc: Rising Tier List 2026 — Best Heroes Ranked"
    meta_desc = f"Complete War Inc: Rising hero tier list for 2026. {len(all_sorted)} heroes ranked from S-Tier to F-Tier. Find the best heroes for your team."
    pages.append({
        "slug": tier_slug,
        "name": f"{tier_name} Tier List",
        "title": title,
        "meta_description": meta_desc,
        "type": "tier-lists",
        "tier_name": tier_name,
        "tiers": {t: tiered.get(t, []) for t in tier_order},
        "count": len(all_sorted),
        "schema": {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": title,
            "description": meta_desc,
        },
    })

    # Per-mode tier lists
    for mid, mode in mode_data.items():
        mode_name = loc.get(f"game_mode_name_{mid}", f"Mode {mid}")
        tier_slug = slugify(f"{mode_name}-tier-list")

        tiered = {}
        for u in all_heroes:
            t = assign_tier(u["combat_power"])
            tiered.setdefault(t, []).append(u)

        title = f"War Inc: Rising {mode_name} Tier List 2026 — Best Heroes"
        meta_desc = f"Best heroes for {mode_name} in War Inc: Rising. Ranked from S-Tier to F-Tier. Build the optimal team for {mode_name}."

        pages.append({
            "slug": tier_slug,
            "name": f"{mode_name} Tier List",
            "title": title,
            "meta_description": meta_desc,
            "type": "tier-lists",
            "tier_name": mode_name,
            "mode_id": int(mid),
            "tiers": {t: tiered.get(t, []) for t in tier_order},
            "count": len(all_heroes),
            "schema": {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "name": title,
                "description": meta_desc,
            },
        })

    # Profession tier lists
    for prof_id, prof_name in PROFESSION_MAP.items():
        prof_heroes = [u for u in all_heroes if u.get("profession") == prof_id]
        if not prof_heroes:
            continue
        prof_heroes.sort(key=lambda u: -u["combat_power"])
        tier_slug = slugify(f"{prof_name}-tier-list")
        tiered = {}
        for u in prof_heroes:
            t = assign_tier(u["combat_power"])
            tiered.setdefault(t, []).append(u)

        title = f"War Inc: Rising Best {prof_name} Heroes — {prof_name} Tier List 2026"
        meta_desc = f"Ranking of all {len(prof_heroes)} {prof_name} heroes in War Inc: Rising. S-Tier to F-Tier. Find the best {prof_name} for your team."

        pages.append({
            "slug": tier_slug,
            "name": f"{prof_name} Tier List",
            "title": title,
            "meta_description": meta_desc,
            "type": "tier-lists",
            "tier_name": f"{prof_name} Heroes",
            "profession_id": prof_id,
            "profession_name": prof_name,
            "class_name": prof_name,
            "tiers": {t: tiered.get(t, []) for t in tier_order if tiered.get(t)},
            "count": len(prof_heroes),
            "schema": {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "name": title,
                "description": meta_desc,
            },
        })

    return pages


# ─── Blog posts ────────────────────────────────────────────────────

BLOG_POSTS = [
    {
        "slug": "war-inc-rising-beginner-guide",
        "name": "War Inc: Rising Beginner Guide — How to Start Strong in 2026",
        "title": "War Inc: Rising Beginner Guide — Tips, Strategy and Progression",
        "meta_description": "New to War Inc: Rising? This beginner guide covers early priorities, summoning strategy, resource management, team building, and progression tips to level up fast.",
        "date": "2026-01-15",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Play through campaign to unlock all modes first. Spend your gems on Permanent Summon scrolls until you have a solid roster. Upgrade your Command Center for passive income. Never waste gems on speed-ups or building resources. Build a balanced team of 5-7 heroes with at least one Tank, one damage dealer, and one Support.\n\nThis guide walks through everything a new player needs to know — from your first 60 levels to endgame team building. If you learn nothing else, remember this: Forge Stones are the most scarce resource in the game, so spend them wisely.",
            },
            {
                "heading": "Early Priorities (Levels 1-60)",
                "content": "Your first 60 levels are about unlocking options. Every campaign stage you clear opens a new game mode, building, or feature. Don't stress about optimization yet — just push through content gates.\n\nSpend your initial gems on Permanent Summon scrolls. It's tempting to chase the shiny Limited Banner hero, but a broad roster beats a narrow one every time. Building depth early gives you flexibility for different game modes and events.\n\nUpgrade your Command Center whenever possible. Each level increases your passive income, and those small amounts add up over days and weeks.",
            },
            {
                "heading": "Where to Spend Gems (and Where Not To)",
                "content": "Gems are the most valuable currency. Here's where they should go:\n\n- Permanent Summon scrolls: Your bread and butter for roster depth.\n- Energy refills (50 gems): Only during events with Mythic shard rewards or double-drop campaigns.\n- Limited Summon banners: Save 30,000-50,000 gems for chasing specific meta heroes.\n\nWhere NOT to spend gems:\n- Building construction speed-ups. Time is free. Wait.\n- Resources (gold, wood) from the shop. Terrible value.\n- Refreshing daily missions. The return is minimal.\n\nA common beginner trap is spending gems on the first Limited Banner you see. Don't. Build your foundation first.",
            },
            {
                "heading": "Gold and Forge Stones: The Real Bottleneck",
                "content": "Gold comes naturally from campaign, events, and the mine dice rolls. You'll mostly use it for rolling the mine and basic upgrades. It's not usually a problem.\n\nForge Stones are a different story. You need them from Merge Level 6 onwards, and they're the most scarce resource in the game. Hunting mode is your best source. Never spend Forge Stones on heroes you don't regularly use. A common mistake is spreading them across 10+ heroes instead of focusing on 3-5 core units.\n\nOne level 8 hero is worth more than eight level 5 heroes. Pick your core team and stick with it.",
            },
            {
                "heading": "Building Your First Team",
                "content": "A balanced team needs three things: a frontline that can take hits, damage dealers to dish it out, and support to keep everyone alive.\n\nStart with lower-cost units (2-3 Elixir) so you can deploy early. Swordsman (cost 2) and Archer (cost 2) are your best common options. They'll carry you through early content while you collect better heroes.\n\nAs you unlock higher rarities, gradually replace commons. But never merge away your last copy of a hero you actively use. Keep at least one deployable version.\n\nAim for profession diversity: one Tank, one Warrior, one Mage, and one Support covers most situations. You can specialize later when you know which game modes you enjoy most.",
            },
            {
                "heading": "Common Mistakes New Players Make",
                "content": "1. Spending gems on speed-ups and shop resources. Just wait.\n2. Investing Forge Stones in every hero they own. Focus on 3-5 core units.\n3. Merging away the last copy of a hero they use. Always keep one.\n4. Chasing Limited Banners before building roster depth. Build first, specialize later.\n5. Ignoring the Command Center. Upgrade it whenever possible — passive income matters.\n6. Using Wood Shield Guard. Seriously, don't. It's a single-unit common with terrible stats.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-tier-list-2026",
        "name": "War Inc: Rising Tier List 2026 — Complete Hero Rankings",
        "title": "War Inc: Rising Tier List 2026 — All Heroes Ranked S-Tier to F-Tier",
        "meta_description": "Our complete War Inc: Rising tier list ranks all 95 heroes from S-Tier to F-Tier. Find the best heroes for Arena, Co-Op, and every game mode.",
        "date": "2026-01-20",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "S-Tier heroes dominate every game mode. Light Seeker, Radiant Warrior, Frost Queen, Bone Marksman, and Mist Archer are the strongest heroes in the game right now. If you have the chance to acquire any of them, take it.\n\nBut having five S-Tier heroes won't automatically win battles. Team composition, synergy bonuses, and proper positioning matter just as much as raw power. Use this tier list to prioritize acquisition, but build your teams around complementing strengths rather than stacking top-tier names.",
            },
            {
                "heading": "How We Rank Heroes",
                "content": "These rankings are based on combat power, skill effectiveness, and versatility across game modes. A hero that dominates in Arena but fails in Co-Op gets a lower rank than a hero that performs well everywhere.\n\nS-Tier heroes excel in multiple modes and team compositions. A-Tier heroes are strong with minor limitations. B-Tier heroes perform well in specific situations. C-Tier and below are generally outclassed but can still work in early progression.\n\nCheck individual hero pages for the full community rankings with strategy tips and minimum level requirements.",
            },
            {
                "heading": "S-Tier Heroes (Best of the Best)",
                "content": "These are the heroes you should prioritize acquiring and investing in:\n\n- Radiant Warrior (S+): Best tank in the game. Use 2-4 in every formation. Level 6 gives +20% elemental resistance to all allies.\n- Frost Queen (S+): Best control mage. Her massive AoE ice damage dominates Arena and Infinite War.\n- Bone Marksman (S+): Best marksman deletion. Pseudo-level 6 at level 4 — one of the best early investments.\n- Light Seeker (S+): PvP destroyer. Holy Wash heals to 100% when below 50% HP. Needs level 4 to shine.\n- Necromancer (S+): PvE king. Skeletons deal massive AoE damage. Needs Goddess of War shielding to survive.\n- Goddess of War (S+): Essential support. Shields nearby troops and combos with Red Blade + Barbarian.\n\nCombat power for S-Tier heroes exceeds 80,000 at max level. These are your long-term investment targets.",
            },
            {
                "heading": "A-Tier Heroes (Excellent Choices)",
                "content": "A-Tier heroes are powerful in specific modes and team compositions. They can carry you through most content when built correctly.\n\n- Oracle (S): Best epic. Attack buffer used in 99% of army setups. Level 7 is transformative.\n- Ursa Champion (S): Best Legendary forge stone investment. Level 7 stun is game-changing.\n- Elven Archer (S): Best Legendary range damage. Excellent forge stone target.\n- Ripple Wizard (S): Best energy battery. Aqua Revival grants energy every 2.5 seconds.\n- Poison Master (S): Carries early-mid Infinite War. 8-10 at level 6 is transformative.\n\nThese heroes fall between 45,000 and 80,000 combat power. They're not the absolute best, but they'll never let you down in the right composition.",
            },
            {
                "heading": "Building Around Your Tier List",
                "content": "A team of five S-Tier Mages will struggle against a balanced composition. Raw power isn't everything.\n\nUse the tier list as a guide for which heroes to invest Forge Stones in. But build your actual teams around synergy bonuses, cost curves, and formation compatibility.\n\nCheck the hero synergy sections on each page to find which heroes work well together. A smart B-Tier pick that enables your S-Tier carry is often better than a second S-Tier that doesn't fit.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-arena-pvp-guide",
        "name": "War Inc: Rising Arena PvP Guide — Best Formations and Heroes",
        "title": "War Inc: Rising Arena PvP Guide — Formations, Heroes, and Strategy",
        "meta_description": "Master Arena PvP in War Inc: Rising. Learn the four key formations (Dash, Backstab, Outflank, Split), best heroes for PvP, and advanced strategy tips.",
        "date": "2026-02-01",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Arena PvP Basics",
                "content": "Arena is War Inc: Rising's main PvP mode where you battle other players in real-time. Matches are won through smart deployment, proper formation, and understanding hero matchups. Your Arena rank determines your seasonal rewards and bragging rights. Climbing the Arena ladder requires adapting your strategy to counter the current meta.",
            },
            {
                "heading": "The Four Key Formations",
                "content": "Dash Formation is the standard baseline — your A1 attacks enemy F1, and so on. It maximizes aura abilities and unit synergies but is predictable. Backstab Formation sends units to the enemy's back line to devastate their damage dealers — excellent with Bomber units targeting B2-B3 and B5-B6 positions. Outflank Formation sends edge units into enemy lines to draw aggro while your front advances — great for countering Frost Queen. Split Formation shifts units to create two battle fronts — the hardest formation to predict.",
            },
            {
                "heading": "Best Heroes for Arena PvP",
                "content": "The current Arena meta favors heroes with AoE damage and crowd control. Frost Queen leads the pack with massive area damage. Light Seeker provides holy AoE with healing. Bone Marksman delivers piercing shots from range. Radiant Warrior combines durability with damage. Tide Lord brings water-elemental wave attacks. For support, Starlight Apostle and Melody Weaver provide crucial buffs.",
            },
            {
                "heading": "Countering Common Strategies",
                "content": "If your opponent uses Backstab formation, counter with Split formation to minimize damage. Against Dash, use Backstab to disrupt their formation. Frost Queen teams are vulnerable to Outflank formation that spreads units wide. Always scout your opponent's formation before the match starts and adjust your deployment accordingly.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-coop-guide",
        "name": "War Inc: Rising Co-Op Guide — Best Heroes and Strategies for Level 80+",
        "title": "War Inc: Rising Co-Op Guide — Best Heroes, Strategy and Rewards",
        "meta_description": "Master Co-Op mode in War Inc: Rising. Learn the best hero picks, strategy for reaching level 80+, mine upgrades, dice rolling, and team coordination.",
        "date": "2026-02-10",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Co-Op is the best source of gems and rare hero shards in War Inc: Rising. You team up with another player to survive increasingly difficult waves. The key to reaching level 80+ is simple: one player builds economy (mine upgrades), the other builds military (recruits). Communicate before the match starts.\n\nThis guide covers the best heroes, the mine upgrade strategy, and how to coordinate with your partner for maximum wave progress.",
            },
            {
                "heading": "How Co-Op Works",
                "content": "You and a partner face waves of enemies that get harder over time. Between waves, you use Silver Coins and Gold to upgrade your mine, recruit new units, and roll the dice. Your partner does the same on their side.\n\nThe rewards scale with how far you get — higher waves mean better loot. Reaching level 80+ requires both players to understand the strategy and execute their roles.",
            },
            {
                "heading": "Best Heroes for Co-Op",
                "content": "Co-Op favors sustained damage and survivability. Burst heroes that shine in PvP often fall flat here.\n\n- Mist Archer: Consistent ranged DPS with stealth. Never stops dealing damage.\n- Venospore Killer: Excellent damage-over-time. Wears down tanky wave enemies.\n- Flame Duelist: Combo attacks stack up well over long fights.\n- Nine-Tailed Fox: Burst damage that resets between waves.\n- Melody Weaver: Buffs your partner's team too, not just yours.\n- Oracle: Level 7 aura buffs cover extensive battlefield area.",
            },
            {
                "heading": "The Mine Upgrade Strategy (Reach Level 80+)",
                "content": "Silver Coins are the most important resource in Co-Op. Here's the priority:\n\n1. Mine upgrades first. Each level gives compounding returns throughout the match.\n2. Recruit Chance second. Get your units on the field sooner.\n3. Gold to roll the Dice consistently. Dice map upgrades can give +100 Silver Coins, +60 Gold, and even Legendary minions.\n\nA common mistake is spending Silver Coins on recruit upgrades too early. The mine pays for everything over time — invest in it first.",
            },
            {
                "heading": "Team Coordination: The Split Strategy",
                "content": "Before the match starts, agree on roles:\n\n- Player 1: Economy focus. Spend on mine upgrades and dice rolls.\n- Player 2: Military focus. Spend on recruit upgrades and unit deployment.\n\nBoth players should have at least one high-level Mythic hero for the later waves. Don't panic if early waves feel easy — the difficulty ramps significantly after wave 50.\n\nIf you're playing with a random partner, assume they won't coordinate. Build a self-sufficient team that can carry if needed.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-best-team-compositions",
        "name": "War Inc: Rising Best Team Compositions — Synergies and Formations",
        "title": "War Inc: Rising Best Team Compositions — Ultimate Synergy Guide",
        "meta_description": "Build the ultimate team in War Inc: Rising. Learn the best hero synergies, team compositions for each game mode, and how to balance cost, rarity, and professions.",
        "date": "2026-02-20",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "The Fundamentals of Team Building",
                "content": "A winning team composition balances frontline durability, damage output, and support. Every team needs at least one Tank to absorb damage, 2-3 damage dealers (Mage, Assassin, or Ranger), and at least one Support for sustain. Mixing professions triggers synergy bonuses that multiply your team's effectiveness. Pay attention to Elixir cost — a balanced cost curve ensures you can deploy units throughout the match.",
            },
            {
                "heading": "Cost-Bracket Strategies",
                "content": "Low-cost teams (0-2 Elixir) rely on numbers and quick deployment. They excel at overwhelming opponents with swarms but lack the punch to take down high-HP targets. Mid-cost teams (3-4 Elixir) offer the best balance of value and power — most competitive teams fall here. High-cost teams (5+ Elixir) are powerful but slow to deploy; use them when you can protect them long enough to reach the battlefield.",
            },
            {
                "heading": "Profession Synergies",
                "content": "Tank + Mage combinations create a classic wall-and-spray formation. Warrior + Support pairs provide sustained frontline pressure. Assassin + Ranger combinations offer focused backline elimination. The key is ensuring your damage dealers match the enemy's vulnerabilities while your frontline holds position.",
            },
            {
                "heading": "Mode-Specific Team Building",
                "content": "For General Lineup, balance is key — aim for one hero from each profession. For Ace Showdown, prioritize high-burst heroes and Assassins. For Co-Op, focus on sustainability and AoE damage. For Hunting mode, single-target damage dealers shine. Always check the mode rules before building your team.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-how-to-get-mythic-heroes",
        "name": "How to Get Mythic Heroes in War Inc: Rising — Complete Summoning Guide",
        "title": "How to Get Mythic Heroes in War Inc: Rising — Summoning and Gem Guide",
        "meta_description": "Learn how to get Mythic heroes in War Inc: Rising. Complete guide to summoning, gem spending, limited banners, events, and the best strategies for building your Mythic roster.",
        "date": "2026-03-01",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Save 30,000-50,000 gems for Limited Summon events targeting specific Mythic heroes. Use Permanent Summon for roster depth. Never spend gems on random permanent summons if you're chasing a specific hero. The $5 monthly gem pass is the best value if you spend money.\n\nThere are currently 34 Mythic heroes in War Inc: Rising. Building a solid Mythic roster takes months of consistent play — but these strategies will get you there faster.",
            },
            {
                "heading": "What Makes Mythic Heroes Special",
                "content": "Mythic (5-star) heroes have the highest base stats, strongest skills, and combat power exceeding 80,000 at max level. Think Light Seeker, Frost Queen, Radiant Warrior, Tide Lord — the heroes that define the meta.\n\nBut here's the thing: a level 3 Mythic is often worse than a level 9 Epic. Getting the hero is step one. Getting multiple copies to level them up is where the real investment lives.",
            },
            {
                "heading": "Three Summoning Methods Compared",
                "content": "You have three ways to get Mythic heroes:\n\n1. Permanent Summon (300 gems each): Consistent Mythic chances over time. No expiration. Best for building roster depth. The pity system guarantees progress toward your next Mythic.\n\n2. Limited Summon (variable cost): Features specific Mythic heroes at boosted rates. Higher rates per pull but resets your pity counter if you don't hit the banner hero. Best when you need one specific hero.\n\n3. Event Summons: Appear during seasonal content. Often include exclusive Mythic units you can't get anywhere else. Use event currency on Mythic-specific rewards, not lower-rarity items.\n\nThe optimal strategy: use Permanent Summon for 80% of your gems, save 20% for Limited Summon events featuring S+ tier Mythics.",
            },
            {
                "heading": "Savings Targets: How Many Gems You Need",
                "content": "Here's what to aim for:\n\n- To guarantee one Limited Banner Mythic: 30,000-50,000 gems\n- For a strong Permanent Summon session: Save 10-15 summons (3,000-4,500 gems)\n- Daily + weekly income without spending: Roughly 200-300 free gems per week from missions and Arena rewards\n- The $5 monthly gem pass: Best value-to-cost ratio if you spend money\n\nAt free-to-play rates, a major Limited Banner push takes about 3-4 months of saving. Start now.",
            },
            {
                "heading": "Which Mythics to Prioritize",
                "content": "Not all Mythics are created equal. Here's the priority:\n\n- S+ priority: Radiant Warrior, Frost Queen, Bone Marksman, Light Seeker, Goddess of War\n- First Mythic? Bone Marksman. It's playable at level 4 (unlike most Mythics that need level 6+) and carries hard.\n- Avoid: Don't chase niche Mythics until you have the core S+ roster.\n\nCheck the tier list and individual hero pages for detailed community rankings.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-formation-guide",
        "name": "War Inc: Rising Formation Guide — Dash, Backstab, Outflank and Split",
        "title": "War Inc: Rising Formation Guide — Master All 4 Battle Formations",
        "meta_description": "Master the four battle formations in War Inc: Rising: Dash, Backstab, Outflank, and Split. Learn when to use each formation and how to counter common strategies.",
        "date": "2026-03-10",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Your formation determines which enemies your units target first, how they move across the battlefield, and whether they survive the first engagement. It's the single biggest skill gap between intermediate and advanced players.\n\nThere are four formations: Dash (standard), Backstab (aggressive), Outflank (tactical), and Split (defensive). Each counters one other formation and loses to another. The key is scouting your opponent before the match and picking the right counter.",
            },
            {
                "heading": "Dash Formation — The Standard",
                "content": "Dash is the default formation. Your leftmost units engage the enemy's front line directly — A1 attacks F1, A2 attacks F2, and so on.\n\nThis formation maximizes aura abilities and unit synergies. Frontline Tanks cover the most area, and support units sit safely behind. It's the safest choice when you don't know what your opponent is using.\n\nStrong against: Nothing in particular. It's the neutral option.\nWeak against: Backstab formations that bypass your frontline to hit damage dealers.",
            },
            {
                "heading": "Backstab Formation — The Aggressor",
                "content": "Backstab sends units directly to the enemy's back line, targeting their damage dealers first. This is the most potent offensive formation.\n\nUse it with Bomber units that self-destruct for massive AoE damage. Place Bombers to target positions B2-B3 and B5-B6 for maximum coverage.\n\nStrong against: Dash formations that rely on a tank wall.\nWeak against: Split formations that spread your backstab force into two ineffective groups.",
            },
            {
                "heading": "Outflank Formation — The Tactician's Choice",
                "content": "Outflank sends 10 edge units (columns 1 and 7) into the enemy's flanks. They draw aggro while your main force advances through the center.\n\nThis is the best counter to Frost Queen, whose AoE is most dangerous against tightly-packed formations. Spreading out forces her to choose which group to target.\n\nStrong against: Frost Queen-centric teams.\nWeak against: Split formations that split your flanking forces into isolated groups.",
            },
            {
                "heading": "Split Formation — The Defensive Master",
                "content": "Split shifts your left units 3 spaces left and right units 2 spaces right, creating two separate battle fronts.\n\nThis is the hardest formation to predict and the best defensive setup. It counters Backstab by splitting the backstab into two ineffective groups.\n\nStrong against: Backstab.\nWeak against: Dash, which engages each half of your split force individually.",
            },
            {
                "heading": "How to Counter Each Formation",
                "content": "Here's the counter wheel at a glance:\n\n- See Dash coming? Use Backstab to hit their backline.\n- See Backstab coming? Use Split to neutralize it.\n- See Split coming? Use Dash to engage each half 1v1.\n- See Outflank? Split works well here too.\n\nScouting is everything. If you can identify your opponent's formation before the match starts, you can pick the counter and win before the first unit deploys.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-progression-guide",
        "name": "War Inc: Rising Progression Guide — Level 1 to Endgame",
        "title": "War Inc: Rising Progression Guide — Leveling Fast to Endgame",
        "meta_description": "Complete progression guide for War Inc: Rising. From level 1 to endgame — campaign tips, building upgrades, hero merging, and when to transition between phases.",
        "date": "2026-03-20",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Early Game (Levels 1-30): Learning the Basics",
                "content": "Focus on completing the campaign to unlock all game modes. Build a core team of 5-7 heroes using primarily Common and Rare units. Upgrade your Command Center to level 5 for passive income. Complete daily missions for gems and resources. Don't worry about optimizing yet — experiment with different heroes to understand their roles.",
            },
            {
                "heading": "Mid Game (Levels 31-60): Building Your Roster",
                "content": "Start replacing Common heroes with Rare and Epic units. Unlock buildings — Sawmill for wood, Gold Mine for gold. Join a clan to access Clan Wars and Clan Hunt rewards. Focus your Forge Stones on 3-4 core heroes. Begin saving gems for limited summon events. Your team should start having defined roles at this stage.",
            },
            {
                "heading": "Late Game (Levels 61-90): Optimization",
                "content": "Buildings unlock at level 61, providing passive resource income. Focus on Legendary and Mythic heroes for your main team. Max out key buildings before expanding. Join Arena and Co-Op regularly for rewards. This is where profession synergies and formation strategy matter most.",
            },
            {
                "heading": "Endgame (Level 90+): Min-Maxing",
                "content": "At endgame, you're optimizing Mythic hero lineups for each game mode. Focus on hero merge levels rather than unlocking new heroes. Save resources for new Mythic releases through limited banners. Coordinate with your clan for top-tier Clan War rankings. The difference between good and great endgame players comes down to formation adjustments and hero timing.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-gem-spending-guide",
        "name": "War Inc: Rising Gem Spending Guide — Best Value for Your Gems",
        "title": "War Inc: Rising Gem Spending Guide — Best Value and Optimization",
        "meta_description": "Learn the best ways to spend gems in War Inc: Rising. Permanent vs Limited summon, energy refills, event spending, and common gem mistakes to avoid.",
        "date": "2026-04-01",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Your First 10,000 Gems",
                "content": "Spend your first 10,000 gems on Permanent Summon scrolls to build roster depth. A broad roster gives you flexibility for different game modes and events. Avoid the temptation of limited banners early — get your core team first, then chase specific heroes. Save 500 gems for energy refills during events that offer Mythic shards.",
            },
            {
                "heading": "Permanent Summon vs Limited Summon",
                "content": "Permanent Summon is better for consistent long-term value. It guarantees progress toward your next Legendary or Mythic. Limited Summon offers higher rates for specific heroes but resets your pity counter if you don't pull. The optimal strategy: use Permanent Summon for 80% of your gems, save 20% for Limited Summon events featuring top-tier Mythics.",
            },
            {
                "heading": "Energy Refills — When and When Not",
                "content": "Energy refills (50 gems) are worth it during events with Mythic shard rewards, double-drop campaigns, or when farming Forge Stones. Avoid energy refills for normal farming. The daily free energy and event claim rewards are usually sufficient for baseline progression.",
            },
            {
                "heading": "Common Gem Mistakes",
                "content": "Don't spend gems on speeding up building construction — time is free. Don't buy resources (gold, wood) from the shop with gems — they're poor value. Don't refresh daily missions with gems — the return is minimal. Don't spend gems on random hero shards in the shop — targeted summoning is more efficient.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-hunting-mode-guide",
        "name": "War Inc: Rising Hunting Mode Guide — Bosses, Tips and Rewards",
        "title": "War Inc: Rising Hunting Mode Guide — Best Heroes and Boss Strategy",
        "meta_description": "Master Hunting mode in War Inc: Rising. Guide to all 20 Hunting bosses, best heroes for each boss, rewards, and strategies for maximizing your Hunting runs.",
        "date": "2026-04-10",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Hunting Mode Overview",
                "content": "Hunting mode sends you against powerful boss monsters for valuable rewards. Each boss has unique attack patterns and weaknesses. The mode resets daily with a new boss rotation. Hunting is one of the best sources of Forge Stones and Legendary hero shards — both essential for progression.",
            },
            {
                "heading": "Best Heroes for Hunting",
                "content": "Hunting mode favors single-target damage dealers over AoE specialists. Assassins and Rangers perform best here — Ghost Assassin, Bone Marksman, and Mist Archer are top picks. Frontline Tanks are essential to keep the boss occupied while your damage dealers work. Support heroes with healing like Grace Priest extend your team's survivability.",
            },
            {
                "heading": "Hunting Rewards Explained",
                "content": "Higher difficulty levels in Hunting mode yield better rewards. Forge Stones are a common drop and essential for pushing hero merge levels past 6. Gold and hero shards are also available. Building a dedicated Hunting team that can consistently clear the highest difficulty is one of the best long-term investments in the game.",
            },
            {
                "heading": "Daily Hunting Strategy",
                "content": "Always complete your daily Hunting runs — even if you can't clear the highest difficulty, the lower-tier rewards still provide value. Study each boss's attack patterns before the fight. Time your hero deployment to avoid the boss's AoE attacks. Save your hero skills for boss vulnerability phases to maximize damage.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-best-tanks",
        "name": "War Inc: Rising Best Tank Heroes — Tank Tier List and Guide",
        "title": "War Inc: Rising Best Tank Heroes — Complete Tank Tier List 2026",
        "meta_description": "Complete guide to Tank heroes in War Inc: Rising. Rankings for all Tank heroes, best tanks for each game mode, and how to build an unbreakable frontline.",
        "date": "2026-04-20",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "What Makes a Good Tank?",
                "content": "Tanks are defined by high HP and DEF stats, allowing them to absorb damage while your damage dealers work. The best Tanks also have crowd control abilities — stuns, taunts, or slows that keep enemies locked down. Position your Tank at the front of your formation to maximize their damage absorption. A good Tank can protect your entire team.",
            },
            {
                "heading": "Top Tank Heroes Ranked",
                "content": "The best Tank in War Inc: Rising is Radiant Warrior — a Mythic Tank with excellent HP scaling and holy damage abilities. Ironguard and Paladin provide excellent defensive utility at lower rarities. Woodland Guardian and Pumpkin Guard offer unique taunt mechanics. For early game, Scudiero (Common) is a surprisingly effective budget Tank that punches above its cost.",
            },
            {
                "heading": "Tank Synergies",
                "content": "Tanks pair best with Support heroes that provide healing — Grace Priest and Melody Weaver extend your Tank's survivability dramatically. Mages behind a Tank can safely deal damage while the Tank holds the line. Some Tanks have self-healing abilities that make them independent — prioritize these in modes where Support slots are limited.",
            },
            {
                "heading": "Tank Positioning Tips",
                "content": "Place your Tank at position A1, A4, or directly in front of your most vulnerable damage dealer. Against Backstab formations, consider running two Tanks to protect both front and back lines. Level your Tank's DEF stat at least as much as HP — raw HP without DEF melts quickly against high-ATK opponents.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-merge-evolution-guide",
        "name": "War Inc: Rising Merge and Evolution Guide — Forge Stones Strategy",
        "title": "War Inc: Rising Merge and Evolution Guide — Level Up Your Heroes",
        "meta_description": "Master hero merging and evolution in War Inc: Rising. Complete guide to merge levels, Forge Stones, evolution costs, and when to upgrade your heroes for maximum value.",
        "date": "2026-05-01",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Merge Levels Explained",
                "content": "Hero merge levels increase base stats and unlock new skill tiers. Each merge level requires copies of the same hero and Forge Stones. Merge Level 6 is where most heroes unlock their first significant power spike. Merge Level 12 is the maximum and grants the strongest version of every skill. Focus on getting your core team to Merge 6 before spreading resources to backup heroes.",
            },
            {
                "heading": "Forge Stones — The Bottleneck Resource",
                "content": "Forge Stones are required from Merge Level 6 onwards and are the most scarce resource in the game. You can obtain them from Hunting mode rewards, Infinite War, daily chests, and event shops. Never spend Forge Stones on heroes you don't use regularly — they're too valuable. A common mistake is spreading Forge Stones across 10+ heroes instead of focusing on 3-5 core units.",
            },
            {
                "heading": "Evolution Paths and Costs",
                "content": "Hero evolution uses Forge Stones and Silver Coins. The cost increases with each merge level. Save your Silver Coins for evolution rather than spending on random upgrades. Higher-rarity heroes have higher evolution costs but also higher stat gains per level. Use our evolution calculator tool to plan which hero to upgrade next based on your available resources.",
            },
            {
                "heading": "When to Merge vs When to Wait",
                "content": "Merging temporarily reduces your roster because you consume copies of the hero. Plan merges between game sessions when you won't need full strength for 12-24 hours. Never merge your last deployable copy of a hero you actively use. Save major merges for after you've completed daily missions and Arena placements.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-best-mages",
        "name": "War Inc: Rising Best Mage Heroes — Mage Tier List and Guide",
        "title": "War Inc: Rising Best Mage Heroes — Complete Mage Tier List 2026",
        "meta_description": "Complete guide to Mage heroes in War Inc: Rising. Rankings for all Mage heroes, best Mages for each game mode, and how to maximize magic damage output.",
        "date": "2026-05-10",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "The Mage Role",
                "content": "Mages deal area magic damage from a safe distance, making them essential for clearing grouped enemies and controlling the battlefield. Mages are generally fragile with low HP and DEF, requiring frontline protection. Their damage scales exceptionally well with merge levels. Most Mages have elemental attributes (Fire, Water, Wood, Earth) that interact with the game's damage system.",
            },
            {
                "heading": "Top Mage Heroes Ranked",
                "content": "Frost Queen is the premier Mage — her massive AoE ice damage makes her a top-tier pick in Arena and campaign. Storm Maiden and Starlight Apostle provide excellent area control. Blazewing Lord offers aerial mage damage. For lower rarities, Flame Mage and Apprentice Mage provide solid magic DPS. Wind Apostle and Geomancer offer unique utility that complements mage-heavy compositions.",
            },
            {
                "heading": "Mage Synergies and Positioning",
                "content": "Mages need Tanks in front to survive. Position them in the back row (positions G1-G7) for maximum safety. Pair Mages with Support heroes that can heal or shield. Some Mages have self-peel abilities — prioritize these in aggressive formations. In Co-Op mode, Mages with AoE damage can handle wave clearing while your teammate focuses on single-target DPS.",
            },
            {
                "heading": "Mage vs Mage: Countering Enemy Magic",
                "content": "Elemental advantages matter in mage duels. Water beats Fire, Wood beats Water, Fire beats Wood. Check the enemy team's mage composition and counter with the appropriate element. Support Mages like Starlight Apostle can neutralize enemy mage advantages through buffs and healing.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-best-synergies",
        "name": "War Inc: Rising Best Synergies Guide — Team Bonus Effects",
        "title": "War Inc: Rising Best Synergies Guide — Max Your Team Bonuses",
        "meta_description": "Complete guide to War Inc: Rising synergies. Learn all 9 synergy effects, how to activate team bonuses, best hero combinations for each synergy, and which synergies dominate the meta.",
        "date": "2026-05-20",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "What Are Synergies?",
                "content": "Synergies are team-wide bonus effects triggered by fielding heroes with matching attributes. Each synergy provides unique combat bonuses like increased damage, damage reduction, or special effects. Activating multiple synergy tiers requires more heroes of the matching type. Understanding and building around synergies is key to competitive play.",
            },
            {
                "heading": "The 9 Synergy Types",
                "content": "War Inc: Rising features 9 distinct synergy/lib effects. Each requires specific hero combinations to activate. Some synergies boost raw stats while others grant unique combat mechanics. The most impactful synergies in the current meta are those that boost burst damage and survivability simultaneously.",
            },
            {
                "heading": "Building Around Synergies",
                "content": "Build your team to activate 2-3 synergy bonuses rather than trying to activate all available types. A focused synergy strategy outperforms a spread-out one. For example, pairing multiple Assassins triggers synergy bonuses that boost their burst damage, making them even more lethal. Use the synergy guides on each hero page to plan your team composition.",
            },
            {
                "heading": "Meta Synergy Combinations",
                "content": "The strongest current meta combinations include Water-element teams with Frost Queen and Tide Lord, and Light-element teams with Light Seeker and Radiant Warrior. Profession-based synergies (all Tanks, all Mages) provide reliable bonuses. Experiment with different combinations to find what works best for your playstyle and available heroes.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-infinite-war-guide",
        "name": "War Inc: Rising Infinite War Guide — Endless Mode Tips",
        "title": "War Inc: Rising Infinite War Guide — Survive Endless Mode",
        "meta_description": "Master Infinite War in War Inc: Rising. Learn how to survive endless waves, best heroes for sustained combat, resource management during runs, and when to push deeper.",
        "date": "2026-06-01",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "What is Infinite War?",
                "content": "Infinite War is an endless wave survival mode where you test how long your team can last against increasingly difficult enemies. It's one of the best sources of Forge Stones and gold. Each wave increases in difficulty, with boss waves appearing every 10 levels. Your record determines your tier rewards.",
            },
            {
                "heading": "Best Heroes for Endless Mode",
                "content": "Infinite War favors sustainability over burst damage. Heroes with self-healing, shields, or life steal excel here. Radiant Warrior and Night Scion can sustain themselves indefinitely with proper support. Necromancer's summoned skeletons provide valuable meat shields. Seraph's resurrection ability can save a run from collapse. Avoid glass-cannon heroes that die to incidental damage.",
            },
            {
                "heading": "Resource Management in Infinite War",
                "content": "Don't deploy all your heroes at once in early waves — conserve them for later. Learn which waves are safe to auto and which require manual skill timing. Save your strongest skills for boss waves. Energy management between runs matters too — don't exhaust your energy right before daily reset.",
            },
            {
                "heading": "Pushing Your Record",
                "content": "To push beyond your current record, study where your team typically fails and address that weakness. If your Tank dies early, consider a secondary off-tank. If damage falls off, replace your lowest-performing damage dealer. Small optimizations compound over 50+ waves — every hero choice and skill timing matters.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-clan-war-guide",
        "name": "War Inc: Rising Clan Wars Guide — Dominate Clan Battles",
        "title": "War Inc: Rising Clan Wars Guide — Strategy and Best Heroes",
        "meta_description": "Master Clan Wars in War Inc: Rising. Learn clan battle strategy, best heroes for clan war scenarios, coordination tips, and how to maximize clan rewards.",
        "date": "2026-06-05",
        "author": "War Inc Wiki Team",
        "sections": [
            {
                "heading": "Clan Wars Overview",
                "content": "Clan Wars are large-scale PvP battles between clans. Each war lasts several days with multiple battle phases. Coordination and strategy matter more than individual hero power. Clan Wars reward you with gems, exclusive hero shards, and clan currency for the clan shop. Active clans that communicate consistently outperform more powerful but disorganized clans.",
            },
            {
                "heading": "Clan War Battle Strategy",
                "content": "Coordinate attack waves with your clanmates to overwhelm enemy defenses. Focus fire on key enemy players rather than spreading attacks. Save your strongest teams for the final phase when points are doubled. Communicate enemy formations in clan chat so teammates can counter-pick effectively.",
            },
            {
                "heading": "Best Heroes for Clan Wars",
                "content": "Versatile heroes that perform well in multiple scenarios are most valuable in Clan Wars. Frost Queen and Light Seeker excel across attack and defense. Mist Archer and Tide Lord provide flexible deployment options. Build 2-3 strong teams rather than one super-team so you can launch multiple attacks per war phase.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-common-troops-guide",
        "name": "Beginner Tips: Common Troops Guide — Best Commons to Use",
        "title": "Beginner Tips: Common Troops Guide — Best Common Heroes | War Inc: Rising Wiki",
        "meta_description": "Learn which common troops are worth using in War Inc: Rising. Archer vs Gunner vs Snowball Thrower, Swordsman vs Demoman, and why level 7 commons are a huge power spike.",
        "date": "2026-06-10",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Swordsman is the best common melee. Archer is the best common range. Everything else is filler or trash. Never use Wood Shield Guard. Upgrade one Swordsman and one Archer to level 7 for the 100-gem Power Stance achievement, then stop investing in commons entirely.\n\nHere's the full breakdown of every common unit so you know exactly which ones to use and which to avoid.",
            },
            {
                "heading": "Why Level 7 Commons Matter",
                "content": "Level 7 is a massive power spike for any unit — higher stats AND the Trigger Master passive unlock. For a new account with low deployment limits, even commons matter at this level.\n\nBut Forge Stones are scarce. You should only push one of each common type to 7 for the Power Stance achievement (100 gems each). After that, commons get replaced by rares and epics. Save your Forge Stones for Ursa Champion, Oracle, Elven Archer, and Flame Mage — units that actually scale into endgame.",
            },
            {
                "heading": "Melee Commons: Swordsman vs the Rest",
                "content": "Swordsman is the clear winner. He's a multi-unit with splash damage in his skill radius — meaning each troop in the squad can trigger the splash independently. In a 2-deployment-point mirror match, Swordsman beats Demoman every single time.\n\nDemoman's stun only hits one target. Inferior in every way. Only use him if you literally have no Swordsman copies left.\n\nWood Shield Guard is a single unit (not multi-unit), meaning his stats apply to just one troop. He's completely useless. The most common beginner mistake is thinking he's a tank — he's not. Skip entirely. Don't even upgrade him for the achievement.",
            },
            {
                "heading": "Range Commons: Archer vs Gunner vs Snowball Thrower",
                "content": "Archer is your pick. Highest attack among common range units, multi-target skill for reliable damage, and consistent performance regardless of enemy composition.\n\nGunner deals fire damage but it's too low to matter — even against fire-weak enemies like Pumpkin Guard, Archer deals more effective damage. Snowball Thrower is the worst of the three. Water damage is irrelevant early game, and the slow effect on skill is practically useless.\n\nWhen filling last deployment points with range, Archer stands above as the most reliable choice.",
            },
            {
                "heading": "When to Stop Using Commons",
                "content": "Start replacing commons with rares and epics as soon as your roster allows. The main exceptions:\n\n- Swordsman and Archer are viable until you have decent rare replacements (Forest Scout, Flail Warden) at level 5+\n- Don't invest Forge Stones in commons beyond the achievement threshold\n- A level 9 common is still worse than a level 6 rare in most cases\n\nIf you're past level 60 and still using commons in your main lineup, check the rare and epic guides for better options.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-rare-troops-guide",
        "name": "Rare Troop Guide — Best Rare Heroes to Invest In",
        "title": "Rare Troop Guide — Best Rare Units and Upgrades | War Inc: Rising Wiki",
        "meta_description": "Complete rare troop guide for War Inc: Rising. Which rares are worth forge stones, multi-unit vs single-unit mechanics, and the one rare that beats a level 6 mythic.",
        "date": "2026-06-12",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Forest Scout is the best rare range. Flail Warden is the best rare melee. Goblin Chef beats a level 6 Mythic at level 9 — the single best rare investment if you can get copies. Bomber dominates the 2,500-5,000 trophy range. Skip Apprentice Mage, Goblin Shaman, and Berserker entirely.\n\nThis guide covers every rare unit so you know exactly which ones deserve your Forge Stones and which are traps.",
            },
            {
                "heading": "Multi-Unit vs Single-Unit: What the Stats Actually Mean",
                "content": "This is the most important thing to understand about rare troops: the displayed HP and ATK stats for multi-units apply to EACH individual, not the entire squad.\n\nExample: A level 6 Berserker has 8 individuals. Each has ~4,600 HP and ~100 ATK shown in the stat sheet. The combined squad has roughly 36K HP and 800 ATK. Single units like Goblin Chef show their actual stats directly.\n\nMulti-units are better at triggering multiple abilities per attack cycle. Single units perform better as heavy hitters with concentrated stats. Knowing the difference changes how you evaluate every unit.",
            },
            {
                "heading": "Best Rare Range: Forest Scout",
                "content": "Forest Scout has the highest attack of the three rare range options and a multi-target ability dealing 200% damage. At level 7 with Trigger Master, the damage output spikes dramatically. He's the best rare troop to invest Forge Stones in — worth taking all the way to level 9.\n\nPosition: Place him away from other archers in a safe back position. Archers and marksmen are priority targets for enemy abilities. A dead Forest Scout deals no damage.\n\nApprentice Mage and Goblin Shaman are not worth your resources. Apprentice Mage gets replaced by Flame Mage eventually, and Goblin Shaman requires a wheel unlock before you can even use him.",
            },
            {
                "heading": "Best Rare Melee: Flail Warden",
                "content": "Flail Warden has lower individual stats than Goblin Warrior, but his splash damage handles multi-units extremely well. In the early-mid game where you face mostly multi-unit enemies, Flail Warden outperforms every other rare melee.\n\nGoblin Warrior has decent HP and damage but isn't a priority investment. Berserker has the least value of all rare melees — 8 individuals sounds good on paper, but each is fragile at ~4,600 HP and falls off quickly.",
            },
            {
                "heading": "Goblin Chef: The Rare That Beats Mythics",
                "content": "Goblin Chef (also called Shredder) is the one rare that's better than a level 6 Mythic. At level 9 with ~1,000 Forge Stones invested, he has HP near a level 6 Night King and ATK near Light Seeker — for half the deployment cost.\n\nHis ability hits a small area for splash damage plus a 2-second stun. That's longer than Griffin Rider's 1s and Ursa's 0.5s stun.\n\nThe catch: he's wheel/cardmaster only. Getting copies is hard. But if you can, he's the single best rare investment in the game.",
            },
            {
                "heading": "Utility Rares: Bomber, Paladin, Frost Skeleton",
                "content": "Bomber is a suicide unit dealing 3x base ATK on death. At level 7, he stuns enemies on death. He dominates the 2,500-5,000 trophy range in Arena. The cheapest way to get him is uncommon fusion with gold.\n\nPaladin is a multi-unit tank with shields every 10 seconds. Combo him with Radiant Warrior for shield overlap: Radiant's shield activates at battle start (8s duration), Paladin's at 10s — creating a 2-second window where both shields are active.\n\nFrost Skeleton deals area damage + speed reduction on death. Flexible placement: front for instant slow, middle for delayed slow, back for long-delayed slow. Pairs best with Bone Marksman, Bone Gunner, and Iron Bulwark for attack speed synergy.",
            },
        ],
    },
    {
        "slug": "war-inc-rising-epic-troops-guide",
        "name": "Epic Troop Guide — Best Epic Heroes and Upgrade Priority",
        "title": "Epic Troop Guide — Best Epic Units Ranked | War Inc: Rising Wiki",
        "meta_description": "Complete epic troop guide for War Inc: Rising. Oracle upgrade priority, Poison Master for Infinite War, Bone Warlock + Bone Gunner combo, and playable level thresholds for epic units.",
        "date": "2026-06-14",
        "author": "Klown Kollege",
        "sections": [
            {
                "heading": "The Short Version",
                "content": "Oracle is the best epic in the game — upgrade to level 7 first, before any other epic. Poison Master carries early-mid Infinite War. Bone Warlock + Bone Gunner is the strongest epic combo. Every other epic has a specific role or is outclassed by rares.\n\nHere's the full breakdown with playability thresholds, upgrade priorities, and which epics to skip.",
            },
            {
                "heading": "Epic Troop Playability Thresholds",
                "content": "Epics are harder to get than rares, so most newer players have them at level 3 or 4. That's fine — here's when each type becomes playable:\n\n- Multi-unit epics: Generally playable at level 5 (stats become comparable to a level 6 rare)\n- Exceptions: Poison Master (useful at level 4 thanks to toxic field ability), Oracle (attack buff works at any level)\n- Range units: Need 10,000+ HP to survive common burst abilities\n- Melee troops: Need around 20,000+ HP to tank effectively\n\nDon't judge an epic by its level 3 stats. Most need a few levels to hit their stride.",
            },
            {
                "heading": "Oracle — Priority #1, Invest Here First",
                "content": "Oracle is the best epic troop in the game. You'll use them in 99% of your army setups. Here's why:\n\nEach Oracle provides a 4% attack buff to nearby allies, stacking up to 20 times. At level 6, each Oracle gives 4% per stack, for a max of 32% increased attack power. With 9 Oracles, that's a 36% team-wide buff. With 18, it's 72%.\n\nLevel 7 is critical — it dramatically increases the ability range so the full effect applies consistently to your whole formation. Getting Oracle to level 7 should be your highest epic priority by far.",
            },
            {
                "heading": "Poison Master — Infinite War Carry",
                "content": "Poison Master shreds multi-unit armies with splash damage. In Infinite War, many enemies are weak to water damage, making Poison Master a primary damage dealer.\n\nBuild 8-10 level 6 Poison Masters to carry your Infinite War progression. It's one of the best early-to-mid game investments you can make.\n\nAs your account progresses and you unlock stronger AoE options, Poison Master's usage falls off. But for the first few months, this unit will earn its keep.",
            },
            {
                "heading": "Bone Warlock + Bone Gunner Combo",
                "content": "Bone Warlock's slow effect is dangerous because it triggers Bone Gunner's execution barrage. The combo deals massive damage to slowed targets.\n\nBone Warlock has very long range — keep him in the back line. His energy-based ability pairs well with Ripple Wizard for faster casts. Also useful in Twin Dragon Hunt for wind damage.\n\nSnowman Warrior is a weaker alternative. He excels at slowing enemy front lines instead of back-line units, which helps your tanks win engagements. Use him until you get Bone Warlock leveled up.",
            },
            {
                "heading": "The Rest: When Each Epic Shines",
                "content": "- Rockthrower: Below average overall. His niche is sacrificial stun against Frost Queen flanking — stunning her on landing prevents her devastating AoE from activating.\n- Flame Mage: Underperforms compared to a level 9 Forest Scout even at level 7. Excels specifically in Evil Ivy Hunt where fire damage matters.\n- Pumpkin Guard: Use until you get a level 8 Goblin Chef. Taunt is useful in Infinite War for keeping pressure off other tanks.\n- Woodland Wizard: Wheel/cardmaster only, hard to obtain. More reliable healer than Woodland Guardian with faster activation. Excellent in Evil Ivy Hunt.\n- Royal Archer and Dwarf Berserker: Wheel/cardmaster only and very expensive. Skip unless you're a heavy spender.",
            },
        ],
    },
]


def build_blog_posts(name_map: dict, slug_map: dict) -> list:
    pages = []
    for post in BLOG_POSTS:
        slug = post["slug"]
        sections = post["sections"]
        meta_desc = post["meta_description"]

        # Build content preview (first section)
        preview = sections[0]["content"][:200] + "..." if sections else ""

        title = post["title"]

        # Related links to heroes mentioned in the post
        related_heroes = []
        all_text = " ".join(s["content"] for s in sections).lower()
        # Find heroes mentioned by name
        mentioned = set()
        for uid, slug_name in slug_map.items():
            name = (name_map.get(uid) or "").lower()
            if name and len(name) > 2 and name in all_text:
                if name not in mentioned:
                    mentioned.add(name)
                    related_heroes.append({
                        "name": (name_map.get(uid) or name.title()),
                        "slug": slug_name,
                    })
                    if len(related_heroes) >= 8:
                        break

        pages.append({
            "slug": slug,
            "name": post["name"],
            "title": title,
            "meta_description": meta_desc,
            "type": "blog",
            "date": post["date"],
            "author": post.get("author", "War Inc Wiki Team"),
            "sections": sections,
            "preview": preview,
            "related_heroes": related_heroes,
            "word_count": sum(len(s["content"].split()) for s in sections),
            "schema": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": post["name"],
                "description": meta_desc,
                "datePublished": post["date"],
                "author": {"@type": "Person", "name": post.get("author", "War Inc Wiki Team")},
            },
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

    print("Loading building upgrade data...")
    building_upgrade_map, resource_bd_map = load_building_upgrades()

    # Load card_growth to filter playable units
    cg = load_json(DATA_DIR / "config" / "card_growth.json")
    battle_units = cg.get("battleUnits", {})
    # Build set of unit IDs that are actually shown in game (canShow=True)
    shown_ids = set()
    for uid, u in battle_units.items():
        if isinstance(u, dict) and u.get("canShow") == True:
            shown_ids.add(str(u.get("id", uid)))

    print("Loading image map...")
    image_map = load_json(DATA_DIR / "unit_image_map.json")

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
        page = build_page_data(unit_id, unit, name_map, loc, skill_attrs, skill_descs, filtered_db, slug_map, image_map)
        if not page:
            continue

        page["slug"] = slug_map.get(str(unit["id"]), page["slug"])

        if unit.get("unit_type") is None:
            uid_int = unit.get("id") or (int(unit_id) if str(unit_id).isdigit() else 0)
            if 2001 <= uid_int <= 2010:
                page["type"] = "followers"
            elif uid_int in BUILDING_IDS:
                page["type"] = "buildings"
            else:
                page["type"] = "special"

        # Also catch type=5 buildings
        if unit.get("unit_type") == 5 and unit.get("id") in BUILDING_IDS:
            page["type"] = "buildings"

        # Inject building upgrade costs if available
        if page["type"] == "buildings":
            inject_building_upgrades(page, building_upgrade_map, resource_bd_map, loc)

        # Inject image URL from extracted game assets
        img_key = f'{page["type"]}/{page["id"]}'
        if image_map and img_key in image_map:
            page["image"] = image_map[img_key]

        all_pages.append(page)

    # Inject video guide references from YouTube transcripts
    print("Injecting video guide references into hero pages...")
    VIDEO_GUIDES = {
        "swordsman": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Best common melee. Multi-unit with splash damage in skill radius. In a 2-deployment-point mirror match, Swordsman beats Demoman every time."}],
        "demoman": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Stun only hits one target. Inferior to Swordsman — mirror match always loses. Only use if you have no Swordsman copies."}],
        "woodshield-guard": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Trash. Single unit (not multi-unit) so stats apply only to one troop. Alone and useless — skip entirely. Don't spend forge stones here even for achievement."}],
        "archer": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Best common range pick. Highest attack among common range units, multi-target skill for reliable damage. When filling last deployment points with range, Archer is the best choice."}],
        "gunner": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Fire damage is too low to matter even against fire-weak enemies like Pumpkin Guard. Archer deals more effective damage despite no elemental advantage."}],
        "snowball-thrower": [{"title": "Beginner Tips: Common Troops", "url": "https://www.youtube.com/watch?v=eSiJN4w0y-o", "advice": "Water damage is irrelevant. Slow effect on skill is useless. Archer is strictly better in every situation."}],
        "forest-scout": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Best rare range unit. Highest attack of the three rare range options. Multi-target ability deals 200% damage. At level 7 with Trigger Master, damage output spikes dramatically. Place away from other archers in a safe back position."}],
        "apprentice-mage": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Passable but replaced by Flame Mage. Fire damage barely matters — a level 7 Mage does only ~5% more damage than a level 6 Forest Scout even against fire-weak enemies. Don't waste forge stones."}],
        "goblin-shaman": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Not worth the investment loop. Must unlock in wheel first. By the time you can fuse and upgrade him, Woodland Wizard will replace him. Skip."}],
        "berserker": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Low value. Multi-unit with 8 individuals at level 6, but each individual is fragile (4,600 HP). Falls off quickly. Don't invest forge stones."}],
        "goblin-warrior": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "High HP and decent damage from ability make him useable but not a priority. Flail Warden is generally the better rare melee pick for new players."}],
        "flail-warden": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Best rare melee. Lower stats than Goblin Warrior but splash damage handles multi-units extremely well. Play more Wardens than Goblin Warriors as a new player."}],
        "paladin": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Multi-unit tank with high HP and surprisingly high attack. Generates a shield every 10 seconds. Combo with Radiant Warrior: Radiant's shield starts at battle (8s duration), Paladin's activates at 10s — creates 2s overlap for extra survivability."}],
        "goblin-chef": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Better than a level 6 mythic. Single unit with very high HP and ATK for a tank. Ability deals splash + 2-second stun (longer than Griffin Rider at 1s and Ursa at 0.5s). At level 9 (~1,000 forge stones): HP near level 6 Night King, ATK near Light Seeker, for half the deployment cost. Hard to get copies (wheel/cardmaster unlock required)."}],
        "bomber": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "Suicide unit dealing 3x base ATK on death. At level 7, stuns on death. Best in backstab/outflank strategies. In split formation vs backstabs, place front close to corner so he charges enemy front line rather than chasing stabbers."}],
        "frost-skeleton": [{"title": "Rare Troop Guide", "url": "https://www.youtube.com/watch?v=TR2W-ndo_Ms", "advice": "On death, deals area damage + speed reduction. Flexible placement: front for instant slow, middle for delayed slow, back for long delayed slow. Pairs best with Bone Marksman, Bone Gunner, Bone Warden, and Iron Bulwark for attack speed synergy."}],
        "oracle": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Best epic troop in the game — used in 99% of army setups. 4% attack buff per Oracle stacks up to 20 times (32% max at level 6). Level 7 dramatically increases ability range so full effect applies consistently. Highest forge stone priority among all epics."}],
        "poison-master": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Excellent for new player PvP against multi-unit armies — splash damage shreds them. Primary damage dealer in Infinite War since many enemies are weak to water. Falls off as you unlock stronger AoE options."}],
        "bone-warlock": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Slow effect is dangerous when paired with Bone Gunner (triggers execution barrage). Very long range ability — keep positioned safely in back line. Energy-based ability pairs well with Ripple Wizard. Also useful in Twin Dragon Hunt for wind damage."}],
        "snowman-warrior": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Weaker alternative to Bone Warlock. Multi-unit (each can trigger own ability). Better at slowing enemy front lines and helping your tanks win engagements. Use until you get a playable Bone Warlock."}],
        "rock-thrower": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Below average overall — low HP and damage for 6-cost melee. However, has a niche use: place as sacrificial stun against Frost Queen flanks/backstabs. Stunning her on landing prevents her devastating AoE from activating."}],
        "flame-mage": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Replacement for Apprentice Mage but underperforms compared to level 9 Forest Scout even at level 7. Limited arena use (situational against bone warlocks/ninja assassins). Excels in Evil Ivy Hunt where fire damage matters."}],
        "pumpkin-guard": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Use until you get level 8 Goblin Chef. Taunt ability useful in Infinite War to keep pressure off other tanks. Surprisingly high damage output for a tank — solid in Evil Ivy Hunt for maximizing total damage."}],
        "wooden-wizard": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Wheel/cardmaster only — hard to obtain. More reliable healer than Woodland Guardian with faster activation. Excellent at keeping range units alive in arena. Very useful in Evil Ivy Hunt where sustained healing matters."}],
        "royal-archer": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Wheel/cardmaster only. Expensive and difficult to obtain copies of. Unrealistic option for most free-to-play players."}],
        "dwarf-berserker": [{"title": "Epic Troop Guide", "url": "https://www.youtube.com/watch?v=VRxHfkJX8D0", "advice": "Wheel/cardmaster only. Expensive and difficult to obtain copies of. Unrealistic option for most free-to-play players."}],
    }
    for page in all_pages:
        if page["type"] == "heroes" and page["slug"] in VIDEO_GUIDES:
            page["video_guides"] = VIDEO_GUIDES[page["slug"]]
    print(f"  Injected video guides for {len(VIDEO_GUIDES)} heroes")

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

    print("Building tier list pages...")
    for page in build_tier_list_pages(filtered_db, name_map, slug_map, loc):
        all_pages.append(page)

    print("Building blog posts...")
    for page in build_blog_posts(name_map, slug_map):
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
            "rarity_name": page.get("rarity_name"),
            "profession_name": page.get("profession_name"),
            "cost": page.get("cost"),
            "combat_power": page.get("combat_power"),
            "image": page.get("image"),
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
