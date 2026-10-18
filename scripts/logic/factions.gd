class_name FactionsLogic
extends RefCounted
## Gestión de Múltiples Facciones, Diplomacia y Alianzas estilo Age of Empires.
## Estilo procedimental puro: funciones estáticas y estructuras de datos planas.

static func find_distributed_base_nodes(nodes_dict: Dictionary, count: int = 2) -> Array:
	if count <= 1:
		return [0]

	var all_ids: Array = nodes_dict.keys()
	all_ids.sort()

	if count == 2:
		var base_0: int = all_ids[0]
		var base_1: int = IcosphereLogic.find_antipodal_node(nodes_dict, base_0)
		return [base_0, base_1]

	# Greedy farthest point sampling
	var chosen: Array = [all_ids[0]]
	for step in range(1, count):
		var best_node: int = -1
		var max_min_dist: float = -1.0

		for candidate in all_ids:
			if chosen.has(candidate):
				continue

			var cand_pos: Vector3 = nodes_dict[candidate]["pos"]
			var min_dist_to_chosen: float = 999999.0
			for c in chosen:
				var d: float = IcosphereLogic.get_spherical_distance(cand_pos, nodes_dict[c]["pos"])
				if d < min_dist_to_chosen:
					min_dist_to_chosen = d

			if min_dist_to_chosen > max_min_dist:
				max_min_dist = min_dist_to_chosen
				best_node = candidate

		if best_node != -1:
			chosen.append(best_node)

	return chosen


static func create_faction(faction_id: int, name: String, race_id: String, is_ai: bool, team_id: int, base_node_id: int, starting_energy: float = 100.0) -> Dictionary:
	var race_data = RacesLogic.get_race_data(race_id)
	var base_income = RacesLogic.calculate_base_passive_income(5.0, race_id)

	return {
		"id": faction_id,
		"name": name,
		"race": race_id,
		"is_ai": is_ai,
		"team": team_id,
		"base_node": base_node_id,
		"energy": starting_energy,
		"base_income_rate": base_income,
		"is_alive": true,
		"color": race_data.get("color", "#22c55e"),
	}


static func initialize_factions_game(icosphere: Dictionary, faction_configs: Array) -> Dictionary:
	var nodes: Dictionary = icosphere["nodes"]
	var num_factions: int = faction_configs.size()
	var base_nodes: Array = find_distributed_base_nodes(nodes, num_factions)

	var factions_dict: Dictionary = {}
	for i in range(num_factions):
		var cfg: Dictionary = faction_configs[i]
		var fid: int = i + 1
		var b_node: int = cfg.get("base_node", base_nodes[i])
		var f_data = create_faction(
			fid,
			cfg.get("name", "Facción #" + str(fid)),
			cfg.get("race", "solarian"),
			cfg.get("is_ai", true),
			cfg.get("team", fid),
			b_node,
			cfg.get("starting_energy", 100.0)
		)
		factions_dict[fid] = f_data

	var diplomacy_matrix: Dictionary = {}
	for f1 in factions_dict:
		diplomacy_matrix[f1] = {}
		for f2 in factions_dict:
			if f1 == f2 or factions_dict[f1]["team"] == factions_dict[f2]["team"]:
				diplomacy_matrix[f1][f2] = "ally"
			else:
				diplomacy_matrix[f1][f2] = "enemy"

	var teams_set: Dictionary = {}
	for f in factions_dict.values():
		teams_set[f["team"]] = true

	var game_mode: String = "ffa" if teams_set.size() == factions_dict.size() else "teams"

	return {
		"factions": factions_dict,
		"diplomacy_matrix": diplomacy_matrix,
		"game_mode": game_mode,
		"status": "in_progress",
		"winning_team": null,
	}


static func _get_factions_and_matrix(factions_data: Dictionary) -> Array:
	if factions_data.has("factions"):
		return [factions_data["factions"], factions_data.get("diplomacy_matrix")]
	return [factions_data, null]


static func get_diplomatic_stance(factions_data: Dictionary, from_faction_id: int, to_faction_id: int) -> String:
	if from_faction_id == to_faction_id:
		return "ally"

	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var matrix = split[1]

	if matrix != null and matrix.has(from_faction_id) and matrix[from_faction_id].has(to_faction_id):
		return matrix[from_faction_id][to_faction_id]

	if factions.has(from_faction_id) and factions.has(to_faction_id):
		return "ally" if factions[from_faction_id]["team"] == factions[to_faction_id]["team"] else "enemy"

	return "enemy"


static func set_diplomatic_stance(factions_state: Dictionary, from_faction_id: int, to_faction_id: int, new_stance: String) -> Array:
	if new_stance != "ally" and new_stance != "neutral" and new_stance != "enemy":
		return [false, factions_state, "Postura '%s' inválida (debe ser 'ally', 'neutral' o 'enemy')" % new_stance]

	if from_faction_id == to_faction_id:
		return [false, factions_state, "Una facción no puede alterar su postura hacia sí misma"]

	var split = _get_factions_and_matrix(factions_state)
	var factions: Dictionary = split[0]
	var matrix = split[1]

	if not factions.has(from_faction_id) or not factions.has(to_faction_id):
		return [false, factions_state, "Identificador de facción no encontrado"]

	if matrix == null:
		matrix = {}
		for f1 in factions:
			matrix[f1] = {}
			for f2 in factions:
				matrix[f1][f2] = "ally" if factions[f1]["team"] == factions[f2]["team"] else "enemy"
		factions_state["diplomacy_matrix"] = matrix

	if not matrix.has(from_faction_id):
		matrix[from_faction_id] = {}

	var old_stance: String = matrix[from_faction_id].get(to_faction_id, "enemy")
	matrix[from_faction_id][to_faction_id] = new_stance

	var from_name: String = factions[from_faction_id]["name"]
	var to_name: String = factions[to_faction_id]["name"]
	var msg = "%s ha cambiado su postura hacia %s de '%s' a '%s'" % [from_name, to_name, old_stance, new_stance]
	return [true, factions_state, msg]


static func are_allies(faction_a_id: int, faction_b_id: int, factions_data: Dictionary) -> bool:
	if faction_a_id == faction_b_id:
		return true

	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var matrix = split[1]

	if not factions.has(faction_a_id) or not factions.has(faction_b_id):
		return false

	if matrix != null:
		var stance_a: String = matrix.get(faction_a_id, {}).get(faction_b_id, "enemy")
		var stance_b: String = matrix.get(faction_b_id, {}).get(faction_a_id, "enemy")
		return stance_a == "ally" and stance_b == "ally"

	return factions[faction_a_id]["team"] == factions[faction_b_id]["team"]


static func are_enemies(faction_a_id: int, faction_b_id: int, factions_data: Dictionary) -> bool:
	if faction_a_id == 0 or faction_b_id == 0 or faction_a_id == faction_b_id:
		return false

	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var matrix = split[1]

	if not factions.has(faction_a_id) or not factions.has(faction_b_id):
		return false

	if matrix != null:
		var stance_a: String = matrix.get(faction_a_id, {}).get(faction_b_id, "enemy")
		var stance_b: String = matrix.get(faction_b_id, {}).get(faction_a_id, "enemy")
		return stance_a == "enemy" or stance_b == "enemy"

	return factions[faction_a_id]["team"] != factions[faction_b_id]["team"]


static func is_hostile(from_faction_id: int, to_faction_id: int, factions_data: Dictionary) -> bool:
	return get_diplomatic_stance(factions_data, from_faction_id, to_faction_id) == "enemy"


static func are_in_active_war(faction_a_id: int, faction_b_id: int, factions_data: Dictionary) -> bool:
	return are_enemies(faction_a_id, faction_b_id, factions_data)


static func send_tribute(factions_state: Dictionary, from_faction_id: int, to_faction_id: int, amount: float, fee_rate: float = 0.0) -> Array:
	if from_faction_id == to_faction_id:
		return [false, factions_state, "No es posible enviarse tributos a uno mismo"]

	if amount <= 0.0:
		return [false, factions_state, "El monto del tributo debe ser mayor a 0"]

	var split = _get_factions_and_matrix(factions_state)
	var factions: Dictionary = split[0]

	if not factions.has(from_faction_id) or not factions.has(to_faction_id):
		return [false, factions_state, "Facción remitente o destinataria no existe"]

	var sender = factions[from_faction_id]
	var receiver = factions[to_faction_id]

	if not sender.get("is_alive", true):
		return [false, factions_state, "La facción remitente '%s' ha sido eliminada" % sender["name"]]
	if not receiver.get("is_alive", true):
		return [false, factions_state, "La facción destinataria '%s' ha sido eliminada" % receiver["name"]]

	if float(sender["energy"]) < amount:
		return [false, factions_state, "Energía insuficiente (%.1f E disponible, se requieren %.1f E)" % [float(sender["energy"]), amount]]

	sender["energy"] = float(sender["energy"]) - amount
	var fee = clampf(fee_rate, 0.0, 1.0)
	var net_received: float = amount * (1.0 - fee)
	receiver["energy"] = float(receiver["energy"]) + net_received

	var msg: String = "Tributo exitoso: %s envió %.1f E a %s (Neto recibido: %.1f E)" % [sender["name"], amount, receiver["name"], net_received]
	return [true, factions_state, msg]



static func get_enemy_factions(faction_id: int, factions_data: Dictionary) -> Array:
	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var enemies: Array = []
	for fid in factions:
		var fdata = factions[fid]
		if fdata is Dictionary and fdata.get("is_alive", true) and are_enemies(faction_id, fid, factions_data):
			enemies.append(fid)
	return enemies


static func get_allied_factions(faction_id: int, factions_data: Dictionary, include_self: bool = true) -> Array:
	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var allies: Array = []
	for fid in factions:
		var fdata = factions[fid]
		if fdata is Dictionary and fdata.get("is_alive", true) and are_allies(faction_id, fid, factions_data):
			if include_self or fid != faction_id:
				allies.append(fid)
	return allies


static func calculate_multi_faction_territory(icosphere: Dictionary, world_nodes: Dictionary, factions_dict: Dictionary) -> Dictionary:
	var nodes: Dictionary = icosphere["nodes"]
	var updated_nodes: Dictionary = {}
	for nid in world_nodes:
		updated_nodes[nid] = world_nodes[nid].duplicate(true)

	var faction_reach: Dictionary = {}
	for fid in factions_dict:
		if factions_dict[fid]["is_alive"]:
			faction_reach[fid] = {}

	for nid in updated_nodes:
		var ndata = updated_nodes[nid]
		var bld = ndata.get("building")
		if bld == null or bld.get("hp", 0.0) <= 0.0:
			continue

		var b_fid: int = bld.get("faction_id", 0)
		if not faction_reach.has(b_fid):
			continue

		var hops: int = bld.get("influence_hops", 1)
		if bld.get("type") == "base":
			var race_id: String = factions_dict[b_fid].get("race", "terran_protocore")
			hops = RacesLogic.calculate_initial_influence_hops(race_id)

		var in_range: Array = IcosphereLogic.get_nodes_within_hops(nodes, nid, hops)
		for target_nid in in_range:
			var curr_hops: int = faction_reach[b_fid].get(target_nid, 999)
			if hops < curr_hops:
				faction_reach[b_fid][target_nid] = hops

	for nid in updated_nodes:
		var ndata = updated_nodes[nid]
		var claiming: Array = []
		for fid in faction_reach:
			if faction_reach[fid].has(nid):
				claiming.append(fid)

		if claiming.is_empty():
			ndata["controller"] = 0
		elif claiming.size() == 1:
			ndata["controller"] = claiming[0]
		else:
			var first_fid: int = claiming[0]
			var all_friendly: bool = true
			for other_fid in claiming:
				if not are_allies(first_fid, other_fid, factions_dict):
					all_friendly = false
					break

			if all_friendly:
				ndata["controller"] = first_fid
			else:
				var b_owner: int = ndata.get("building", {}).get("faction_id", 0) if ndata.get("building") != null else 0
				if b_owner != 0:
					ndata["controller"] = b_owner
				else:
					ndata["controller"] = 0

	return updated_nodes


static func update_multi_faction_economy(factions_dict: Dictionary, world_nodes: Dictionary, icosphere: Dictionary, delta_seconds: float) -> Dictionary:
	if delta_seconds <= 0.0:
		return factions_dict

	var updated: Dictionary = {}
	for fid in factions_dict:
		updated[fid] = factions_dict[fid].duplicate(true)

	for fid in updated:
		var fdata = updated[fid]
		if not fdata["is_alive"]:
			continue

		var income_this_tick: float = 0.0

		var base_id: int = fdata["base_node"]
		var base_node = world_nodes.get(base_id)
		if base_node != null and base_node.get("building") != null and base_node["building"].get("hp", 0.0) > 0.0:
			income_this_tick += float(fdata.get("base_income_rate", 5.0))

			var allies: Array = get_allied_factions(fid, updated, false)
			for ally_id in allies:
				var ally_race = RacesLogic.get_race_data(updated[ally_id]["race"])
				var t_bonus: Dictionary = ally_race.get("team_bonus", {})
				if t_bonus.get("type") == "passive_income_bonus":
					income_this_tick += float(fdata.get("base_income_rate", 5.0)) * float(t_bonus.get("value", 0.10))

		for nid in world_nodes:
			var ndata = world_nodes[nid]
			var bld = ndata.get("building")
			if bld != null and bld.get("faction_id") == fid and bld.get("type") == "harvester" and bld.get("hp", 0.0) > 0.0:
				var inf_hops: int = bld.get("influence_hops", 1)
				var surrounding: Array = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], nid, inf_hops)
				var controlled_count: int = 0
				for s_id in surrounding:
					if world_nodes.get(s_id, {}).get("controller") == fid:
						controlled_count += 1
				var rate_per_node: float = float(bld.get("rate_per_node", 1.5))
				var harv_income: float = RacesLogic.calculate_harvester_income(rate_per_node, controlled_count, fdata["race"])
				harv_income *= TechTreeLogic.get_tech_economic_multiplier(fdata.get("researched_techs", []))
				income_this_tick += harv_income

		fdata["energy"] += income_this_tick * delta_seconds

	return updated


static func evaluate_factions_victory_defeat(factions_data: Dictionary, world_nodes: Dictionary, player_faction_id: int = 1) -> Array:
	var split = _get_factions_and_matrix(factions_data)
	var factions: Dictionary = split[0]
	var matrix = split[1]

	var updated_factions: Dictionary = {}
	for fid in factions:
		updated_factions[fid] = factions[fid].duplicate(true)

	for fid in updated_factions:
		var fdata = updated_factions[fid]
		var base_id: int = fdata["base_node"]
		var base_node = world_nodes.get(base_id)
		if base_node == null or base_node.get("building") == null or base_node["building"].get("hp", 0.0) <= 0.0:
			if fdata.get("is_alive", true):
				fdata["is_alive"] = false
				for nid in world_nodes:
					var b = world_nodes[nid].get("building")
					if b != null and b.get("faction_id") == fid:
						world_nodes[nid]["building"] = null

	var player_alive: bool = updated_factions.get(player_faction_id, {}).get("is_alive", false)
	var player_team: int = updated_factions.get(player_faction_id, {}).get("team", -1)

	if matrix != null:
		if not player_alive:
			return ["defeat", null, updated_factions]

		var has_living_enemies: bool = false
		for fid in updated_factions:
			if fid != player_faction_id and updated_factions[fid]["is_alive"]:
				if are_enemies(player_faction_id, fid, factions_data):
					has_living_enemies = true
					break

		if not has_living_enemies:
			return ["victory", player_team, updated_factions]

		return ["in_progress", null, updated_factions]

	var player_team_alive: bool = false
	for fdata in updated_factions.values():
		if fdata["team"] == player_team and fdata["is_alive"]:
			player_team_alive = true
			break

	if not player_team_alive:
		return ["defeat", null, updated_factions]

	var enemy_teams_alive: Dictionary = {}
	for fdata in updated_factions.values():
		if fdata["is_alive"] and fdata["team"] != player_team:
			enemy_teams_alive[fdata["team"]] = true

	if enemy_teams_alive.is_empty():
		return ["victory", player_team, updated_factions]

	return ["in_progress", null, updated_factions]
