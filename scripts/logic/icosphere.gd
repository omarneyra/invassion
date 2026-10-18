class_name IcosphereLogic
extends RefCounted
## Módulo matemático para la generación y navegación del grafo de la Icosfera.
## Enfoque procedimental puro: funciones estáticas y estructuras planas (Dictionary/Array).

static func _normalize_point(p: Vector3, radius: float = 1.0) -> Vector3:
	var length = p.length()
	if length == 0.0:
		return Vector3.ZERO
	return p * (radius / length)

static func create_base_icosahedron(radius: float = 1.0) -> Dictionary:
	var phi: float = (1.0 + sqrt(5.0)) * 0.5
	var raw_vertices: Array[Vector3] = [
		Vector3(-1.0,  phi, 0.0),
		Vector3( 1.0,  phi, 0.0),
		Vector3(-1.0, -phi, 0.0),
		Vector3( 1.0, -phi, 0.0),
		Vector3(0.0, -1.0,  phi),
		Vector3(0.0,  1.0,  phi),
		Vector3(0.0, -1.0, -phi),
		Vector3(0.0,  1.0, -phi),
		Vector3( phi, 0.0, -1.0),
		Vector3( phi, 0.0,  1.0),
		Vector3(-phi, 0.0, -1.0),
		Vector3(-phi, 0.0,  1.0),
	]

	var vertices: Array[Vector3] = []
	for v in raw_vertices:
		vertices.append(_normalize_point(v, radius))

	var faces: Array = [
		[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
		[1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
		[3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
		[4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
	]

	return {"vertices": vertices, "faces": faces}

static func create_icosphere(subdivisions: int = 2, radius: float = 1.0) -> Dictionary:
	var base = create_base_icosahedron(radius)
	var vertices: Array[Vector3] = base["vertices"]
	var faces: Array = base["faces"]
	var midpoint_cache: Dictionary = {}

	for step in range(subdivisions):
		var new_faces: Array = []
		for tri in faces:
			var v1: int = tri[0]
			var v2: int = tri[1]
			var v3: int = tri[2]

			var m12: int = _get_or_create_midpoint(v1, v2, vertices, midpoint_cache, radius)
			var m23: int = _get_or_create_midpoint(v2, v3, vertices, midpoint_cache, radius)
			var m31: int = _get_or_create_midpoint(v3, v1, vertices, midpoint_cache, radius)

			new_faces.append([v1, m12, m31])
			new_faces.append([v2, m23, m12])
			new_faces.append([v3, m31, m23])
			new_faces.append([m12, m23, m31])
		faces = new_faces

	# Adyacencias
	var adjacency: Dictionary = {}
	for i in range(vertices.size()):
		adjacency[i] = []

	for tri in faces:
		var a: int = tri[0]
		var b: int = tri[1]
		var c: int = tri[2]
		if not adjacency[a].has(b): adjacency[a].append(b)
		if not adjacency[a].has(c): adjacency[a].append(c)
		if not adjacency[b].has(a): adjacency[b].append(a)
		if not adjacency[b].has(c): adjacency[b].append(c)
		if not adjacency[c].has(a): adjacency[c].append(a)
		if not adjacency[c].has(b): adjacency[c].append(b)

	var nodes: Dictionary = {}
	for idx in range(vertices.size()):
		var neighbors: Array = adjacency[idx]
		neighbors.sort()
		nodes[idx] = {
			"id": idx,
			"pos": vertices[idx],
			"neighbors": neighbors,
		}

	return {
		"nodes": nodes,
		"faces": faces,
		"node_count": vertices.size(),
		"radius": radius,
		"subdivisions": subdivisions,
	}

static func _get_or_create_midpoint(idx1: int, idx2: int, vertices: Array[Vector3], cache: Dictionary, radius: float) -> int:
	var k_min: int = mini(idx1, idx2)
	var k_max: int = maxi(idx1, idx2)
	var key: String = str(k_min) + "_" + str(k_max)

	if cache.has(key):
		return cache[key]

	var mid: Vector3 = (vertices[idx1] + vertices[idx2]) * 0.5
	var new_v: Vector3 = _normalize_point(mid, radius)
	var new_idx: int = vertices.size()
	vertices.append(new_v)
	cache[key] = new_idx
	return new_idx

static func get_spherical_distance(pos1: Vector3, pos2: Vector3, radius: float = 1.0) -> float:
	var dot: float = pos1.dot(pos2) / (radius * radius)
	dot = clampf(dot, -1.0, 1.0)
	return radius * acos(dot)

static func get_nodes_within_hops(nodes: Dictionary, start_id: int, max_hops: int) -> Array:
	if not nodes.has(start_id):
		return []

	var visited: Dictionary = {start_id: true}
	var queue: Array = [{"id": start_id, "hops": 0}]

	while not queue.is_empty():
		var curr = queue.pop_front()
		var curr_id: int = curr["id"]
		var hops: int = curr["hops"]

		if hops < max_hops:
			for neighbor in nodes[curr_id]["neighbors"]:
				if not visited.has(neighbor):
					visited[neighbor] = true
					queue.push_back({"id": neighbor, "hops": hops + 1})

	return visited.keys()

static func find_shortest_path(nodes: Dictionary, start_id: int, target_id: int, excluded_nodes: Array = []) -> Array:
	if not nodes.has(start_id) or not nodes.has(target_id):
		return []
	if start_id == target_id:
		return [start_id]

	var excluded: Dictionary = {}
	for nid in excluded_nodes:
		if nid != start_id and nid != target_id:
			excluded[nid] = true

	var queue: Array = [start_id]
	var predecessor: Dictionary = {start_id: -1}

	while not queue.is_empty():
		var curr_id: int = queue.pop_front()
		if curr_id == target_id:
			break

		for neighbor in nodes[curr_id]["neighbors"]:
			if not predecessor.has(neighbor) and not excluded.has(neighbor):
				predecessor[neighbor] = curr_id
				queue.push_back(neighbor)

	if not predecessor.has(target_id):
		return []

	var path: Array = []
	var curr: int = target_id
	while curr != -1:
		path.append(curr)
		curr = predecessor[curr]

	path.reverse()
	return path


static func find_antipodal_node(nodes: Dictionary, start_node_id: int) -> int:
	if not nodes.has(start_node_id):
		return 0
	var start_pos: Vector3 = nodes[start_node_id]["pos"]
	var best_id: int = start_node_id
	var min_dot: float = 2.0
	for nid in nodes.keys():
		var p: Vector3 = nodes[nid]["pos"]
		var dot: float = start_pos.dot(p)
		if dot < min_dot:
			min_dot = dot
			best_id = nid
	return best_id
