"""
Módulo de cálculo de territorio, zonas de influencia y corrupción.
Estilo procedimental puro: funciones independientes y diccionarios planos.
"""

from logic.icosphere import get_nodes_within_hops


def initialize_world_state(icosphere, base_node_id, crater_node_ids):
    """
    Inicializa el estado del planeta con los nodos, la base del jugador y los cráteres.
    Retorna un diccionario plano del estado del juego.
    """
    nodes_state = {}
    for node_id in icosphere["nodes"]:
        nodes_state[node_id] = {
            "controller": "neutral",
            "building": None,
            "is_crater": node_id in crater_node_ids,
            "is_base": node_id == base_node_id,
        }

    world = {
        "nodes": nodes_state,
        "base_node_id": base_node_id,
        "crater_node_ids": list(crater_node_ids),
        "craters": {
            cid: {"hp": 100.0, "max_hp": 100.0, "is_sealed": False}
            for cid in crater_node_ids
        },
        "game_status": "in_progress",  # "in_progress", "victory", "defeat"
    }

    # Asignar la base inicial
    world["nodes"][base_node_id]["building"] = {
        "type": "base",
        "hp": 500.0,
        "max_hp": 500.0,
        "influence_hops": 2,
    }

    # Recalcular territorio inicial
    return update_territory(world, icosphere)


def update_territory(world_state, icosphere):
    """
    Recalcula la influencia territorial de cada nodo:
      1. Los cráteres proyectan zona corrupta (radio 1 salto).
      2. Las instalaciones del jugador proyectan territorio (según su influence_hops).
      3. La corrupción enemiga tiene prioridad de bloqueo: un nodo corrupto no puede ser dominado por el jugador.
    Retorna una copia actualizada del world_state.
    """
    new_state = {
        "nodes": {nid: dict(data) for nid, data in world_state["nodes"].items()},
        "base_node_id": world_state["base_node_id"],
        "crater_node_ids": list(world_state.get("crater_node_ids", [])),
        "craters": {
            cid: dict(cdata)
            for cid, cdata in world_state.get("craters", {}).items()
        },
        "game_status": world_state["game_status"],
    }

    # 1. Calcular nodos corruptos por cráteres (1 salto)
    corrupt_nodes = set()
    for crater_id in new_state["crater_node_ids"]:
        if crater_id in icosphere["nodes"]:
            in_range = get_nodes_within_hops(icosphere["nodes"], crater_id, max_hops=1)
            corrupt_nodes.update(in_range)

    # 2. Calcular nodos alcanzados por edificios del jugador
    player_nodes = set()
    for nid, ndata in new_state["nodes"].items():
        building = ndata.get("building")
        if building and building["hp"] > 0:
            b_fid = building.get("faction_id", 1)
            if str(b_fid) in ("1", "player"):
                hops = building.get("influence_hops", 0)
                if hops > 0:
                    controlled = get_nodes_within_hops(icosphere["nodes"], nid, max_hops=hops)
                    player_nodes.update(controlled)

    # 3. Asignar controladores
    for nid, ndata in new_state["nodes"].items():
        if nid in corrupt_nodes:
            ndata["controller"] = "corrupt"
        elif nid in player_nodes:
            ndata["controller"] = "player"
        else:
            ndata["controller"] = "neutral"

    # 4. Evaluar estado de victoria / derrota
    new_state["game_status"] = evaluate_victory_defeat(new_state, icosphere)
    return new_state


def can_build_on_node(world_state, node_id, building_type="turret"):
    """
    Valida si un jugador puede construir en un nodo específico:
      - Debe estar controlado por el jugador ('player').
      - No debe tener un edificio existente.
      - No debe ser un cráter ni estar corrupto.
    Retorna (True, "") o (False, "motivo").
    """
    if node_id not in world_state["nodes"]:
        return False, "El nodo no existe"

    node = world_state["nodes"][node_id]

    if node["is_crater"] or str(node["controller"]) == "corrupt":
        return False, "Zona corrupta o cráter: no se puede construir"

    ctrl_str = str(node["controller"])
    if ctrl_str != "player" and ctrl_str != "1":
        return False, "El nodo no está dentro del territorio dominado"

    if node["building"] is not None:
        return False, "Ya existe una instalación en este nodo"

    return True, ""


def place_building(world_state, icosphere, node_id, building_data):
    """
    Coloca un edificio en el nodo si la validación es exitosa.
    Retorna (True, new_world_state) o (False, error_msg).
    """
    can_build, reason = can_build_on_node(world_state, node_id, building_data.get("type"))
    if not can_build:
        return False, reason

    new_state = {
        "nodes": {nid: dict(data) for nid, data in world_state["nodes"].items()},
        "base_node_id": world_state["base_node_id"],
        "crater_node_ids": list(world_state["crater_node_ids"]),
        "craters": {
            cid: dict(cdata)
            for cid, cdata in world_state.get("craters", {}).items()
        },
        "game_status": world_state["game_status"],
    }

    new_state["nodes"][node_id]["building"] = dict(building_data)
    updated_world = update_territory(new_state, icosphere)
    return True, updated_world


def remove_building(world_state, icosphere, node_id):
    """
    Elimina un edificio (por destrucción enemiga o demolición) y recalcula el territorio.
    """
    if node_id not in world_state["nodes"]:
        return world_state

    new_state = {
        "nodes": {nid: dict(data) for nid, data in world_state["nodes"].items()},
        "base_node_id": world_state["base_node_id"],
        "crater_node_ids": list(world_state.get("crater_node_ids", [])),
        "craters": {
            cid: dict(cdata)
            for cid, cdata in world_state.get("craters", {}).items()
        },
        "game_status": world_state["game_status"],
    }

    new_state["nodes"][node_id]["building"] = None
    return update_territory(new_state, icosphere)


def evaluate_victory_defeat(world_state, icosphere):
    """
    Evalúa las condiciones de fin de partida:
      - Derrota: Si la base está destruida o la salud es <= 0.
      - Victoria Ofensiva: Si todos los cráteres alienígenas han sido purificados y sellados.
      - Victoria Territorial: Si todos los nodos no corruptos están bajo control del jugador.
      - En progreso: En cualquier otro caso.
    """
    base_id = world_state["base_node_id"]
    base_node = world_state["nodes"].get(base_id)

    if not base_node or not base_node.get("building") or base_node["building"]["hp"] <= 0:
        return "defeat"

    # Victoria Ofensiva: todos los cráteres originales fueron sellados
    craters_dict = world_state.get("craters", {})
    if len(world_state.get("crater_node_ids", [])) == 0 and len(craters_dict) > 0:
        return "victory"

    # Contar nodos libres de cráteres
    non_corrupt_nodes = [
        nid for nid, ndata in world_state["nodes"].items()
        if not ndata["is_crater"]
    ]

    player_count = sum(
        1 for nid in non_corrupt_nodes
        if world_state["nodes"][nid]["controller"] == "player"
    )

    if player_count == len(non_corrupt_nodes) and len(non_corrupt_nodes) > 0:
        return "victory"

    return "in_progress"
