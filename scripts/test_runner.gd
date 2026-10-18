extends SceneTree

func _init() -> void:
	print("==========================================")
	print(" Verificando Lógica en Godot 4.3 (Headless)")
	print("==========================================")

	# 1. Probar Icosphere
	var iso = IcosphereLogic.create_icosphere(2, 5.0)
	assert(iso["node_count"] == 162, "Debe tener 162 nodos")
	print("✓ Icosfera generada con éxito: 162 nodos.")

	# 2. Probar Territorio
	var world = TerritoryLogic.initialize_world_state(iso, 0, [85])
	assert(world["nodes"][0]["controller"] == "player")
	assert(world["nodes"][85]["controller"] == "corrupt")
	print("✓ Territorio y corrupción inicializados correctamente.")

	# 3. Probar Economía
	var econ = EconomyLogic.create_initial_economy(100.0, 5.0)
	var afford = EconomyLogic.can_afford(econ, "turret")
	assert(afford[0] == true)
	print("✓ Catálogo económico y saldo verificados.")

	# 4. Probar Combate
	var lane = CombatLogic.generate_invasion_lane(iso, 85, 0)
	assert(lane.size() > 2)
	assert(lane[0] == 85 and lane[-1] == 0)
	print("✓ Carril geodésico de invasión verificado: " + str(lane.size()) + " nodos de longitud.")

	print("==========================================")
	print(" TODOS LOS MÓDULOS DE GDSCRIPT FUNCIONAN.")
	print("==========================================")
	quit(0)
