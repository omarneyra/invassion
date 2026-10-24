class_name PlanetView
extends Node3D
## Renderizado 3D completo: Planeta, Estructuras (Base, Torreta, Extractor, Cráter),
## Invasores animados caminando sobre la esfera, proyectiles láser y efectos de combate.

@export var planet_radius: float = 6.2
@export var subdivisions: int = 3
@export var node_marker_radius: float = 0.10

@export var use_tactical_tokens: bool = false

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
var mat_railgun_glow: StandardMaterial3D
var mat_optics: StandardMaterial3D
var mat_copper: StandardMaterial3D
var mat_harvester: StandardMaterial3D
var mat_wall: StandardMaterial3D

# Solarian Models
const MESH_TURRET = preload("res://assets/models/turret.obj")
const MESH_BASE = preload("res://assets/models/base.obj")
const MESH_HARVESTER = preload("res://assets/models/harvester.obj")
const MESH_WALL = preload("res://assets/models/wall.obj")
const MESH_PURIFIER = preload("res://assets/models/purifier.obj")
const MESH_VANGUARD = preload("res://assets/models/vanguard.obj")
const MESH_MARINE = preload("res://assets/models/marine.obj")
const SCENE_SOLARIAN_VANGUARD = preload("res://assets/models/solarian_vanguard.glb")
const SCENE_SOLARIAN_TURRET = preload("res://assets/models/solarian_turret.glb")

# Krynn Swarm Models
const MESH_KRYNN_TURRET = preload("res://assets/models/krynn_turret.obj")
const MESH_KRYNN_BASE = preload("res://assets/models/krynn_base.obj")
const MESH_KRYNN_HARVESTER = preload("res://assets/models/krynn_harvester.obj")
const MESH_KRYNN_WALL = preload("res://assets/models/krynn_wall.obj")
const MESH_KRYNN_PURIFIER = preload("res://assets/models/krynn_purifier.obj")
const MESH_KRYNN_RAVAGER = preload("res://assets/models/krynn_ravager.obj")

# Krynn Materials
var mat_krynn_chitin: StandardMaterial3D
var mat_krynn_flesh: StandardMaterial3D
var mat_krynn_acid: StandardMaterial3D
var mat_krynn_bone: StandardMaterial3D

const TEX_TURRET_TOKEN = preload("res://assets/models/turret_token.png")
const TEX_TURRET_ALBEDO = preload("res://assets/models/turret_titanium_albedo.png")
const TEX_TURRET_NORMAL = preload("res://assets/models/turret_titanium_normal.png")
const TEX_TURRET_ROUGH = preload("res://assets/models/turret_titanium_rough.png")
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
	mat_turret.albedo_texture = TEX_TURRET_ALBEDO
	mat_turret.albedo_color = Color(1.0, 1.0, 1.0)
	mat_turret.metallic = 0.88
	mat_turret.roughness_texture = TEX_TURRET_ROUGH
	mat_turret.normal_enabled = true
	mat_turret.normal_texture = TEX_TURRET_NORMAL
	mat_turret.normal_scale = 1.6
	mat_turret.rim_enabled = true
	mat_turret.rim = 0.60
	mat_turret.rim_tint = 0.3
	mat_turret.rim_color = Color("#e2e8f0")
	mat_turret.uv1_triplanar = true
	mat_turret.uv1_triplanar_sharpness = 4.0
	mat_turret.uv1_scale = Vector3(1.8, 1.8, 1.8)
	mat_turret.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_railgun_glow = StandardMaterial3D.new()
	mat_railgun_glow.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat_railgun_glow.albedo_color = Color("#00f5ff")
	mat_railgun_glow.emission_enabled = true
	mat_railgun_glow.emission = Color("#00f5ff")
	mat_railgun_glow.emission_energy_multiplier = 3.0
	mat_railgun_glow.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_optics = StandardMaterial3D.new()
	mat_optics.albedo_color = Color("#0a1525")
	mat_optics.metallic = 0.95
	mat_optics.roughness = 0.05
	mat_optics.emission_enabled = true
	mat_optics.emission = Color("#00e5ff")
	mat_optics.emission_energy_multiplier = 2.2
	mat_optics.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_copper = StandardMaterial3D.new()
	mat_copper.albedo_color = Color("#d97706")
	mat_copper.metallic = 0.92
	mat_copper.roughness = 0.22
	mat_copper.emission_enabled = true
	mat_copper.emission = Color("#b45309")
	mat_copper.emission_energy_multiplier = 0.5
	mat_copper.cull_mode = BaseMaterial3D.CULL_DISABLED

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

	# 4. Materiales Orgánicos PBR Krynn Swarm
	mat_krynn_chitin = StandardMaterial3D.new()
	mat_krynn_chitin.albedo_color = Color("#261530")
	mat_krynn_chitin.metallic = 0.70
	mat_krynn_chitin.roughness = 0.22
	mat_krynn_chitin.rim_enabled = true
	mat_krynn_chitin.rim = 0.85
	mat_krynn_chitin.rim_tint = 0.5
	mat_krynn_chitin.rim_color = Color("#a855f7")
	mat_krynn_chitin.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_krynn_flesh = StandardMaterial3D.new()
	mat_krynn_flesh.albedo_color = Color("#581c87")
	mat_krynn_flesh.roughness = 0.60
	mat_krynn_flesh.normal_enabled = true
	mat_krynn_flesh.normal_texture = bio_normal
	mat_krynn_flesh.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_krynn_acid = StandardMaterial3D.new()
	mat_krynn_acid.albedo_color = Color("#84cc16")
	mat_krynn_acid.emission_enabled = true
	mat_krynn_acid.emission = Color("#a3e635")
	mat_krynn_acid.emission_energy_multiplier = 2.4
	mat_krynn_acid.cull_mode = BaseMaterial3D.CULL_DISABLED

	mat_krynn_bone = StandardMaterial3D.new()
	mat_krynn_bone.albedo_color = Color("#e2e8f0")
	mat_krynn_bone.roughness = 0.50
	mat_krynn_bone.cull_mode = BaseMaterial3D.CULL_DISABLED

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
	var pole = Vector3.UP
	if absf(normal.dot(pole)) > 0.92:
		pole = Vector3.FORWARD
	var north_tangent = (pole - normal * normal.dot(pole)).normalized()
	var east_tangent = normal.cross(north_tangent).normalized()

	node_3d.basis = Basis(east_tangent, up, north_tangent)

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
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		_faction_materials[faction_id] = mat
	elif color_hex != "":
		var mat = _faction_materials[faction_id]
		if mat.albedo_color != col:
			mat.albedo_color = col
			mat.emission = col.darkened(0.15)

	return _faction_materials[faction_id]

func get_faction_armor_material(faction_id: int, color_hex: String = "") -> StandardMaterial3D:
	var def_color = "#15803d" if faction_id == 1 else "#6b21a8"
	var col_str = color_hex if color_hex != "" else def_color
	var col = Color(col_str)
	var key = "armor_" + str(faction_id)

	if not _faction_materials.has(key):
		var mat = StandardMaterial3D.new()
		mat.albedo_texture = TEX_TURRET_ALBEDO
		mat.albedo_color = col
		mat.metallic = 0.72
		mat.roughness_texture = TEX_TURRET_ROUGH
		mat.normal_enabled = true
		mat.normal_texture = TEX_TURRET_NORMAL
		mat.normal_scale = 1.4
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		mat.uv1_triplanar = true
		mat.uv1_triplanar_sharpness = 4.0
		mat.uv1_scale = Vector3(2.0, 2.0, 2.0)
		mat.rim_enabled = true
		mat.rim = 0.45
		mat.rim_tint = 0.5
		mat.rim_color = col.lightened(0.3)
		_faction_materials[key] = mat
	elif color_hex != "":
		var mat = _faction_materials[key]
		if mat.albedo_color != col:
			mat.albedo_color = col

	return _faction_materials[key]

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
			var b_race: String = "solarian"
			if factions_state != null and (factions_state is Dictionary) and factions_state.has("factions"):
				if factions_state["factions"].has(b_fid):
					b_col = factions_state["factions"][b_fid].get("color", "")
					b_race = factions_state["factions"][b_fid].get("race", "solarian")

			# Crear o actualizar si cambió la facción o raza de la estructura
			if not building_instances.has(nid) or building_instances[nid].get_meta("faction_id", -1) != b_fid or building_instances[nid].get_meta("race", "") != b_race:
				if building_instances.has(nid):
					building_instances[nid].queue_free()
					building_instances.erase(nid)
				var bld_obj = _create_building_3d(btype, b_fid, b_col, b_race)
				bld_obj.set_meta("faction_id", b_fid)
				bld_obj.set_meta("race", b_race)
				_align_with_surface(bld_obj, node_pos)
				add_child(bld_obj)
				building_instances[nid] = bld_obj

		elif not has_structure and not is_crater and building_instances.has(nid):
			# Estructura destruida: eliminar modelo 3D
			building_instances[nid].queue_free()
			building_instances.erase(nid)

func _apply_building_materials(mi: MeshInstance3D, fact_armor: StandardMaterial3D) -> void:
	mi.set_surface_override_material(0, mat_turret)
	mi.set_surface_override_material(1, fact_armor)
	mi.set_surface_override_material(2, mat_railgun_glow)
	mi.set_surface_override_material(3, mat_optics)
	mi.set_surface_override_material(4, mat_copper)

func _apply_krynn_materials(mi: MeshInstance3D, fact_armor: StandardMaterial3D) -> void:
	# Surface 0: Mat_KrynnChitin (blended with faction armor or chitin)
	mi.set_surface_override_material(0, fact_armor if fact_armor != null else mat_krynn_chitin)
	# Surface 1: Mat_KrynnFlesh
	mi.set_surface_override_material(1, mat_krynn_flesh)
	# Surface 2: Mat_KrynnAcid
	mi.set_surface_override_material(2, mat_krynn_acid)
	# Surface 3: Mat_KrynnBone
	mi.set_surface_override_material(3, mat_krynn_bone)

func _create_building_3d(btype: String, faction_id: int = 1, color_hex: String = "", race_id: String = "solarian") -> Node3D:
	var root = Node3D.new()
	var fact_armor: StandardMaterial3D = get_faction_armor_material(faction_id, color_hex)
	var is_krynn: bool = (race_id == "krynn")
	var glow_color: Color = Color("#84cc16") if is_krynn else Color("#00f5ff")

	if btype == "base":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_KRYNN_BASE if is_krynn else MESH_BASE
		mi.scale = Vector3(1.10, 1.10, 1.10)
		if is_krynn:
			_apply_krynn_materials(mi, fact_armor)
		else:
			_apply_building_materials(mi, fact_armor)
		root.add_child(mi)

		var light = OmniLight3D.new()
		light.light_color = glow_color
		light.light_energy = 0.7 if is_krynn else 0.6
		light.omni_range = 1.8
		light.position = Vector3(0, 0.40, 0)
		root.add_child(light)

	elif btype == "turret":
		if not is_krynn:
			var turret_inst = SCENE_SOLARIAN_TURRET.instantiate()
			turret_inst.scale = Vector3(0.52, 0.52, 0.52)
			var anim = turret_inst.get_node_or_null("AnimationPlayer")
			if anim and anim.has_animation("idle"):
				anim.play("idle")
			root.add_child(turret_inst)

			var light = OmniLight3D.new()
			light.light_color = Color("#00f5ff")
			light.light_energy = 0.85
			light.omni_range = 1.8
			light.position = Vector3(0, 0.65, 0.2)
			root.add_child(light)
		else:
			var mi = MeshInstance3D.new()
			mi.mesh = MESH_KRYNN_TURRET
			mi.scale = Vector3(1.10, 1.10, 1.10)
			_apply_krynn_materials(mi, fact_armor)
			root.add_child(mi)

			var light = OmniLight3D.new()
			light.light_color = glow_color
			light.light_energy = 0.55
			light.omni_range = 1.4
			light.position = Vector3(0, 0.32, 0.22)
			root.add_child(light)

	elif btype == "harvester":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_KRYNN_HARVESTER if is_krynn else MESH_HARVESTER
		mi.scale = Vector3(1.10, 1.10, 1.10)
		if is_krynn:
			_apply_krynn_materials(mi, fact_armor)
		else:
			_apply_building_materials(mi, fact_armor)
		root.add_child(mi)

		var light = OmniLight3D.new()
		light.light_color = glow_color
		light.light_energy = 0.6 if is_krynn else 0.5
		light.omni_range = 1.6
		light.position = Vector3(0, 0.32, 0)
		root.add_child(light)

	elif btype == "wall":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_KRYNN_WALL if is_krynn else MESH_WALL
		mi.scale = Vector3(1.10, 1.10, 1.10)
		if is_krynn:
			_apply_krynn_materials(mi, fact_armor)
		else:
			_apply_building_materials(mi, fact_armor)
		root.add_child(mi)

		var light = OmniLight3D.new()
		light.light_color = glow_color
		light.light_energy = 0.5 if is_krynn else 0.4
		light.omni_range = 1.2
		light.position = Vector3(0, 0.25, 0)
		root.add_child(light)

	elif btype == "purifier":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_KRYNN_PURIFIER if is_krynn else MESH_PURIFIER
		mi.scale = Vector3(1.10, 1.10, 1.10)
		if is_krynn:
			_apply_krynn_materials(mi, fact_armor)
		else:
			_apply_building_materials(mi, fact_armor)
		root.add_child(mi)

		var light = OmniLight3D.new()
		light.light_color = glow_color
		light.light_energy = 0.7 if is_krynn else 0.6
		light.omni_range = 2.0
		light.position = Vector3(0, 0.50, 0)
		root.add_child(light)

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

	if archetype == "vanguard":
		var mech_inst = SCENE_SOLARIAN_VANGUARD.instantiate()
		mech_inst.scale = Vector3(scale_val * 0.38, scale_val * 0.38, scale_val * 0.38)
		var anim = mech_inst.get_node_or_null("AnimationPlayer")
		if anim and anim.has_animation("idle"):
			anim.play("idle")
		root.add_child(mech_inst)
		return root

	elif archetype == "marine":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_MARINE
		mi.scale = Vector3(scale_val, scale_val, scale_val)
		_apply_building_materials(mi, custom_mat if custom_mat != null else mat_turret)
		root.add_child(mi)
		return root

	elif archetype == "ravager":
		var mi = MeshInstance3D.new()
		mi.mesh = MESH_KRYNN_RAVAGER
		mi.scale = Vector3(scale_val, scale_val, scale_val)
		_apply_krynn_materials(mi, custom_mat)
		root.add_child(mi)
		return root

	elif archetype == "scout" or archetype == "psionic_disciple":
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
