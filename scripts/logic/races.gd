class_name RacesLogic
extends RefCounted
## Catálogo de Razas y Modificadores Planetarios estilo Age of Empires.
## Estilo procedimental puro: funciones estáticas y datos planos en diccionarios.

const RACES_CATALOG: Dictionary = {
	"solarian": {
		"id": "solarian",
		"name": "Solarian Hegemony",
		"category": "industrial",
		"color": "#22c55e",
		"description": "Humanos industriales especializados en macro-economía, asedio e ingeniería balística pesada.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.25,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 0.80,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.25,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.0,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "vanguard",
			"name": "Vanguard Mech",
			"hp": 120.0,
			"max_hp": 120.0,
			"speed": 0.50,
			"damage": 20.0,
			"trait": "Infantería mecanizada pesada con blindaje reforzado.",
		},
		"squad_doctrine": {
			"name": "Armored Spearhead",
			"units": [
				{"archetype": "vanguard", "name": "Vanguard Mech", "hp": 120.0, "max_hp": 120.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.2},
				{"archetype": "marine", "name": "Infantry Marine", "hp": 40.0, "max_hp": 40.0, "speed": 0.70, "damage": 10.0, "role": "light", "spawn_delay": 0.3, "scale": 0.8},
				{"archetype": "marine", "name": "Infantry Marine", "hp": 40.0, "max_hp": 40.0, "speed": 0.70, "damage": 10.0, "role": "light", "spawn_delay": 0.6, "scale": 0.8},
			],
		},
		"team_bonus": {
			"type": "passive_income_bonus",
			"description": "Aliados reciben +10% de ingreso pasivo base.",
			"value": 0.10,
		},
	},
	"krynn": {
		"id": "krynn",
		"name": "Krynn Swarm",
		"category": "biological",
		"color": "#a855f7",
		"description": "Enjambre insectoide de rápida reproducción, estructuras de bajo coste y alta regeneración.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 0.80,
			"wall_cost_mult": 0.80,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.25,
			"unit_hp_regen": 1.5,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "broodling",
			"name": "Broodling Swarm",
			"hp": 45.0,
			"max_hp": 45.0,
			"speed": 1.10,
			"damage": 10.0,
			"trait": "Avanza a gran velocidad y regenera tejido biológico.",
		},
		"squad_doctrine": {
			"name": "Brood Swarm",
			"units": [
				{"archetype": "broodling", "name": "Broodling", "hp": 45.0, "max_hp": 45.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.0, "scale": 0.7},
				{"archetype": "broodling", "name": "Broodling", "hp": 45.0, "max_hp": 45.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.2, "scale": 0.7},
				{"archetype": "broodling", "name": "Broodling", "hp": 45.0, "max_hp": 45.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.4, "scale": 0.7},
				{"archetype": "broodling", "name": "Broodling", "hp": 45.0, "max_hp": 45.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.6, "scale": 0.7},
				{"archetype": "broodling", "name": "Broodling", "hp": 45.0, "max_hp": 45.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.8, "scale": 0.7},
			],
		},
		"team_bonus": {
			"type": "spawn_delay_reduction",
			"description": "Unidades aliadas reducen su tiempo de preparación en 15%.",
			"value": 0.15,
		},
	},
	"nexus": {
		"id": "nexus",
		"name": "Nexus Protocol",
		"category": "synthetic",
		"color": "#06b6d4",
		"description": "Autómatas y mentes sintéticas que dominan la energía cuántica y el combate de largo alcance.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 3.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 1,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.0,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "railgun_mech",
			"name": "Railgun Automaton",
			"hp": 90.0,
			"max_hp": 90.0,
			"speed": 0.45,
			"damage": 35.0,
			"trait": "Artillería electromagnética con impacto a distancia.",
		},
		"squad_doctrine": {
			"name": "Quantum Battery",
			"units": [
				{"archetype": "railgun_mech", "name": "Railgun Automaton", "hp": 90.0, "max_hp": 90.0, "speed": 0.45, "damage": 35.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.1},
				{"archetype": "pulse_drone", "name": "Pulse Drone", "hp": 40.0, "max_hp": 40.0, "speed": 0.75, "damage": 8.0, "role": "light", "spawn_delay": 0.35, "scale": 0.75},
				{"archetype": "pulse_drone", "name": "Pulse Drone", "hp": 40.0, "max_hp": 40.0, "speed": 0.75, "damage": 8.0, "role": "light", "spawn_delay": 0.70, "scale": 0.75},
			],
		},
		"team_bonus": {
			"type": "turret_damage_bonus",
			"description": "Torretas aliadas obtienen +10% de daño balístico.",
			"value": 0.10,
		},
	},
	"aethelian": {
		"id": "aethelian",
		"name": "Aethelian Enclave",
		"category": "psionic",
		"color": "#eab308",
		"description": "Ancestrales psiónicos enfocados en la purificación territorial masiva y campos de plasma.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 3,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.0,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 2.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "archon_strider",
			"name": "Archon Strider",
			"hp": 130.0,
			"max_hp": 130.0,
			"speed": 0.50,
			"damage": 24.0,
			"trait": "Emite campos de energía psiónica al avanzar.",
		},
		"squad_doctrine": {
			"name": "Psionic Phalanx",
			"units": [
				{"archetype": "archon_strider", "name": "Archon Strider", "hp": 130.0, "max_hp": 130.0, "speed": 0.50, "damage": 24.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.2},
				{"archetype": "psionic_disciple", "name": "Psionic Disciple", "hp": 40.0, "max_hp": 40.0, "speed": 0.65, "damage": 10.0, "role": "light", "spawn_delay": 0.35, "scale": 0.8},
				{"archetype": "psionic_disciple", "name": "Psionic Disciple", "hp": 40.0, "max_hp": 40.0, "speed": 0.65, "damage": 10.0, "role": "light", "spawn_delay": 0.70, "scale": 0.8},
			],
		},
		"team_bonus": {
			"type": "purification_range_bonus",
			"description": "Instalaciones de purificación aliadas obtienen +1 salto de alcance.",
			"value": 1,
		},
	},
	"vorash": {
		"id": "vorash",
		"name": "Vorash Scavengers",
		"category": "nomad",
		"color": "#f97316",
		"description": "Piratas y chatarreros que prosperan mediante el pillaje y la demolición acelerada.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 2,
			"salvage_bounty": 35.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.0,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 2.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "raider_scout",
			"name": "Raider Scout",
			"hp": 55.0,
			"max_hp": 55.0,
			"speed": 0.90,
			"damage": 14.0,
			"trait": "Infiltrador táctico con bonificación extrema de demolición.",
		},
		"squad_doctrine": {
			"name": "Scavenger Raiding Party",
			"units": [
				{"archetype": "raider_scout", "name": "Raider Scout", "hp": 55.0, "max_hp": 55.0, "speed": 0.90, "damage": 14.0, "role": "siege", "spawn_delay": 0.0, "scale": 0.85},
				{"archetype": "raider_scout", "name": "Raider Scout", "hp": 55.0, "max_hp": 55.0, "speed": 0.90, "damage": 14.0, "role": "siege", "spawn_delay": 0.30, "scale": 0.85},
				{"archetype": "raider_scout", "name": "Raider Scout", "hp": 55.0, "max_hp": 55.0, "speed": 0.90, "damage": 14.0, "role": "siege", "spawn_delay": 0.60, "scale": 0.85},
			],
		},
		"team_bonus": {
			"type": "salvage_share",
			"description": "Aliados reciben el 50% del botín de chatarra por cada baja enemiga.",
			"value": 0.50,
		},
	},
	"titanforge": {
		"id": "titanforge",
		"name": "Titanforge Lithoids",
		"category": "mineral",
		"color": "#78716c",
		"description": "Seres minerales ultra acorazados, maestros de fortificaciones y guerra de desgaste.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 0.48,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.20,
			"unit_speed_mult": 0.85,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "juggernaut",
			"name": "Juggernaut Colossus",
			"hp": 240.0,
			"max_hp": 240.0,
			"speed": 0.25,
			"damage": 36.0,
			"trait": "Armadura monolítica masiva resistente a fuego cruzado.",
		},
		"squad_doctrine": {
			"name": "Monolithic Colossus",
			"units": [
				{"archetype": "juggernaut", "name": "Juggernaut Colossus", "hp": 240.0, "max_hp": 240.0, "speed": 0.25, "damage": 36.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.5},
			],
		},
		"team_bonus": {
			"type": "ally_building_hp_bonus",
			"description": "Edificios de aliados obtienen +20% de salud máxima.",
			"value": 0.20,
		},
	},
	"zephyrian": {
		"id": "zephyrian",
		"name": "Zephyrian Nomads",
		"category": "aerial",
		"color": "#38bdf8",
		"description": "Nómadas de los cielos planetarios con extrema agilidad, evasión y maniobras aéreas.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.0,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.15,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.25,
			"reanimate_chance": 0.0,
		},
		"unique_unit": {
			"type": "storm_skimmer",
			"name": "Storm Skimmer",
			"hp": 60.0,
			"max_hp": 60.0,
			"speed": 0.90,
			"damage": 14.0,
			"trait": "Deslizador atmosférico que puede volar sobre obstáculos.",
		},
		"squad_doctrine": {
			"name": "Sky Wing",
			"units": [
				{"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 60.0, "max_hp": 60.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.0, "scale": 0.85},
				{"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 60.0, "max_hp": 60.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.30, "scale": 0.85},
				{"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 60.0, "max_hp": 60.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.60, "scale": 0.85},
			],
		},
		"team_bonus": {
			"type": "ally_speed_bonus",
			"description": "La velocidad de marcha de todas las tropas aliadas aumenta 10%.",
			"value": 0.10,
		},
	},
	"umbral": {
		"id": "umbral",
		"name": "Umbral Parasites",
		"category": "void",
		"color": "#831843",
		"description": "Entidades del vacío que cosechan corrupción territorial y asimilan las bajas enemigas.",
		"econ_modifiers": {
			"harvester_yield_mult": 1.0,
			"base_income_bonus": 0.0,
			"building_cost_mult": 1.0,
			"wall_cost_mult": 1.0,
			"base_influence_hops": 2,
			"salvage_bounty": 0.0,
			"corrupt_node_income": 0.5,
		},
		"combat_modifiers": {
			"turret_cooldown_mult": 1.0,
			"turret_range_bonus": 0,
			"turret_damage_mult": 1.0,
			"wall_hp_mult": 1.0,
			"damage_reduction": 0.0,
			"unit_speed_mult": 1.0,
			"unit_hp_regen": 0.0,
			"purify_rate_mult": 1.0,
			"structure_damage_mult": 1.0,
			"evasion_chance": 0.0,
			"reanimate_chance": 0.30,
		},
		"unique_unit": {
			"type": "void_infestor",
			"name": "Void Infestor",
			"hp": 100.0,
			"max_hp": 100.0,
			"speed": 0.50,
			"damage": 20.0,
			"trait": "Corrompe nodos terrestres al desplazarse.",
		},
		"squad_doctrine": {
			"name": "Void Incursion",
			"units": [
				{"archetype": "void_infestor", "name": "Void Infestor", "hp": 100.0, "max_hp": 100.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.1},
				{"archetype": "void_infestor", "name": "Void Infestor", "hp": 100.0, "max_hp": 100.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.40, "scale": 1.1},
			],
		},
		"team_bonus": {
			"type": "corruption_immunity",
			"description": "Aliados son inmunes a penalizaciones de movimiento en zonas infectadas.",
			"value": 1.0,
		},
	},
}

static func get_all_race_ids() -> Array:
	return RACES_CATALOG.keys()

static func get_race_data(race_id: String) -> Dictionary:
	if RACES_CATALOG.has(race_id):
		return RACES_CATALOG[race_id]
	return RACES_CATALOG["solarian"]

static func calculate_building_cost(base_cost: float, building_type: String, race_id: String) -> float:
	var race = get_race_data(race_id)
	var econ: Dictionary = race.get("econ_modifiers", {})
	if building_type == "wall":
		return base_cost * float(econ.get("wall_cost_mult", 1.0))
	return base_cost * float(econ.get("building_cost_mult", 1.0))

static func calculate_harvester_income(base_rate_per_node: float, node_count: int, race_id: String) -> float:
	var race = get_race_data(race_id)
	var mult: float = float(race.get("econ_modifiers", {}).get("harvester_yield_mult", 1.0))
	return base_rate_per_node * float(node_count) * mult

static func calculate_base_passive_income(default_base_income: float, race_id: String) -> float:
	var race = get_race_data(race_id)
	var bonus: float = float(race.get("econ_modifiers", {}).get("base_income_bonus", 0.0))
	return default_base_income + bonus

static func calculate_initial_influence_hops(race_id: String) -> int:
	var race = get_race_data(race_id)
	return int(race.get("econ_modifiers", {}).get("base_influence_hops", 2))

static func apply_building_combat_stats(building_data: Dictionary, race_id: String) -> Dictionary:
	var modified: Dictionary = building_data.duplicate(true)
	var race = get_race_data(race_id)
	var c_mod: Dictionary = race.get("combat_modifiers", {})
	var btype: String = modified.get("type", "")

	if btype == "wall":
		var mult: float = float(c_mod.get("wall_hp_mult", 1.0))
		modified["max_hp"] = float(modified.get("max_hp", 300.0) * mult)
		modified["hp"] = modified["max_hp"]
	elif btype == "turret":
		var cd_mult: float = float(c_mod.get("turret_cooldown_mult", 1.0))
		var range_bonus: int = int(c_mod.get("turret_range_bonus", 0))
		var dmg_mult: float = float(c_mod.get("turret_damage_mult", 1.0))
		modified["cooldown"] = float(modified.get("cooldown", 1.0) * cd_mult)
		modified["attack_range_hops"] = int(modified.get("attack_range_hops", 2) + range_bonus)
		modified["damage"] = float(modified.get("damage", 25.0) * dmg_mult)
	elif btype == "purifier":
		var p_mult: float = float(c_mod.get("purify_rate_mult", 1.0))
		modified["purify_rate"] = float(modified.get("purify_rate", 15.0) * p_mult)

	return modified

static func calculate_incoming_damage(raw_damage: float, is_target_structure: bool, attacker_race_id: String = "", defender_race_id: String = "", attacker_role: String = "heavy") -> float:
	var damage: float = raw_damage
	if is_target_structure:
		if attacker_role == "light":
			damage *= 0.5
		if attacker_race_id != "":
			var att_race = get_race_data(attacker_race_id)
			damage *= float(att_race.get("combat_modifiers", {}).get("structure_damage_mult", 1.0))
	if defender_race_id != "":
		var def_race = get_race_data(defender_race_id)
		var reduction: float = float(def_race.get("combat_modifiers", {}).get("damage_reduction", 0.0))
		damage *= (1.0 - reduction)
	return maxf(0.0, damage)

static func get_race_squad_composition(race_id: String) -> Array:
	var race = get_race_data(race_id)
	var doctrine = race.get("squad_doctrine")
	if doctrine != null and (doctrine is Dictionary) and doctrine.has("units"):
		var res: Array = []
		for u in doctrine["units"]:
			res.append(u.duplicate(true))
		return res

	var unique: Dictionary = race.get("unique_unit", {})
	return [
		{
			"archetype": unique.get("type", "vanguard"),
			"name": unique.get("name", "Vanguard Mech"),
			"hp": float(unique.get("hp", 120.0)),
			"max_hp": float(unique.get("max_hp", 120.0)),
			"speed": float(unique.get("speed", 0.5)),
			"damage": float(unique.get("damage", 20.0)),
			"role": "heavy",
			"spawn_delay": 0.0,
			"scale": 1.2,
		},
		{
			"archetype": "scout",
			"name": "Scout",
			"hp": 40.0,
			"max_hp": 40.0,
			"speed": 0.8,
			"damage": 10.0,
			"role": "light",
			"spawn_delay": 0.35,
			"scale": 0.75,
		},
		{
			"archetype": "scout",
			"name": "Scout",
			"hp": 40.0,
			"max_hp": 40.0,
			"speed": 0.8,
			"damage": 10.0,
			"role": "light",
			"spawn_delay": 0.70,
			"scale": 0.75,
		},
	]

