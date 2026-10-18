class_name ThreatRadarLogic
extends RefCounted
## Módulo de Radar y Alertas de Amenazas en Hemisferio Ciego.
## Estilo procedimental puro: funciones estáticas y estructuras de datos planas.

static func is_point_occluded_by_sphere(point: Vector3, camera_pos: Vector3, sphere_radius: float) -> bool:
	var cam_dist: float = camera_pos.length()
	if cam_dist <= sphere_radius or cam_dist <= 0.001:
		return false

	var norm_cam: Vector3 = camera_pos / cam_dist
	var pt_len: float = point.length()
	if pt_len <= 0.001:
		return false

	var norm_pt: Vector3 = point / pt_len
	var cos_angle: float = norm_pt.dot(norm_cam)
	var horizon_cos: float = sphere_radius / cam_dist

	# Margen de seguridad leve para ocultamiento claro
	return cos_angle < (horizon_cos - 0.02)

static func project_to_camera_screen_dir(point: Vector3, camera_right: Vector3, camera_up: Vector3) -> Vector2:
	var dx: float = point.dot(camera_right)
	var dy: float = -point.dot(camera_up) # En pantalla 2D, +Y es hacia abajo

	var dir: Vector2 = Vector2(dx, dy)
	if dir.length_squared() <= 0.0001:
		return Vector2.UP
	return dir.normalized()

static func clamp_direction_to_screen_bounds(dir: Vector2, screen_size: Vector2, margin: float = 55.0) -> Dictionary:
	var cx: float = screen_size.x * 0.5
	var cy: float = screen_size.y * 0.5

	var half_w: float = maxf(10.0, cx - margin)
	var half_h: float = maxf(10.0, cy - margin)

	var tx: float = half_w / absf(dir.x) if absf(dir.x) > 0.0001 else 1e9
	var ty: float = half_h / absf(dir.y) if absf(dir.y) > 0.0001 else 1e9

	var t: float = minf(tx, ty)
	var sx: float = cx + dir.x * t
	var sy: float = cy + dir.y * t

	return {
		"pos": Vector2(sx, sy),
		"angle": atan2(dir.y, dir.x)
	}

static func get_arrow_glyph(angle_radians: float) -> String:
	var pi: float = PI
	var a: float = fposmod(angle_radians + pi, 2.0 * pi) - pi
	var step: float = pi / 4.0

	if -step * 0.5 <= a and a < step * 0.5:
		return "➡"
	elif step * 0.5 <= a and a < step * 1.5:
		return "↘"
	elif step * 1.5 <= a and a < step * 2.5:
		return "⬇"
	elif step * 2.5 <= a and a < step * 3.5:
		return "↙"
	elif a >= step * 3.5 or a < -step * 3.5:
		return "⬅"
	elif -step * 3.5 <= a and a < -step * 2.5:
		return "↖"
	elif -step * 2.5 <= a and a < -step * 1.5:
		return "⬆"
	else:
		return "↗"

static func compute_threat_indicators(invaders: Array, nodes_data: Dictionary, camera_pos: Vector3,
		camera_right: Vector3, camera_up: Vector3, planet_radius: float,
		screen_size: Vector2, margin: float = 55.0) -> Array:
	var indicators: Array = []

	for inv in invaders:
		var state: String = inv.get("state", "")
		if state == "dead" or state == "spawning":
			continue

		var nid: int = inv.get("current_node", -1)
		if not nodes_data.has(nid):
			continue

		var pos: Vector3 = nodes_data[nid]["pos"]
		var occluded: bool = is_point_occluded_by_sphere(pos, camera_pos, planet_radius)

		if occluded:
			var dir: Vector2 = project_to_camera_screen_dir(pos, camera_right, camera_up)
			var clamp_res: Dictionary = clamp_direction_to_screen_bounds(dir, screen_size, margin)
			var arrow: String = get_arrow_glyph(clamp_res["angle"])

			var path: Array = inv.get("path", [])
			var path_idx: int = inv.get("path_index", 0)
			var remaining_hops: int = maxi(0, path.size() - 1 - path_idx)

			indicators.append({
				"invader_id": inv["id"],
				"archetype": inv.get("archetype", "crawler"),
				"hp": inv.get("hp", 0.0),
				"max_hp": inv.get("max_hp", 1.0),
				"current_node": nid,
				"remaining_hops": remaining_hops,
				"screen_pos": clamp_res["pos"],
				"angle": clamp_res["angle"],
				"arrow": arrow,
				"is_occluded": true,
				"world_pos": pos
			})

	return indicators
