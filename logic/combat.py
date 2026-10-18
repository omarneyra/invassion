"""
Módulo de combate, invasión geodésica y simulación de daño.
Estilo procedimental puro: funciones independientes y estructuras de datos planas.
"""

from logic.icosphere import find_shortest_path, get_nodes_within_hops
from logic.territory import update_territory, remove_building

INVADER_ARCHETYPES = {
    "crawler": {
        "type": "crawler",
        "hp": 70.0,
        "max_hp": 70.0,
        "speed": 0.45,
        "damage": 15.0,
        "scale": 1.0,
        "color": "red",
    },
    "scout": {
        "type": "scout",
        "hp": 35.0,
        "max_hp": 35.0,
        "speed": 0.85,
        "damage": 8.0,
        "scale": 0.75,
        "color": "orange",
    },
    "brute": {
        "type": "brute",
        "hp": 220.0,
        "max_hp": 220.0,
        "speed": 0.22,
        "damage": 35.0,
        "scale": 1.4,
        "color": "purple",
    },
}


def generate_invasion_lane(icosphere, crater_id, base_id):
    """
    Genera el carril geodésico principal desde el cráter hasta la base del jugador.
    """
    return find_shortest_path(icosphere["nodes"], crater_id, base_id)


def generate_multiple_invasion_lanes(icosphere, crater_id, base_id, count=2):
    """
    Genera 'count' carriles geodésicos divergentes para ataque en pinza/flanqueo.
    - Carril 1: Ruta directa geodésica más corta.
    - Carril 2: Ruta divergente que rodea el hemisferio opuesto eligiendo el vecino
      del cráter más alejado angularmente de la ruta 1 y excluyendo nodos intermedios de la ruta 1.
    """
    primary_lane = generate_invasion_lane(icosphere, crater_id, base_id)
    if count <= 1 or not primary_lane or len(primary_lane) <= 3:
        return [primary_lane]

    lanes = [primary_lane]
    nodes = icosphere["nodes"]
    crater_pos = nodes[crater_id]["pos"]
    prim_step = primary_lane[1]
    prim_pos = nodes[prim_step]["pos"]

    # Vector de salida del carril 1
    v_prim = (
        prim_pos[0] - crater_pos[0],
        prim_pos[1] - crater_pos[1],
        prim_pos[2] - crater_pos[2],
    )

    # Buscar el vecino del cráter más diametralmente opuesto a prim_step
    best_flank_neighbor = None
    min_dot = 1e9

    for neighbor_id in nodes[crater_id]["neighbors"]:
        if neighbor_id == prim_step:
            continue
        npos = nodes[neighbor_id]["pos"]
        v_cand = (
            npos[0] - crater_pos[0],
            npos[1] - crater_pos[1],
            npos[2] - crater_pos[2],
        )
        dot = v_cand[0] * v_prim[0] + v_cand[1] * v_prim[1] + v_cand[2] * v_prim[2]
        if dot < min_dot:
            min_dot = dot
            best_flank_neighbor = neighbor_id

    if best_flank_neighbor is not None:
        # Excluir nodos intermedios de la ruta 1 para obligar a rodear por el otro flanco
        cutoff = max(2, len(primary_lane) - 2)
        excluded = set(primary_lane[1:cutoff])

        flank_path = find_shortest_path(nodes, best_flank_neighbor, base_id, excluded_nodes=excluded)
        if flank_path:
            lane_2 = [crater_id] + flank_path
            lanes.append(lane_2)
        else:
            alt_path = find_shortest_path(nodes, best_flank_neighbor, base_id)
            if alt_path:
                lanes.append([crater_id] + alt_path)

    return lanes


def create_wave_composition(wave_number: int) -> list:
    """
    Genera la composición de enemigos para la oleada 'wave_number'.
    Escalamiento táctico:
      - Oleada 1: 2 Crawlers
      - Oleada 2: 2 Crawlers + 1 Scout
      - Oleada 3: 3 Crawlers + 2 Scouts + 1 Brute
      - Oleadas 4+: Composición reforzada progresiva
    """
    w = max(1, wave_number)
    composition = []

    if w == 1:
        composition = ["crawler", "crawler"]
    elif w == 2:
        composition = ["crawler", "scout", "crawler"]
    elif w == 3:
        composition = ["crawler", "scout", "crawler", "brute"]
    else:
        # A partir de la oleada 4: escalado dinámico
        crawlers_count = 2 + (w - 3)
        scouts_count = 1 + (w // 2)
        brutes_count = w // 3

        for _ in range(crawlers_count):
            composition.append("crawler")
        for _ in range(scouts_count):
            composition.append("scout")
        for _ in range(brutes_count):
            composition.append("brute")

    return composition


def spawn_invader(invader_id, path, archetype="crawler", custom_delay=0.0):
    """
    Crea un invasor en el carril a partir de una plantilla de arquetipo.
    """
    if not path:
        return None

    template = INVADER_ARCHETYPES.get(archetype, INVADER_ARCHETYPES["crawler"])

    return {
        "id": invader_id,
        "archetype": template["type"],
        "hp": float(template["hp"]),
        "max_hp": float(template["max_hp"]),
        "speed": float(template["speed"]),
        "progress": 0.0,
        "current_node": path[0],
        "path": list(path),
        "path_index": 0,
        "damage": float(template["damage"]),
        "attack_cooldown": 1.0,
        "attack_timer": 0.0,
        "state": "spawning" if custom_delay > 0.0 else "marching",
        "spawn_delay": float(custom_delay),
        "scale": template["scale"],
        "color": template["color"],
    }


def find_turret_target(turret_node_id, turret_data, active_invaders, icosphere, factions_data=None):
    """
    Busca el invasor vivo más avanzado dentro del alcance de la torreta.
    """
    range_hops = turret_data.get("attack_range_hops", 2)
    in_range_nodes = get_nodes_within_hops(icosphere["nodes"], turret_node_id, range_hops)
    turret_fid = turret_data.get("faction_id", 1)

    candidates = []
    for inv in active_invaders:
        if inv["state"] not in ("dead", "spawning") and inv["current_node"] in in_range_nodes:
            inv_fid = inv.get("faction_id", 0)
            if factions_data and inv_fid > 0:
                from logic.factions import are_enemies
                if not are_enemies(turret_fid, inv_fid, factions_data):
                    continue
            candidates.append(inv)

    if not candidates:
        return None

    # Prioridad táctica RTS (Focus Fire):
    # 1. Atacantes directos de la torreta (current_node == turret_node_id y state == "attacking")
    # 2. Menor HP restante (focus fire para eliminar DPS entrante rápidamente)
    # 3. Mayor avance hacia la base (path_index)
    def _target_priority(inv):
        is_direct = 0 if (inv.get("current_node") == turret_node_id and inv.get("state") == "attacking") else 1
        hp = float(inv.get("hp", 999.0))
        p_index = -int(inv.get("path_index", 0))
        return (is_direct, hp, p_index)

    candidates.sort(key=_target_priority)
    return candidates[0]



def find_turret_building_target(turret_node_id, turret_data, world_nodes, icosphere, factions_data=None):
    """
    Busca un edificio o base de facción enemiga dentro del alcance de la torreta.
    Prioriza la base enemiga si está en rango, luego torretas, luego otros edificios.
    """
    if not factions_data:
        return None

    range_hops = turret_data.get("attack_range_hops", 2)
    in_range_nodes = get_nodes_within_hops(icosphere["nodes"], turret_node_id, range_hops)
    turret_fid = turret_data.get("faction_id", 1)

    from logic.factions import are_enemies
    candidates = []
    for nid in in_range_nodes:
        if nid == turret_node_id:
            continue
        ndata = world_nodes.get(nid)
        if not ndata or not ndata.get("building"):
            continue
        bld = ndata["building"]
        if bld.get("hp", 0.0) <= 0.0:
            continue
        bld_fid = bld.get("faction_id", 0)
        if bld_fid > 0 and are_enemies(turret_fid, bld_fid, factions_data):
            priority = 0 if bld.get("type") == "base" else (1 if bld.get("type") == "turret" else 2)
            candidates.append((priority, bld["hp"], nid))

    if not candidates:
        return None

    candidates.sort()
    return candidates[0][2]



def update_combat_tick(world_state, invaders, icosphere, delta_time, factions_data=None):
    """
    Ejecuta un paso de simulación de combate:
      1. Actualiza tiempos de spawn de invasores en cola.
      2. Las torretas del jugador disparan a invasores o bombardean edificios hostiles en rango.
      3. Los invasores avanzan por su carril o atacan edificios que bloqueen su paso.
      4. Se resuelven daños y destrucciones.
    Retorna (updated_world, updated_invaders, events).
    """
    if delta_time <= 0.0:
        return world_state, invaders, []

    events = []
    updated_invaders = [dict(inv) for inv in invaders if inv["state"] != "dead"]
    new_world = {
        "nodes": {nid: dict(data) for nid, data in world_state["nodes"].items()},
        "base_node_id": world_state["base_node_id"],
        "crater_node_ids": list(world_state["crater_node_ids"]),
        "game_status": world_state["game_status"],
    }

    if factions_data and isinstance(factions_data, dict) and "factions" in factions_data:
        from logic.factions import calculate_multi_faction_territory
        new_world["nodes"] = calculate_multi_faction_territory(icosphere, new_world["nodes"], factions_data["factions"])
    else:
        new_world = update_territory(new_world, icosphere)

    # 1. ACTUALIZAR TIEMPOS DE COLA DE SPAWN
    for inv in updated_invaders:
        if inv["state"] == "spawning":
            inv["spawn_delay"] -= delta_time
            if inv["spawn_delay"] <= 0.0:
                inv["state"] = "marching"
                events.append({
                    "type": "invader_emerged",
                    "invader_id": inv["id"],
                    "archetype": inv["archetype"],
                    "node_id": inv["current_node"],
                })

    # 2. DISPARO DEFENSIVO (Torretas y Guarnición de Base)
    buildings_destroyed = []
    for nid, ndata in new_world["nodes"].items():
        building = ndata.get("building")
        if not building or building.get("type") not in ("turret", "base") or building["hp"] <= 0:
            continue

        cooldown = building.get("cooldown", 0.8 if building.get("type") == "turret" else 1.0)
        timer = building.get("shoot_timer", 0.0) + delta_time

        target = find_turret_target(nid, building, updated_invaders, icosphere, factions_data)
        if target and timer >= cooldown:
            damage = building.get("damage", 35.0 if building.get("type") == "turret" else 20.0)
            target["hp"] -= damage
            timer = 0.0
            events.append({
                "type": "turret_shot",
                "turret_node": nid,
                "target_id": target["id"],
                "damage": damage,
            })
            if target["hp"] <= 0:
                target["state"] = "dead"
                events.append({
                    "type": "invader_killed",
                    "invader_id": target["id"],
                    "archetype": target["archetype"],
                })
        elif not target and factions_data and timer >= cooldown and building.get("type") == "turret":
            target_bld_node = find_turret_building_target(nid, building, new_world["nodes"], icosphere, factions_data)
            if target_bld_node is not None:
                damage = building.get("damage", 35.0)
                target_bld = new_world["nodes"][target_bld_node]["building"]
                target_bld["hp"] -= damage
                timer = 0.0
                events.append({
                    "type": "turret_shot_building",
                    "turret_node": nid,
                    "target_node": target_bld_node,
                    "target_bld_type": target_bld.get("type", "building"),
                    "damage": damage,
                    "target_faction": target_bld.get("faction_id", 0),
                    "remaining_hp": target_bld["hp"],
                })
                if target_bld["hp"] <= 0:
                    buildings_destroyed.append(target_bld_node)

        building["shoot_timer"] = timer

    alive_invaders = [inv for inv in updated_invaders if inv["state"] != "dead"]

    # 3. MOVIMIENTO Y ATAQUE DE INVASORES
    for inv in alive_invaders:
        if inv["state"] == "spawning":
            continue

        curr_node = inv["current_node"]
        node_data = new_world["nodes"].get(curr_node)

        # Si el nodo actual tiene un edificio de facción enemiga (o sin facción / cráter), atacar
        if node_data and node_data.get("building") and node_data["building"]["hp"] > 0:
            target_bld = node_data["building"]
            bld_fid = target_bld.get("faction_id", 1)
            inv_fid = inv.get("faction_id", 0)

            should_attack = True
            if factions_data and inv_fid > 0:
                from logic.factions import are_enemies
                should_attack = are_enemies(inv_fid, bld_fid, factions_data)

            if should_attack:
                inv["state"] = "attacking"
                inv["attack_timer"] += delta_time
                if inv["attack_timer"] >= inv["attack_cooldown"]:
                    inv["attack_timer"] = 0.0
                    target_bld["hp"] -= inv["damage"]
                    events.append({
                        "type": "building_damaged",
                        "node_id": curr_node,
                        "damage": inv["damage"],
                        "remaining_hp": target_bld["hp"],
                        "target_faction": bld_fid,
                        "attacker_faction": inv_fid,
                    })
                    if target_bld["hp"] <= 0:
                        buildings_destroyed.append(curr_node)
                        inv["state"] = "marching"
                continue

        # Si no hay obstáculo, marchar
        inv["state"] = "marching"
        inv["progress"] += inv["speed"] * delta_time

        if inv["progress"] >= 1.0:
            inv["progress"] = 0.0
            if inv["path_index"] + 1 < len(inv["path"]):
                inv["path_index"] += 1
                inv["current_node"] = inv["path"][inv["path_index"]]
                events.append({
                    "type": "invader_moved",
                    "invader_id": inv["id"],
                    "new_node": inv["current_node"],
                })

    # 4. Remover edificios destruidos y recalcular territorio
    for b_node in buildings_destroyed:
        new_world["nodes"][b_node]["building"] = None
        events.append({"type": "building_destroyed", "node_id": b_node})

    if buildings_destroyed:
        if factions_data and isinstance(factions_data, dict) and "factions" in factions_data:
            from logic.factions import calculate_multi_faction_territory
            new_world["nodes"] = calculate_multi_faction_territory(icosphere, new_world["nodes"], factions_data["factions"])
        else:
            new_world = update_territory(new_world, icosphere)

    return new_world, alive_invaders, events
