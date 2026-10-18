class_name EconomyLogic
extends RefCounted
## Módulo de economía y recursos del juego.
## Estilo procedimental puro: funciones estáticas y datos planos.

const BUILDING_CATALOG: Dictionary = {
	"harvester": {
		"cost": 50.0,
		"hp": 100.0,
		"max_hp": 100.0,
		"influence_hops": 2,
		"rate_per_node": 0.8,
	},
	"turret": {
		"cost": 75.0,
		"hp": 400.0,
		"max_hp": 400.0,
		"influence_hops": 2,
		"attack_range_hops": 3,
		"damage": 35.0,
		"cooldown": 0.8,
	},
	"wall": {
		"cost": 25.0,
		"hp": 350.0,
		"max_hp": 350.0,
		"influence_hops": 0,
	},
	"purifier": {
		"cost": 120.0,
		"hp": 200.0,
		"max_hp": 200.0,
		"influence_hops": 2,
		"purify_range_hops": 4,
		"purify_rate": 15.0,
	},
	"base": {
		"cost": 300.0,
		"hp": 1500.0,
		"max_hp": 1500.0,
		"influence_hops": 2,
		"attack_range_hops": 1,
		"damage": 40.0,
		"cooldown": 0.8,
	},
}

static func create_initial_economy(starting_energy: float = 100.0, base_income: float = 5.0) -> Dictionary:
	return {
		"energy": starting_energy,
		"base_income_rate": base_income,
	}

static func calculate_tick_income(economy_state: Dictionary, world_state: Dictionary, icosphere: Dictionary, delta_seconds: float) -> float:
	if delta_seconds <= 0.0:
		return 0.0

	var total_income: float = 0.0

	# 1. Ingreso de la Base
	var base_id: int = world_state["base_node_id"]
	var base_node = world_state["nodes"].get(base_id)
	if base_node != null and base_node.get("building") != null and base_node["building"].get("hp", 0.0) > 0.0:
		total_income += economy_state.get("base_income_rate", 5.0) * delta_seconds

	# 2. Ingreso de los Extractores (Harvesters)
	for nid in world_state["nodes"].keys():
		var ndata = world_state["nodes"][nid]
		var building = ndata.get("building")
		if building != null and building.get("type") == "harvester" and building.get("hp", 0.0) > 0.0:
			var hops: int = building.get("influence_hops", 1)
			var controlled = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], nid, hops)
			var valid_player_nodes: int = 0
			for cid in controlled:
				var c_str = str(world_state["nodes"][cid]["controller"])
				if c_str == "player" or c_str == "1":
					valid_player_nodes += 1
			var rate: float = building.get("rate_per_node", 1.5)
			total_income += valid_player_nodes * rate * delta_seconds

	return total_income

static func apply_income(economy_state: Dictionary, income_amount: float) -> Dictionary:
	var new_econ = economy_state.duplicate()
	new_econ["energy"] = new_econ.get("energy", 0.0) + maxf(0.0, income_amount)
	return new_econ

static func can_afford(economy_state: Dictionary, building_type: String) -> Array:
	if not BUILDING_CATALOG.has(building_type):
		return [false, 0.0]

	var cost: float = BUILDING_CATALOG[building_type]["cost"]
	return [economy_state.get("energy", 0.0) >= cost, cost]

static func purchase_building(economy_state: Dictionary, building_type: String) -> Array:
	var check = can_afford(economy_state, building_type)
	if not check[0]:
		return [false, economy_state, null]

	var cost: float = check[1]
	var new_econ = economy_state.duplicate()
	new_econ["energy"] = new_econ["energy"] - cost

	var template = BUILDING_CATALOG[building_type].duplicate(true)
	template["type"] = building_type

	return [true, new_econ, template]
