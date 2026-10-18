"""
Módulo de Gestión de Múltiples Facciones, Diplomacia y Alianzas estilo Age of Empires.
Estilo procedimental puro: funciones independientes y datos planos sin clases ni herencia.
"""

from logic.icosphere import find_antipodal_node, get_spherical_distance, get_nodes_within_hops
from logic.races import (
    get_race_data,
    calculate_base_passive_income,
    calculate_harvester_income,
    calculate_initial_influence_hops,
)


def find_distributed_base_nodes(nodes_dict, count=2):
    """
    Selecciona 'count' nodos distribuidos sobre la icosfera maximizando la distancia esférica.
    - Para 2 facciones: polo inicial (nodo 0) y su polo antipodal opuesto exacto.
    - Para 3 o más: muestreo greedy de punto más lejano (farthest-point sampling).
    """
    if count <= 1:
        return [0]

    all_ids = sorted(list(nodes_dict.keys()))
    if count == 2:
        base_0 = all_ids[0]
        base_1 = find_antipodal_node(nodes_dict, base_0)
        return [base_0, base_1]

    # Greedy farthest point sampling
    chosen = [all_ids[0]]
    for _ in range(1, count):
        best_node = None
        max_min_dist = -1.0

        for candidate in all_ids:
            if candidate in chosen:
                continue

            # Calcular la distancia mínima a cualquiera de los nodos ya seleccionados
            cand_pos = nodes_dict[candidate]["pos"]
            min_dist_to_chosen = min(
                get_spherical_distance(cand_pos, nodes_dict[c]["pos"]) for c in chosen
            )

            if min_dist_to_chosen > max_min_dist:
                max_min_dist = min_dist_to_chosen
                best_node = candidate

        if best_node is not None:
            chosen.append(best_node)

    return chosen


def create_faction(faction_id, name, race_id, is_ai, team_id, base_node_id, starting_energy=100.0):
    """
    Crea la estructura plana de una facción en el planeta.
    """
    race_data = get_race_data(race_id)
    base_income = calculate_base_passive_income(5.0, race_id)

    return {
        "id": int(faction_id),
        "name": str(name),
        "race": str(race_id),
        "is_ai": bool(is_ai),
        "team": int(team_id),
        "base_node": int(base_node_id),
        "energy": float(starting_energy),
        "base_income_rate": float(base_income),
        "is_alive": True,
        "color": race_data.get("color", "#22c55e"),
    }


def initialize_factions_game(icosphere, faction_configs):
    """
    Inicializa una partida con N facciones a partir de una lista de configuraciones:
    [
        {"name": "Solarian Empire", "race": "solarian", "is_ai": False, "team": 1},
        {"name": "Krynn Hive", "race": "krynn", "is_ai": True, "team": 2},
        ...
    ]
    Asigna automáticamente bases distribuidas equidistantemente si no se especifican.
    """
    nodes = icosphere["nodes"]
    num_factions = len(faction_configs)
    base_nodes = find_distributed_base_nodes(nodes, num_factions)

    factions_dict = {}
    for i, cfg in enumerate(faction_configs):
        fid = i + 1
        b_node = cfg.get("base_node", base_nodes[i])
        f_data = create_faction(
            faction_id=fid,
            name=cfg.get("name", f"Facción #{fid}"),
            race_id=cfg.get("race", "solarian"),
            is_ai=cfg.get("is_ai", True),
            team_id=cfg.get("team", fid),  # Por defecto cada una es su propio equipo (FFA)
            base_node_id=b_node,
            starting_energy=cfg.get("starting_energy", 100.0),
        )
        factions_dict[fid] = f_data

    # Inicializar matriz diplomática dinámica: matrix[f_from][f_to] -> "ally" | "neutral" | "enemy"
    diplomacy_matrix = {}
    for f1 in factions_dict:
        diplomacy_matrix[f1] = {}
        for f2 in factions_dict:
            if f1 == f2 or factions_dict[f1]["team"] == factions_dict[f2]["team"]:
                diplomacy_matrix[f1][f2] = "ally"
            else:
                diplomacy_matrix[f1][f2] = "enemy"

    teams = {f["team"] for f in factions_dict.values()}
    game_mode = "ffa" if len(teams) == len(factions_dict) else "teams"

    return {
        "factions": factions_dict,
        "diplomacy_matrix": diplomacy_matrix,
        "game_mode": game_mode,
        "status": "in_progress",
        "winning_team": None,
    }


def _get_factions_and_matrix(factions_data):
    """Auxiliar para aceptar indistintamente un factions_state o un factions_dict directo."""
    if isinstance(factions_data, dict) and "factions" in factions_data:
        return factions_data["factions"], factions_data.get("diplomacy_matrix")
    return factions_data, None


def get_diplomatic_stance(factions_data, from_faction_id, to_faction_id):
    """
    Retorna la postura diplomática unilateral ('ally', 'neutral', 'enemy') de from_id hacia to_id.
    """
    if from_faction_id == to_faction_id:
        return "ally"

    factions, matrix = _get_factions_and_matrix(factions_data)
    if matrix and from_faction_id in matrix and to_faction_id in matrix[from_faction_id]:
        return matrix[from_faction_id][to_faction_id]

    if from_faction_id in factions and to_faction_id in factions:
        return "ally" if factions[from_faction_id]["team"] == factions[to_faction_id]["team"] else "enemy"

    return "enemy"


def set_diplomatic_stance(factions_state, from_faction_id, to_faction_id, new_stance):
    """
    Modifica la postura diplomática unilateral de una facción hacia otra en tiempo real.
    'new_stance' debe ser 'ally', 'neutral' o 'enemy'.
    """
    if new_stance not in ("ally", "neutral", "enemy"):
        return False, factions_state, f"Postura '{new_stance}' inválida (debe ser 'ally', 'neutral' o 'enemy')"

    if from_faction_id == to_faction_id:
        return False, factions_state, "Una facción no puede alterar su postura hacia sí misma"

    factions, matrix = _get_factions_and_matrix(factions_state)
    if from_faction_id not in factions or to_faction_id not in factions:
        return False, factions_state, "Identificador de facción no encontrado"

    if matrix is None:
        matrix = {}
        for f1 in factions:
            matrix[f1] = {
                f2: ("ally" if factions[f1]["team"] == factions[f2]["team"] else "enemy")
                for f2 in factions
            }
        factions_state["diplomacy_matrix"] = matrix

    if from_faction_id not in matrix:
        matrix[from_faction_id] = {}

    old_stance = matrix[from_faction_id].get(to_faction_id, "enemy")
    matrix[from_faction_id][to_faction_id] = new_stance

    from_name = factions[from_faction_id]["name"]
    to_name = factions[to_faction_id]["name"]
    msg = f"{from_name} ha cambiado su postura hacia {to_name} de '{old_stance}' a '{new_stance}'"
    return True, factions_state, msg


def are_allies(faction_a_id, faction_b_id, factions_data):
    """
    Retorna True si dos facciones son aliadas.
    En diplomacia dinámica, requiere que ambas mantengan postura 'ally'.
    """
    if faction_a_id == faction_b_id:
        return True

    factions, matrix = _get_factions_and_matrix(factions_data)
    if faction_a_id not in factions or faction_b_id not in factions:
        return False

    if matrix:
        stance_a = matrix.get(faction_a_id, {}).get(faction_b_id, "enemy")
        stance_b = matrix.get(faction_b_id, {}).get(faction_a_id, "enemy")
        return stance_a == "ally" and stance_b == "ally"

    return factions[faction_a_id]["team"] == factions[faction_b_id]["team"]


def are_enemies(faction_a_id, faction_b_id, factions_data):
    """
    Retorna True si dos facciones están en guerra / son hostiles.
    En diplomacia dinámica, si cualquiera de las dos fija la postura como 'enemy', hay hostilidad.
    """
    if faction_a_id == 0 or faction_b_id == 0 or faction_a_id == faction_b_id:
        return False

    factions, matrix = _get_factions_and_matrix(factions_data)
    if faction_a_id not in factions or faction_b_id not in factions:
        return False

    if matrix:
        stance_a = matrix.get(faction_a_id, {}).get(faction_b_id, "enemy")
        stance_b = matrix.get(faction_b_id, {}).get(faction_a_id, "enemy")
        return stance_a == "enemy" or stance_b == "enemy"

    return factions[faction_a_id]["team"] != factions[faction_b_id]["team"]


def is_hostile(from_faction_id, to_faction_id, factions_data):
    """
    Determina si from_faction considera a to_faction como objetivo hostil legítimo ('enemy').
    """
    return get_diplomatic_stance(factions_data, from_faction_id, to_faction_id) == "enemy"


def are_in_active_war(faction_a_id, faction_b_id, factions_data):
    """
    Retorna True si existe conflicto bélico activo entre ambas facciones.
    """
    return are_enemies(faction_a_id, faction_b_id, factions_data)


def send_tribute(factions_state, from_faction_id, to_faction_id, amount, fee_rate=0.0):
    """
    Transfiere energía entre facciones (Tributo estilo Age of Empires).
    Aplica una tasa de arancel/comisión por transporte (fee_rate, ej: 0.10 = 10%).
    Retorna (éxito, factions_state_actualizado, mensaje).
    """
    if from_faction_id == to_faction_id:
        return False, factions_state, "No es posible enviarse tributos a uno mismo"

    amount_val = float(amount)
    if amount_val <= 0.0:
        return False, factions_state, "El monto del tributo debe ser mayor a 0"

    factions, _ = _get_factions_and_matrix(factions_state)
    if from_faction_id not in factions or to_faction_id not in factions:
        return False, factions_state, "Facción remitente o destinataria no existe"

    sender = factions[from_faction_id]
    receiver = factions[to_faction_id]

    if not sender.get("is_alive", True):
        return False, factions_state, f"La facción remitente '{sender['name']}' ha sido eliminada"
    if not receiver.get("is_alive", True):
        return False, factions_state, f"La facción destinataria '{receiver['name']}' ha sido eliminada"

    if sender["energy"] < amount_val:
        return False, factions_state, f"Energía insuficiente ({sender['energy']:.1f} E disponible, se requieren {amount_val:.1f} E)"

    sender["energy"] -= amount_val
    fee = max(0.0, min(1.0, float(fee_rate)))
    net_received = amount_val * (1.0 - fee)
    receiver["energy"] += net_received

    msg = f"Tributo exitoso: {sender['name']} envió {amount_val:.1f} E a {receiver['name']} (Neto recibido: {net_received:.1f} E)"
    return True, factions_state, msg


def get_enemy_factions(faction_id, factions_data):
    """
    Retorna la lista de IDs de facciones enemigas vivas.
    """
    factions, _ = _get_factions_and_matrix(factions_data)
    enemies = []
    for fid, fdata in factions.items():
        if isinstance(fdata, dict) and fdata.get("is_alive", True) and are_enemies(faction_id, fid, factions_data):
            enemies.append(fid)
    return enemies


def get_allied_factions(faction_id, factions_data, include_self=True):
    """
    Retorna la lista de IDs de facciones aliadas vivas.
    """
    factions, _ = _get_factions_and_matrix(factions_data)
    allies = []
    for fid, fdata in factions.items():
        if isinstance(fdata, dict) and fdata.get("is_alive", True) and are_allies(faction_id, fid, factions_data):
            if include_self or fid != faction_id:
                allies.append(fid)
    return allies


def calculate_multi_faction_territory(icosphere, world_nodes, factions_dict):
    """
    Calcula la proyección territorial simétrica de todas las facciones sobre el planeta.
    - Cada edificio vivo de una facción proyecta influencia territorial (hops).
    - La base proyecta influencia según su raza (Aethelian = 3, otras = 2).
    - En caso de frontera contigua entre enemigos, el nodo se disputa o asigna al edificio más cercano.
    Retorna una copia de world_nodes con 'controller' actualizado (ID de facción o 0 = neutral).
    """
    nodes = icosphere["nodes"]
    updated_nodes = {nid: dict(ndata) for nid, ndata in world_nodes.items()}

    # Mapear qué nodos están influenciados por cada facción y a qué distancia de saltos
    # faction_node_hops[fid][node_id] = min_hops
    faction_reach = {fid: {} for fid in factions_dict if factions_dict[fid]["is_alive"]}

    for nid, ndata in updated_nodes.items():
        bld = ndata.get("building")
        if not bld or bld.get("hp", 0) <= 0:
            continue

        b_fid = bld.get("faction_id", 0)
        if b_fid not in faction_reach:
            continue

        hops = bld.get("influence_hops", 1)
        if bld.get("type") == "base":
            race_id = factions_dict[b_fid].get("race", "terran_protocore")
            hops = calculate_initial_influence_hops(race_id)

        in_range = get_nodes_within_hops(nodes, nid, max_hops=hops)
        for target_nid in in_range:
            # Calcular distancia aproximada en saltos al edificio
            curr_hops = faction_reach[b_fid].get(target_nid, 999)
            if hops < curr_hops:
                faction_reach[b_fid][target_nid] = hops

    # Asignar controladores
    for nid, ndata in updated_nodes.items():
        claiming_factions = [fid for fid in faction_reach if nid in faction_reach[fid]]

        if not claiming_factions:
            ndata["controller"] = 0  # Neutral
        elif len(claiming_factions) == 1:
            ndata["controller"] = claiming_factions[0]
        else:
            # Si todas las facciones que reclaman son aliadas entre sí, otorgar al primero
            first_fid = claiming_factions[0]
            all_friendly = all(are_allies(first_fid, other_fid, factions_dict) for other_fid in claiming_factions)
            if all_friendly:
                ndata["controller"] = first_fid
            else:
                # Frontera disputada entre enemigos: el que tenga menor distancia o edificio propio
                building_owner = ndata.get("building", {}).get("faction_id", 0) if ndata.get("building") else 0
                if building_owner != 0:
                    ndata["controller"] = building_owner
                else:
                    # Empate en disputa neutral
                    ndata["controller"] = 0

    return updated_nodes


def update_multi_faction_economy(factions_dict, world_nodes, icosphere, delta_seconds):
    """
    Actualiza la energía de cada facción en el tick según:
    - Ingreso pasivo de Base (afectado por raza).
    - Extractores que posea la facción y cantidad de nodos controlados en su radio.
    - Bonos de equipo de aliados (ej. Solarian +10% base pasiva compartida).
    """
    if delta_seconds <= 0.0:
        return factions_dict

    updated = {fid: dict(fdata) for fid, fdata in factions_dict.items()}

    for fid, fdata in updated.items():
        if not fdata["is_alive"]:
            continue

        income_this_tick = 0.0

        # 1. Ingreso Base
        base_id = fdata["base_node"]
        base_node = world_nodes.get(base_id)
        if base_node and base_node.get("building") and base_node["building"].get("hp", 0) > 0:
            income_this_tick += fdata.get("base_income_rate", 5.0)

            # Verificar si algún aliado vivo tiene bono de equipo 'passive_income_bonus' (ej. Solarian)
            allies = get_allied_factions(fid, updated, include_self=False)
            for ally_id in allies:
                ally_race = get_race_data(updated[ally_id]["race"])
                t_bonus = ally_race.get("team_bonus", {})
                if t_bonus.get("type") == "passive_income_bonus":
                    income_this_tick += fdata.get("base_income_rate", 5.0) * t_bonus.get("value", 0.10)

        # 2. Extractores de la facción
        for nid, ndata in world_nodes.items():
            bld = ndata.get("building")
            if bld and bld.get("faction_id") == fid and bld.get("type") == "harvester" and bld.get("hp", 0) > 0:
                inf_hops = bld.get("influence_hops", 1)
                surrounding = get_nodes_within_hops(icosphere["nodes"], nid, max_hops=inf_hops)
                # Contar nodos controlados por esta facción
                controlled_count = sum(1 for s_id in surrounding if world_nodes.get(s_id, {}).get("controller") == fid)
                rate_per_node = bld.get("rate_per_node", 1.5)
                harv_income = calculate_harvester_income(rate_per_node, controlled_count, fdata["race"])
                from logic.tech_tree import get_tech_economic_multiplier
                harv_income *= get_tech_economic_multiplier(fdata.get("researched_techs", []))
                income_this_tick += harv_income

        fdata["energy"] += income_this_tick * delta_seconds

    return updated


def evaluate_factions_victory_defeat(factions_data, world_nodes, player_faction_id=1):
    """
    Evalúa el estado de la partida:
    - Una facción muere si su Base cae a 0 HP.
    - Derrota: El jugador (o todo su equipo/alianza) ha sido eliminado.
    - Victoria: No quedan facciones vivas que sean hostiles/enemigas hacia el jugador.
    """
    factions, matrix = _get_factions_and_matrix(factions_data)
    updated_factions = {fid: dict(fdata) for fid, fdata in factions.items()}

    # Actualizar estado is_alive y colapsar edificios de facción derrotada
    for fid, fdata in updated_factions.items():
        base_id = fdata["base_node"]
        base_node = world_nodes.get(base_id)
        if not base_node or not base_node.get("building") or base_node["building"].get("hp", 0) <= 0:
            if fdata.get("is_alive", True):
                fdata["is_alive"] = False
                for nid, ndata in world_nodes.items():
                    b = ndata.get("building")
                    if b and b.get("faction_id") == fid:
                        ndata["building"] = None

    player_alive = updated_factions.get(player_faction_id, {}).get("is_alive", False)
    player_team = updated_factions.get(player_faction_id, {}).get("team", None)

    # Si hay matriz dinámica:
    if matrix:
        if not player_alive:
            return "defeat", None, updated_factions

        # Buscar si queda algún enemigo vivo hacia el jugador o viceversa
        has_living_enemies = False
        for fid, fdata in updated_factions.items():
            if fid != player_faction_id and fdata["is_alive"]:
                if are_enemies(player_faction_id, fid, factions_data):
                    has_living_enemies = True
                    break

        if not has_living_enemies:
            return "victory", player_team, updated_factions

        return "in_progress", None, updated_factions

    # Modo clásico por equipos fijos
    player_team_alive = any(
        fdata["is_alive"] for fdata in updated_factions.values() if fdata["team"] == player_team
    )
    if not player_team_alive:
        return "defeat", None, updated_factions

    enemy_teams_alive = {
        fdata["team"] for fdata in updated_factions.values() if fdata["is_alive"] and fdata["team"] != player_team
    }

    if len(enemy_teams_alive) == 0:
        return "victory", player_team, updated_factions

    return "in_progress", None, updated_factions

