"""
Módulo de economía y recursos del juego.
Estilo procedimental puro: funciones independientes y datos planos.
"""

from logic.icosphere import get_nodes_within_hops

BUILDING_CATALOG = {
    "harvester": {
        "cost": 50.0,
        "hp": 100.0,
        "max_hp": 100.0,
        "influence_hops": 1,
        "rate_per_node": 1.5,
    },
    "turret": {
        "cost": 75.0,
        "hp": 280.0,
        "max_hp": 280.0,
        "influence_hops": 1,
        "attack_range_hops": 2,
        "damage": 35.0,
        "cooldown": 0.8,
    },
    "wall": {
        "cost": 25.0,
        "hp": 300.0,
        "max_hp": 300.0,
        "influence_hops": 0,
    },
    "purifier": {
        "cost": 120.0,
        "hp": 200.0,
        "max_hp": 200.0,
        "influence_hops": 1,
        "purify_range_hops": 4,
        "purify_rate": 15.0,
    },
    "base": {
        "cost": 300.0,
        "hp": 1500.0,
        "max_hp": 1500.0,
        "influence_hops": 2,
        "attack_range_hops": 1,
        "damage": 40.0,
        "cooldown": 0.8,
    },
}

INITIAL_ECONOMY = {
    "energy": 100.0,
    "base_income_rate": 5.0,  # Energía base por segundo producida por la base
}


def create_initial_economy(starting_energy=100.0, base_income=5.0):
    return {
        "energy": float(starting_energy),
        "base_income_rate": float(base_income),
    }


def calculate_tick_income(economy_state, world_state, icosphere, delta_seconds):
    """
    Calcula los recursos generados en un intervalo delta_seconds:
      - Flujo base del Puesto de Comando (si está viva).
      - Flujo de cada Extractor/Recolector según los nodos del jugador dentro de su radio.
    """
    if delta_seconds <= 0.0:
        return 0.0

    total_income = 0.0

    # 1. Ingreso de la Base
    base_id = world_state["base_node_id"]
    base_node = world_state["nodes"].get(base_id)
    if base_node and base_node.get("building") and base_node["building"]["hp"] > 0:
        total_income += economy_state.get("base_income_rate", 5.0) * delta_seconds

    # 2. Ingreso de los Extractores (Harvesters)
    for nid, ndata in world_state["nodes"].items():
        building = ndata.get("building")
        if building and building.get("type") == "harvester" and building["hp"] > 0:
            hops = building.get("influence_hops", 1)
            controlled = get_nodes_within_hops(icosphere["nodes"], nid, max_hops=hops)
            # Solo cuentan nodos bajo control efectivo del jugador
            valid_player_nodes = sum(
                1 for c_id in controlled
                if world_state["nodes"][c_id]["controller"] == "player"
            )
            rate = building.get("rate_per_node", 1.5)
            total_income += valid_player_nodes * rate * delta_seconds

    return round(total_income, 4)


def apply_income(economy_state, income_amount):
    """
    Retorna un nuevo estado de economía con los recursos incrementados.
    """
    new_econ = dict(economy_state)
    new_econ["energy"] = round(new_econ.get("energy", 0.0) + max(0.0, income_amount), 4)
    return new_econ


def can_afford(economy_state, building_type):
    """
    Verifica si hay suficiente energía para comprar el edificio del catálogo.
    Retorna (True, cost) o (False, cost).
    """
    if building_type not in BUILDING_CATALOG:
        return False, 0.0

    cost = BUILDING_CATALOG[building_type]["cost"]
    return economy_state.get("energy", 0.0) >= cost, cost


def purchase_building(economy_state, building_type):
    """
    Deduce el costo del edificio y retorna (True, new_economy_state, building_template).
    Si no alcanza, retorna (False, economy_state, None).
    """
    affordable, cost = can_afford(economy_state, building_type)
    if not affordable:
        return False, economy_state, None

    new_econ = dict(economy_state)
    new_econ["energy"] = round(new_econ["energy"] - cost, 4)
    building_template = dict(BUILDING_CATALOG[building_type])
    building_template["type"] = building_type

    return True, new_econ, building_template
