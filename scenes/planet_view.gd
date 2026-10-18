class_name PlanetView
extends Node3D
## Renderizado 3D completo: Planeta, Estructuras (Base, Torreta, Extractor, Cráter),
## Invasores animados caminando sobre la esfera, proyectiles láser y efectos de combate.

@export var planet_radius: float = 6.2
@export var subdivisions: int = 3
@export var node_marker_radius: float = 0.10

var icosphere_data: Dictionary = {}
var node_instances: Dictionary = {}     # {node_id: MeshInstance3D}
var building_instances: Dictionary = {} # {node_id: Node3D}
var invader_instances: Dictionary = {}  # {invader_id: Node3D}

# Materiales reutilizables
var mat_neutral: StandardMaterial3D
var mat_player: StandardMaterial3D
var mat_corrupt: StandardMaterial3D
var mat_hover: StandardMaterial3D
var mat_lines: StandardMaterial3D
var mat_planet_core: StandardMaterial3D

# Materiales de estructuras y unidades
var mat_base_glow: StandardMaterial3D
var mat_turret: StandardMaterial3D
var mat_harvester: StandardMaterial3D
var mat_wall: StandardMaterial3D
var mat_alien_hive: StandardMaterial3D
var mat_invader: StandardMaterial3D
var mat_invader_scout: StandardMaterial3D
var mat_invader_brute: StandardMaterial3D
var mat_laser: StandardMaterial3D
var mat_purifier: StandardMaterial3D
var mat_purifier_beam: StandardMaterial3D

var _hovered_node_id: int = -1

func _ready() -> void:
	_setup_materials()
	generate_planet()

func _setup_materials() -> void:
	# 1. Procedural Planetary Surface & Normal Map
	var planet_noise = FastNoiseLite.new()
	planet_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX
	planet_noise.frequency = 0.014
	planet_noise.fractal_octaves = 5
	planet_noise.fractal_lacunarity = 2.0
	planet_noise.fractal_gain = 0.52

	var planet_albedo_tex = NoiseTexture2D.new()
	planet_albedo_tex.seamless = true
	planet_albedo_tex.width = 1024
	planet_albedo_tex.height = 512
	planet_albedo_tex.noise = planet_noise

	var grad = Gradient.new()
	grad.add_point(0.00, Color("#050b18")) # Deep Ocean Trench
	grad.add_point(0.35, Color("#0d223f")) # Continental Shelf
	grad.add_point(0.42, Color("#0284c7")) # Cyan Bioluminescent Coast
	grad.add_point(0.48, Color("#1e293b")) # Coastal Lowlands
	grad.add_point(0.68, Color("#334155")) # Continental Plateaus
	grad.add_point(0.85, Color("#475569")) # Mountain Ridges
	grad.add_point(1.00, Color("#38bdf8")) # Energy Fissures / Mineral Peaks
	planet_albedo_tex.color_ramp = grad

	var planet_normal_tex = NoiseTexture2D.new()
	planet_normal_tex.seamless = true
	planet_normal_tex.as_normal_map = true
	planet_normal_tex.bump_strength = 3.2
	planet_normal_tex.width = 1024
	planet_normal_tex.height = 512
	planet_normal_tex.noise = planet_noise

	mat_planet_core = StandardMaterial3D.new()
	mat_planet_core.albedo_texture = planet_albedo_tex
	mat_planet_core.normal_enabled = true
	mat_planet_core.normal_texture = planet_normal_tex
	mat_planet_core.normal_scale = 1.6
	mat_planet_core.roughness = 0.72
	mat_planet_core.rim_enabled = true
	mat_planet_core.rim = 0.85
	mat_planet_core.rim_tint = 0.5
	mat_planet_core.rim_color = Color("#38bdf8")

	# 2. Textura de Blindaje Metálico Sci-Fi (Paneles y Remaches)
	var panel_noise = FastNoiseLite.new()
	panel_noise.noise_type = FastNoiseLite.TYPE_CELLULAR
	panel_noise.cellular_return_type = FastNoiseLite.RETURN_CELL_VALUE
	panel_noise.frequency = 0.08

	var panel_normal = NoiseTexture2D.new()
	panel_normal.seamless = true
	panel_normal.as_normal_map = true
	panel_normal.bump_strength = 2.2
	panel_normal.width = 256
	panel_normal.height = 256
	panel_normal.noise = panel_noise

	# 3. Textura Quitino-Biológica Alienígena
	var bio_noise = FastNoiseLite.new()
	bio_noise.noise_type = FastNoiseLite.TYPE_CELLULAR
	bio_noise.cellular_distance_function = FastNoiseLite.DISTANCE_MANHATTAN
	bio_noise.frequency = 0.05

	var bio_normal = NoiseTexture2D.new()
	bio_normal.seamless = true
	bio_normal.as_normal_map = true
	bio_normal.bump_strength = 3.0
	bio_normal.width = 256
	bio_normal.height = 256
	bio_normal.noise = bio_noise

	mat_neutral = StandardMaterial3D.new()
	mat_neutral.albedo_color = Color("#475569")
	mat_neutral.roughness = 0.7

	mat_player = StandardMaterial3D.new()
	mat_player.albedo_color = Color("#22c55e")
	mat_player.emission_enabled = true
	mat_player.emission = Color("#15803d")
	mat_player.emission_energy_multiplier = 0.8

	mat_corrupt = StandardMaterial3D.new()
	mat_corrupt.albedo_color = Color("#ef4444")
	mat_corrupt.emission_enabled = true
	mat_corrupt.emission = Color("#991b1b")
	mat_corrupt.emission_energy_multiplier = 0.8

	mat_hover = StandardMaterial3D.new()
	mat_hover.albedo_color = Color("#38bdf8")
	mat_hover.emission_enabled = true
	mat_hover.emission = Color("#0284c7")
	mat_hover.emission_energy_multiplier = 1.5

	mat_lines = StandardMaterial3D.new()
	mat_lines.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat_lines.albedo_color = Color(0.2, 0.35, 0.5, 0.45)

	# Materiales de entidades con texturas
	mat_base_glow = StandardMaterial3D.new()
	mat_base_glow.albedo_color = Color("#38bdf8")
	mat_base_glow.emission_enabled = true
	mat_base_glow.emission = Color("#0284c7")
	mat_base_glow.emission_energy_multiplier = 1.2
	mat_base_glow.normal_enabled = true
	mat_base_glow.normal_texture = panel_normal

	mat_turret = StandardMaterial3D.new()
	mat_turret.albedo_color = Color("#e2e8f0")
	mat_turret.metallic = 0.85
	mat_turret.roughness = 0.28
	mat_turret.normal_enabled = true
	mat_turret.normal_texture = panel_normal

	mat_harvester = StandardMaterial3D.new()
	mat_harvester.albedo_color = Color("#f59e0b")
	mat_harvester.emission_enabled = true
	mat_harvester.emission = Color("#b45309")
	mat_harvester.emission_energy_multiplier = 0.6
	mat_harvester.metallic = 0.6
	mat_harvester.roughness = 0.35
	mat_harvester.normal_enabled = true
	mat_harvester.normal_texture = panel_normal

	mat_alien_hive = StandardMaterial3D.new()
	mat_alien_hive.albedo_color = Color("#7f1d1d")
	mat_alien_hive.emission_enabled = true
	mat_alien_hive.emission = Color("#dc2626")
	mat_alien_hive.emission_energy_multiplier = 1.0
	mat_alien_hive.normal_enabled = true
	mat_alien_hive.normal_texture = bio_normal

	mat_invader = StandardMaterial3D.new()
	mat_invader.albedo_color = Color("#ff2222")
	mat_invader.emission_enabled = true
	mat_invader.emission = Color("#ff0000")
	mat_invader.emission_energy_multiplier = 1.2
	mat_invader.normal_enabled = true
	mat_invader.normal_texture = bio_normal

	mat_wall = StandardMaterial3D.new()
	mat_wall.albedo_color = Color("#38bdf8")
	mat_wall.emission_enabled = true
	mat_wall.emission = Color("#0284c7")
	mat_wall.emission_energy_multiplier = 0.9
	mat_wall.roughness = 0.2
	mat_wall.normal_enabled = true
	mat_wall.normal_texture = panel_normal

	mat_invader_scout = StandardMaterial3D.new()
	mat_invader_scout.albedo_color = Color("#f97316")
	mat_invader_scout.emission_enabled = true
	mat_invader_scout.emission = Color("#ea580c")
	mat_invader_scout.emission_energy_multiplier = 1.2
	mat_invader_scout.normal_enabled = true
	mat_invader_scout.normal_texture = bio_normal

	mat_invader_brute = StandardMaterial3D.new()
	mat_invader_brute.albedo_color = Color("#7e22ce")
	mat_invader_brute.emission_enabled = true
	mat_invader_brute.emission = Color("#581c87")
	mat_invader_brute.emission_energy_multiplier = 1.0
	mat_invader_brute.normal_enabled = true
	mat_invader_brute.normal_texture = bio_normal

	mat_laser = StandardMaterial3D.new()
	mat_laser.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat_laser.albedo_color = Color(0.2, 1.0, 0.4, 0.95)

	mat_purifier = StandardMaterial3D.new()
	mat_purifier.albedo_color = Color("#06b6d4")
	mat_purifier.emission_enabled = true
	mat_purifier.emission = Color("#0891b2")
	mat_purifier.emission_energy_multiplier = 1.4

	mat_purifier_beam = StandardMaterial3D.new()
	mat_purifier_beam.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat_purifier_beam.albedo_color = Color(0.2, 0.95, 0.85, 0.95)

func generate_planet() -> void:
	icosphere_data = IcosphereLogic.create_icosphere(subdivisions, planet_radius)

	# 1. Esfera central del planeta con textura procedural y normal map
	var core_mesh = SphereMesh.new()
	core_mesh.radial_segments = 64
	core_mesh.rings = 32
	core_mesh.radius = planet_radius * 0.985
	core_mesh.height = planet_radius * 1.97
	core_mesh.material = mat_planet_core

	var core_instance = MeshInstance3D.new()
	core_instance.mesh = core_mesh
	core_instance.name = "PlanetCore"
	add_child(core_instance)

	# 2. Velo Atmosférico / Halo orbital
	var atmo_mesh = SphereMesh.new()
	atmo_mesh.radial_segments = 48
	atmo_mesh.rings = 24
	atmo_mesh.radius = planet_radius * 1.035
	atmo_mesh.height = planet_radius * 2.07
	var atmo_mat = StandardMaterial3D.new()
	atmo_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	atmo_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	atmo_mat.cull_mode = BaseMaterial3D.CULL_FRONT
	atmo_mat.albedo_color = Color(0.12, 0.45, 0.95, 0.14)
	atmo_mesh.material = atmo_mat

	var atmo_inst = MeshInstance3D.new()
	atmo_inst.mesh = atmo_mesh
	atmo_inst.name = "AtmosphereShell"
	add_child(atmo_inst)

	# 2. Aristas de la cuadrícula geodésica
	_build_wireframe_mesh()

	# 3. Nodos tácticos
	var sphere_mesh = SphereMesh.new()
	sphere_mesh.radius = node_marker_radius
	sphere_mesh.height = node_marker_radius * 2.0

	var nodes_container = Node3D.new()
	nodes_container.name = "NodesContainer"
	add_child(nodes_container)

	for nid in icosphere_data["nodes"].keys():
		var ndata = icosphere_data["nodes"][nid]
		var mi = MeshInstance3D.new()
		mi.mesh = sphere_mesh
		mi.material_override = mat_neutral
		mi.position = ndata["pos"]
		nodes_container.add_child(mi)
		node_instances[nid] = mi

func _build_wireframe_mesh() -> void:
	var surface_tool = SurfaceTool.new()
	surface_tool.begin(Mesh.PRIMITIVE_LINES)
	surface_tool.set_material(mat_lines)

	var drawn_edges: Dictionary = {}
	for tri in icosphere_data["faces"]:
		var p1: Vector3 = icosphere_data["nodes"][tri[0]]["pos"]
		var p2: Vector3 = icosphere_data["nodes"][tri[1]]["pos"]
		var p3: Vector3 = icosphere_data["nodes"][tri[2]]["pos"]

		_add_edge_line(surface_tool, tri[0], tri[1], p1, p2, drawn_edges)
		_add_edge_line(surface_tool, tri[1], tri[2], p2, p3, drawn_edges)
		_add_edge_line(surface_tool, tri[2], tri[0], p3, p1, drawn_edges)

	var line_mesh = surface_tool.commit()
	if line_mesh != null:
		var line_instance = MeshInstance3D.new()
		line_instance.mesh = line_mesh
		line_instance.name = "WireframeGrid"
		add_child(line_instance)

func _add_edge_line(st: SurfaceTool, i1: int, i2: int, p1: Vector3, p2: Vector3, cache: Dictionary) -> void:
	var key: String = str(mini(i1, i2)) + "_" + str(maxi(i1, i2))
	if cache.has(key):
		return
	cache[key] = true
	st.add_vertex(p1)
	st.add_vertex(p2)

# --- SISTEMA DE ESTRUCTURAS 3D (BASE, TORRETA, EXTRACTOR, CRÁTER) ---

func _align_with_surface(node_3d: Node3D, pos: Vector3) -> void:
	var normal = pos.normalized()
	node_3d.position = pos

	var up = normal
	var forward = Vector3.FORWARD
	if absf(up.dot(forward)) > 0.9:
		forward = Vector3.RIGHT
	var right = up.cross(forward).normalized()
	forward = right.cross(up).normalized()

	node_3d.basis = Basis(right, up, forward)

var _faction_materials: Dictionary = {}
var current_world_state: Dictionary = {}

func get_faction_material(faction_id: int, color_hex: String = "") -> StandardMaterial3D:
	var def_color = "#22c55e" if faction_id == 1 else "#a855f7"
	var col_str = color_hex if color_hex != "" else def_color
	var col = Color(col_str)

	if not _faction_materials.has(faction_id):
		var mat = StandardMaterial3D.new()
		mat.albedo_color = col
		mat.emission_enabled = true
		mat.emission = col.darkened(0.15)
		mat.emission_energy_multiplier = 1.3
		mat.roughness = 0.25
		_faction_materials[faction_id] = mat
	elif color_hex != "":
		var mat = _faction_materials[faction_id]
		if mat.albedo_color != col:
			mat.albedo_color = col
			mat.emission = col.darkened(0.15)

	return _faction_materials[faction_id]

func update_visuals(world_state: Dictionary, factions_state: Variant = null) -> void:
	current_world_state = world_state
	if factions_state != null:
		current_factions_state = factions_state

	# 1. Actualizar materiales de nodos tácticos
	for nid in world_state["nodes"].keys():
		var ndata = world_state["nodes"][nid]
		var mi: MeshInstance3D = node_instances.get(nid)
		if mi == null:
			continue

		var ctrl = ndata.get("controller", 0)
		if nid == _hovered_node_id:
			mi.material_override = mat_hover
		elif str(ctrl) == "player" or str(ctrl) == "1":
			mi.material_override = mat_player
		elif str(ctrl) == "corrupt":
			mi.material_override = mat_corrupt
		elif ctrl is int and ctrl > 0:
			var col_hex = ""
			if factions_state != null and (factions_state is Dictionary) and factions_state.has("factions"):
				if factions_state["factions"].has(ctrl):
					col_hex = factions_state["factions"][ctrl].get("color", "")
			mi.material_override = get_faction_material(ctrl, col_hex)
		else:
			mi.material_override = mat_neutral

		# 2. Gestionar estructuras 3D físicas sobre los nodos
		var building = ndata.get("building")
		var has_structure = building != null and building.get("hp", 0.0) > 0.0
		var is_crater = ndata.get("is_crater", false)

		var node_pos: Vector3 = icosphere_data["nodes"][nid]["pos"]

		if is_crater and not building_instances.has(nid):
			var crater_obj = _create_crater_3d()
			_align_with_surface(crater_obj, node_pos)
			add_child(crater_obj)
			building_instances[nid] = crater_obj

		elif has_structure:
			var btype = building.get("type", "turret")
			var b_fid: int = building.get("faction_id", 1)
			var b_col: String = ""
			if factions_state != null and (factions_state is Dictionary) and factions_state.has("factions"):
				if factions_state["factions"].has(b_fid):
					b_col = factions_state["factions"][b_fid].get("color", "")

			# Crear o actualizar si cambió la facción de la estructura
			if not building_instances.has(nid) or building_instances[nid].get_meta("faction_id", -1) != b_fid:
				if building_instances.has(nid):
					building_instances[nid].queue_free()
					building_instances.erase(nid)
				var bld_obj = _create_building_3d(btype, b_fid, b_col)
				bld_obj.set_meta("faction_id", b_fid)
				_align_with_surface(bld_obj, node_pos)
				add_child(bld_obj)
				building_instances[nid] = bld_obj

		elif not has_structure and not is_crater and building_instances.has(nid):
			# Estructura destruida: eliminar modelo 3D
			building_instances[nid].queue_free()
			building_instances.erase(nid)

func _create_building_3d(btype: String, faction_id: int = 1, color_hex: String = "") -> Node3D:
	var root = Node3D.new()
	var fact_mat: StandardMaterial3D = get_faction_material(faction_id, color_hex)

	if btype == "base":
		# Domo central de comando iluminado con el color de la facción
		var dome = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.45
		s_mesh.height = 0.5
		dome.mesh = s_mesh
		dome.material_override = fact_mat
		dome.position = Vector3(0, 0.15, 0)
		root.add_child(dome)

		# Anillo exterior de cimiento
		var ring = MeshInstance3D.new()
		var torus = TorusMesh.new()
		torus.inner_radius = 0.42
		torus.outer_radius = 0.55
		ring.mesh = torus
		ring.material_override = mat_turret
		ring.position = Vector3(0, 0.05, 0)
		root.add_child(ring)

		# Antena de energía
		var pylon = MeshInstance3D.new()
		var c_mesh = CylinderMesh.new()
		c_mesh.top_radius = 0.06
		c_mesh.bottom_radius = 0.15
		c_mesh.height = 0.6
		pylon.mesh = c_mesh
		pylon.material_override = mat_turret
		pylon.position = Vector3(0, 0.35, 0)
		root.add_child(pylon)

		# Faro orbital superior (esfera brillante de facción)
		var beacon = MeshInstance3D.new()
		var s_beacon = SphereMesh.new()
		s_beacon.radius = 0.12
		s_beacon.height = 0.24
		beacon.mesh = s_beacon
		beacon.material_override = fact_mat
		beacon.position = Vector3(0, 0.68, 0)
		root.add_child(beacon)

	elif btype == "turret":
		# 1. Base cilíndrica blindada metálica
		var base = MeshInstance3D.new()
		var base_mesh = CylinderMesh.new()
		base_mesh.top_radius = 0.24
		base_mesh.bottom_radius = 0.32
		base_mesh.height = 0.16
		base.mesh = base_mesh
		base.material_override = mat_turret
		base.position = Vector3(0, 0.08, 0)
		root.add_child(base)

		# 2. ANILLO Y CAPUCHÓN LUMINOSO DE FACCIÓN (distinción visual total entre equipos)
		var collar = MeshInstance3D.new()
		var collar_mesh = CylinderMesh.new()
		collar_mesh.top_radius = 0.26
		collar_mesh.bottom_radius = 0.26
		collar_mesh.height = 0.07
		collar.mesh = collar_mesh
		collar.material_override = fact_mat
		collar.position = Vector3(0, 0.17, 0)
		root.add_child(collar)

		var cap = MeshInstance3D.new()
		var cap_mesh = SphereMesh.new()
		cap_mesh.radius = 0.18
		cap_mesh.height = 0.22
		cap.mesh = cap_mesh
		cap.material_override = fact_mat
		cap.position = Vector3(0, 0.24, 0)
		root.add_child(cap)

		# 3. Cañón gemelo con bocas de fuego del color de la facción
		var gun = MeshInstance3D.new()
		var box_mesh = BoxMesh.new()
		box_mesh.size = Vector3(0.12, 0.10, 0.40)
		gun.mesh = box_mesh
		gun.material_override = mat_turret
		gun.position = Vector3(0, 0.23, 0.14)
		root.add_child(gun)

		var muzzle = MeshInstance3D.new()
		var muzzle_box = BoxMesh.new()
		muzzle_box.size = Vector3(0.14, 0.12, 0.08)
		muzzle.mesh = muzzle_box
		muzzle.material_override = fact_mat
		muzzle.position = Vector3(0, 0.23, 0.34)
		root.add_child(muzzle)

	elif btype == "harvester":
		# Extractor minero con núcleo y aros del color de la facción
		var tower = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.25
		cyl.bottom_radius = 0.18
		cyl.height = 0.4
		tower.mesh = cyl
		tower.material_override = mat_harvester
		tower.position = Vector3(0, 0.2, 0)
		root.add_child(tower)

		var ring = MeshInstance3D.new()
		var r_mesh = CylinderMesh.new()
		r_mesh.top_radius = 0.28
		r_mesh.bottom_radius = 0.28
		r_mesh.height = 0.06
		ring.mesh = r_mesh
		ring.material_override = fact_mat
		ring.position = Vector3(0, 0.20, 0)
		root.add_child(ring)

		var core = MeshInstance3D.new()
		var s_core = SphereMesh.new()
		s_core.radius = 0.16
		s_core.height = 0.32
		core.mesh = s_core
		core.material_override = fact_mat
		core.position = Vector3(0, 0.42, 0)
		root.add_child(core)

	elif btype == "wall":
		# Muro de Plasma / Barricada con escudo de energía de la facción
		var shield = MeshInstance3D.new()
		var box = BoxMesh.new()
		box.size = Vector3(0.5, 0.35, 0.12)
		shield.mesh = box
		shield.material_override = fact_mat
		shield.position = Vector3(0, 0.18, 0)
		root.add_child(shield)

		var pylon_left = MeshInstance3D.new()
		var cyl_p = CylinderMesh.new()
		cyl_p.top_radius = 0.08
		cyl_p.bottom_radius = 0.1
		cyl_p.height = 0.4
		pylon_left.mesh = cyl_p
		pylon_left.material_override = mat_turret
		pylon_left.position = Vector3(-0.25, 0.2, 0)
		root.add_child(pylon_left)

		var pylon_right = MeshInstance3D.new()
		pylon_right.mesh = cyl_p
		pylon_right.material_override = mat_turret
		pylon_right.position = Vector3(0.25, 0.2, 0)
		root.add_child(pylon_right)

	elif btype == "purifier":
		# Aguja de Purificación
		var spire = MeshInstance3D.new()
		var prism = PrismMesh.new()
		prism.size = Vector3(0.32, 0.65, 0.32)
		spire.mesh = prism
		spire.material_override = mat_purifier
		spire.position = Vector3(0, 0.32, 0)
		root.add_child(spire)

		var orb = MeshInstance3D.new()
		var orb_mesh = SphereMesh.new()
		orb_mesh.radius = 0.12
		orb_mesh.height = 0.24
		orb.mesh = orb_mesh
		orb.material_override = fact_mat
		orb.position = Vector3(0, 0.72, 0)
		root.add_child(orb)

	return root

func _create_crater_3d() -> Node3D:
	var root = Node3D.new()

	# 1. Borde volcánico masivo de la caldera
	var caldera = MeshInstance3D.new()
	var torus = TorusMesh.new()
	torus.inner_radius = 0.45
	torus.outer_radius = 0.95
	caldera.mesh = torus
	caldera.material_override = mat_alien_hive
	caldera.position = Vector3(0, 0.15, 0)
	root.add_child(caldera)

	# 2. Núcleo de lava alienígena ardiente
	var lava = MeshInstance3D.new()
	var cyl = CylinderMesh.new()
	cyl.top_radius = 0.52
	cyl.bottom_radius = 0.52
	cyl.height = 0.1
	lava.mesh = cyl
	lava.material_override = mat_corrupt
	lava.position = Vector3(0, 0.12, 0)
	root.add_child(lava)

	# 3. Espinas biomecánicas quitinosas alrededor del borde
	for i in range(4):
		var angle = i * (PI * 0.5)
		var spire = MeshInstance3D.new()
		var pmesh = PrismMesh.new()
		pmesh.size = Vector3(0.22, 0.75, 0.22)
		spire.mesh = pmesh
		spire.material_override = mat_alien_hive
		spire.position = Vector3(cos(angle) * 0.72, 0.38, sin(angle) * 0.72)
		spire.rotation = Vector3(sin(angle) * 0.25, -angle, cos(angle) * 0.25)
		root.add_child(spire)

	# 4. Columna de energía volcánica visible desde la órbita
	var plume = MeshInstance3D.new()
	var cyl_plume = CylinderMesh.new()
	cyl_plume.top_radius = 0.1
	cyl_plume.bottom_radius = 0.35
	cyl_plume.height = 1.3
	plume.mesh = cyl_plume
	plume.material_override = mat_corrupt
	plume.position = Vector3(0, 0.75, 0)
	root.add_child(plume)

	return root

# --- SISTEMA DE INVASORES 3D ANIMADOS EN LA ESFERA ---

func update_invaders_visuals(active_invaders: Array) -> void:
	var living_ids: Dictionary = {}

	for inv in active_invaders:
		if inv.get("state") == "spawning":
			continue

		var i_id = inv["id"]
		living_ids[i_id] = true

		var inv_node: Node3D = invader_instances.get(i_id)
		if inv_node == null:
			var arch = inv.get("archetype", "crawler")
			var scale_val = inv.get("scale", 1.0)
			var color_hex = inv.get("color", "")
			var inv_fid = inv.get("faction_id", 0)
			if color_hex == "" and current_factions_state != null and (current_factions_state is Dictionary) and current_factions_state.has("factions"):
				if current_factions_state["factions"].has(inv_fid):
					color_hex = current_factions_state["factions"][inv_fid].get("color", "")
			inv_node = _create_invader_3d(arch, scale_val, color_hex)
			add_child(inv_node)
			invader_instances[i_id] = inv_node

		# Calcular posición 3D exacta sobre la esfera usando Slerp
		var p_idx: int = inv["path_index"]
		var path: Array = inv["path"]
		var curr_nid: int = path[p_idx]
		var next_nid: int = path[mini(p_idx + 1, path.size() - 1)]

		var p_start: Vector3 = icosphere_data["nodes"][curr_nid]["pos"]
		var p_end: Vector3 = icosphere_data["nodes"][next_nid]["pos"]

		var progress: float = inv.get("progress", 0.0)
		var raw_pos = p_start.slerp(p_end, progress)
		var sphere_pos = raw_pos.normalized() * (planet_radius + 0.18)

		_align_with_surface(inv_node, sphere_pos)

	# Limpiar modelos de invasores muertos
	var dead_ids: Array = []
	for i_id in invader_instances.keys():
		if not living_ids.has(i_id):
			dead_ids.append(i_id)

	for d_id in dead_ids:
		invader_instances[d_id].queue_free()
		invader_instances.erase(d_id)

func _create_invader_3d(archetype: String, scale_val: float = 1.0, color_hex: String = "") -> Node3D:
	var root = Node3D.new()
	var custom_mat: StandardMaterial3D = null
	if color_hex != "":
		custom_mat = StandardMaterial3D.new()
		var col = Color(color_hex)
		custom_mat.albedo_color = col
		custom_mat.emission_enabled = true
		custom_mat.emission = col.darkened(0.15)
		custom_mat.emission_energy_multiplier = 1.3

	if archetype == "scout" or archetype == "marine" or archetype == "psionic_disciple":
		# Infantería / Scout veloz (cono aerodinámico)
		var body = MeshInstance3D.new()
		var cone = CylinderMesh.new()
		cone.top_radius = 0.04
		cone.bottom_radius = 0.16
		cone.height = 0.32
		body.mesh = cone
		body.material_override = custom_mat if custom_mat != null else mat_invader_scout
		body.position = Vector3(0, 0.12, 0)
		root.add_child(body)

	elif archetype == "broodling":
		# Enjambre insectoide: cuerpo aplanado con púas dorsales
		var body = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.14
		s_mesh.height = 0.16
		body.mesh = s_mesh
		body.material_override = custom_mat if custom_mat != null else mat_invader
		body.position = Vector3(0, 0.08, 0)
		root.add_child(body)

		var horn = MeshInstance3D.new()
		var c_mesh = CylinderMesh.new()
		c_mesh.top_radius = 0.01
		c_mesh.bottom_radius = 0.08
		c_mesh.height = 0.22
		horn.mesh = c_mesh
		horn.material_override = custom_mat if custom_mat != null else mat_invader
		horn.position = Vector3(0, 0.16, 0.08)
		horn.rotation_degrees = Vector3(30, 0, 0)
		root.add_child(horn)

	elif archetype == "ravager":
		# Bestia insectoide de asalto: cabeza con mandíbulas y caparazón
		var body = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.22
		s_mesh.height = 0.28
		body.mesh = s_mesh
		body.material_override = custom_mat if custom_mat != null else mat_invader
		body.position = Vector3(0, 0.14, 0)
		root.add_child(body)

		var jaw = MeshInstance3D.new()
		var pmesh = PrismMesh.new()
		pmesh.size = Vector3(0.24, 0.16, 0.24)
		jaw.mesh = pmesh
		jaw.material_override = mat_alien_hive
		jaw.position = Vector3(0, 0.18, 0.16)
		jaw.rotation_degrees = Vector3(60, 0, 0)
		root.add_child(jaw)

	elif archetype == "scrap_tank":
		# Tanque blindado de chatarra reciclada
		var body = MeshInstance3D.new()
		var b_mesh = BoxMesh.new()
		b_mesh.size = Vector3(0.34, 0.24, 0.36)
		body.mesh = b_mesh
		body.material_override = custom_mat if custom_mat != null else mat_turret
		body.position = Vector3(0, 0.12, 0)
		root.add_child(body)

		var plow = MeshInstance3D.new()
		var p_mesh = BoxMesh.new()
		p_mesh.size = Vector3(0.42, 0.16, 0.08)
		plow.mesh = p_mesh
		plow.material_override = custom_mat if custom_mat != null else mat_turret
		plow.position = Vector3(0, 0.08, 0.20)
		root.add_child(plow)

	elif archetype == "juggernaut" or archetype == "brute":
		# Coloso / Brute acorazado monolítico
		var body = MeshInstance3D.new()
		var b_mesh = BoxMesh.new()
		b_mesh.size = Vector3(0.38, 0.32, 0.38)
		body.mesh = b_mesh
		body.material_override = custom_mat if custom_mat != null else mat_invader_brute
		body.position = Vector3(0, 0.16, 0)
		root.add_child(body)

		var armor = MeshInstance3D.new()
		var armor_box = BoxMesh.new()
		armor_box.size = Vector3(0.46, 0.12, 0.46)
		armor.mesh = armor_box
		armor.material_override = mat_turret
		armor.position = Vector3(0, 0.26, 0)
		root.add_child(armor)

	elif archetype == "railgun_mech":
		# Artillería electromagnética con cañón largo
		var body = MeshInstance3D.new()
		var b_mesh = BoxMesh.new()
		b_mesh.size = Vector3(0.28, 0.22, 0.28)
		body.mesh = b_mesh
		body.material_override = custom_mat if custom_mat != null else mat_invader
		body.position = Vector3(0, 0.12, 0)
		root.add_child(body)

		var barrel = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.03
		cyl.bottom_radius = 0.05
		cyl.height = 0.45
		barrel.mesh = cyl
		barrel.material_override = custom_mat if custom_mat != null else mat_turret
		barrel.position = Vector3(0, 0.22, 0.18)
		barrel.rotation_degrees = Vector3(70, 0, 0)
		root.add_child(barrel)

	elif archetype == "storm_skimmer":
		# Deslizador aéreo / ala en delta
		var body = MeshInstance3D.new()
		var prism = PrismMesh.new()
		prism.size = Vector3(0.38, 0.08, 0.32)
		body.mesh = prism
		body.material_override = custom_mat if custom_mat != null else mat_invader_scout
		body.position = Vector3(0, 0.15, 0)
		root.add_child(body)

	else:
		# Vanguard / Crawler / Void Infestor estándar
		var body = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.2
		s_mesh.height = 0.35
		body.mesh = s_mesh
		body.material_override = custom_mat if custom_mat != null else mat_invader
		body.position = Vector3(0, 0.1, 0)
		root.add_child(body)

	root.scale = Vector3.ONE * scale_val
	return root

func _create_laser_bolt(start_pos: Vector3, end_pos: Vector3, source_node: int) -> void:
	var delta_vec: Vector3 = end_pos - start_pos
	var dist: float = delta_vec.length()
	if dist <= 0.05:
		return

	var l_mat = mat_laser
	if current_world_state != null and current_world_state.get("nodes", {}).has(source_node):
		var bld = current_world_state["nodes"][source_node].get("building")
		if bld != null:
			var b_fid: int = bld.get("faction_id", 1)
			l_mat = get_faction_material(b_fid)

	var bolt = MeshInstance3D.new()
	var cyl = CylinderMesh.new()
	cyl.top_radius = 0.04
	cyl.bottom_radius = 0.04
	cyl.height = dist
	bolt.mesh = cyl
	bolt.material_override = l_mat
	bolt.position = start_pos + delta_vec * 0.5

	var up: Vector3 = delta_vec.normalized()
	var forward: Vector3 = Vector3.FORWARD
	if absf(up.dot(forward)) > 0.9:
		forward = Vector3.RIGHT
	var right: Vector3 = up.cross(forward).normalized()
	forward = right.cross(up).normalized()
	bolt.basis = Basis(right, up, forward)

	add_child(bolt)

	var tween = create_tween()
	tween.tween_property(bolt, "scale", Vector3(0.01, 1.0, 0.01), 0.16)
	tween.tween_callback(bolt.queue_free)

func fire_laser(turret_node_id: int, target_invader_id: Variant) -> void:
	if not icosphere_data["nodes"].has(turret_node_id):
		return
	var inv_node = invader_instances.get(target_invader_id)
	if inv_node == null:
		return

	var start_pos = icosphere_data["nodes"][turret_node_id]["pos"] + (icosphere_data["nodes"][turret_node_id]["pos"].normalized() * 0.35)
	var end_pos = inv_node.position
	_create_laser_bolt(start_pos, end_pos, turret_node_id)

func fire_laser_to_node(from_node: int, to_node: int) -> void:
	if not icosphere_data["nodes"].has(from_node) or not icosphere_data["nodes"].has(to_node):
		return

	var start_pos = icosphere_data["nodes"][from_node]["pos"] + (icosphere_data["nodes"][from_node]["pos"].normalized() * 0.35)
	var end_pos = icosphere_data["nodes"][to_node]["pos"] + (icosphere_data["nodes"][to_node]["pos"].normalized() * 0.35)
	_create_laser_bolt(start_pos, end_pos, from_node)

func fire_purification_beam(purifier_node_id: int, crater_node_id: int) -> void:
	if not icosphere_data["nodes"].has(purifier_node_id) or not icosphere_data["nodes"].has(crater_node_id):
		return

	var start_pos: Vector3 = icosphere_data["nodes"][purifier_node_id]["pos"] + (icosphere_data["nodes"][purifier_node_id]["pos"].normalized() * 0.72)
	var end_pos: Vector3 = icosphere_data["nodes"][crater_node_id]["pos"] + (icosphere_data["nodes"][crater_node_id]["pos"].normalized() * 0.25)

	var delta_vec: Vector3 = end_pos - start_pos
	var dist: float = delta_vec.length()
	if dist <= 0.05:
		return

	var beam = MeshInstance3D.new()
	var cyl = CylinderMesh.new()
	cyl.top_radius = 0.06
	cyl.bottom_radius = 0.06
	cyl.height = dist
	beam.mesh = cyl
	beam.material_override = mat_purifier_beam

	# Posicionar en el punto medio del segmento
	beam.position = start_pos + delta_vec * 0.5

	# Alinear el cilindro (+Y) con el vector delta_vec
	var up: Vector3 = delta_vec.normalized()
	var forward: Vector3 = Vector3.FORWARD
	if absf(up.dot(forward)) > 0.9:
		forward = Vector3.RIGHT
	var right: Vector3 = up.cross(forward).normalized()
	forward = right.cross(up).normalized()
	beam.basis = Basis(right, up, forward)

	add_child(beam)

	var tween = create_tween()
	tween.tween_property(beam, "scale", Vector3(0.05, 1.0, 0.05), 0.22)
	tween.tween_callback(beam.queue_free)

# --- RAYCASTING DE SELECCIÓN ---

var current_factions_state: Variant = null

func set_hover_node(node_id: int, world_state: Dictionary, factions_state: Variant = null) -> void:
	if factions_state != null:
		current_factions_state = factions_state
	if _hovered_node_id != node_id:
		_hovered_node_id = node_id
		update_visuals(world_state, current_factions_state)

func get_closest_node_from_ray(ray_origin: Vector3, ray_dir: Vector3) -> int:
	var a: float = ray_dir.dot(ray_dir)
	var b: float = 2.0 * ray_origin.dot(ray_dir)
	var c: float = ray_origin.dot(ray_origin) - (planet_radius * planet_radius)
	var discriminant: float = b * b - 4.0 * a * c

	if discriminant < 0.0:
		return -1

	var t: float = (-b - sqrt(discriminant)) / (2.0 * a)
	if t < 0.0:
		return -1

	var hit_point: Vector3 = ray_origin + ray_dir * t
	var best_id: int = -1
	var best_dot: float = -2.0

	for nid in icosphere_data["nodes"].keys():
		var npos: Vector3 = icosphere_data["nodes"][nid]["pos"]
		var dot: float = npos.dot(hit_point)
		if dot > best_dot:
			best_dot = dot
			best_id = nid

	return best_id
