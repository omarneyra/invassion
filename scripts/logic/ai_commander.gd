class_name AICommanderLogic
extends RefCounted
## Comandante de Inteligencia Artificial Simétrica estilo Age of Empires.
## Estilo procedimental puro: funciones estáticas y datos planos en diccionarios y arrays.

static func analyze_faction_territory(faction_id: int, world_nodes: Dictionary, icosphere: Dictionary, factions_data: Dictionary) -> Dictionary:
	var nodes_graph: Dictionary = icosphere["nodes"]
	var controlled_nodes: Array = []
	for nid in world_nodes:
		if world_nodes[nid].get("controller") == faction_id:
			controlled_nodes.append(nid)

	var interior_empty: Array = []
	var frontier_empty: Array = []
	var enemy_adjacent_empty: Array = []

	var harvester_count: int = 0
	var turret_count: int = 0
	var wall_count: int = 0

	for nid in controlled_nodes:
		var ndata = world_nodes[nid]
		var bld = ndata.get("building")

		if bld != null:
			var btype: String = bld.get("type", "")
			if btype == "harvester":
				harvester_count += 1
			elif btype == "turret":
				turret_count += 1
			elif btype == "wall":
				wall_count += 1
			continue

		var neighbors: Array = nodes_graph.get(nid, {}).get("neighbors", [])
		var has_enemy_neighbor: bool = false
		var has_neutral_neighbor: bool = false

		for n_id in neighbors:
			var n_ctrl: int = world_nodes.get(n_id, {}).get("controller", 0)
			if n_ctrl == 0:
				has_neutral_neighbor = true
			elif n_ctrl != faction_id:
				if not FactionsLogic.are_allies(faction_id, n_ctrl, factions_data):
					has_enemy_neighbor = true

		if has_enemy_neighbor:
			enemy_adjacent_empty.append(nid)
		elif has_neutral_neighbor:
			frontier_empty.append(nid)
		else:
			interior_empty.append(nid)

	return {
		"controlled_nodes": controlled_nodes,
		"controlled_count": controlled_nodes.size(),
		"interior_empty": interior_empty,
		"frontier_empty": frontier_empty,
		"enemy_adjacent_empty": enemy_adjacent_empty,
		"harvester_count": harvester_count,
		"turret_count": turret_count,
		"wall_count": wall_count,
	}


static func find_closest_enemy_base(faction_id: int, world_nodes: Dictionary, factions_data: Dictionary, icosphere: Dictionary) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	if not factions.has(faction_id):
		return [null, null, []]

	var my_base: int = factions[faction_id].get("base_node", 0)
	var enemy_ids: Array = FactionsLogic.get_enemy_factions(faction_id, factions_data)

	var best_enemy_fid = null
	var best_target_base = null
	var shortest_path_found: Array = []
	var min_hops: int = 999999

	for e_fid in enemy_ids:
		var e_base = factions[e_fid].get("base_node")
		if e_base == null or not icosphere["nodes"].has(e_base):
			continue

		var base_node_data = world_nodes.get(e_base, {})
		var base_bld = base_node_data.get("building")
		if base_bld == null or base_bld.get("hp", 0.0) <= 0.0:
			continue

		var path: Array = IcosphereLogic.find_shortest_path(icosphere["nodes"], my_base, e_base)
		if not path.is_empty() and path.size() < min_hops:
			min_hops = path.size()
			best_enemy_fid = e_fid
			best_target_base = e_base
			shortest_path_found = path

	return [best_enemy_fid, best_target_base, shortest_path_found]


static func decide_ai_construction(faction_id: int, factions_data: Dictionary, world_nodes: Dictionary, icosphere: Dictionary) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var fdata = factions.get(faction_id)
	if fdata == null or not fdata.get("is_alive", true):
		return [false, null, null, null, 0.0]

	var energy: float = float(fdata.get("energy", 0.0))
	var race_id: String = fdata.get("race", "solarian")

	var analysis: Dictionary = analyze_faction_territory(faction_id, world_nodes, icosphere, factions_data)

	var harv_base_cost: float = EconomyLogic.BUILDING_CATALOG["harvester"]["cost"]
	var harv_cost: float = RacesLogic.calculate_building_cost(harv_base_cost, "harvester", race_id)

	if analysis["harvester_count"] < 2 and not analysis["interior_empty"].is_empty() and energy >= harv_cost:
		var target_node: int = analysis["interior_empty"][0]
		var template: Dictionary = EconomyLogic.BUILDING_CATALOG["harvester"].duplicate(true)
		template["faction_id"] = faction_id
		template = RacesLogic.apply_building_combat_stats(template, race_id)
		return [true, target_node, "harvester", template, harv_cost]

	var turret_base_cost: float = EconomyLogic.BUILDING_CATALOG["turret"]["cost"]
	var turret_cost: float = RacesLogic.calculate_building_cost(turret_base_cost, "turret", race_id)
	var wall_base_cost: float = EconomyLogic.BUILDING_CATALOG["wall"]["cost"]
	var wall_cost: float = RacesLogic.calculate_building_cost(wall_base_cost, "wall", race_id)

	if not analysis["enemy_adjacent_empty"].is_empty():
		var target_node: int = analysis["enemy_adjacent_empty"][0]
		if energy >= turret_cost and analysis["turret_count"] <= analysis["wall_count"]:
			var template: Dictionary = EconomyLogic.BUILDING_CATALOG["turret"].duplicate(true)
			template["faction_id"] = faction_id
			template = RacesLogic.apply_building_combat_stats(template, race_id)
			return [true, target_node, "turret", template, turret_cost]
		elif energy >= wall_cost:
			var template: Dictionary = EconomyLogic.BUILDING_CATALOG["wall"].duplicate(true)
			template["faction_id"] = faction_id
			template = RacesLogic.apply_building_combat_stats(template, race_id)
			return [true, target_node, "wall", template, wall_cost]

	if not analysis["frontier_empty"].is_empty() and energy >= (turret_cost + 40.0):
		var target_node: int = analysis["frontier_empty"][0]
		var template: Dictionary = EconomyLogic.BUILDING_CATALOG["turret"].duplicate(true)
		template["faction_id"] = faction_id
		template = RacesLogic.apply_building_combat_stats(template, race_id)
		return [true, target_node, "turret", template, turret_cost]

	return [false, null, null, null, 0.0]


static func launch_faction_assault(faction_id: int, factions_data: Dictionary, world_nodes: Dictionary, icosphere: Dictionary, assault_cost: float = 60.0) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var fdata = factions.get(faction_id)
	if fdata == null or not fdata.get("is_alive", true):
		return [false, [], 0.0, null, "La facción no está activa"]

	var energy: float = float(fdata.get("energy", 0.0))
	if energy < assault_cost:
		return [false, [], 0.0, null, "Energía insuficiente (%.0f E, se requieren %.0f E)" % [energy, assault_cost]]

	var closest = find_closest_enemy_base(faction_id, world_nodes, factions_data, icosphere)
	var enemy_fid = closest[0]
	var enemy_base = closest[1]
	var path: Array = closest[2]

	if enemy_fid == null or path.is_empty() or path.size() <= 1:
		return [false, [], 0.0, null, "No se encontró base enemiga alcanzable"]

	var race_data: Dictionary = RacesLogic.get_race_data(fdata.get("race", "solarian"))
	var unique: Dictionary = race_data.get("unique_unit", {})

	var squad: Array = []
	var base_node = fdata.get("base_node", 0)

	# Unidad líder de raza
	squad.append({
		"id": "%d_%d_lead_%d" % [faction_id, base_node, int(energy)],
		"faction_id": faction_id,
		"target_faction": enemy_fid,
		"archetype": unique.get("type", "vanguard"),
		"hp": float(unique.get("hp", 100.0)),
		"max_hp": float(unique.get("max_hp", 100.0)),
		"speed": float(unique.get("speed", 0.5)),
		"damage": float(unique.get("damage", 20.0)),
		"progress": 0.0,
		"current_node": path[0],
		"path": path.duplicate(),
		"path_index": 0,
		"attack_cooldown": 1.0,
		"attack_timer": 0.0,
		"state": "marching",
		"color": race_data.get("color", "#22c55e"),
	})

	# Escoltas
	for idx in range(1, 3):
		squad.append({
			"id": "%d_%d_escort_%d_%d" % [faction_id, base_node, idx, int(energy)],
			"faction_id": faction_id,
			"target_faction": enemy_fid,
			"archetype": "scout",
			"hp": 40.0,
			"max_hp": 40.0,
			"speed": 0.8,
			"damage": 10.0,
			"progress": 0.0,
			"current_node": path[0],
			"path": path.duplicate(),
			"path_index": 0,
			"attack_cooldown": 1.0,
			"attack_timer": 0.0,
			"state": "marching",
			"spawn_delay": float(idx * 0.8),
			"color": race_data.get("color", "#22c55e"),
		})

	squad = TechTreeLogic.apply_tech_to_squad(squad, fdata.get("researched_techs", []))

	fdata["energy"] = energy - assault_cost
	var msg = "¡Escuadrón militar de %s desplegado (%d unidades) hacia la base enemiga!" % [fdata.get("name", "Facción"), squad.size()]
	return [true, squad, assault_cost, enemy_base, msg]


static func decide_ai_assault(faction_id: int, factions_data: Dictionary, world_nodes: Dictionary, icosphere: Dictionary, assault_threshold: float = 110.0) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var fdata = factions.get(faction_id)
	if fdata == null or not fdata.get("is_alive", true):
		return [false, [], 0.0, null]

	var energy: float = float(fdata.get("energy", 0.0))

	# Umbral de emergencia: si la base está dañada, movilizar defensa desde 65 E
	var effective_threshold: float = assault_threshold
	var my_base: int = fdata.get("base_node", 0)
	var base_bld = world_nodes.get(my_base, {}).get("building")
	if base_bld != null and float(base_bld.get("hp", 500.0)) < float(base_bld.get("max_hp", 500.0)):
		effective_threshold = minf(assault_threshold, 65.0)

	if energy < effective_threshold:
		return [false, [], 0.0, null]

	var res = launch_faction_assault(faction_id, factions_data, world_nodes, icosphere, 65.0)
	if res[0]:
		fdata["energy"] = float(fdata["energy"]) + float(res[2])
		return [true, res[1], res[2], res[3]]
	return [false, [], 0.0, null]


static func process_ai_diplomacy_reaction(faction_id: int, factions_state: Dictionary, event: Dictionary) -> Array:
	var etype: String = event.get("type", "")

	if etype == "tribute_received" and event.get("to_faction") == faction_id:
		var from_fid: int = event.get("from_faction", 0)
		var amount: float = float(event.get("amount", 0.0))
		var curr_stance: String = FactionsLogic.get_diplomatic_stance(factions_state, faction_id, from_fid)

		if amount >= 100.0 and curr_stance != "ally":
			FactionsLogic.set_diplomatic_stance(factions_state, faction_id, from_fid, "ally")
			var msg = "La Facción #%d ha aceptado un pacto de alianza tras recibir %.1f E de tributo." % [faction_id, amount]
			return [true, factions_state, msg]
		elif amount >= 50.0 and curr_stance == "enemy":
			FactionsLogic.set_diplomatic_stance(factions_state, faction_id, from_fid, "neutral")
			var msg = "La Facción #%d ha concedido una tregua neutral tras recibir %.1f E de tributo." % [faction_id, amount]
			return [true, factions_state, msg]

	elif etype == "building_damaged" and event.get("target_faction") == faction_id:
		var attacker_fid: int = event.get("attacker_faction", 0)
		if attacker_fid != 0 and attacker_fid != faction_id:
			var curr_stance: String = FactionsLogic.get_diplomatic_stance(factions_state, faction_id, attacker_fid)
			if curr_stance == "ally" or curr_stance == "neutral":
				FactionsLogic.set_diplomatic_stance(factions_state, faction_id, attacker_fid, "enemy")
				var msg = "¡Alerta! La Facción #%d ha declarado la guerra a la Facción #%d en represalia a un ataque sorpresa." % [faction_id, attacker_fid]
				return [true, factions_state, msg]

	return [false, factions_state, ""]


static func run_ai_tick(faction_id: int, factions_state: Dictionary, world_nodes: Dictionary, icosphere: Dictionary, _delta_time: float, events: Array = []) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_state)
	var factions: Dictionary = split[0]
	var fdata = factions.get(faction_id)
	if fdata == null or not fdata.get("is_alive", true) or not fdata.get("is_ai", true):
		return [factions_state, world_nodes, [], []]

	var actions_taken: Array = []
	var new_spawns: Array = []

	if not events.is_empty():
		for ev in events:
			var reaction = process_ai_diplomacy_reaction(faction_id, factions_state, ev)
			if reaction[0]:
				actions_taken.append({"type": "diplomacy_change", "message": reaction[2]})

	var build_decision = decide_ai_construction(faction_id, factions_state, world_nodes, icosphere)
	if build_decision[0] and build_decision[1] != null:
		var b_node: int = build_decision[1]
		var b_type: String = build_decision[2]
		var b_template: Dictionary = build_decision[3]
		var b_cost: float = build_decision[4]

		fdata["energy"] = float(fdata["energy"]) - b_cost
		world_nodes[b_node]["building"] = b_template
		actions_taken.append({
			"type": "building_constructed",
			"node_id": b_node,
			"building_type": b_type,
			"cost": b_cost,
		})

	var assault_decision = decide_ai_assault(faction_id, factions_state, world_nodes, icosphere)
	if assault_decision[0]:
		var squad: Array = assault_decision[1]
		var assault_cost: float = assault_decision[2]
		var target_base = assault_decision[3]

		fdata["energy"] = float(fdata["energy"]) - assault_cost
		new_spawns.append_array(squad)
		actions_taken.append({
			"type": "military_assault_launched",
			"target_base": target_base,
			"units_count": squad.size(),
			"cost": assault_cost,
		})

	var tech_res = decide_ai_tech_research(faction_id, factions_state, world_nodes)
	if tech_res[0]:
		actions_taken.append({
			"type": "tech_researched",
			"tech_id": tech_res[1],
			"cost": tech_res[2],
			"message": tech_res[3],
		})

	return [factions_state, world_nodes, new_spawns, actions_taken]


static func decide_ai_tech_research(faction_id: int, factions_data: Dictionary, world_nodes: Dictionary, energy_threshold: float = 110.0) -> Array:
	var split = FactionsLogic._get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var fdata = factions.get(faction_id)
	if fdata == null or not fdata.get("is_alive", true):
		return [false, null, 0.0, ""]

	if float(fdata.get("energy", 0.0)) < energy_threshold:
		return [false, null, 0.0, ""]

	var researched: Array = fdata.get("researched_techs", [])
	for tid in ["composite_armor", "laser_optics", "rapid_fire", "quantum_harvesters", "military_training"]:
		if not researched.has(tid):
			var can_r = TechTreeLogic.can_research_tech(tid, fdata)
			if can_r[0]:
				var res = TechTreeLogic.research_tech(tid, fdata, world_nodes)
				if res[0]:
					factions[faction_id] = res[1]
					return [true, tid, res[2], res[3]]

	return [false, null, 0.0, ""]
