class_name UIThemeLogic
extends RefCounted
## Procedural Sci-Fi RTS UI & Palette formatting logic.
## Strict parity with logic/ui_theme.py. Simple procedural functions, no OOP.

static func get_scifi_hud_colors() -> Dictionary:
	return {
		"bg_topbar": Color("#060a14f5"),
		"bg_console": Color("#040810f8"),
		"bg_bay_panel": Color("#02050cf0"),
		"bg_button_normal": Color("#091222"),
		"bg_button_hover": Color("#0f233f"),
		"bg_button_pressed": Color("#0284c7"),
		"bg_button_disabled": Color("#040810"),
		"border_panel": Color("#1b3552"),
		"border_button_normal": Color("#244569"),
		"border_button_hover": Color("#00e5ff"),
		"border_button_active": Color("#38bdf8"),
		"border_button_disabled": Color("#0f1f30"),
		"text_primary": Color("#e2e8f0"),
		"text_secondary": Color("#94a3b8"),
		"text_cyan_glow": Color("#38bdf8"),
		"text_green_glow": Color("#22c55e"),
		"text_amber_warning": Color("#f59e0b"),
		"text_red_alert": Color("#ef4444"),
		"hp_bar_bg": Color("#091220"),
		"hp_bar_fill_high": Color("#22c55e"),
		"hp_bar_fill_mid": Color("#f59e0b"),
		"hp_bar_fill_low": Color("#ef4444"),
	}

static func get_planetary_surface_palette() -> Dictionary:
	return {
		"ocean_deep": Color("#050b18"),
		"ocean_shallow": Color("#0d223f"),
		"shelf_cyan": Color("#0284c7"),
		"coastal_lowland": Color("#1e293b"),
		"continental_rock": Color("#334155"),
		"mountain_ridge": Color("#475569"),
		"crater_fissure": Color("#38bdf8"),
		"atmosphere_rim": Color("#38bdf8"),
		"atmosphere_glow": Color("#0ea5e9"),
		"normal_bump_strength": 3.2,
		"roughness_water": 0.22,
		"roughness_land": 0.82,
		"noise_frequency": 0.015,
		"noise_octaves": 5,
	}

static func format_energy_display(energy: float, income_rate: float) -> Dictionary:
	var val: float = maxf(0.0, energy)
	var rate: float = income_rate
	var is_low: bool = val < 25.0
	return {
		"label": "ENERGY: %d E" % int(val),
		"rate_label": "(+%.1f/s)" % rate,
		"full_text": "ENERGY: %d E  (+%.1f/s)" % [int(val), rate],
		"is_low": is_low,
		"color": Color("#ef4444") if is_low else Color("#22c55e"),
	}

static func format_wave_threat_alert(is_wave_active: bool, wave_num: int, remaining_time: float, active_invaders_count: int) -> Dictionary:
	if is_wave_active:
		return {
			"badge": "[ ACTIVE INCURSION ]",
			"text": "WAVE #%d // %d HOSTILES ACTIVE" % [wave_num, active_invaders_count],
			"progress_pct": 100.0,
			"status_color": Color("#ef4444"),
			"is_critical": true,
		}

	var t_left: float = maxf(0.0, remaining_time)
	var total_cycle: float = 20.0
	var progress: float = clampf(((total_cycle - t_left) / total_cycle) * 100.0, 0.0, 100.0)
	var is_near: bool = t_left <= 5.0
	return {
		"badge": "[ THREAT IMMINENT ]" if is_near else "[ SURVEILLANCE ]",
		"text": "NEXT WAVE #%d IN T-%02ds" % [wave_num, int(t_left)],
		"progress_pct": progress,
		"status_color": Color("#ef4444") if is_near else Color("#f59e0b"),
		"is_critical": is_near,
	}

static func calculate_health_bar_color(current_hp: float, max_hp: float) -> Color:
	if max_hp <= 0.0:
		return Color("#ef4444")
	var pct: float = clampf((current_hp / max_hp) * 100.0, 0.0, 100.0)
	if pct > 60.0:
		return Color("#22c55e")
	elif pct > 30.0:
		return Color("#f59e0b")
	return Color("#ef4444")

static func format_structure_inspector_data(node_id: int, node_data: Dictionary, faction_data: Dictionary) -> Dictionary:
	if node_id < 0 or node_data.is_empty():
		return {
			"is_selected": false,
			"sector_code": "SECTOR // ORBITAL",
			"affiliation_name": "NEUTRAL ORBIT",
			"affiliation_color": Color("#64748b"),
			"structure_tag": "[ UNSELECTED ]",
			"structure_name": "GEODESIC SECTOR",
			"portrait_key": "empty",
			"hp": 0,
			"max_hp": 0,
			"hp_percent": 0.0,
			"hp_color": Color("#64748b"),
			"hp_text": "STATUS: IDLE",
			"stats_line_1": "TELEMETRY: Drag to orbit planet",
			"stats_line_2": "ACTION: Click any node to command",
		}

	var ctrl: Variant = node_data.get("controller", 0)
	var c_str: String = str(ctrl)
	var fname: String = "UNCLAIMED SECTOR"
	var fcolor: Color = Color("#64748b")

	if c_str == "1" or c_str == "player":
		fname = faction_data.get(1, {}).get("name", "Solarian Federation") + " [ALLIED]"
		fcolor = Color(faction_data.get(1, {}).get("color", "#22c55e"))
	elif faction_data.has(ctrl):
		fname = faction_data[ctrl].get("name", "Faction #" + str(ctrl)) + " [HOSTILE]"
		fcolor = Color(faction_data[ctrl].get("color", "#a855f7"))

	var bld: Variant = node_data.get("building")
	if bld != null:
		var btype: String = bld.get("type", "unknown")
		var hp: int = int(maxf(0.0, bld.get("hp", 0.0)))
		var max_hp: int = int(maxf(1.0, bld.get("max_hp", 100.0)))
		var pct: float = clampf((float(hp) / float(max_hp)) * 100.0, 0.0, 100.0)
		var hp_col: Color = calculate_health_bar_color(float(hp), float(max_hp))
		var hp_txt: String = "%d / %d HP  (%d%%)" % [hp, max_hp, int(pct)]

		if btype == "base":
			return {
				"is_selected": true,
				"sector_code": "SECTOR // %03d" % node_id,
				"affiliation_name": fname,
				"affiliation_color": fcolor,
				"structure_tag": "[ COMMAND HQ ]",
				"structure_name": "STRATEGIC NEXUS",
				"portrait_key": "base",
				"hp": hp,
				"max_hp": max_hp,
				"hp_percent": pct,
				"hp_color": hp_col,
				"hp_text": hp_txt,
				"stats_line_1": "CLASS: Planetary Command Core",
				"stats_line_2": "ENERGY FLOW: +5.0 E/s  |  BATTERY: 40 DMG (1 Hop)",
			}
		elif btype == "harvester":
			var neighbors_cnt: int = node_data.get("neighbors", []).size()
			var prod: int = 1 + int(neighbors_cnt / 2)
			return {
				"is_selected": true,
				"sector_code": "SECTOR // %03d" % node_id,
				"affiliation_name": fname,
				"affiliation_color": fcolor,
				"structure_tag": "[ HARVESTER ]",
				"structure_name": "QUANTUM EXTRACTOR",
				"portrait_key": "harvester",
				"hp": hp,
				"max_hp": max_hp,
				"hp_percent": pct,
				"hp_color": hp_col,
				"hp_text": hp_txt,
				"stats_line_1": "CLASS: Economic Generator",
				"stats_line_2": "EXTRACTION YIELD: +%d E/s via %d Conduits" % [prod, neighbors_cnt],
			}
		elif btype == "turret":
			var dmg: float = bld.get("damage", 35.0)
			var cd: float = bld.get("cooldown", 0.8)
			var dps: float = (dmg / cd) if cd > 0.0 else 0.0
			var r_hops: int = bld.get("attack_range_hops", 2)
			return {
				"is_selected": true,
				"sector_code": "SECTOR // %03d" % node_id,
				"affiliation_name": fname,
				"affiliation_color": fcolor,
				"structure_tag": "[ TURRET ]",
				"structure_name": "PULSE DEFENSE CANNON",
				"portrait_key": "turret",
				"hp": hp,
				"max_hp": max_hp,
				"hp_percent": pct,
				"hp_color": hp_col,
				"hp_text": hp_txt,
				"stats_line_1": "CLASS: Kinetic Rapid-Fire Battery",
				"stats_line_2": "FIREPOWER: %d DMG (%.1f DPS)  |  RANGE: %d Hops" % [int(dmg), dps, r_hops],
			}
		elif btype == "wall":
			return {
				"is_selected": true,
				"sector_code": "SECTOR // %03d" % node_id,
				"affiliation_name": fname,
				"affiliation_color": fcolor,
				"structure_tag": "[ FORTIFICATION ]",
				"structure_name": "PLASMA BARRICADE",
				"portrait_key": "wall",
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
				"is_selected": true,
				"sector_code": "SECTOR // %03d" % node_id,
				"affiliation_name": fname,
				"affiliation_color": fcolor,
				"structure_tag": "[ %s ]" % btype.to_upper(),
				"structure_name": btype.to_upper(),
				"portrait_key": "empty",
				"hp": hp,
				"max_hp": max_hp,
				"hp_percent": pct,
				"hp_color": hp_col,
				"hp_text": hp_txt,
				"stats_line_1": "CLASS: Surface Facility",
				"stats_line_2": "STATUS: Operational",
			}

	return {
		"is_selected": true,
		"sector_code": "SECTOR // %03d" % node_id,
		"affiliation_name": fname,
		"affiliation_color": fcolor,
		"structure_tag": "[ UNCLAIMED ]",
		"structure_name": "SURFACE NODE",
		"portrait_key": "empty",
		"hp": 0,
		"max_hp": 0,
		"hp_percent": 0.0,
		"hp_color": Color("#64748b"),
		"hp_text": "SECTOR CLEAR",
		"stats_line_1": "TOPOLOGY: Available for Strategic Expansion",
		"stats_line_2": "DEPLOYMENT: Wall (25E), Harvester (50E), Turret (75E)",
	}

static func format_command_button_data(action_type: String, current_energy: float, cost: float, cooldown: float, is_active_mode: bool) -> Dictionary:
	var names: Dictionary = {
		"wall": "WALL",
		"harvester": "HARVESTER",
		"turret": "TURRET",
		"purifier": "PURIFIER",
		"assault": "ASSAULT SQUAD",
		"wave": "FORCE INCURSION",
	}
	var hotkeys: Dictionary = {
		"wall": "[1]",
		"harvester": "[2]",
		"turret": "[3]",
		"purifier": "[4]",
		"assault": "[R]",
		"wave": "[SPC]",
	}

	var title: String = names.get(action_type, action_type.to_upper())
	var hotkey: String = hotkeys.get(action_type, "")
	var is_affordable: bool = (current_energy >= cost)
	var is_on_cooldown: bool = (cooldown > 0.0)

	var status_text: String = ""
	if is_on_cooldown:
		status_text = "RECHARGE (%ds)" % int(cooldown + 0.99)
	elif is_active_mode:
		status_text = "[ ACTIVE TARGET ]"
	elif cost > 0:
		status_text = "%d E" % int(cost)
	else:
		status_text = "+15 E BONUS"

	return {
		"title": title,
		"hotkey": hotkey,
		"cost": cost,
		"cost_label": status_text,
		"full_button_text": "%s %s\n%s" % [hotkey, title, status_text],
		"is_enabled": is_affordable and not is_on_cooldown,
		"is_active": is_active_mode,
		"is_affordable": is_affordable,
		"is_on_cooldown": is_on_cooldown,
	}
