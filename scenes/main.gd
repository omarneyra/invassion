class_name MainGame
extends Node3D
## Controlador principal del RTS Planetario 3D 'invassion'.
## Conecta la vista 3D pasiva con la simulación procedimental pura (Facciones, IA, Diplomacia, Combate).

@onready var camera_orbit: CameraOrbit = $CameraOrbit
@onready var planet_view: PlanetView = $PlanetView

# Elementos del HUD (CanvasLayer)
@onready var hud: CanvasLayer = $HUD

var label_energy: Label = null
var label_wave_timer: Label = null
var label_status: Label = null
var btn_focus_base: Button = null
var btn_focus_threat: Button = null
var btn_focus_crater: Button = null
var label_crater_status: Label = null
var btn_zoom_in: Button = null
var btn_zoom_out: Button = null
var btn_save: Button = null
var btn_load: Button = null
var btn_diplomacy: Button = null
var panel_diplomacy: Panel = null
var factions_list_container: VBoxContainer = null
var btn_close_diplo: Button = null

var btn_tech_tree: Button = null
var panel_tech_tree: Panel = null
var tech_list_container: VBoxContainer = null
var btn_close_tech: Button = null

const SAVE_FILE_PATH: String = "user://quicksave.json"

var factions_state: Dictionary = {}
var ai_tick_timer: float = 0.0
var ai_base_node_id: int = -1

var btn_wall: Button = null
var btn_harvester: Button = null
var btn_turret: Button = null
var btn_purifier: Button = null
var btn_assault: Button = null
var btn_wave: Button = null
var banner_game_over: Control = null
var label_game_over: Label = null
var label_game_over_details: Label = null
var btn_restart_game: Button = null
var btn_spectate_game: Button = null
var radar_overlay: Control = null

# Elementos del Inspector de Selección RTS
var inspector_icon: Label = null
var inspector_title: Label = null
var inspector_owner: Label = null
var inspector_hp: Label = null
var inspector_stats: Label = null
var selected_inspector_node: int = -1

var world_state: Dictionary = {}
var economy_state: Dictionary = {}
var active_invaders: Array = []
var selected_building_type: String = "" # "wall", "harvester", "turret", "purifier" o ""
var _radar_indicator_buttons: Array = []

var base_node_id: int = 0
var invader_counter: int = 0
var assault_cooldown_timer: float = 0.0

# Sistema de Asaltos / Oleadas
var current_wave: int = 1
var wave_countdown: float = 20.0
var is_wave_active: bool = false

func _ready() -> void:
	# 1. Configuración de Facciones Planetarias (Jugador vs IA Simétrica)
	var faction_configs: Array = [
		{"name": "Imperio Solar", "race": "solarian", "is_ai": false, "team": 1, "starting_energy": 100.0},
		{"name": "Enclave Krynn", "race": "krynn", "is_ai": true, "team": 2, "starting_energy": 100.0}
	]
	factions_state = FactionsLogic.initialize_factions_game(planet_view.icosphere_data, faction_configs)
	base_node_id = factions_state["factions"][1]["base_node"]
	ai_base_node_id = factions_state["factions"][2]["base_node"]

	# 2. Inicializar lógica del mundo
	world_state = TerritoryLogic.initialize_world_state(
		planet_view.icosphere_data, base_node_id, []
	)

	# Asignar base del jugador (Facción 1) con batería defensiva
	world_state["nodes"][base_node_id]["building"]["faction_id"] = 1
	world_state["nodes"][base_node_id]["building"]["attack_range_hops"] = 1
	world_state["nodes"][base_node_id]["building"]["damage"] = 40.0
	world_state["nodes"][base_node_id]["building"]["cooldown"] = 0.8
	world_state["nodes"][base_node_id]["building"]["shoot_timer"] = 0.0
	world_state["nodes"][base_node_id]["is_base"] = true

	# Asignar base de la IA (Facción 2) con batería defensiva
	world_state["nodes"][ai_base_node_id]["building"] = {
		"type": "base",
		"hp": 1500.0,
		"max_hp": 1500.0,
		"influence_hops": RacesLogic.calculate_initial_influence_hops(factions_state["factions"][2]["race"]),
		"faction_id": 2,
		"attack_range_hops": 1,
		"damage": 40.0,
		"cooldown": 0.8,
		"shoot_timer": 0.0
	}
	world_state["nodes"][ai_base_node_id]["is_base"] = true

	# Proyección de territorio multi-facción
	world_state["nodes"] = FactionsLogic.calculate_multi_faction_territory(
		planet_view.icosphere_data, world_state["nodes"], factions_state["factions"]
	)

	economy_state = EconomyLogic.create_initial_economy(100.0, 5.0)

	# 3. Inicializar referencias del HUD dinámicamente
	label_energy = hud.find_child("LabelEnergy", true, false)
	label_wave_timer = hud.find_child("LabelWaveTimer", true, false)
	label_status = hud.find_child("LabelStatus", true, false)
	btn_focus_base = hud.find_child("BtnFocusBase", true, false)
	btn_focus_threat = hud.find_child("BtnFocusThreat", true, false)
	btn_focus_crater = hud.find_child("BtnFocusCrater", true, false)
	label_crater_status = hud.find_child("LabelCraterStatus", true, false)
	btn_zoom_in = hud.find_child("BtnZoomIn", true, false)
	btn_zoom_out = hud.find_child("BtnZoomOut", true, false)
	btn_save = hud.find_child("BtnSave", true, false)
	btn_load = hud.find_child("BtnLoad", true, false)
	btn_diplomacy = hud.find_child("BtnDiplomacy", true, false)
	panel_diplomacy = hud.find_child("PanelDiplomacy", true, false)
	factions_list_container = hud.find_child("FactionsList", true, false)
	btn_close_diplo = hud.find_child("BtnCloseDiplo", true, false)

	btn_tech_tree = hud.find_child("BtnTechTree", true, false)
	panel_tech_tree = hud.find_child("PanelTechTree", true, false)
	if panel_tech_tree != null:
		tech_list_container = panel_tech_tree.find_child("TechList", true, false)
		btn_close_tech = panel_tech_tree.find_child("BtnCloseTech", true, false)
		panel_tech_tree.visible = false
		if btn_close_tech != null:
			btn_close_tech.pressed.connect(close_tech_panel)

	if btn_tech_tree != null:
		btn_tech_tree.pressed.connect(toggle_tech_panel)

	btn_wall = hud.find_child("BtnWall", true, false)
	btn_harvester = hud.find_child("BtnHarvester", true, false)
	btn_turret = hud.find_child("BtnTurret", true, false)
	btn_purifier = hud.find_child("BtnPurifier", true, false)
	btn_assault = hud.find_child("BtnAssault", true, false)
	btn_wave = hud.find_child("BtnWave", true, false)
	banner_game_over = hud.find_child("BannerGameOver", true, false)
	label_game_over = hud.find_child("LabelResult", true, false)
	label_game_over_details = hud.find_child("LabelDetails", true, false)
	btn_restart_game = hud.find_child("BtnRestart", true, false)
	btn_spectate_game = hud.find_child("BtnSpectate", true, false)
	radar_overlay = hud.find_child("RadarOverlay", true, false)

	# Inspector de Selección RTS
	inspector_icon = hud.find_child("InspectorIcon", true, false)
	inspector_title = hud.find_child("InspectorTitle", true, false)
	inspector_owner = hud.find_child("InspectorOwner", true, false)
	inspector_hp = hud.find_child("InspectorHp", true, false)
	inspector_stats = hud.find_child("InspectorStats", true, false)

	# 4. Conectar señales de input de cámara y HUD
	camera_orbit.clicked_screen.connect(_on_screen_clicked)

	if btn_focus_base: btn_focus_base.pressed.connect(focus_base)
	if btn_focus_threat: btn_focus_threat.pressed.connect(focus_threat)
	if btn_focus_crater: btn_focus_crater.pressed.connect(focus_crater)
	if btn_zoom_in: btn_zoom_in.pressed.connect(func(): camera_orbit.zoom_in())
	if btn_zoom_out: btn_zoom_out.pressed.connect(func(): camera_orbit.zoom_out())
	if btn_save: btn_save.pressed.connect(save_game_state)
	if btn_load: btn_load.pressed.connect(load_game_state)

	if btn_diplomacy: btn_diplomacy.pressed.connect(toggle_diplomacy_panel)
	if btn_close_diplo: btn_close_diplo.pressed.connect(close_diplomacy_panel)

	if btn_wall: btn_wall.pressed.connect(func(): _select_building("wall"))
	if btn_harvester: btn_harvester.pressed.connect(func(): _select_building("harvester"))
	if btn_turret: btn_turret.pressed.connect(func(): _select_building("turret"))
	if btn_purifier: btn_purifier.pressed.connect(func(): _select_building("purifier"))

	if btn_assault: btn_assault.pressed.connect(_launch_player_assault)
	if btn_wave: btn_wave.pressed.connect(_on_wave_button_pressed)

	if btn_restart_game: btn_restart_game.pressed.connect(restart_game)
	if btn_spectate_game: btn_spectate_game.pressed.connect(spectate_game)

	if banner_game_over: banner_game_over.visible = false
	if panel_diplomacy: panel_diplomacy.visible = false

	# Estilización de Botoneras estilo StarCraft / Age of Empires
	_apply_rts_button_theme(btn_wall, Color(0.2, 0.7, 0.9))
	_apply_rts_button_theme(btn_harvester, Color(0.95, 0.65, 0.15))
	_apply_rts_button_theme(btn_turret, Color(0.2, 0.85, 0.4))
	_apply_rts_button_theme(btn_assault, Color(0.9, 0.3, 0.25))
	_apply_rts_button_theme(btn_wave, Color(0.7, 0.35, 0.9))
	_apply_rts_button_theme(btn_focus_base, Color(0.3, 0.5, 0.7))
	_apply_rts_button_theme(btn_focus_threat, Color(0.9, 0.5, 0.2))
	_apply_rts_button_theme(btn_focus_crater, Color(0.8, 0.3, 0.6))
	_apply_rts_button_theme(btn_zoom_in, Color(0.3, 0.5, 0.7))
	_apply_rts_button_theme(btn_zoom_out, Color(0.3, 0.5, 0.7))
	_apply_rts_button_theme(btn_tech_tree, Color(0.2, 0.8, 0.6))
	_apply_rts_button_theme(btn_diplomacy, Color(0.3, 0.6, 0.9))
	_apply_rts_button_theme(btn_save, Color(0.4, 0.5, 0.6))
	_apply_rts_button_theme(btn_load, Color(0.4, 0.5, 0.6))
	_apply_rts_button_theme(btn_restart_game, Color(0.2, 0.85, 0.4))
	_apply_rts_button_theme(btn_spectate_game, Color(0.3, 0.6, 0.9))

	_update_ui()
	_update_inspector(base_node_id)
	planet_view.update_visuals(world_state, factions_state)

func _apply_rts_button_theme(btn: Button, accent_color: Color = Color(0.2, 0.45, 0.7)) -> void:
	if btn == null:
		return
	var sb_normal = StyleBoxFlat.new()
	sb_normal.bg_color = Color(0.06, 0.09, 0.14, 0.95)
	sb_normal.set_border_width_all(1)
	sb_normal.border_color = accent_color * 0.8
	sb_normal.set_corner_radius_all(4)
	sb_normal.set_content_margin_all(5)

	var sb_hover = StyleBoxFlat.new()
	sb_hover.bg_color = Color(0.09, 0.14, 0.22, 0.98)
	sb_hover.set_border_width_all(1)
	sb_hover.border_color = accent_color * 1.5
	sb_hover.set_corner_radius_all(4)
	sb_hover.set_content_margin_all(5)

	var sb_pressed = StyleBoxFlat.new()
	sb_pressed.bg_color = Color(0.12, 0.18, 0.28, 1.0)
	sb_pressed.set_border_width_all(2)
	sb_pressed.border_color = Color(0.38, 0.74, 0.98)
	sb_pressed.set_corner_radius_all(4)
	sb_pressed.set_content_margin_all(5)

	var sb_disabled = StyleBoxFlat.new()
	sb_disabled.bg_color = Color(0.03, 0.05, 0.08, 0.6)
	sb_disabled.set_border_width_all(1)
	sb_disabled.border_color = Color(0.12, 0.16, 0.22, 0.5)
	sb_disabled.set_corner_radius_all(4)
	sb_disabled.set_content_margin_all(5)

	btn.add_theme_stylebox_override("normal", sb_normal)
	btn.add_theme_stylebox_override("hover", sb_hover)
	btn.add_theme_stylebox_override("pressed", sb_pressed)
	btn.add_theme_stylebox_override("disabled", sb_disabled)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			if world_state.get("game_status") != "in_progress":
				restart_game()
			else:
				focus_base()
		elif event.keycode == KEY_B:
			focus_base()
		elif event.keycode == KEY_F:
			focus_threat()
		elif event.keycode == KEY_C:
			focus_crater()
		elif event.keycode == KEY_D:
			toggle_diplomacy_panel()
		elif event.keycode == KEY_T:
			toggle_tech_panel()
		elif event.keycode == KEY_R:
			_launch_player_assault()
		elif event.keycode == KEY_ESCAPE:
			if panel_diplomacy.visible:
				close_diplomacy_panel()
			if panel_tech_tree != null and panel_tech_tree.visible:
				close_tech_panel()
		elif event.keycode == KEY_F6:
			save_game_state()
		elif event.keycode == KEY_F7:
			load_game_state()

func focus_base() -> void:
	var base_pos: Vector3 = planet_view.icosphere_data["nodes"][base_node_id]["pos"]
	camera_orbit.focus_on_point(base_pos)
	label_status.text = "🎯 Cámara centrada en tu Puesto de Comando Solar."

func focus_crater() -> void:
	if ai_base_node_id != -1 and planet_view.icosphere_data["nodes"].has(ai_base_node_id):
		var base_pos: Vector3 = planet_view.icosphere_data["nodes"][ai_base_node_id]["pos"]
		camera_orbit.focus_on_point(base_pos)
		label_status.text = "🏛️ Enfocando base de la facción IA (Nodo #" + str(ai_base_node_id) + ")."
	else:
		label_status.text = "No hay base enemiga activa."

func focus_threat() -> void:
	var alive = active_invaders.filter(func(x): return x.get("state") != "spawning")
	if not alive.is_empty():
		var target_inv = alive[0]
		var target_node = target_inv["current_node"]
		var threat_pos: Vector3 = planet_view.icosphere_data["nodes"][target_node]["pos"]
		camera_orbit.focus_on_point(threat_pos)
		label_status.text = "⚠️ Enfocando amenaza: " + target_inv.get("archetype", "unidad").capitalize() + " #" + str(target_inv["id"]) + "."
	else:
		if ai_base_node_id != -1:
			focus_crater()
		else:
			focus_base()

func _process(delta: float) -> void:
	if world_state.get("game_status") != "in_progress":
		return

	# 1. Simulación de economía multi-facción continua
	factions_state["factions"] = FactionsLogic.update_multi_faction_economy(
		factions_state["factions"], world_state["nodes"], planet_view.icosphere_data, delta
	)
	if factions_state["factions"].has(1):
		economy_state["energy"] = factions_state["factions"][1]["energy"]

	# 2. Gestión del temporizador de oleadas / asaltos
	if assault_cooldown_timer > 0.0:
		assault_cooldown_timer = maxf(0.0, assault_cooldown_timer - delta)
	_update_wave_system(delta)

	# 3. Comandante de Inteligencia Artificial procedimental simétrica (cada 1.5s)
	ai_tick_timer += delta
	if ai_tick_timer >= 1.5:
		ai_tick_timer = 0.0
		var territory_changed: bool = false
		for fid in factions_state["factions"]:
			var fdata = factions_state["factions"][fid]
			if fdata.get("is_ai") and fdata.get("is_alive"):
				var ai_res = AICommanderLogic.run_ai_tick(
					fid, factions_state, world_state["nodes"], planet_view.icosphere_data, 1.5
				)
				factions_state = ai_res[0]
				world_state["nodes"] = ai_res[1]
				var new_units: Array = ai_res[2]
				var ai_actions: Array = ai_res[3]

				for u in new_units:
					invader_counter += 1
					u["id"] = invader_counter
					active_invaders.append(u)

				for act in ai_actions:
					if act.get("type") == "building_constructed":
						territory_changed = true
						label_status.text = "🏗️ " + fdata["name"] + " construyó " + act["building_type"].capitalize() + " en nodo #" + str(act["node_id"]) + "."
					elif act.get("type") == "military_assault_launched":
						label_status.text = "⚔️ ¡ALERTA! " + fdata["name"] + " lanzó asalto geodésico (" + str(act["units_count"]) + " unidades) hacia tu base."
					elif act.get("type") == "diplomacy_change":
						label_status.text = "📜 " + act["message"]
					elif act.get("type") == "tech_researched":
						label_status.text = "🔬 ¡ALERTA! " + fdata["name"] + " investigó: " + act["message"]

		if territory_changed:
			world_state["nodes"] = FactionsLogic.calculate_multi_faction_territory(
				planet_view.icosphere_data, world_state["nodes"], factions_state["factions"]
			)
			planet_view.update_visuals(world_state, factions_state)

	# 4. Simulación de combate (unidades móviles y asedio de torretas)
	var combat_res = CombatLogic.update_combat_tick(
		world_state, active_invaders, planet_view.icosphere_data, delta, factions_state
	)
	world_state = combat_res[0]
	active_invaders = combat_res[1]
	var events: Array = combat_res[2]

	var recheck_territory: bool = false
	for ev in events:
		if ev.get("type") == "turret_shot":
			planet_view.fire_laser(ev["turret_node"], ev["target_id"])
		elif ev.get("type") == "turret_shot_building":
			planet_view.fire_laser_to_node(ev["turret_node"], ev["target_node"])
			label_status.text = "🎯 ¡Torreta bombardeando instalación enemiga (#%d)!" % [ev["target_node"]]
		elif ev.get("type") == "invader_killed":
			label_status.text = "¡Unidad enemiga eliminada por la torreta defensiva!"
		elif ev.get("type") == "building_damaged":
			if ev.get("shield_active", false):
				label_status.text = "🛡️ ¡Escudo Perimetral activo (-60% daño a base)! Neutraliza las torretas primero."
			else:
				label_status.text = "¡Alerta! Instalación bajo asedio militar enemigo."
		elif ev.get("type") == "building_destroyed":
			label_status.text = "¡Una instalación ha sido demolida en combate!"
			recheck_territory = true

	if recheck_territory:
		world_state["nodes"] = FactionsLogic.calculate_multi_faction_territory(
			planet_view.icosphere_data, world_state["nodes"], factions_state["factions"]
		)

	planet_view.update_visuals(world_state, factions_state)
	planet_view.update_invaders_visuals(active_invaders)

	# 5. Detección de Hover (iluminar nodo bajo el cursor)
	_update_mouse_hover()

	# 6. Radar de amenazas en el hemisferio ciego
	_update_threat_radar()

	# 7. Verificar fin de juego (Victoria / Derrota simétrica de facciones)
	var vic_res = FactionsLogic.evaluate_factions_victory_defeat(factions_state, world_state["nodes"], 1)
	var outcome: String = vic_res[0]
	factions_state["factions"] = vic_res[2]

	if outcome == "victory":
		world_state["game_status"] = "victory"
		_show_game_over(true)
	elif outcome == "defeat":
		world_state["game_status"] = "defeat"
		_show_game_over(false)

	_update_ui()

func _update_wave_system(delta: float) -> void:
	if is_wave_active:
		if active_invaders.is_empty():
			is_wave_active = false
			current_wave += 1
			wave_countdown = 20.0
			economy_state = EconomyLogic.apply_income(economy_state, 25.0)
			if factions_state["factions"].has(1):
				factions_state["factions"][1]["energy"] = economy_state["energy"]
			label_status.text = "¡Asalto superado con éxito! Bono de victoria: +25 Energía."
	else:
		wave_countdown -= delta
		if wave_countdown <= 0.0:
			_launch_wave(false)

func _on_wave_button_pressed() -> void:
	if not is_wave_active:
		economy_state = EconomyLogic.apply_income(economy_state, 15.0)
		if factions_state["factions"].has(1):
			factions_state["factions"][1]["energy"] = economy_state["energy"]
		_launch_wave(true)

func _launch_player_assault() -> void:
	if assault_cooldown_timer > 0.0:
		label_status.text = "⚠️ Recargando transportes de asalto (%.1fs restantes)" % assault_cooldown_timer
		return
	if factions_state.is_empty() or not factions_state.has("factions"):
		return

	# Sincronizar economía del jugador con la facción 1
	factions_state["factions"][1]["energy"] = economy_state["energy"]

	var assault_res = AICommanderLogic.launch_faction_assault(
		1, factions_state, world_state["nodes"], planet_view.icosphere_data, 85.0
	)
	if assault_res[0]:
		assault_cooldown_timer = 15.0
		var squad: Array = assault_res[1]
		var cost: float = assault_res[2]
		var msg: String = assault_res[4]

		economy_state["energy"] = float(factions_state["factions"][1]["energy"])

		for u in squad:
			invader_counter += 1
			u["id"] = invader_counter
			active_invaders.append(u)

		label_status.text = "🚀 " + msg
		_update_ui()
		planet_view.update_invaders_visuals(active_invaders)
	else:
		var err_msg: String = assault_res[4]
		label_status.text = "⚠️ " + err_msg

func _launch_wave(early_bonus: bool) -> void:
	var spawn_node: int = ai_base_node_id
	var active_craters: Array = world_state.get("crater_node_ids", [])
	if not active_craters.is_empty():
		spawn_node = active_craters[0]
	elif ai_base_node_id == -1 or not factions_state.get("factions", {}).get(2, {}).get("is_alive", false):
		label_status.text = "¡La facción enemiga ha capitulado! El planeta está pacificado."
		return

	is_wave_active = true
	var composition = CombatLogic.create_wave_composition(current_wave)

	var lanes: Array = []
	if current_wave >= 3:
		lanes = CombatLogic.generate_multiple_invasion_lanes(
			planet_view.icosphere_data, spawn_node, base_node_id, 2
		)
	else:
		lanes = [CombatLogic.generate_invasion_lane(
			planet_view.icosphere_data, spawn_node, base_node_id
		)]

	for i in range(composition.size()):
		invader_counter += 1
		var arch = composition[i]
		var target_lane = lanes[i % lanes.size()]
		var delay = i * 0.4
		var new_inv = CombatLogic.spawn_invader(invader_counter, target_lane, arch, delay)
		new_inv["faction_id"] = 2
		active_invaders.append(new_inv)

	var bonus_text = " (+15 E por inicio rápido)" if early_bonus else ""
	var pincer_text = " ¡ATAQUE EN PINZA (2 FRENTES)!" if lanes.size() > 1 else ""
	label_status.text = "¡ASALTO #" + str(current_wave) + pincer_text + " EN MARCHA! " + str(composition.size()) + " tropas enemigas" + bonus_text + "."

func _update_mouse_hover() -> void:
	var viewport = get_viewport()
	if not viewport:
		return
	var mouse_pos = viewport.get_mouse_position()
	var cam: Camera3D = camera_orbit.camera
	if cam:
		var ray_origin = cam.project_ray_origin(mouse_pos)
		var ray_dir = cam.project_ray_normal(mouse_pos)
		var hover_id = planet_view.get_closest_node_from_ray(ray_origin, ray_dir)
		planet_view.set_hover_node(hover_id, world_state, factions_state)

func _select_building(btype: String) -> void:
	if selected_building_type == btype:
		selected_building_type = ""
		label_status.text = "Navegación libre: Arrastra para girar con inercia."
	else:
		selected_building_type = btype
		if btype == "purifier":
			label_status.text = "Seleccionado: Purificador (120 E). Alcance: 4 saltos."
		else:
			label_status.text = "Seleccionado: " + btype.capitalize() + ". Haz clic en un nodo de tu territorio verde para construir."

func _on_screen_clicked(screen_pos: Vector2) -> void:
	var cam: Camera3D = camera_orbit.camera
	var ray_origin = cam.project_ray_origin(screen_pos)
	var ray_dir = cam.project_ray_normal(screen_pos)

	var clicked_node = planet_view.get_closest_node_from_ray(ray_origin, ray_dir)
	if clicked_node == -1:
		return

	if selected_building_type != "":
		var afford_check = EconomyLogic.purchase_building(economy_state, selected_building_type)
		if not afford_check[0]:
			label_status.text = "Energía insuficiente para construir " + selected_building_type.capitalize()
			return

		var new_econ = afford_check[1]
		var template = afford_check[2]
		template["faction_id"] = 1

		var build_res = TerritoryLogic.place_building(
			world_state, planet_view.icosphere_data, clicked_node, template
		)

		if build_res[0]:
			economy_state = new_econ
			if factions_state["factions"].has(1):
				factions_state["factions"][1]["energy"] = economy_state["energy"]
			world_state = build_res[1]
			var bld = world_state["nodes"][clicked_node].get("building")
			if bld != null:
				TechTreeLogic.apply_tech_to_building(bld, factions_state["factions"][1].get("researched_techs", []))
			world_state["nodes"] = FactionsLogic.calculate_multi_faction_territory(
				planet_view.icosphere_data, world_state["nodes"], factions_state["factions"]
			)
			planet_view.update_visuals(world_state, factions_state)
			label_status.text = "¡" + selected_building_type.capitalize() + " construida! Territorio actualizado."
			selected_building_type = ""
			_update_inspector(clicked_node)
		else:
			label_status.text = "No se puede construir aquí: " + build_res[1]
	else:
		_update_inspector(clicked_node)
		var ndata = world_state["nodes"].get(clicked_node, {})
		var bld = ndata.get("building")
		var bname = bld.get("type", "ninguno").capitalize() if bld != null else "ninguno"
		var ctrl = ndata.get("controller", 0)
		var cname = "Neutro"
		var c_str = str(ctrl)
		if c_str == "1" or c_str == "player":
			cname = factions_state.get("factions", {}).get(1, {}).get("name", "Imperio Solar")
		elif factions_state.get("factions", {}).has(ctrl):
			cname = factions_state["factions"][ctrl].get("name", "Facción #" + str(ctrl))
		label_status.text = "Nodo #" + str(clicked_node) + " | Dominio: " + cname + " | Estructura: " + bname

func _update_ui() -> void:
	if label_energy != null:
		label_energy.text = "⚡ %d E" % int(economy_state.get("energy", 0.0))
	if btn_assault != null:
		var has_energy: bool = (economy_state.get("energy", 0.0) >= 85.0)
		var on_cooldown: bool = (assault_cooldown_timer > 0.0)
		btn_assault.disabled = (not has_energy or on_cooldown)
		if on_cooldown:
			btn_assault.text = "Asalto (%.0fs)" % ceil(assault_cooldown_timer)
		else:
			btn_assault.text = "Asalto [R] (85 E)"

	if is_wave_active:
		if label_wave_timer != null:
			label_wave_timer.text = "⚔️ ¡Asalto #%d! (%d restantes)" % [current_wave, active_invaders.size()]
		if btn_wave != null:
			btn_wave.disabled = true
			btn_wave.text = "Defendiendo..."
	else:
		if label_wave_timer != null:
			label_wave_timer.text = "⏳ Asalto #%d en %ds" % [current_wave, maxi(0, int(wave_countdown))]
		if btn_wave != null:
			btn_wave.disabled = false
			btn_wave.text = "💀 Iniciar (+15 E)"

	if label_crater_status != null:
		if ai_base_node_id != -1 and factions_state.get("factions", {}).has(2):
			var enemy_base_bld = world_state["nodes"].get(ai_base_node_id, {}).get("building")
			if enemy_base_bld != null and enemy_base_bld.get("hp", 0.0) > 0.0:
				var hp_pct: int = int((enemy_base_bld["hp"] / enemy_base_bld.get("max_hp", 1500.0)) * 100.0)
				label_crater_status.text = "🏛️ Base IA: %d%% HP" % hp_pct
				label_crater_status.modulate = Color(1.0, 0.4, 0.3)
			else:
				label_crater_status.text = "🏛️ Base IA: Destruida"
				label_crater_status.modulate = Color.GREEN

	if selected_inspector_node != -1:
		_update_inspector(selected_inspector_node)

func _update_inspector(node_id: int) -> void:
	selected_inspector_node = node_id
	if inspector_title == null:
		return
	if node_id == -1 or not world_state.get("nodes", {}).has(node_id):
		if inspector_icon: inspector_icon.text = "🪐"
		if inspector_title: inspector_title.text = "Planeta Invassion"
		if inspector_owner:
			inspector_owner.text = "Haz clic en cualquier nodo para inspeccionar o construir"
			inspector_owner.modulate = Color(0.38, 0.74, 0.98)
		if inspector_hp: inspector_hp.text = "Integridad: --"
		if inspector_stats: inspector_stats.text = "Navegación: Arrastra para rotar"
		return

	var ndata: Dictionary = world_state["nodes"][node_id]
	var bld = ndata.get("building")
	var ctrl = ndata.get("controller", 0)
	var c_str = str(ctrl)
	var fname = "Territorio Neutral"
	var fcolor = Color(0.55, 0.65, 0.75)

	if c_str == "1" or c_str == "player":
		fname = factions_state.get("factions", {}).get(1, {}).get("name", "Imperio Solar") + " (Aliado)"
		fcolor = Color(factions_state.get("factions", {}).get(1, {}).get("color", "#22c55e"))
	elif factions_state.get("factions", {}).has(ctrl):
		fname = factions_state["factions"][ctrl].get("name", "Facción #" + str(ctrl)) + " (Rival)"
		fcolor = Color(factions_state["factions"][ctrl].get("color", "#a855f7"))

	if inspector_owner:
		inspector_owner.text = "Dominio: " + fname
		inspector_owner.modulate = fcolor

	if bld != null:
		var btype: String = bld.get("type", "")
		var hp: int = int(bld.get("hp", 0))
		var max_hp: int = int(bld.get("max_hp", 100))
		if inspector_hp:
			inspector_hp.text = "Integridad: %d / %d HP" % [hp, max_hp]
		match btype:
			"base":
				if inspector_icon: inspector_icon.text = "🏛️"
				if inspector_title: inspector_title.text = "PUESTO DE COMANDO"
				if inspector_stats: inspector_stats.text = "Núcleo estratégico • Generación: +5.0 E/s"
			"harvester":
				if inspector_icon: inspector_icon.text = "⚡"
				if inspector_title: inspector_title.text = "EXTRACTOR CUÁNTICO"
				var hops_prod = 1 + int(ndata.get("neighbors", []).size() / 2)
				if inspector_stats: inspector_stats.text = "Producción continua: +%d E/s" % hops_prod
			"turret":
				if inspector_icon: inspector_icon.text = "🎯"
				if inspector_title: inspector_title.text = "TORRETA DEFENSIVA"
				var r_hops = bld.get("attack_range_hops", 2)
				var cd = bld.get("cooldown", 1.0)
				if inspector_stats: inspector_stats.text = "Rango: %d saltos • Recarga: %.1fs" % [r_hops, cd]
			"wall":
				if inspector_icon: inspector_icon.text = "🛡️"
				if inspector_title: inspector_title.text = "MURO DE CONTENCIÓN"
				if inspector_stats: inspector_stats.text = "Blindaje estructural de alta absorción"
			_:
				if inspector_icon: inspector_icon.text = "🏗️"
				if inspector_title: inspector_title.text = btype.to_upper()
				if inspector_stats: inspector_stats.text = "Instalación táctica en superficie"
	else:
		if inspector_icon: inspector_icon.text = "📍"
		if inspector_title: inspector_title.text = "NODO GEODÉSICO #%d" % node_id
		if inspector_hp: inspector_hp.text = "Sector Disponible"
		if inspector_stats: inspector_stats.text = "Listo para despliegue de instalaciones"

func _show_game_over(is_victory: bool) -> void:
	if banner_game_over != null:
		banner_game_over.visible = true
	if is_victory:
		if label_game_over != null:
			label_game_over.text = "¡VICTORIA PLANETARIA TOTAL!"
			label_game_over.modulate = Color(0.2, 0.95, 0.4)
		if label_game_over_details != null:
			label_game_over_details.text = "Has dominado el planeta y neutralizado el comando de la facción hostil.\nTodas sus instalaciones han colapsado."
	else:
		if label_game_over != null:
			label_game_over.text = "¡DERROTA!"
			label_game_over.modulate = Color(0.95, 0.25, 0.25)
		if label_game_over_details != null:
			label_game_over_details.text = "Tu puesto de comando central ha sucumbido ante las fuerzas enemigas."

func spectate_game() -> void:
	if banner_game_over != null:
		banner_game_over.visible = false
	label_status.text = "🔭 Modo Libre: Puedes orbitar e inspeccionar el planeta. Pulsa [Espacio] para jugar otra partida."

func restart_game() -> void:
	# 1. Resetear colecciones de simulación
	active_invaders.clear()
	planet_view.update_invaders_visuals(active_invaders)
	current_wave = 1
	wave_countdown = 20.0
	is_wave_active = false
	invader_counter = 0
	ai_tick_timer = 0.0
	assault_cooldown_timer = 0.0
	selected_building_type = ""
	selected_inspector_node = -1

	# 2. Configuración de Facciones Planetarias (Jugador vs IA Simétrica)
	var faction_configs: Array = [
		{"name": "Imperio Solar", "race": "solarian", "is_ai": false, "team": 1, "starting_energy": 100.0},
		{"name": "Enclave Krynn", "race": "krynn", "is_ai": true, "team": 2, "starting_energy": 100.0}
	]
	factions_state = FactionsLogic.initialize_factions_game(planet_view.icosphere_data, faction_configs)
	base_node_id = factions_state["factions"][1]["base_node"]
	ai_base_node_id = factions_state["factions"][2]["base_node"]

	# 3. Inicializar lógica del mundo
	world_state = TerritoryLogic.initialize_world_state(
		planet_view.icosphere_data, base_node_id, []
	)

	# Asignar base del jugador (Facción 1) con batería defensiva
	world_state["nodes"][base_node_id]["building"]["faction_id"] = 1
	world_state["nodes"][base_node_id]["building"]["attack_range_hops"] = 1
	world_state["nodes"][base_node_id]["building"]["damage"] = 40.0
	world_state["nodes"][base_node_id]["building"]["cooldown"] = 0.8
	world_state["nodes"][base_node_id]["building"]["shoot_timer"] = 0.0
	world_state["nodes"][base_node_id]["is_base"] = true

	# Asignar base de la IA (Facción 2) con batería defensiva
	world_state["nodes"][ai_base_node_id]["building"] = {
		"type": "base",
		"hp": 1500.0,
		"max_hp": 1500.0,
		"influence_hops": RacesLogic.calculate_initial_influence_hops(factions_state["factions"][2]["race"]),
		"faction_id": 2,
		"attack_range_hops": 1,
		"damage": 40.0,
		"cooldown": 0.8,
		"shoot_timer": 0.0
	}
	world_state["nodes"][ai_base_node_id]["is_base"] = true

	# Proyección de territorio multi-facción
	world_state["nodes"] = FactionsLogic.calculate_multi_faction_territory(
		planet_view.icosphere_data, world_state["nodes"], factions_state["factions"]
	)

	economy_state = EconomyLogic.create_initial_economy(100.0, 5.0)

	if banner_game_over != null:
		banner_game_over.visible = false

	label_status.text = "🎮 ¡Nueva partida iniciada! Defiende tu base o asalta el puesto de mando enemigo."
	_update_ui()
	_update_inspector(base_node_id)
	planet_view.update_visuals(world_state, factions_state)
	focus_base()

func _update_threat_radar() -> void:
	if not radar_overlay or not camera_orbit or not camera_orbit.camera:
		return

	var cam: Camera3D = camera_orbit.camera
	var cam_pos: Vector3 = cam.global_position
	var cam_right: Vector3 = cam.global_transform.basis.x
	var cam_up: Vector3 = cam.global_transform.basis.y
	var viewport = get_viewport()
	if not viewport:
		return
	var screen_size: Vector2 = viewport.get_visible_rect().size

	var indicators: Array = ThreatRadarLogic.compute_threat_indicators(
		active_invaders,
		planet_view.icosphere_data["nodes"],
		cam_pos,
		cam_right,
		cam_up,
		planet_view.planet_radius,
		screen_size,
		65.0
	)

	while _radar_indicator_buttons.size() < indicators.size():
		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_STOP
		btn.add_theme_font_size_override("font_size", 13)
		btn.pressed.connect(func():
			if btn.has_meta("world_pos"):
				_on_radar_indicator_pressed(btn.get_meta("world_pos"), btn.get_meta("arch"), btn.get_meta("inv_id"))
		)
		radar_overlay.add_child(btn)
		_radar_indicator_buttons.append(btn)

	for i in range(_radar_indicator_buttons.size()):
		var btn: Button = _radar_indicator_buttons[i]
		if i < indicators.size():
			var ind: Dictionary = indicators[i]
			btn.visible = true
			var arch: String = ind["archetype"]
			var hops: int = ind["remaining_hops"]
			var arrow: String = ind.get("arrow", "➡")
			btn.text = arrow + " " + arch.capitalize() + " (" + str(hops) + "s)"

			var border_color: Color = Color(0.95, 0.25, 0.25)
			if arch == "scout":
				border_color = Color(1.0, 0.75, 0.1)
			elif arch == "brute":
				border_color = Color(0.85, 0.3, 0.95)

			var style = StyleBoxFlat.new()
			style.bg_color = Color(0.06, 0.08, 0.12, 0.88)
			style.border_color = border_color
			style.set_border_width_all(2)
			style.set_corner_radius_all(5)
			style.set_content_margin_all(6)
			btn.add_theme_stylebox_override("normal", style)
			btn.add_theme_stylebox_override("hover", style)
			btn.add_theme_stylebox_override("pressed", style)

			btn.size = btn.get_combined_minimum_size()
			var target_pos: Vector2 = ind["screen_pos"] - btn.size * 0.5
			target_pos.x = clampf(target_pos.x, 15.0, screen_size.x - btn.size.x - 15.0)
			target_pos.y = clampf(target_pos.y, 65.0, screen_size.y - btn.size.y - 75.0)
			btn.position = target_pos

			btn.set_meta("world_pos", ind["world_pos"])
			btn.set_meta("arch", arch)
			btn.set_meta("inv_id", ind["invader_id"])
		else:
			btn.visible = false

func _on_radar_indicator_pressed(target_pos: Vector3, archetype: String, inv_id: Variant) -> void:
	camera_orbit.focus_on_point(target_pos)
	label_status.text = "🎯 Radar: Enfocando amenaza " + archetype.capitalize() + " #" + str(inv_id) + " en el hemisferio ciego."

# --- SISTEMA DE DIPLOMACIA Y TRIBUTOS INTERACTIVO ---

func toggle_diplomacy_panel() -> void:
	panel_diplomacy.visible = not panel_diplomacy.visible
	if panel_diplomacy.visible:
		_render_diplomacy_panel()

func close_diplomacy_panel() -> void:
	panel_diplomacy.visible = false

func _render_diplomacy_panel() -> void:
	for child in factions_list_container.get_children():
		child.queue_free()

	var my_fid: int = 1
	var factions: Dictionary = factions_state.get("factions", {})
	var my_energy: float = factions.get(my_fid, {}).get("energy", 0.0)

	for fid in factions:
		if fid == my_fid:
			continue
		var fdata: Dictionary = factions[fid]
		var f_name: String = fdata.get("name", "Facción #" + str(fid))
		var f_race: String = fdata.get("race", "desconocida").capitalize()
		var f_color: String = fdata.get("color", "#38bdf8")
		var is_alive: bool = fdata.get("is_alive", true)
		var f_energy: float = fdata.get("energy", 0.0)

		var my_stance: String = FactionsLogic.get_diplomatic_stance(factions_state, my_fid, fid)
		var their_stance: String = FactionsLogic.get_diplomatic_stance(factions_state, fid, my_fid)

		var row = PanelContainer.new()
		var row_style = StyleBoxFlat.new()
		row_style.bg_color = Color(0.08, 0.1, 0.14, 0.95)
		row_style.set_border_width_all(1)
		row_style.border_color = Color(f_color)
		row_style.set_corner_radius_all(6)
		row_style.set_content_margin_all(8)
		row.add_theme_stylebox_override("panel", row_style)

		var hbox = HBoxContainer.new()
		hbox.add_theme_constants_override("separation", 12)
		row.add_child(hbox)

		# Info Label
		var label_info = Label.new()
		label_info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var alive_str = " [ACTIVA]" if is_alive else " [DERROTADA]"
		var stance_desc = "Tu postura: " + my_stance.to_upper() + " | Su postura hacia ti: " + their_stance.to_upper()
		label_info.text = f_name + " (" + f_race + ")" + alive_str + "\n" + stance_desc + " | Energía: " + str(int(f_energy)) + " E"
		label_info.add_theme_color_override("font_color", Color(f_color))
		hbox.add_child(label_info)

		if is_alive:
			# Stance buttons
			var btn_ally = Button.new()
			btn_ally.text = "🤝 Aliado"
			btn_ally.disabled = (my_stance == "ally")
			btn_ally.pressed.connect(func(): _on_change_stance_pressed(fid, "ally"))
			hbox.add_child(btn_ally)

			var btn_neutral = Button.new()
			btn_neutral.text = "⚖️ Neutral"
			btn_neutral.disabled = (my_stance == "neutral")
			btn_neutral.pressed.connect(func(): _on_change_stance_pressed(fid, "neutral"))
			hbox.add_child(btn_neutral)

			var btn_enemy = Button.new()
			btn_enemy.text = "⚔️ Hostil"
			btn_enemy.disabled = (my_stance == "enemy")
			btn_enemy.pressed.connect(func(): _on_change_stance_pressed(fid, "enemy"))
			hbox.add_child(btn_enemy)

			# Tribute buttons
			var btn_trib_25 = Button.new()
			btn_trib_25.text = "🎁 +25 E"
			btn_trib_25.disabled = (my_energy < 25.0)
			btn_trib_25.pressed.connect(func(): _on_send_tribute_pressed(fid, 25.0))
			hbox.add_child(btn_trib_25)

			var btn_trib_50 = Button.new()
			btn_trib_50.text = "🎁 +50 E"
			btn_trib_50.disabled = (my_energy < 50.0)
			btn_trib_50.pressed.connect(func(): _on_send_tribute_pressed(fid, 50.0))
			hbox.add_child(btn_trib_50)

			var btn_trib_100 = Button.new()
			btn_trib_100.text = "🎁 +100 E"
			btn_trib_100.disabled = (my_energy < 100.0)
			btn_trib_100.pressed.connect(func(): _on_send_tribute_pressed(fid, 100.0))
			hbox.add_child(btn_trib_100)

		factions_list_container.add_child(row)

func _on_change_stance_pressed(target_fid: int, stance: String) -> void:
	var res = FactionsLogic.set_diplomatic_stance(factions_state, 1, target_fid, stance)
	if res[0]:
		label_status.text = "📜 " + res[2]
		if stance == "enemy":
			var ev = {"type": "building_damaged", "attacker_faction": 1, "target_faction": target_fid}
			var react = AICommanderLogic.process_ai_diplomacy_reaction(target_fid, factions_state, ev)
			if react[0]:
				label_status.text = "📜 " + react[2]
	_render_diplomacy_panel()
	planet_view.update_visuals(world_state, factions_state)

func _on_send_tribute_pressed(target_fid: int, amount: float) -> void:
	var res = FactionsLogic.send_tribute(factions_state, 1, target_fid, amount, 0.0)
	if res[0]:
		economy_state["energy"] = factions_state["factions"][1]["energy"]
		label_status.text = "🎁 " + res[2]
		var ev = {"type": "tribute_received", "from_faction": 1, "to_faction": target_fid, "amount": amount}
		var react = AICommanderLogic.process_ai_diplomacy_reaction(target_fid, factions_state, ev)
		if react[0]:
			label_status.text = "📜 " + react[2]
	else:
		label_status.text = "❌ " + res[2]
	_render_diplomacy_panel()
	_update_ui()

# --- SISTEMA DE ÁRBOL TECNOLÓGICO Y MEJORAS ---

func toggle_tech_panel() -> void:
	if panel_tech_tree == null:
		return
	panel_tech_tree.visible = not panel_tech_tree.visible
	if panel_tech_tree.visible:
		_render_tech_panel()

func close_tech_panel() -> void:
	if panel_tech_tree != null:
		panel_tech_tree.visible = false

func _render_tech_panel() -> void:
	if tech_list_container == null:
		return
	for child in tech_list_container.get_children():
		child.queue_free()

	var catalog: Dictionary = TechTreeLogic.get_tech_catalog()
	var my_fdata: Dictionary = factions_state.get("factions", {}).get(1, {})
	var researched: Array = my_fdata.get("researched_techs", [])
	var my_energy: float = economy_state.get("energy", 0.0)

	for tech_id in catalog.keys():
		var tech: Dictionary = catalog[tech_id]
		var is_researched: bool = researched.has(tech_id)
		var cost: float = float(tech.get("cost", 0.0))

		var row = PanelContainer.new()
		var row_style = StyleBoxFlat.new()
		row_style.bg_color = Color(0.08, 0.12, 0.16, 0.95)
		row_style.set_border_width_all(1)
		row_style.border_color = Color(0.13, 0.77, 0.37) if is_researched else Color(0.2, 0.35, 0.5)
		row_style.set_corner_radius_all(6)
		row_style.set_content_margin_all(8)
		row.add_theme_stylebox_override("panel", row_style)

		var hbox = HBoxContainer.new()
		hbox.add_theme_constants_override("separation", 12)
		row.add_child(hbox)

		var label_info = Label.new()
		label_info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var status_str = " [INVESTIGADO]" if is_researched else " (Costo: %d E)" % int(cost)
		label_info.text = tech.get("icon", "🔬") + " " + tech.get("name", "") + status_str + "\n" + tech.get("description", "")
		if is_researched:
			label_info.add_theme_color_override("font_color", Color(0.2, 0.9, 0.4))
		else:
			label_info.add_theme_color_override("font_color", Color(0.85, 0.9, 0.95))
		hbox.add_child(label_info)

		var btn_res = Button.new()
		btn_res.custom_minimum_size = Vector2(130, 38)
		if is_researched:
			btn_res.text = "✓ Activo"
			btn_res.disabled = true
		else:
			btn_res.text = "🔬 Investigar"
			btn_res.disabled = (my_energy < cost)
			btn_res.pressed.connect(func(): _on_research_tech_pressed(tech_id))
		hbox.add_child(btn_res)

		tech_list_container.add_child(row)

func _on_research_tech_pressed(tech_id: String) -> void:
	if not factions_state.get("factions", {}).has(1):
		return
	factions_state["factions"][1]["energy"] = economy_state["energy"]
	var res = TechTreeLogic.research_tech(tech_id, factions_state["factions"][1], world_state["nodes"])
	if res[0]:
		factions_state["factions"][1] = res[1]
		economy_state["energy"] = float(factions_state["factions"][1]["energy"])
		label_status.text = "🔬 " + res[3]
	else:
		label_status.text = "❌ " + res[3]

	_render_tech_panel()
	_update_ui()
	planet_view.update_visuals(world_state, factions_state)

# --- SISTEMA DE GUARDADO Y CARGA (SAVE / LOAD) ---

func save_game_state() -> void:
	var wave_dict: Dictionary = {
		"current_wave": current_wave,
		"wave_countdown": wave_countdown,
		"is_wave_active": is_wave_active,
		"invader_counter": invader_counter,
		"active_invaders": active_invaders,
	}
	var serialized: Dictionary = SaveSystemLogic.serialize_game_state(world_state, economy_state, wave_dict)
	var result: Array = SaveSystemLogic.save_game_to_file(SAVE_FILE_PATH, serialized)
	if result[0]:
		label_status.text = "💾 " + result[1]
	else:
		label_status.text = "❌ " + result[1]

func load_game_state() -> void:
	var result: Array = SaveSystemLogic.load_game_from_file(SAVE_FILE_PATH)
	if not result[0]:
		label_status.text = "❌ " + result[2]
		return

	var loaded_state: Dictionary = result[1]
	world_state = loaded_state["world"]
	economy_state = loaded_state["economy"]
	var wave_data: Dictionary = loaded_state["wave"]

	current_wave = wave_data["current_wave"]
	wave_countdown = wave_data["wave_countdown"]
	is_wave_active = wave_data["is_wave_active"]
	invader_counter = wave_data["invader_counter"]
	active_invaders = wave_data["active_invaders"]
	base_node_id = world_state["base_node_id"]

	planet_view.update_visuals(world_state, factions_state)
	planet_view.update_invaders_visuals(active_invaders)

	selected_building_type = ""
	banner_game_over.visible = false
	if world_state.get("game_status") == "victory":
		_show_game_over(true)
	elif world_state.get("game_status") == "defeat":
		_show_game_over(false)

	_update_ui()
	_update_threat_radar()
	label_status.text = "📂 Partida cargada exitosamente [F7]."
