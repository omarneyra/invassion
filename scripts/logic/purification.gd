class_name PurificationLogic
extends RefCounted
## Módulo de purificación y neutralización ofensiva de cráteres alienígenas.
## Estilo procedimental puro: funciones estáticas y estructuras de datos planas.

const PURIFIER_SPECS: Dictionary = {
	"type": "purifier",
	"cost": 120.0,
	"hp": 200.0,
	"max_hp": 200.0,
	"influence_hops": 1,
	"purify_range_hops": 4, # Alcance geodésico para alcanzar el cráter a través de la zona corrupta
	"purify_rate": 15.0, # Puntos de purificación por segundo
}

static func can_purify_crater(purifier_node_id: int, crater_node_id: int, icosphere: Dictionary, max_hops: int = 4) -> bool:
	if not icosphere["nodes"].has(purifier_node_id) or not icosphere["nodes"].has(crater_node_id):
		return false
	var in_range: Array = IcosphereLogic.get_nodes_within_hops(icosphere["nodes"], purifier_node_id, max_hops)
	return in_range.has(crater_node_id)

static func initialize_craters_data(crater_node_ids: Array, default_hp: float = 100.0) -> Dictionary:
	var craters: Dictionary = {}
	for cid in crater_node_ids:
		craters[cid] = {
			"hp": default_hp,
			"max_hp": default_hp,
			"is_sealed": false,
		}
	return craters

static func update_purification_tick(world_state: Dictionary, icosphere: Dictionary, delta: float) -> Array:
	var new_state: Dictionary = {
		"nodes": world_state["nodes"].duplicate(true),
		"base_node_id": world_state["base_node_id"],
		"crater_node_ids": world_state.get("crater_node_ids", []).duplicate(),
		"craters": world_state.get("craters", {}).duplicate(true),
		"game_status": world_state.get("game_status", "in_progress"),
	}

	if new_state["craters"].is_empty() and not new_state["crater_node_ids"].is_empty():
		new_state["craters"] = initialize_craters_data(new_state["crater_node_ids"])

	var events: Array = []
	var sealed_craters: Array = []

	var purifiers: Array = []
	for nid in new_state["nodes"].keys():
		var ndata: Dictionary = new_state["nodes"][nid]
		var bld = ndata.get("building")
		if bld != null and bld.get("type") == "purifier" and bld.get("hp", 0.0) > 0.0:
			purifiers.append({
				"node_id": nid,
				"range_hops": bld.get("purify_range_hops", 2),
				"rate": bld.get("purify_rate", 15.0),
			})

	for cid in new_state["crater_node_ids"]:
		var cdata = new_state["craters"].get(cid)
		if cdata == null or cdata.get("is_sealed", false):
			continue

		var total_rate: float = 0.0
		var active_purifiers: Array = []

		for p in purifiers:
			if can_purify_crater(p["node_id"], cid, icosphere, p["range_hops"]):
				total_rate += p["rate"]
				active_purifiers.append(p["node_id"])
				events.append({
					"type": "purification_beam",
					"purifier_node": p["node_id"],
					"crater_node": cid,
				})

		if total_rate > 0.0:
			cdata["hp"] = maxf(0.0, cdata["hp"] - total_rate * delta)
			events.append({
				"type": "crater_purifying",
				"crater_node": cid,
				"hp": cdata["hp"],
				"max_hp": cdata["max_hp"],
				"purifiers": active_purifiers,
			})

			if cdata["hp"] <= 0.0:
				cdata["is_sealed"] = true
				sealed_craters.append(cid)
				events.append({
					"type": "crater_sealed",
					"crater_node": cid,
				})

	if not sealed_craters.is_empty():
		for scid in sealed_craters:
			new_state["crater_node_ids"].erase(scid)
			if new_state["nodes"].has(scid):
				new_state["nodes"][scid]["is_crater"] = false

		new_state = TerritoryLogic.update_territory(new_state, icosphere)

		if new_state["crater_node_ids"].is_empty():
			new_state["game_status"] = "victory"
			events.append({
				"type": "all_craters_sealed",
				"message": "¡Todos los cráteres alienígenas han sido purificados!",
			})

	return [new_state, events]
