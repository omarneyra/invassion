class_name TechTreeLogic
extends RefCounted
## Árbol Tecnológico y Mejoras de Base.
## Estilo procedimental puro: funciones estáticas y diccionarios planos.

const TECH_CATALOG: Dictionary = {
	"laser_optics": {
		"id": "laser_optics",
		"name": "Óptica Láser de Precisión",
		"cost": 80.0,
		"icon": "🔭",
		"description": "Incrementa el rango de ataque de todas las torretas en +1 salto geodésico.",
	},
	"rapid_fire": {
		"id": "rapid_fire",
		"name": "Sobrecarga de Condensadores",
		"cost": 75.0,
		"icon": "⚡",
		"description": "Reduce el tiempo de recarga de las torretas en un 30% (mayor cadencia).",
	},
	"composite_armor": {
		"id": "composite_armor",
		"name": "Blindaje de Nanocompuesto",
		"cost": 60.0,
		"icon": "🛡️",
		"description": "Aumenta la integridad estructural máxima de muros y edificios en +40%.",
	},
	"quantum_harvesters": {
		"id": "quantum_harvesters",
		"name": "Extracción Cuántica",
		"cost": 90.0,
		"icon": "💎",
		"description": "Aumenta la producción de energía de todos los extractores en +50%.",
	},
	"military_training": {
		"id": "military_training",
		"name": "Doctrina Militar Avanzada",
		"cost": 100.0,
		"icon": "⚔️",
		"description": "Las tropas de asalto marchan 25% más rápido y causan 30% más de daño.",
	},
}

static func get_tech_catalog() -> Dictionary:
	return TECH_CATALOG.duplicate(true)

static func can_research_tech(tech_id: String, faction_data: Dictionary) -> Array:
	if not TECH_CATALOG.has(tech_id):
		return [false, "La tecnología '%s' no existe en el catálogo." % tech_id]

	var researched: Array = faction_data.get("researched_techs", [])
	if researched.has(tech_id):
		return [false, "Esta tecnología ya ha sido investigada."]

	var cost: float = float(TECH_CATALOG[tech_id]["cost"])
	var current_energy: float = float(faction_data.get("energy", 0.0))
	if current_energy < cost:
		return [false, "Energía insuficiente (%.0f E, requiere %.0f E)." % [current_energy, cost]]

	return [true, "Listo para investigar."]

static func research_tech(tech_id: String, faction_data: Dictionary, world_nodes: Dictionary = {}) -> Array:
	var can_r = can_research_tech(tech_id, faction_data)
	if not can_r[0]:
		return [false, faction_data, 0.0, can_r[1]]

	var tech_info = TECH_CATALOG[tech_id]
	var cost: float = float(tech_info["cost"])

	var updated_fdata = faction_data.duplicate(true)
	updated_fdata["energy"] = float(updated_fdata.get("energy", 0.0)) - cost

	var researched: Array = updated_fdata.get("researched_techs", []).duplicate()
	researched.append(tech_id)
	updated_fdata["researched_techs"] = researched

	if not world_nodes.is_empty():
		var fid: int = updated_fdata.get("id", 1)
		for nid in world_nodes.keys():
			var bld = world_nodes[nid].get("building")
			if bld != null and bld.get("hp", 0.0) > 0.0 and bld.get("faction_id", 1) == fid:
				apply_tech_to_building(bld, [tech_id])

	var msg: String = "¡Tecnología '%s' investigada con éxito (-%.0f E)!" % [tech_info["name"], cost]
	return [true, updated_fdata, cost, msg]

static func apply_tech_to_building(building: Dictionary, researched_techs: Array) -> Dictionary:
	var btype: String = building.get("type", "")

	if researched_techs.has("laser_optics") and btype == "turret":
		building["attack_range_hops"] = building.get("attack_range_hops", 2) + 1

	if researched_techs.has("rapid_fire") and btype == "turret":
		building["cooldown"] = building.get("cooldown", 1.0) * 0.70

	if researched_techs.has("composite_armor") and (btype in ["wall", "base", "harvester", "turret"]):
		var current_max: float = float(building.get("max_hp", 100.0))
		var new_max: float = current_max * 1.40
		var diff: float = new_max - current_max
		building["max_hp"] = new_max
		building["hp"] = float(building.get("hp", current_max)) + diff

	return building

static func apply_tech_to_squad(squad: Array, researched_techs: Array) -> Array:
	if researched_techs.has("military_training"):
		for unit in squad:
			unit["speed"] = float(unit.get("speed", 0.5)) * 1.25
			unit["damage"] = float(unit.get("damage", 10.0)) * 1.30
	return squad

static func get_tech_economic_multiplier(researched_techs: Array) -> float:
	var mult: float = 1.0
	if researched_techs.has("quantum_harvesters"):
		mult += 0.50
	return mult
