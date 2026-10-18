# logic/ui_theme.py
# Pure procedural functions for Sci-Fi Tactical RTS UI and Visual Palette formatting.
# No OOP: pure dictionaries, numbers, and strings.

def get_scifi_hud_colors() -> dict:
    """Returns standard color definitions for the modernized military sci-fi HUD."""
    return {
        "bg_topbar": "#060a14f5",
        "bg_console": "#040810f8",
        "bg_bay_panel": "#02050cf0",
        "bg_button_normal": "#091222",
        "bg_button_hover": "#0f233f",
        "bg_button_pressed": "#0284c7",
        "bg_button_disabled": "#040810",
        "border_panel": "#1b3552",
        "border_button_normal": "#244569",
        "border_button_hover": "#00e5ff",
        "border_button_active": "#38bdf8",
        "border_button_disabled": "#0f1f30",
        "text_primary": "#e2e8f0",
        "text_secondary": "#94a3b8",
        "text_cyan_glow": "#38bdf8",
        "text_green_glow": "#22c55e",
        "text_amber_warning": "#f59e0b",
        "text_red_alert": "#ef4444",
        "hp_bar_bg": "#091220",
        "hp_bar_fill_high": "#22c55e",
        "hp_bar_fill_mid": "#f59e0b",
        "hp_bar_fill_low": "#ef4444",
    }


def get_planetary_surface_palette() -> dict:
    """Returns procedural color stops and noise generation parameters for planetary textures."""
    return {
        "ocean_deep": "#050b18",
        "ocean_shallow": "#0d223f",
        "shelf_cyan": "#0284c7",
        "coastal_lowland": "#1e293b",
        "continental_rock": "#334155",
        "mountain_ridge": "#475569",
        "crater_fissure": "#38bdf8",
        "atmosphere_rim": "#38bdf8",
        "atmosphere_glow": "#0ea5e9",
        "normal_bump_strength": 3.2,
        "roughness_water": 0.22,
        "roughness_land": 0.82,
        "noise_frequency": 0.015,
        "noise_octaves": 5,
    }


def format_energy_display(energy: float, income_rate: float) -> dict:
    """Formats the energy readout with status tags and income rate."""
    val = max(0.0, float(energy))
    rate = float(income_rate)
    is_low = val < 25.0
    return {
        "label": f"ENERGY: {int(val)} E",
        "rate_label": f"(+{rate:.1f}/s)",
        "full_text": f"ENERGY: {int(val)} E  (+{rate:.1f}/s)",
        "is_low": is_low,
        "color": "#ef4444" if is_low else "#22c55e",
    }


def format_wave_threat_alert(is_wave_active: bool, wave_num: int, remaining_time: float, active_invaders_count: int) -> dict:
    """Formats tactical wave status, progress percentages, and alert color."""
    if is_wave_active:
        return {
            "badge": "[ ACTIVE INCURSION ]",
            "text": f"WAVE #{wave_num} // {active_invaders_count} HOSTILES ACTIVE",
            "progress_pct": 100.0,
            "status_color": "#ef4444",
            "is_critical": True,
        }
    
    t_left = max(0.0, float(remaining_time))
    total_cycle = 20.0
    progress = max(0.0, min(100.0, ((total_cycle - t_left) / total_cycle) * 100.0))
    is_near = t_left <= 5.0
    return {
        "badge": "[ THREAT IMMINENT ]" if is_near else "[ SURVEILLANCE ]",
        "text": f"NEXT WAVE #{wave_num} IN T-{int(t_left):02d}s",
        "progress_pct": progress,
        "status_color": "#ef4444" if is_near else "#f59e0b",
        "is_critical": is_near,
    }


def calculate_health_bar_color(current_hp: float, max_hp: float) -> str:
    """Calculates health percentage and returns corresponding sci-fi status color."""
    if max_hp <= 0.0:
        return "#ef4444"
    pct = max(0.0, min(100.0, (current_hp / max_hp) * 100.0))
    if pct > 60.0:
        return "#22c55e"
    elif pct > 30.0:
        return "#f59e0b"
    return "#ef4444"


def format_structure_inspector_data(node_id: int, node_data: dict, faction_data: dict) -> dict:
    """Produces clean, emoji-free sci-fi tactical inspector card data."""
    if node_id < 0 or not node_data:
        return {
            "is_selected": False,
            "sector_code": "SECTOR // ORBITAL",
            "affiliation_name": "NEUTRAL ORBIT",
            "affiliation_color": "#64748b",
            "structure_tag": "[ UNSELECTED ]",
            "structure_name": "GEODESIC SECTOR",
            "hp": 0,
            "max_hp": 0,
            "hp_percent": 0.0,
            "hp_color": "#64748b",
            "hp_text": "STATUS: IDLE",
            "stats_line_1": "TELEMETRY: Drag to orbit planet",
            "stats_line_2": "ACTION: Click any node to command",
        }

    ctrl = node_data.get("controller", 0)
    c_str = str(ctrl)
    
    # Determine Faction Affiliation
    if c_str == "1" or c_str == "player":
        fname = faction_data.get(1, {}).get("name", "Solarian Federation") + " [ALLIED]"
        fcolor = faction_data.get(1, {}).get("color", "#22c55e")
    elif ctrl in faction_data:
        fname = faction_data[ctrl].get("name", f"Faction #{ctrl}") + " [HOSTILE]"
        fcolor = faction_data[ctrl].get("color", "#a855f7")
    else:
        fname = "UNCLAIMED SECTOR"
        fcolor = "#64748b"

    bld = node_data.get("building")
    if bld:
        btype = bld.get("type", "unknown")
        hp = max(0, int(bld.get("hp", 0)))
        max_hp = max(1, int(bld.get("max_hp", 100)))
        pct = max(0.0, min(100.0, (hp / float(max_hp)) * 100.0))
        hp_col = calculate_health_bar_color(float(hp), float(max_hp))
        hp_txt = f"{hp} / {max_hp} HP  ({int(pct)}%)"

        if btype == "base":
            return {
                "is_selected": True,
                "sector_code": f"SECTOR // {node_id:03d}",
                "affiliation_name": fname,
                "affiliation_color": fcolor,
                "structure_tag": "[ COMMAND HQ ]",
                "structure_name": "STRATEGIC NEXUS",
                "hp": hp,
                "max_hp": max_hp,
                "hp_percent": pct,
                "hp_color": hp_col,
                "hp_text": hp_txt,
                "stats_line_1": "CLASS: Planetary Command Core",
                "stats_line_2": "ENERGY FLOW: +5.0 E/s  |  BATTERY: 40 DMG (1 Hop)",
            }
        elif btype == "harvester":
            neighbors_cnt = len(node_data.get("neighbors", []))
            prod = 1 + int(neighbors_cnt / 2)
            return {
                "is_selected": True,
                "sector_code": f"SECTOR // {node_id:03d}",
                "affiliation_name": fname,
                "affiliation_color": fcolor,
                "structure_tag": "[ HARVESTER ]",
                "structure_name": "QUANTUM EXTRACTOR",
                "hp": hp,
                "max_hp": max_hp,
                "hp_percent": pct,
                "hp_color": hp_col,
                "hp_text": hp_txt,
                "stats_line_1": f"CLASS: Economic Generator",
                "stats_line_2": f"EXTRACTION YIELD: +{prod} E/s via {neighbors_cnt} Conduits",
            }
        elif btype == "turret":
            dmg = bld.get("damage", 35.0)
            cd = bld.get("cooldown", 0.8)
            dps = (dmg / cd) if cd > 0 else 0.0
            r_hops = bld.get("attack_range_hops", 2)
            return {
                "is_selected": True,
                "sector_code": f"SECTOR // {node_id:03d}",
                "affiliation_name": fname,
                "affiliation_color": fcolor,
                "structure_tag": "[ TURRET ]",
                "structure_name": "PULSE DEFENSE CANNON",
                "hp": hp,
                "max_hp": max_hp,
                "hp_percent": pct,
                "hp_color": hp_col,
                "hp_text": hp_txt,
                "stats_line_1": f"CLASS: Kinetic Rapid-Fire Battery",
                "stats_line_2": f"FIREPOWER: {dmg:.0f} DMG ({dps:.1f} DPS)  |  RANGE: {r_hops} Hops",
            }
        elif btype == "wall":
            return {
                "is_selected": True,
                "sector_code": f"SECTOR // {node_id:03d}",
                "affiliation_name": fname,
                "affiliation_color": fcolor,
                "structure_tag": "[ FORTIFICATION ]",
                "structure_name": "PLASMA BARRICADE",
                "hp": hp,
                "max_hp": max_hp,
                "hp_percent": pct,
                "hp_color": hp_col,
                "hp_text": hp_txt,
                "stats_line_1": "CLASS: Heavy Kinetic Absorber",
                "stats_line_2": "ARMOR: 400 HP Barrier  |  Movement Inhibitor",
            }
        else:
            return {
                "is_selected": True,
                "sector_code": f"SECTOR // {node_id:03d}",
                "affiliation_name": fname,
                "affiliation_color": fcolor,
                "structure_tag": f"[ {btype.upper()} ]",
                "structure_name": btype.upper(),
                "hp": hp,
                "max_hp": max_hp,
                "hp_percent": pct,
                "hp_color": hp_col,
                "hp_text": hp_txt,
                "stats_line_1": "CLASS: Surface Facility",
                "stats_line_2": "STATUS: Operational",
            }

    # Empty node
    return {
        "is_selected": True,
        "sector_code": f"SECTOR // {node_id:03d}",
        "affiliation_name": fname,
        "affiliation_color": fcolor,
        "structure_tag": "[ UNCLAIMED ]",
        "structure_name": "SURFACE NODE",
        "hp": 0,
        "max_hp": 0,
        "hp_percent": 0.0,
        "hp_color": "#64748b",
        "hp_text": "SECTOR CLEAR",
        "stats_line_1": "TOPOLOGY: Available for Strategic Expansion",
        "stats_line_2": "DEPLOYMENT: Wall (25E), Harvester (50E), Turret (75E)",
    }


def format_command_button_data(action_type: str, current_energy: float, cost: float, cooldown: float, is_active_mode: bool) -> dict:
    """Formats tactical command button labels, hotkeys, affordability, and active state."""
    names = {
        "wall": "WALL",
        "harvester": "HARVESTER",
        "turret": "TURRET",
        "purifier": "PURIFIER",
        "assault": "ASSAULT SQUAD",
        "wave": "FORCE INCURSION",
    }
    hotkeys = {
        "wall": "[1]",
        "harvester": "[2]",
        "turret": "[3]",
        "purifier": "[4]",
        "assault": "[R]",
        "wave": "[SPC]",
    }

    title = names.get(action_type, action_type.upper())
    hotkey = hotkeys.get(action_type, "")
    is_affordable = (current_energy >= cost)
    is_on_cooldown = (cooldown > 0.0)

    if is_on_cooldown:
        status_text = f"RECHARGE ({int(cooldown + 0.99)}s)"
    elif is_active_mode:
        status_text = "[ ACTIVE TARGET ]"
    elif cost > 0:
        status_text = f"{int(cost)} E"
    else:
        status_text = "+15 E BONUS"

    return {
        "title": title,
        "hotkey": hotkey,
        "cost": cost,
        "cost_label": status_text,
        "full_button_text": f"{hotkey} {title}\n{status_text}",
        "is_enabled": is_affordable and not is_on_cooldown,
        "is_active": is_active_mode,
        "is_affordable": is_affordable,
        "is_on_cooldown": is_on_cooldown,
    }
