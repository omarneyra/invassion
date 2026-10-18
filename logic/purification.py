"""
Módulo de purificación y neutralización ofensiva de cráteres alienígenas.
Estilo procedimental puro: funciones independientes y estructuras de datos planas.
"""

from logic.icosphere import get_nodes_within_hops
from logic.territory import update_territory

PURIFIER_SPECS = {
    "type": "purifier",
    "cost": 120.0,
    "hp": 200.0,
    "max_hp": 200.0,
    "influence_hops": 1,
    "purify_range_hops": 4,  # Alcance geodésico para alcanzar el cráter a través de la zona corrupta
    "purify_rate": 15.0,  # Puntos de purificación por segundo
}


def can_purify_crater(purifier_node_id, crater_node_id, icosphere, max_hops=4) -> bool:
    """
    Verifica si un cráter está dentro del alcance angular/geodésico del purificador.
    """
    if purifier_node_id not in icosphere["nodes"] or crater_node_id not in icosphere["nodes"]:
        return False
    in_range = get_nodes_within_hops(icosphere["nodes"], purifier_node_id, max_hops)
    return crater_node_id in in_range


def initialize_craters_data(crater_node_ids, default_hp=100.0):
    """
    Crea el diccionario de seguimiento de corrupción y salud de los cráteres.
    """
    return {
        cid: {
            "hp": float(default_hp),
            "max_hp": float(default_hp),
            "is_sealed": False,
        }
        for cid in crater_node_ids
    }


def update_purification_tick(world_state, icosphere, delta: float):
    """
    Simula un paso de tiempo de descontaminación de cráteres.
    Retorna (nuevo_world_state, eventos).
    """
    new_state = {
        "nodes": {nid: dict(data) for nid, data in world_state["nodes"].items()},
        "base_node_id": world_state["base_node_id"],
        "crater_node_ids": list(world_state.get("crater_node_ids", [])),
        "craters": {
            cid: dict(cdata)
            for cid, cdata in world_state.get("craters", {}).items()
        },
        "game_status": world_state.get("game_status", "in_progress"),
    }

    # Asegurar que existan datos de cráteres
    if not new_state["craters"] and new_state["crater_node_ids"]:
        new_state["craters"] = initialize_craters_data(new_state["crater_node_ids"])

    events = []
    sealed_craters = []

    # 1. Identificar purificadores activos del jugador
    purifiers = []
    for nid, ndata in new_state["nodes"].items():
        bld = ndata.get("building")
        if bld and bld.get("type") == "purifier" and bld.get("hp", 0.0) > 0:
            purifiers.append({
                "node_id": nid,
                "range_hops": bld.get("purify_range_hops", 2),
                "rate": bld.get("purify_rate", 15.0),
            })

    # 2. Canalizar purificación hacia cráteres en rango
    for cid in list(new_state["crater_node_ids"]):
        cdata = new_state["craters"].get(cid)
        if not cdata or cdata.get("is_sealed", False):
            continue

        total_rate = 0.0
        active_purifier_nodes = []

        for p in purifiers:
            if can_purify_crater(p["node_id"], cid, icosphere, p["range_hops"]):
                total_rate += p["rate"]
                active_purifier_nodes.append(p["node_id"])
                events.append({
                    "type": "purification_beam",
                    "purifier_node": p["node_id"],
                    "crater_node": cid,
                })

        if total_rate > 0.0:
            cdata["hp"] = max(0.0, cdata["hp"] - total_rate * delta)
            events.append({
                "type": "crater_purifying",
                "crater_node": cid,
                "hp": cdata["hp"],
                "max_hp": cdata["max_hp"],
                "purifiers": active_purifier_nodes,
            })

            # 3. ¿Cráter completamente descontaminado y sellado?
            if cdata["hp"] <= 0.0:
                cdata["is_sealed"] = True
                sealed_craters.append(cid)
                events.append({
                    "type": "crater_sealed",
                    "crater_node": cid,
                })

    # 4. Procesar cráteres sellados y actualizar territorio
    if sealed_craters:
        for scid in sealed_craters:
            if scid in new_state["crater_node_ids"]:
                new_state["crater_node_ids"].remove(scid)
            if scid in new_state["nodes"]:
                new_state["nodes"][scid]["is_crater"] = False

        # El colapso del cráter libera la zona corrupta
        new_state = update_territory(new_state, icosphere)

        # Si todos los cráteres están neutralizados -> Victoria ofensiva inmediata
        if len(new_state["crater_node_ids"]) == 0:
            new_state["game_status"] = "victory"
            events.append({
                "type": "all_craters_sealed",
                "message": "¡Todos los cráteres alienígenas han sido purificados!",
            })

    return new_state, events
