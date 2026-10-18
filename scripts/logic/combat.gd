class_name CombatLogic
extends RefCounted
## Módulo de combate, invasión geodésica y simulación de daño.
## Estilo procedimental puro: funciones estáticas y estructuras de datos planas.

const INVADER_ARCHETYPES: Dictionary = {
	"crawler": {
		"type": "crawler",
		"hp": 70.0,
		"max_hp": 70.0,
		"speed": 0.45,
		"damage": 15.0,
		"scale": 1.0,
		"color": "red",
	},
	"scout": {
		"type": "scout",
		"hp": 35.0,
		"max_hp": 35.0,
		"speed": 0.85,
		"damage": 8.0,
		"scale": 0.75,
		"color": "orange",
	},
	"brute": {
		"type": "brute",
		"hp": 220.0,
		"max_hp": 220.0,
		"speed": 0.22,
		"damage": 35.0,
		"scale": 1.4,
		"color": "purple",
	},
}

static func generate_invasion_lane(icosphere: Dictionary, crater_id: int, base_id: int) -> Array:
	return IcosphereLogic.find_shortest_path(icosphere["nodes"], crater_id, base_id)

static func generate_multiple_invasion_lanes(icosphere: Dictionary, crater_id: int, base_id: int, count: int = 2) -> Array:
	var primary_lane: Array = generate_invasion_lane(icosphere, crater_id, base_id)
	if count <= 1 or primary_lane.is_empty() or primary_lane.size() <= 3:
		return [primary_lane]

	var lanes: Array = [primary_lane]
	var nodes: Dictionary = icosphere["nodes"]
	var crater_pos: Vector3 = nodes[crater_id]["pos"]
	var prim_step: int = primary_lane[1]
	var prim_pos: Vector3 = nodes[prim_step]["pos"]

	var v_prim: Vector3 = prim_pos - crater_pos

	var best_flank_neighbor: int = -1
	var min_dot: float = 1e9

	for neighbor_id in nodes[crater_id]["neighbors"]:
		if neighbor_id == prim_step:
			continue
		var npos: Vector3 = nodes[neighbor_id]["pos"]
		var v_cand: Vector3 = npos - crater_pos
		var dot: float = v_cand.dot(v_prim)
		if dot < min_dot:
			min_dot = dot
			best_flank_neighbor = neighbor_id

	if best_flank_neighbor != -1:
		var cutoff: int = maxi(2, primary_lane.size() - 2)
		var excluded: Array = primary_lane.slice(1, cutoff)

		var flank_path: Array = IcosphereLogic.find_shortest_path(nodes, best_flank_neighbor, base_id, excluded)
		if not flank_path.is_empty():
			var lane_2: Array = [crater_id]
			lane_2.append_array(flank_path)
			lanes.append(lane_2)
		else:
			var alt_path: Array = IcosphereLogic.find_shortest_path(nodes, best_flank_neighbor, base_id)
			if not alt_path.is_empty():
				var lane_2_alt: Array = [crater_id]
				lane_2_alt.append_array(alt_path)
				lanes.append(lane_2_alt)

	return lanes

static func create_wave_composition(wave_number: int) -> Array:
	var w: int = maxi(1, wave_number)
	var composition: Array = []

	if w == 1:
		composition = ["crawler", "crawler"]
	elif w == 2:
		composition = ["crawler", "scout", "crawler"]
	elif w == 3:
		composition = ["crawler", "scout", "crawler", "brute"]
	else:
		var crawlers_count: int = 2 + (w - 3)
		var scouts_count: int = 1 + (w / 2)
		var brutes_count: int = w / 3

		for i in range(crawlers_count):
			composition.append("crawler")
		for i in range(scouts_count):
			composition.append("scout")
		for i in range(brutes_count):
			composition.append("brute")

	return composition

static func spawn_invader(invader_id: int, path: Array, archetype: String = "crawler", custom_delay: float = 0.0) -> Dictionary:
	if path.is_empty():
		return {}

	var template: Dictionary = INVADER_ARCHETYPES.get(archetype, INVADER_ARCHETYPES["crawler"])

	return {
		"id": invader_id,
		"archetype": template["type"],
		"hp": template["hp"],
		"max_hp": template["max_hp"],
		"speed": template["speed"],
		"progress": 0.0,
		"current_node": path[0],
		"path": path.duplicate(),
		"path_index": 0,
		"damage": template["damage"],
		"attack_cooldown": 1.0,
		"attack_timer": 0.0,
		"state": "spawning" if custom_delay > 0.0 else "marching",
		"spawn_delay": custom_delay,
		"scale": template["scale"],
		"color": template["color"],
	}

static func find_turret_target(turret_node_id: int, turret_data: Dictionary, active_invaders: Array, icosphere: Dictionary, factions_data: Variant = null) -> Variant:
	var range_hops: int = turret_data.get("attack_range_hops", 2)
	var in_range_nodes = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], turret_node_id, range_hops)
	var in_range_set: Dictionary = {}
	for nid in in_range_nodes:
		in_range_set[nid] = true

	var candidates: Array = []
	var turret_fid: int = turret_data.get("faction_id", 1)

	for inv in active_invaders:
		if inv["state"] not in ["dead", "spawning"] and in_range_set.has(inv["current_node"]):
			var inv_fid: int = inv.get("faction_id", 0)
			if factions_data != null and (factions_data is Dictionary) and inv_fid > 0:
				if not FactionsLogic.are_enemies(turret_fid, inv_fid, factions_data):
					continue
			candidates.append(inv)

	if candidates.is_empty():
		return null

	candidates.sort_custom(func(a, b):
		var a_direct: int = 0 if (a.get("current_node") == turret_node_id and a.get("state") == "attacking") else 1
		var b_direct: int = 0 if (b.get("current_node") == turret_node_id and b.get("state") == "attacking") else 1
		if a_direct != b_direct:
			return a_direct < b_direct
		var a_hp: float = float(a.get("hp", 999.0))
		var b_hp: float = float(b.get("hp", 999.0))
		if not is_equal_approx(a_hp, b_hp):
			return a_hp < b_hp
		return a.get("path_index", 0) > b.get("path_index", 0)
	)
	return candidates[0]


static func find_turret_building_target(turret_node_id: int, turret_data: Dictionary, world_nodes: Dictionary, icosphere: Dictionary, factions_data: Variant = null) -> Variant:
	if factions_data == null:
		return null

	var range_hops: int = turret_data.get("attack_range_hops", 2)
	var in_range_nodes = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], turret_node_id, range_hops)
	var turret_fid: int = turret_data.get("faction_id", 1)

	var candidates: Array = []
	for nid in in_range_nodes:
		if nid == turret_node_id:
			continue
		var ndata = world_nodes.get(nid)
		if ndata == null or ndata.get("building") == null:
			continue
		var bld = ndata["building"]
		if bld.get("hp", 0.0) <= 0.0:
			continue
		var bld_fid: int = bld.get("faction_id", 0)
		if bld_fid > 0 and FactionsLogic.are_enemies(turret_fid, bld_fid, factions_data):
			var bld_type = bld.get("type", "")
			var priority: int = 0 if bld_type == "base" else (1 if bld_type == "turret" else 2)
			candidates.append({
				"priority": priority,
				"hp": float(bld.get("hp", 0.0)),
				"node_id": nid,
			})

	if candidates.is_empty():
		return null

	candidates.sort_custom(func(a, b):
		if a["priority"] != b["priority"]:
			return a["priority"] < b["priority"]
		return a["hp"] < b["hp"]
	)
	return candidates[0]["node_id"]


static func update_combat_tick(world_state: Dictionary, invaders: Array, icosphere: Dictionary, delta_time: float, factions_data: Variant = null) -> Array:
	if delta_time <= 0.0:
		return [world_state, invaders, []]

	var events: Array = []
	var updated_invaders: Array = []
	for inv in invaders:
		if inv["state"] != "dead":
			updated_invaders.append(inv.duplicate(true))

	var new_world: Dictionary = {
		"nodes": {},
		"base_node_id": world_state["base_node_id"],
		"crater_node_ids": world_state.get("crater_node_ids", []).duplicate(),
		"craters": world_state.get("craters", {}).duplicate(true),
		"game_status": world_state.get("game_status", "in_progress"),
	}
	for nid in world_state["nodes"]:
		new_world["nodes"][nid] = world_state["nodes"][nid].duplicate(true)

	if factions_data != null and (factions_data is Dictionary) and factions_data.has("factions"):
		new_world["nodes"] = FactionsLogic.calculate_multi_faction_territory(icosphere, new_world["nodes"], factions_data["factions"])
	else:
		new_world = TerritoryLogic.update_territory(new_world, icosphere)

	# 1. ACTUALIZAR TIEMPOS DE COLA DE SPAWN
	for inv in updated_invaders:
		if inv["state"] == "spawning":
			inv["spawn_delay"] -= delta_time
			if inv["spawn_delay"] <= 0.0:
				inv["state"] = "marching"
				events.append({
					"type": "invader_emerged",
					"invader_id": inv["id"],
					"archetype": inv["archetype"],
					"node_id": inv["current_node"],
				})

	# 2. DISPARO DE TORRETAS
	var buildings_destroyed: Array = []
	for nid in new_world["nodes"].keys():
		var building = new_world["nodes"][nid].get("building")
		if building == null or (building.get("type") != "turret" and building.get("type") != "base") or building.get("hp", 0.0) <= 0.0:
			continue

		var cooldown: float = building.get("cooldown", 0.8 if building.get("type") == "turret" else 1.0)
		var timer: float = building.get("shoot_timer", 0.0) + delta_time

		var target = find_turret_target(nid, building, updated_invaders, icosphere, factions_data)
		if target != null and timer >= cooldown:
			var raw_damage: float = building.get("damage", 35.0 if building.get("type") == "turret" else 20.0)
			var target_fid: int = target.get("faction_id", 0)
			var target_race: String = ""
			if factions_data != null and (factions_data is Dictionary) and factions_data.has("factions"):
				if factions_data["factions"].has(target_fid):
					target_race = factions_data["factions"][target_fid].get("race", "")

			var damage: float = RacesLogic.calculate_incoming_damage(
				raw_damage, false, "", target_race
			)
			target["hp"] -= damage
			timer = 0.0
			events.append({
				"type": "turret_shot",
				"turret_node": nid,
				"target_id": target["id"],
				"damage": damage,
			})
			if target["hp"] <= 0.0:
				target["state"] = "dead"
				events.append({
					"type": "invader_killed",
					"invader_id": target["id"],
					"archetype": target["archetype"],
				})
		elif target == null and factions_data != null and timer >= cooldown and building.get("type") == "turret":
			var target_bld_node = find_turret_building_target(nid, building, new_world["nodes"], icosphere, factions_data)
			if target_bld_node != null:
				var raw_damage: float = building.get("damage", 35.0)
				var turret_race: String = ""
				var b_fid: int = building.get("faction_id", 1)
				if factions_data.has("factions") and factions_data["factions"].has(b_fid):
					turret_race = factions_data["factions"][b_fid].get("race", "")

				var target_bld = new_world["nodes"][target_bld_node]["building"]
				var target_bld_fid: int = target_bld.get("faction_id", 0)
				var target_race: String = ""
				if factions_data.has("factions") and factions_data["factions"].has(target_bld_fid):
					target_race = factions_data["factions"][target_bld_fid].get("race", "")

				var damage: float = RacesLogic.calculate_incoming_damage(
					raw_damage, true, turret_race, target_race, "heavy"
				)
				target_bld["hp"] -= damage
				timer = 0.0
				events.append({
					"type": "turret_shot_building",
					"turret_node": nid,
					"target_node": target_bld_node,
					"target_bld_type": target_bld.get("type", "building"),
					"damage": damage,
					"target_faction": target_bld.get("faction_id", 0),
					"remaining_hp": target_bld["hp"],
				})
				if target_bld["hp"] <= 0.0:
					buildings_destroyed.append(target_bld_node)

		building["shoot_timer"] = timer

	var alive_invaders: Array = []
	for inv in updated_invaders:
		if inv["state"] != "dead":
			alive_invaders.append(inv)

	# 3. MOVIMIENTO Y ATAQUE DE INVASORES

	for inv in alive_invaders:
		if inv["state"] == "spawning":
			continue

		var curr_node: int = inv["current_node"]
		var node_data = new_world["nodes"].get(curr_node)

		if node_data != null and node_data.get("building") != null and node_data["building"].get("hp", 0.0) > 0.0:
			var target_bld = node_data["building"]
			var bld_fid: int = target_bld.get("faction_id", 1)
			var inv_fid: int = inv.get("faction_id", 0)

			var should_attack: bool = true
			if factions_data != null and (factions_data is Dictionary) and inv_fid > 0:
				should_attack = FactionsLogic.are_enemies(inv_fid, bld_fid, factions_data)

			if should_attack:
				inv["state"] = "attacking"
				inv["attack_timer"] += delta_time
				if inv["attack_timer"] >= inv["attack_cooldown"]:
					inv["attack_timer"] = 0.0
					var attacker_role: String = inv.get("role", "light" if inv.get("archetype") in ["scout", "broodling", "pulse_drone", "marine", "psionic_disciple", "crawler"] else "heavy")
					var attacker_race: String = ""
					var defender_race: String = ""
					if factions_data != null and (factions_data is Dictionary) and factions_data.has("factions"):
						if factions_data["factions"].has(inv_fid):
							attacker_race = factions_data["factions"][inv_fid].get("race", "")
						if factions_data["factions"].has(bld_fid):
							defender_race = factions_data["factions"][bld_fid].get("race", "")

					var effective_damage: float = RacesLogic.calculate_incoming_damage(
						float(inv["damage"]), true, attacker_race, defender_race, attacker_role
					)
					target_bld["hp"] -= effective_damage
					events.append({
						"type": "building_damaged",
						"node_id": curr_node,
						"damage": effective_damage,
						"remaining_hp": target_bld["hp"],
						"target_faction": bld_fid,
						"attacker_faction": inv_fid,
					})
					if target_bld["hp"] <= 0.0:
						buildings_destroyed.append(curr_node)
						inv["state"] = "marching"
				continue

		# Si el camino está libre, marchar
		inv["state"] = "marching"
		inv["progress"] += inv["speed"] * delta_time

		if inv["progress"] >= 1.0:
			inv["progress"] = 0.0
			if inv["path_index"] + 1 < inv["path"].size():
				inv["path_index"] += 1
				inv["current_node"] = inv["path"][inv["path_index"]]
				events.append({
					"type": "invader_moved",
					"invader_id": inv["id"],
					"new_node": inv["current_node"],
				})

	# 4. Remover edificios destruidos
	for b_node in buildings_destroyed:
		new_world["nodes"][b_node]["building"] = null
		events.append({"type": "building_destroyed", "node_id": b_node})

	if not buildings_destroyed.is_empty():
		if factions_data != null and (factions_data is Dictionary) and factions_data.has("factions"):
			new_world["nodes"] = FactionsLogic.calculate_multi_faction_territory(icosphere, new_world["nodes"], factions_data["factions"])
		else:
			new_world = TerritoryLogic.update_territory(new_world, icosphere)

	return [new_world, alive_invaders, events]
