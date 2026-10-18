class_name SaveSystemLogic
extends RefCounted
## Módulo de guardado y carga del estado del juego (Save / Load State).
## Estilo procedimental puro: funciones estáticas y estructuras de datos planas serializables en JSON.

const SAVE_SCHEMA_VERSION: int = 1

static func serialize_game_state(world_state: Dictionary, economy_state: Dictionary, wave_state: Dictionary) -> Dictionary:
	var nodes_serialized: Dictionary = {}
	for nid in world_state.get("nodes", {}):
		var ndata = world_state["nodes"][nid]
		nodes_serialized[str(nid)] = {
			"controller": ndata.get("controller", "neutral"),
			"building": ndata.get("building").duplicate(true) if ndata.get("building") != null else null,
			"is_crater": bool(ndata.get("is_crater", false)),
			"is_base": bool(ndata.get("is_base", false)),
		}

	var craters_serialized: Dictionary = {}
	for cid in world_state.get("craters", {}):
		var cdata = world_state["craters"][cid]
		craters_serialized[str(cid)] = {
			"hp": float(cdata.get("hp", 100.0)),
			"max_hp": float(cdata.get("max_hp", 100.0)),
			"is_sealed": bool(cdata.get("is_sealed", false)),
		}

	var crater_ids_int: Array = []
	for cid in world_state.get("crater_node_ids", []):
		crater_ids_int.append(int(cid))

	var active_invs_serialized: Array = []
	for inv in wave_state.get("active_invaders", []):
		active_invs_serialized.append(inv.duplicate(true))

	return {
		"version": SAVE_SCHEMA_VERSION,
		"world": {
			"nodes": nodes_serialized,
			"base_node_id": int(world_state.get("base_node_id", 0)),
			"crater_node_ids": crater_ids_int,
			"craters": craters_serialized,
			"game_status": str(world_state.get("game_status", "in_progress")),
		},
		"economy": {
			"energy": float(economy_state.get("energy", 100.0)),
			"base_income_rate": float(economy_state.get("base_income_rate", 5.0)),
		},
		"wave": {
			"current_wave": int(wave_state.get("current_wave", 1)),
			"wave_countdown": float(wave_state.get("wave_countdown", 20.0)),
			"is_wave_active": bool(wave_state.get("is_wave_active", false)),
			"invader_counter": int(wave_state.get("invader_counter", 0)),
			"active_invaders": active_invs_serialized,
		},
	}


static func deserialize_game_state(save_data: Variant) -> Array:
	if not (save_data is Dictionary):
		return [false, {}, "Los datos de guardado no son un diccionario válido"]

	if not save_data.has("world") or not save_data.has("economy") or not save_data.has("wave"):
		return [false, {}, "Estructura de guardado incompleta (faltan claves world, economy o wave)"]

	var world_raw: Dictionary = save_data["world"]
	var nodes_restored: Dictionary = {}
	for str_nid in world_raw.get("nodes", {}):
		var nid: int = int(str_nid)
		var ndata: Dictionary = world_raw["nodes"][str_nid]
		nodes_restored[nid] = {
			"controller": str(ndata.get("controller", "neutral")),
			"building": ndata.get("building").duplicate(true) if ndata.get("building") != null else null,
			"is_crater": bool(ndata.get("is_crater", false)),
			"is_base": bool(ndata.get("is_base", false)),
		}

	var craters_restored: Dictionary = {}
	for str_cid in world_raw.get("craters", {}):
		var cid: int = int(str_cid)
		var cdata: Dictionary = world_raw["craters"][str_cid]
		craters_restored[cid] = {
			"hp": float(cdata.get("hp", 100.0)),
			"max_hp": float(cdata.get("max_hp", 100.0)),
			"is_sealed": bool(cdata.get("is_sealed", false)),
		}

	var crater_ids_restored: Array = []
	for cid in world_raw.get("crater_node_ids", []):
		crater_ids_restored.append(int(cid))

	var restored_world: Dictionary = {
		"nodes": nodes_restored,
		"base_node_id": int(world_raw.get("base_node_id", 0)),
		"crater_node_ids": crater_ids_restored,
		"craters": craters_restored,
		"game_status": str(world_raw.get("game_status", "in_progress")),
	}

	var econ_raw: Dictionary = save_data["economy"]
	var restored_econ: Dictionary = {
		"energy": float(econ_raw.get("energy", 100.0)),
		"base_income_rate": float(econ_raw.get("base_income_rate", 5.0)),
	}

	var wave_raw: Dictionary = save_data["wave"]
	var restored_invaders: Array = []
	for inv in wave_raw.get("active_invaders", []):
		restored_invaders.append(inv.duplicate(true))

	var restored_wave: Dictionary = {
		"current_wave": int(wave_raw.get("current_wave", 1)),
		"wave_countdown": float(wave_raw.get("wave_countdown", 20.0)),
		"is_wave_active": bool(wave_raw.get("is_wave_active", false)),
		"invader_counter": int(wave_raw.get("invader_counter", 0)),
		"active_invaders": restored_invaders,
	}

	return [true, {
		"world": restored_world,
		"economy": restored_econ,
		"wave": restored_wave,
	}, ""]


static func save_game_to_file(filepath: String, save_data: Dictionary) -> Array:
	var file = FileAccess.open(filepath, FileAccess.WRITE)
	if file == null:
		var err_code = FileAccess.get_open_error()
		return [false, "Error al abrir archivo para guardar (código %d)" % err_code]

	var json_str = JSON.stringify(save_data, "\t")
	file.store_string(json_str)
	file.close()
	return [true, "Partida guardada exitosamente en %s" % filepath]


static func load_game_from_file(filepath: String) -> Array:
	if not FileAccess.file_exists(filepath):
		return [false, {}, "No existe archivo de guardado previo en %s" % filepath]

	var file = FileAccess.open(filepath, FileAccess.READ)
	if file == null:
		var err_code = FileAccess.get_open_error()
		return [false, {}, "Error al leer archivo de guardado (código %d)" % err_code]

	var json_text = file.get_as_text()
	file.close()

	var parse_result = JSON.parse_string(json_text)
	if parse_result == null:
		return [false, {}, "El archivo de guardado no contiene JSON válido"]

	var deserialization = deserialize_game_state(parse_result)
	if not deserialization[0]:
		return [false, {}, deserialization[2]]

	return [true, deserialization[1], "Partida cargada exitosamente"]
