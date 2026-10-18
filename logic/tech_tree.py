"""
Módulo del Árbol Tecnológico y Mejoras de Base (tech_tree).
Estilo procedimental puro: funciones estáticas y diccionarios planos.
Sin clases ni OOP.
"""

TECH_CATALOG = {
    "laser_optics": {
        "id": "laser_optics",
        "name": "Óptica Láser de Precisión",
        "cost": 80.0,
        "icon": "🔭",
        "description": "Incrementa el rango de ataque de todas las torretas en +1 salto geodésico.",
    },
    "rapid_fire": {
        "id": "rapid_fire",
        "name": "Sobrecarga de Condensadores",
        "cost": 75.0,
        "icon": "⚡",
        "description": "Reduce el tiempo de recarga de las torretas en un 30% (mayor cadencia).",
    },
    "composite_armor": {
        "id": "composite_armor",
        "name": "Blindaje de Nanocompuesto",
        "cost": 60.0,
        "icon": "🛡️",
        "description": "Aumenta la integridad estructural máxima de muros y edificios en +40%.",
    },
    "quantum_harvesters": {
        "id": "quantum_harvesters",
        "name": "Extracción Cuántica",
        "cost": 90.0,
        "icon": "💎",
        "description": "Aumenta la producción de energía de todos los extractores en +50%.",
    },
    "military_training": {
        "id": "military_training",
        "name": "Doctrina Militar Avanzada",
        "cost": 100.0,
        "icon": "⚔️",
        "description": "Las tropas de asalto marchan 25% más rápido y causan 30% más de daño.",
    },
}


def get_tech_catalog() -> dict:
    """
    Retorna el catálogo plano de tecnologías investigables.
    """
    return {k: dict(v) for k, v in TECH_CATALOG.items()}


def can_research_tech(tech_id: str, faction_data: dict) -> tuple:
    """
    Evalúa si la facción cumple los requisitos económicos y de estado para investigar tech_id.
    Retorna (can_research: bool, reason: str).
    """
    if tech_id not in TECH_CATALOG:
        return False, f"La tecnología '{tech_id}' no existe en el catálogo."

    researched = faction_data.get("researched_techs", [])
    if tech_id in researched:
        return False, "Esta tecnología ya ha sido investigada."

    cost = float(TECH_CATALOG[tech_id]["cost"])
    current_energy = float(faction_data.get("energy", 0.0))
    if current_energy < cost:
        return False, f"Energía insuficiente ({current_energy:.0f} E, requiere {cost:.0f} E)."

    return True, "Listo para investigar."


def research_tech(tech_id: str, faction_data: dict, world_nodes: dict = None) -> tuple:
    """
    Ejecuta la investigación de tech_id para la facción:
    - Deduce el costo de energía.
    - Añade tech_id a 'researched_techs'.
    - Aplica mejoras inmediatas a edificios existentes si se proporciona world_nodes.
    Retorna (success: bool, updated_faction_data: dict, cost: float, message: str).
    """
    can_r, reason = can_research_tech(tech_id, faction_data)
    if not can_r:
        return False, faction_data, 0.0, reason

    tech_info = TECH_CATALOG[tech_id]
    cost = float(tech_info["cost"])

    updated_fdata = dict(faction_data)
    updated_fdata["energy"] = float(updated_fdata.get("energy", 0.0)) - cost
    
    researched = list(updated_fdata.get("researched_techs", []))
    researched.append(tech_id)
    updated_fdata["researched_techs"] = researched

    # Si se pasan los nodos del mundo, actualizar edificios existentes de la facción
    if world_nodes:
        fid = updated_fdata.get("id", 1)
        for nid, ndata in world_nodes.items():
            bld = ndata.get("building")
            if bld and bld.get("hp", 0.0) > 0.0 and bld.get("faction_id", 1) == fid:
                apply_tech_to_building(bld, [tech_id])

    msg = f"¡Tecnología '{tech_info['name']}' investigada con éxito (-{cost:.0f} E)!"
    return True, updated_fdata, cost, msg


def apply_tech_to_building(building: dict, researched_techs: list) -> dict:
    """
    Aplica modificadores de tecnologías activas a una estructura.
    Modifica el diccionario in-place y lo retorna.
    """
    btype = building.get("type", "")

    if "laser_optics" in researched_techs and btype == "turret":
        building["attack_range_hops"] = building.get("attack_range_hops", 2) + 1

    if "rapid_fire" in researched_techs and btype == "turret":
        building["cooldown"] = building.get("cooldown", 1.0) * 0.70

    if "composite_armor" in researched_techs and btype in ["wall", "base", "harvester", "turret"]:
        current_max = float(building.get("max_hp", 100.0))
        new_max = current_max * 1.40
        diff = new_max - current_max
        building["max_hp"] = new_max
        building["hp"] = float(building.get("hp", current_max)) + diff

    return building


def apply_tech_to_squad(squad: list, researched_techs: list) -> list:
    """
    Aplica modificadores tecnológicos a un escuadrón militar antes de marchar.
    """
    if "military_training" in researched_techs:
        for unit in squad:
            unit["speed"] = float(unit.get("speed", 0.5)) * 1.25
            unit["damage"] = float(unit.get("damage", 10.0)) * 1.30
    return squad


def get_tech_economic_multiplier(researched_techs: list) -> float:
    """
    Retorna el factor multiplicador para la producción de energía según las tecnologías investigadas.
    """
    mult = 1.0
    if "quantum_harvesters" in researched_techs:
        mult += 0.50
    return mult
