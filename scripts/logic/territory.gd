class_name TerritoryLogic
extends RefCounted
## Módulo de cálculo de territorio, zonas de influencia y corrupción.
## Estilo procedimental puro: funciones estáticas y diccionarios planos.

static func initialize_world_state(icosphere: Dictionary, base_node_id: int, crater_node_ids: Array) -> Dictionary:
	var nodes_state: Dictionary = {}
	for node_id in icosphere["nodes"].keys():
		nodes_state[node_id] = {
			"controller": "neutral",
			"building": null,
			"is_crater": crater_node_ids.has(node_id),
			"is_base": node_id == base_node_id,
		}

	var world: Dictionary = {
		"nodes": nodes_state,
		"base_node_id": base_node_id,
		"crater_node_ids": crater_node_ids.duplicate(),
		"craters": {},
		"game_status": "in_progress",
	}

	for cid in crater_node_ids:
		world["craters"][cid] = {"hp": 100.0, "max_hp": 100.0, "is_sealed": false}

	world["nodes"][base_node_id]["building"] = {
		"type": "base",
		"hp": 1500.0,
		"max_hp": 1500.0,
		"influence_hops": 3,
	}

	return update_territory(world, icosphere)

static func update_territory(world_state: Dictionary, icosphere: Dictionary) -> Dictionary:
	var new_state: Dictionary = {
		"nodes": {},
		"base_node_id": world_state["base_node_id"],
		"crater_node_ids": world_state.get("crater_node_ids", []).duplicate(),
		"craters": world_state.get("craters", {}).duplicate(true),
		"game_status": world_state["game_status"],
	}

	for nid in world_state["nodes"].keys():
		var src = world_state["nodes"][nid]
		new_state["nodes"][nid] = {
			"controller": src["controller"],
			"building": src["building"].duplicate(true) if src["building"] != null else null,
			"is_crater": src["is_crater"],
			"is_base": src["is_base"],
		}

	# 1. Nodos corruptos por cráteres (2 saltos en 642 nodos)
	var corrupt_nodes: Dictionary = {}
	for crater_id in new_state["crater_node_ids"]:
		if icosphere["nodes"].has(crater_id):
			var in_range = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], crater_id, 2)
			for cid in in_range:
				corrupt_nodes[cid] = true

	# 2. Nodos alcanzados por edificios del jugador
	var player_nodes: Dictionary = {}
	for nid in new_state["nodes"].keys():
		var building = new_state["nodes"][nid].get("building")
		if building != null and building.get("hp", 0.0) > 0.0:
			var b_fid = building.get("faction_id", 1)
			if str(b_fid) == "1" or str(b_fid) == "player":
				var hops: int = building.get("influence_hops", 0)
				if hops > 0:
					var controlled = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], nid, hops)
					for pid in controlled:
						player_nodes[pid] = true

	# 3. Asignar controladores
	for nid in new_state["nodes"].keys():
		if corrupt_nodes.has(nid):
			new_state["nodes"][nid]["controller"] = "corrupt"
		elif player_nodes.has(nid):
			new_state["nodes"][nid]["controller"] = "player"
		else:
			new_state["nodes"][nid]["controller"] = "neutral"

	new_state["game_status"] = evaluate_victory_defeat(new_state, icosphere)
	return new_state

static func can_build_on_node(world_state: Dictionary, node_id: int, _building_type: String = "turret") -> Array:
	if not world_state["nodes"].has(node_id):
		return [false, "El nodo no existe"]

	var node = world_state["nodes"][node_id]

	if node["is_crater"] or str(node["controller"]) == "corrupt":
		return [false, "Zona corrupta o cráter: no se puede construir"]

	var ctrl_str = str(node["controller"])
	if ctrl_str != "player" and ctrl_str != "1":
		return [false, "El nodo no está dentro del territorio dominado"]

	if node["building"] != null:
		return [false, "Ya existe una instalación en este nodo"]

	return [true, ""]

static func place_building(world_state: Dictionary, icosphere: Dictionary, node_id: int, building_data: Dictionary) -> Array:
	var check = can_build_on_node(world_state, node_id, building_data.get("type", "turret"))
	if not check[0]:
		return [false, check[1]]

	var new_world: Dictionary = update_territory(world_state, icosphere)
	new_world["nodes"][node_id]["building"] = building_data.duplicate(true)
	return [true, update_territory(new_world, icosphere)]

static func remove_building(world_state: Dictionary, icosphere: Dictionary, node_id: int) -> Dictionary:
	if not world_state["nodes"].has(node_id):
		return world_state

	var new_world: Dictionary = update_territory(world_state, icosphere)
	new_world["nodes"][node_id]["building"] = null
	return update_territory(new_world, icosphere)

static func evaluate_victory_defeat(world_state: Dictionary, _icosphere: Dictionary) -> String:
	var base_id: int = world_state["base_node_id"]
	var base_node = world_state["nodes"].get(base_id)

	if base_node == null or base_node.get("building") == null or base_node["building"].get("hp", 0.0) <= 0.0:
		return "defeat"

	# Victoria Ofensiva: Si todos los cráteres fueron neutralizados y sellados
	var craters_dict: Dictionary = world_state.get("craters", {})
	if world_state.get("crater_node_ids", []).is_empty() and not craters_dict.is_empty():
		return "victory"

	var non_corrupt_count: int = 0
	var player_count: int = 0

	for nid in world_state["nodes"].keys():
		var ndata = world_state["nodes"][nid]
		if not ndata["is_crater"]:
			non_corrupt_count += 1
			var c_str = str(ndata["controller"])
			if c_str == "player" or c_str == "1":
				player_count += 1

	if player_count == non_corrupt_count and non_corrupt_count > 0:
		return "victory"

	return "in_progress"
