"""
Módulo del Comandante de Inteligencia Artificial Simétrica estilo Age of Empires.
Estilo procedimental puro: funciones independientes y estructuras de datos planas sin clases.
"""

from logic.icosphere import find_shortest_path
from logic.races import (
    get_race_data,
    calculate_building_cost,
    apply_building_combat_stats,
)
from logic.factions import (
    get_enemy_factions,
    are_allies,
    set_diplomatic_stance,
    get_diplomatic_stance,
)
from logic.economy import BUILDING_CATALOG


def analyze_faction_territory(faction_id, world_nodes, icosphere, factions_data):
    """
    Analiza y clasifica los nodos controlados por una facción en:
    - Nodos interiores (seguros, rodeados de aliados o territorio propio).
    - Nodos de frontera (contiguos a terreno neutral).
    - Nodos de contacto enemigo (contiguos a nodos dominados por enemigos).
    """
    nodes_graph = icosphere["nodes"]
    factions = factions_data.get("factions", factions_data)

    controlled_nodes = [
        nid for nid, ndata in world_nodes.items()
        if ndata.get("controller") == faction_id
    ]

    interior_empty = []
    frontier_empty = []
    enemy_adjacent_empty = []

    harvester_count = 0
    turret_count = 0
    wall_count = 0

    for nid in controlled_nodes:
        ndata = world_nodes[nid]
        bld = ndata.get("building")

        if bld:
            btype = bld.get("type")
            if btype == "harvester":
                harvester_count += 1
            elif btype == "turret":
                turret_count += 1
            elif btype == "wall":
                wall_count += 1
            continue

        # El nodo está vacío: clasificar su nivel de exposición
        neighbors = nodes_graph.get(nid, {}).get("neighbors", [])
        has_enemy_neighbor = False
        has_neutral_neighbor = False

        for n_id in neighbors:
            n_ctrl = world_nodes.get(n_id, {}).get("controller", 0)
            if n_ctrl == 0:
                has_neutral_neighbor = True
            elif n_ctrl != faction_id:
                if not are_allies(faction_id, n_ctrl, factions_data):
                    has_enemy_neighbor = True

        if has_enemy_neighbor:
            enemy_adjacent_empty.append(nid)
        elif has_neutral_neighbor:
            frontier_empty.append(nid)
        else:
            interior_empty.append(nid)

    return {
        "controlled_nodes": controlled_nodes,
        "controlled_count": len(controlled_nodes),
        "interior_empty": interior_empty,
        "frontier_empty": frontier_empty,
        "enemy_adjacent_empty": enemy_adjacent_empty,
        "harvester_count": harvester_count,
        "turret_count": turret_count,
        "wall_count": wall_count,
    }


def find_closest_enemy_base(faction_id, world_nodes, factions_data, icosphere):
    """
    Encuentra la base enemiga más cercana por distancia de ruta geodésica (BFS).
    Retorna (target_faction_id, target_base_node_id, shortest_path).
    """
    factions = factions_data.get("factions", factions_data)
    if faction_id not in factions:
        return None, None, []

    my_base = factions[faction_id].get("base_node", 0)
    enemy_ids = get_enemy_factions(faction_id, factions_data)

    best_enemy_fid = None
    best_target_base = None
    shortest_path_found = []
    min_hops = 999999

    for e_fid in enemy_ids:
        e_base = factions[e_fid].get("base_node")
        if e_base is None or e_base not in icosphere["nodes"]:
            continue

        # Comprobar que la base enemiga siga viva
        base_node_data = world_nodes.get(e_base, {})
        base_bld = base_node_data.get("building")
        if not base_bld or base_bld.get("hp", 0) <= 0:
            continue

        path = find_shortest_path(icosphere["nodes"], my_base, e_base)
        if path and len(path) < min_hops:
            min_hops = len(path)
            best_enemy_fid = e_fid
            best_target_base = e_base
            shortest_path_found = path

    return best_enemy_fid, best_target_base, shortest_path_found


def decide_ai_construction(faction_id, factions_data, world_nodes, icosphere):
    """
    Evalúa la economía y posición territorial para decidir qué edificio construir:
    1. Si hay menos de 2 extractores y hay nodos interiores seguros -> Extractor (Economía).
    2. Si hay nodos adyacentes a enemigos -> Torretas o Muros (Defensa perimetral).
    3. Si hay nodos de frontera neutral y presupuesto suficiente -> Torreta o Extractor de avance.
    Retorna (True, target_node, building_type, building_template, cost) o (False, None, None, None, 0.0).
    """
    factions = factions_data.get("factions", factions_data)
    fdata = factions.get(faction_id)
    if not fdata or not fdata.get("is_alive", True):
        return False, None, None, None, 0.0

    energy = fdata.get("energy", 0.0)
    race_id = fdata.get("race", "solarian")

    analysis = analyze_faction_territory(faction_id, world_nodes, icosphere, factions_data)

    # 1. Prioridad: Economía básica (primeros 2 extractores)
    harv_cost = calculate_building_cost(BUILDING_CATALOG["harvester"]["cost"], "harvester", race_id)
    if analysis["harvester_count"] < 2 and analysis["interior_empty"] and energy >= harv_cost:
        target_node = analysis["interior_empty"][0]
        template = dict(BUILDING_CATALOG["harvester"])
        template["faction_id"] = faction_id
        template = apply_building_combat_stats(template, race_id)
        return True, target_node, "harvester", template, harv_cost

    # 2. Prioridad: Defensa inmediata si hay contacto directo con el enemigo
    turret_cost = calculate_building_cost(BUILDING_CATALOG["turret"]["cost"], "turret", race_id)
    wall_cost = calculate_building_cost(BUILDING_CATALOG["wall"]["cost"], "wall", race_id)

    if analysis["enemy_adjacent_empty"]:
        target_node = analysis["enemy_adjacent_empty"][0]
        if energy >= turret_cost and analysis["turret_count"] <= analysis["wall_count"]:
            template = dict(BUILDING_CATALOG["turret"])
            template["faction_id"] = faction_id
            template = apply_building_combat_stats(template, race_id)
            return True, target_node, "turret", template, turret_cost
        elif energy >= wall_cost:
            template = dict(BUILDING_CATALOG["wall"])
            template["faction_id"] = faction_id
            template = apply_building_combat_stats(template, race_id)
            return True, target_node, "wall", template, wall_cost

    # 3. Expansión perimetral moderada
    if analysis["frontier_empty"] and energy >= (turret_cost + 40.0):
        target_node = analysis["frontier_empty"][0]
        template = dict(BUILDING_CATALOG["turret"])
        template["faction_id"] = faction_id
        template = apply_building_combat_stats(template, race_id)
        return True, target_node, "turret", template, turret_cost

    return False, None, None, None, 0.0


def launch_faction_assault(faction_id, factions_data, world_nodes, icosphere, assault_cost=60.0):
    """
    Despliega un escuadrón militar geodésico hacia la base enemiga más cercana.
    Utilizable simétricamente por el jugador (Facción 1) o la IA.
    Retorna (True, squad, cost, enemy_base, msg) o (False, [], 0.0, None, err_msg).
    """
    factions = factions_data.get("factions", factions_data)
    fdata = factions.get(faction_id)
    if not fdata or not fdata.get("is_alive", True):
        return False, [], 0.0, None, "La facción no está activa"

    energy = float(fdata.get("energy", 0.0))
    if energy < assault_cost:
        return False, [], 0.0, None, f"Energía insuficiente ({energy:.0f} E, se requieren {assault_cost:.0f} E)"

    enemy_fid, enemy_base, path = find_closest_enemy_base(faction_id, world_nodes, factions_data, icosphere)
    if not enemy_fid or not path or len(path) <= 1:
        return False, [], 0.0, None, "No se encontró base enemiga alcanzable"

    race_data = get_race_data(fdata.get("race", "solarian"))
    unique = race_data.get("unique_unit", {})

    squad = []
    base_node = fdata.get("base_node", 0)

    # Unidad líder de raza
    squad.append({
        "id": f"{faction_id}_{base_node}_lead_{int(energy)}",
        "faction_id": faction_id,
        "target_faction": enemy_fid,
        "archetype": unique.get("type", "vanguard"),
        "hp": float(unique.get("hp", 100.0)),
        "max_hp": float(unique.get("max_hp", 100.0)),
        "speed": float(unique.get("speed", 0.5)),
        "damage": float(unique.get("damage", 20.0)),
        "progress": 0.0,
        "current_node": path[0],
        "path": list(path),
        "path_index": 0,
        "attack_cooldown": 1.0,
        "attack_timer": 0.0,
        "state": "marching",
        "color": race_data.get("color", "#22c55e"),
    })

    # Escoltas
    for idx in range(1, 3):
        squad.append({
            "id": f"{faction_id}_{base_node}_escort_{idx}_{int(energy)}",
            "faction_id": faction_id,
            "target_faction": enemy_fid,
            "archetype": "scout",
            "hp": 40.0,
            "max_hp": 40.0,
            "speed": 0.8,
            "damage": 10.0,
            "progress": 0.0,
            "current_node": path[0],
            "path": list(path),
            "path_index": 0,
            "attack_cooldown": 1.0,
            "attack_timer": 0.0,
            "state": "marching",
            "spawn_delay": float(idx * 0.8),
            "color": race_data.get("color", "#22c55e"),
        })

    from logic.tech_tree import apply_tech_to_squad
    squad = apply_tech_to_squad(squad, fdata.get("researched_techs", []))

    fdata["energy"] = energy - assault_cost
    msg = f"¡Escuadrón militar de {fdata['name']} desplegado ({len(squad)} unidades) hacia la base enemiga!"
    return True, squad, assault_cost, enemy_base, msg


def decide_ai_assault(faction_id, factions_data, world_nodes, icosphere, assault_threshold=110.0):
    """
    Decide si la IA lanza una escuadra de invasión geodésica contra la base enemiga más cercana.
    Retorna (True, list_of_units, energy_cost, target_base_node) o (False, [], 0.0, None).
    """
    factions = factions_data.get("factions", factions_data)
    fdata = factions.get(faction_id)
    if not fdata or not fdata.get("is_alive", True):
        return False, [], 0.0, None

    energy = float(fdata.get("energy", 0.0))

    # Umbral de emergencia: si la base de la facción está sufriendo daños, moviliza defensa desde 65 E
    effective_threshold = assault_threshold
    my_base = fdata.get("base_node", 0)
    base_bld = world_nodes.get(my_base, {}).get("building")
    if base_bld and base_bld.get("hp", 500.0) < base_bld.get("max_hp", 500.0):
        effective_threshold = min(assault_threshold, 65.0)

    if energy < effective_threshold:
        return False, [], 0.0, None

    success, squad, cost, enemy_base, msg = launch_faction_assault(
        faction_id, factions_data, world_nodes, icosphere, assault_cost=65.0
    )
    if success:
        fdata["energy"] += cost
        return True, squad, cost, enemy_base
    return False, [], 0.0, None


def process_ai_diplomacy_reaction(faction_id, factions_state, event):
    """
    Reacciona a eventos diplomáticos de forma procedimental:
    - Si recibe tributo >= 50 E de un enemigo, acepta tregua ('neutral').
    - Si recibe tributo >= 100 E, acepta alianza ('ally').
    - Si un aliado ataca un edificio propio, declara la guerra inmediata ('enemy').
    Retorna (did_react, updated_factions_state, reaction_message).
    """
    etype = event.get("type")

    if etype == "tribute_received" and event.get("to_faction") == faction_id:
        from_fid = event.get("from_faction")
        amount = event.get("amount", 0.0)
        curr_stance = get_diplomatic_stance(factions_state, faction_id, from_fid)

        if amount >= 100.0 and curr_stance != "ally":
            set_diplomatic_stance(factions_state, faction_id, from_fid, "ally")
            return True, factions_state, f"La Facción #{faction_id} ha aceptado un pacto de alianza tras recibir {amount:.1f} E de tributo."
        elif amount >= 50.0 and curr_stance == "enemy":
            set_diplomatic_stance(factions_state, faction_id, from_fid, "neutral")
            return True, factions_state, f"La Facción #{faction_id} ha concedido una tregua neutral tras recibir {amount:.1f} E de tributo."

    elif etype == "building_damaged" and event.get("target_faction") == faction_id:
        attacker_fid = event.get("attacker_faction")
        if attacker_fid and attacker_fid != faction_id:
            curr_stance = get_diplomatic_stance(factions_state, faction_id, attacker_fid)
            if curr_stance in ("ally", "neutral"):
                set_diplomatic_stance(factions_state, faction_id, attacker_fid, "enemy")
                return True, factions_state, f"¡Alerta! La Facción #{faction_id} ha declarado la guerra a la Facción #{attacker_fid} en represalia a un ataque sorpresa."

    return False, factions_state, ""


def run_ai_tick(faction_id, factions_state, world_nodes, icosphere, delta_time, events=None):
    """
    Ejecuta un ciclo completo de decisión para la IA de una facción:
    1. Procesar eventos diplomáticos entrantes.
    2. Construir instalaciones prioritarias según presupuesto y territorio.
    3. Desplegar ofensivas militares si se alcanza el umbral de energía.
    Retorna (updated_factions_state, updated_world_nodes, new_invaders_spawned, list_of_actions).
    """
    factions = factions_state.get("factions", factions_state)
    fdata = factions.get(faction_id)
    if not fdata or not fdata.get("is_alive", True) or not fdata.get("is_ai", True):
        return factions_state, world_nodes, [], []

    actions_taken = []
    new_spawns = []

    # 1. Diplomacia reactiva
    if events:
        for ev in events:
            reacted, factions_state, msg = process_ai_diplomacy_reaction(faction_id, factions_state, ev)
            if reacted:
                actions_taken.append({"type": "diplomacy_change", "message": msg})

    # 2. Construcción
    can_build, b_node, b_type, b_template, b_cost = decide_ai_construction(
        faction_id, factions_state, world_nodes, icosphere
    )
    if can_build and b_node is not None:
        fdata["energy"] -= b_cost
        world_nodes[b_node]["building"] = b_template
        actions_taken.append({
            "type": "building_constructed",
            "node_id": b_node,
            "building_type": b_type,
            "cost": b_cost,
        })

    # 3. Asalto militar
    can_assault, squad, assault_cost, target_base = decide_ai_assault(
        faction_id, factions_state, world_nodes, icosphere
    )
    if can_assault:
        fdata["energy"] -= assault_cost
        new_spawns.extend(squad)
        actions_taken.append({
            "type": "military_assault_launched",
            "target_base": target_base,
            "units_count": len(squad),
            "cost": assault_cost,
        })

    # 4. Investigación tecnológica
    did_research, tech_id, tech_cost, tech_msg = decide_ai_tech_research(
        faction_id, factions_state, world_nodes
    )
    if did_research:
        actions_taken.append({
            "type": "tech_researched",
            "tech_id": tech_id,
            "cost": tech_cost,
            "message": tech_msg,
        })

    return factions_state, world_nodes, new_spawns, actions_taken


def decide_ai_tech_research(faction_id, factions_data, world_nodes, energy_threshold=110.0):
    """
    Evalúa si la IA investiga una mejora tecnológica si cuenta con excedente de energía.
    Retorna (did_research, tech_id, cost, message).
    """
    factions = factions_data.get("factions", factions_data)
    fdata = factions.get(faction_id)
    if not fdata or not fdata.get("is_alive", True):
        return False, None, 0.0, None

    if float(fdata.get("energy", 0.0)) < energy_threshold:
        return False, None, 0.0, None

    from logic.tech_tree import can_research_tech, research_tech
    researched = fdata.get("researched_techs", [])

    for tid in ["composite_armor", "laser_optics", "rapid_fire", "quantum_harvesters", "military_training"]:
        if tid not in researched:
            can_r, _ = can_research_tech(tid, fdata)
            if can_r:
                success, updated_fdata, cost, msg = research_tech(tid, fdata, world_nodes)
                if success:
                    factions[faction_id] = updated_fdata
                    return True, tid, cost, msg

    return False, None, 0.0, None
