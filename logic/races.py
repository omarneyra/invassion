"""
Módulo de Catálogo de Razas y Modificadores Planetarios estilo Age of Empires.
Estilo procedimental puro: funciones independientes y datos planos sin clases ni herencia.
"""

RACES_CATALOG = {
    "solarian": {
        "id": "solarian",
        "name": "Solarian Hegemony",
        "category": "industrial",
        "color": "#22c55e",  # Verde militar
        "description": "Humanos industriales especializados en macro-economía, asedio e ingeniería balística pesada.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.25,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 0.80,  # 20% más rápido
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.25,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.0,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "vanguard",
            "name": "Vanguard Mech",
            "hp": 110.0,
            "max_hp": 110.0,
            "speed": 0.50,
            "damage": 20.0,
            "trait": "Infantería mecanizada pesada con blindaje reforzado.",
        },
        "squad_doctrine": {
            "name": "Armored Spearhead",
            "units": [
                {"archetype": "vanguard", "name": "Vanguard Mech", "hp": 110.0, "max_hp": 110.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.2},
                {"archetype": "marine", "name": "Infantry Marine", "hp": 45.0, "max_hp": 45.0, "speed": 0.70, "damage": 10.0, "role": "light", "spawn_delay": 0.3, "scale": 0.8},
                {"archetype": "marine", "name": "Infantry Marine", "hp": 45.0, "max_hp": 45.0, "speed": 0.70, "damage": 10.0, "role": "light", "spawn_delay": 0.6, "scale": 0.8},
            ],
        },
        "team_bonus": {
            "type": "passive_income_bonus",
            "description": "Aliados reciben +10% de ingreso pasivo base.",
            "value": 0.10,
        },
    },
    "krynn": {
        "id": "krynn",
        "name": "Krynn Swarm",
        "category": "biological",
        "color": "#a855f7",  # Púrpura biológico
        "description": "Enjambre insectoide de rápida reproducción, estructuras de bajo coste y alta regeneración.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 0.80,  # 20% de descuento
            "wall_cost_mult": 0.80,
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.25,  # 25% más veloces
            "unit_hp_regen": 1.5,     # 1.5 HP/s
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "ravager",
            "name": "Krynn Ravager",
            "hp": 100.0,
            "max_hp": 100.0,
            "speed": 0.80,
            "damage": 18.0,
            "trait": "Bestia insectoide acorazada de vanguardia.",
        },
        "squad_doctrine": {
            "name": "Brood Swarm",
            "units": [
                {"archetype": "ravager", "name": "Krynn Ravager", "hp": 100.0, "max_hp": 100.0, "speed": 0.80, "damage": 18.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.1},
                {"archetype": "broodling", "name": "Broodling", "hp": 55.0, "max_hp": 55.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.2, "scale": 0.7},
                {"archetype": "broodling", "name": "Broodling", "hp": 55.0, "max_hp": 55.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.4, "scale": 0.7},
                {"archetype": "broodling", "name": "Broodling", "hp": 55.0, "max_hp": 55.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.6, "scale": 0.7},
                {"archetype": "broodling", "name": "Broodling", "hp": 55.0, "max_hp": 55.0, "speed": 1.10, "damage": 10.0, "role": "light", "spawn_delay": 0.8, "scale": 0.7},
            ],
        },
        "team_bonus": {
            "type": "spawn_delay_reduction",
            "description": "Unidades aliadas reducen su tiempo de preparación en 15%.",
            "value": 0.15,
        },
    },
    "nexus": {
        "id": "nexus",
        "name": "Nexus Protocol",
        "category": "synthetic",
        "color": "#06b6d4",  # Cian cuántico
        "description": "Autómatas y mentes sintéticas que dominan la energía cuántica y el combate de largo alcance.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 3.0,  # +3 E/s pasivo fijo
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 1,   # +1 salto de alcance (alcance 3)
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.0,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "railgun_mech",
            "name": "Railgun Automaton",
            "hp": 110.0,
            "max_hp": 110.0,
            "speed": 0.45,
            "damage": 32.0,
            "trait": "Artillería electromagnética con impacto a distancia.",
        },
        "squad_doctrine": {
            "name": "Quantum Battery",
            "units": [
                {"archetype": "railgun_mech", "name": "Railgun Automaton", "hp": 110.0, "max_hp": 110.0, "speed": 0.45, "damage": 32.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.1},
                {"archetype": "pulse_drone", "name": "Pulse Drone", "hp": 48.0, "max_hp": 48.0, "speed": 0.75, "damage": 8.0, "role": "light", "spawn_delay": 0.35, "scale": 0.75},
                {"archetype": "pulse_drone", "name": "Pulse Drone", "hp": 48.0, "max_hp": 48.0, "speed": 0.75, "damage": 8.0, "role": "light", "spawn_delay": 0.70, "scale": 0.75},
            ],
        },
        "team_bonus": {
            "type": "turret_damage_bonus",
            "description": "Torretas aliadas obtienen +10% de daño balístico.",
            "value": 0.10,
        },
    },
    "aethelian": {
        "id": "aethelian",
        "name": "Aethelian Enclave",
        "category": "psionic",
        "color": "#eab308",  # Oro psiónico
        "description": "Ancestrales psiónicos enfocados en la purificación territorial masiva y campos de plasma.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 3,  # Inicia con 3 saltos de territorio
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.0,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 2.0,   # Doble tasa de purificación (30 pts/s)
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "archon_strider",
            "name": "Archon Ophanim",
            "hp": 120.0,
            "max_hp": 120.0,
            "speed": 0.50,
            "damage": 22.0,
            "trait": "Constructo celestial de anillos giroscópicos y núcleo solar.",
        },
        "squad_doctrine": {
            "name": "Psionic Phalanx",
            "units": [
                {"archetype": "archon_strider", "name": "Archon Ophanim", "hp": 120.0, "max_hp": 120.0, "speed": 0.50, "damage": 22.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.2},
                {"archetype": "psionic_disciple", "name": "Psionic Disciple", "hp": 50.0, "max_hp": 50.0, "speed": 0.65, "damage": 10.0, "role": "light", "spawn_delay": 0.35, "scale": 0.8},
                {"archetype": "psionic_disciple", "name": "Psionic Disciple", "hp": 50.0, "max_hp": 50.0, "speed": 0.65, "damage": 10.0, "role": "light", "spawn_delay": 0.70, "scale": 0.8},
            ],
        },
        "team_bonus": {
            "type": "purification_range_bonus",
            "description": "Instalaciones de purificación aliadas obtienen +1 salto de alcance.",
            "value": 1,
        },
    },
    "vorash": {
        "id": "vorash",
        "name": "Vorash Scavengers",
        "category": "nomad",
        "color": "#f97316",  # Naranja chatarra
        "description": "Piratas y chatarreros que prosperan mediante el pillaje y la demolición acelerada.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 2,
            "salvage_bounty": 35.0,    # +35 E por destrucción enemiga
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.0,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 2.0,  # Daño duplicado a muros y edificios
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "scrap_tank",
            "name": "Scrap Tank",
            "hp": 120.0,
            "max_hp": 120.0,
            "speed": 0.55,
            "damage": 20.0,
            "trait": "Tanque acorazado de piezas recicladas con ariete frontal.",
        },
        "squad_doctrine": {
            "name": "Scavenger Raiding Party",
            "units": [
                {"archetype": "scrap_tank", "name": "Scrap Tank", "hp": 120.0, "max_hp": 120.0, "speed": 0.55, "damage": 20.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.2},
                {"archetype": "raider_scout", "name": "Raider Scout", "hp": 55.0, "max_hp": 55.0, "speed": 0.90, "damage": 14.0, "role": "siege", "spawn_delay": 0.30, "scale": 0.85},
                {"archetype": "raider_scout", "name": "Raider Scout", "hp": 55.0, "max_hp": 55.0, "speed": 0.90, "damage": 14.0, "role": "siege", "spawn_delay": 0.60, "scale": 0.85},
            ],
        },
        "team_bonus": {
            "type": "salvage_share",
            "description": "Aliados reciben el 50% del botín de chatarra por cada baja enemiga.",
            "value": 0.50,
        },
    },
    "titanforge": {
        "id": "titanforge",
        "name": "Titanforge Lithoids",
        "category": "mineral",
        "color": "#78716c",  # Gris roca / titanio
        "description": "Seres minerales ultra acorazados, maestros de fortificaciones y guerra de desgaste.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 0.48,    # Muros a solo 12 E en vez de 25 E
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.20,  # -20% de daño recibido en todo
            "unit_speed_mult": 0.85,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "juggernaut",
            "name": "Juggernaut Colossus",
            "hp": 260.0,
            "max_hp": 260.0,
            "speed": 0.25,
            "damage": 32.0,
            "trait": "Armadura monolítica masiva resistente a fuego cruzado.",
        },
        "squad_doctrine": {
            "name": "Monolithic Colossus",
            "units": [
                {"archetype": "juggernaut", "name": "Juggernaut Colossus", "hp": 260.0, "max_hp": 260.0, "speed": 0.25, "damage": 32.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.5},
            ],
        },
        "team_bonus": {
            "type": "ally_building_hp_bonus",
            "description": "Edificios de aliados obtienen +20% de salud máxima.",
            "value": 0.20,
        },
    },
    "zephyrian": {
        "id": "zephyrian",
        "name": "Zephyrian Nomads",
        "category": "aerial",
        "color": "#38bdf8",  # Azul cielo
        "description": "Nómadas de los cielos planetarios con extrema agilidad, evasión y maniobras aéreas.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.0,
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.15,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.30,    # 30% de probabilidad de esquivar
            "reanimate_chance": 0.0,
        },
        "unique_unit": {
            "type": "storm_skimmer",
            "name": "Storm Skimmer",
            "hp": 70.0,
            "max_hp": 70.0,
            "speed": 0.90,
            "damage": 14.0,
            "trait": "Deslizador atmosférico que puede volar sobre obstáculos.",
        },
        "squad_doctrine": {
            "name": "Sky Wing",
            "units": [
                {"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 70.0, "max_hp": 70.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.0, "scale": 0.85},
                {"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 70.0, "max_hp": 70.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.30, "scale": 0.85},
                {"archetype": "storm_skimmer", "name": "Storm Skimmer", "hp": 70.0, "max_hp": 70.0, "speed": 0.90, "damage": 14.0, "role": "light", "spawn_delay": 0.60, "scale": 0.85},
            ],
        },
        "team_bonus": {
            "type": "ally_speed_bonus",
            "description": "La velocidad de marcha de todas las tropas aliadas aumenta 10%.",
            "value": 0.10,
        },
    },
    "umbral": {
        "id": "umbral",
        "name": "Umbral Parasites",
        "category": "void",
        "color": "#831843",  # Borgoña oscuro / vacío
        "description": "Entidades del vacío que cosechan corrupción territorial y asimilan las bajas enemigas.",
        "econ_modifiers": {
            "harvester_yield_mult": 1.0,
            "base_income_bonus": 0.0,
            "building_cost_mult": 1.0,
            "wall_cost_mult": 1.0,
            "base_influence_hops": 2,
            "salvage_bounty": 0.0,
            "corrupt_node_income": 0.5,  # +0.5 E/s por cada nodo corrupto controlado
        },
        "combat_modifiers": {
            "turret_cooldown_mult": 1.0,
            "turret_range_bonus": 0,
            "turret_damage_mult": 1.0,
            "wall_hp_mult": 1.0,
            "damage_reduction": 0.0,
            "unit_speed_mult": 1.0,
            "unit_hp_regen": 0.0,
            "purify_rate_mult": 1.0,
            "structure_damage_mult": 1.0,
            "evasion_chance": 0.0,
            "reanimate_chance": 0.30,  # 30% de transformar bajas enemigas en parásitos
        },
        "unique_unit": {
            "type": "void_infestor",
            "name": "Void Infestor",
            "hp": 110.0,
            "max_hp": 110.0,
            "speed": 0.50,
            "damage": 20.0,
            "trait": "Corrompe nodos terrestres al desplazarse.",
        },
        "squad_doctrine": {
            "name": "Void Incursion",
            "units": [
                {"archetype": "void_infestor", "name": "Void Infestor", "hp": 110.0, "max_hp": 110.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.0, "scale": 1.1},
                {"archetype": "void_infestor", "name": "Void Infestor", "hp": 110.0, "max_hp": 110.0, "speed": 0.50, "damage": 20.0, "role": "heavy", "spawn_delay": 0.40, "scale": 1.1},
            ],
        },
        "team_bonus": {
            "type": "corruption_immunity",
            "description": "Aliados son inmunes a penalizaciones de movimiento en zonas infectadas.",
            "value": 1.0,
        },
    },
}


def get_all_race_ids():
    """Retorna la lista de identificadores de las 8 razas disponibles."""
    return list(RACES_CATALOG.keys())


def get_race_data(race_id):
    """
    Retorna el diccionario de configuración de la raza especificada.
    Por defecto retorna 'solarian' si el ID no existe.
    """
    if race_id in RACES_CATALOG:
        return RACES_CATALOG[race_id]
    return RACES_CATALOG["solarian"]


def calculate_building_cost(base_cost, building_type, race_id):
    """
    Aplica los modificadores de costo de construcción según la raza.
    """
    race = get_race_data(race_id)
    econ = race["econ_modifiers"]

    if building_type == "wall":
        return float(base_cost * econ.get("wall_cost_mult", 1.0))

    return float(base_cost * econ.get("building_cost_mult", 1.0))


def calculate_harvester_income(base_rate_per_node, node_count, race_id):
    """
    Aplica el modificador de rendimiento de extractores según la raza.
    """
    race = get_race_data(race_id)
    mult = race["econ_modifiers"].get("harvester_yield_mult", 1.0)
    return float(base_rate_per_node * node_count * mult)


def calculate_base_passive_income(default_base_income, race_id):
    """
    Calcula el ingreso pasivo base aplicando el bono de raza (ej. Nexus +3.0 E/s).
    """
    race = get_race_data(race_id)
    bonus = race["econ_modifiers"].get("base_income_bonus", 0.0)
    return float(default_base_income + bonus)


def calculate_initial_influence_hops(race_id):
    """
    Retorna los saltos de influencia con los que inicia el Puesto de Comando (Aethelian = 3, otros = 2).
    """
    race = get_race_data(race_id)
    return int(race["econ_modifiers"].get("base_influence_hops", 2))


def apply_building_combat_stats(building_data, race_id):
    """
    Aplica los modificadores de combate a un edificio recién construido o instanciado:
    - Muros: HP máxima modificada por wall_hp_mult.
    - Torretas: cadencia modificada por turret_cooldown_mult, rango por turret_range_bonus.
    - Purificadores: purify_rate por purify_rate_mult.
    """
    modified = dict(building_data)
    race = get_race_data(race_id)
    c_mod = race["combat_modifiers"]

    btype = modified.get("type", "")

    if btype == "wall":
        mult = c_mod.get("wall_hp_mult", 1.0)
        modified["max_hp"] = float(modified.get("max_hp", 300.0) * mult)
        modified["hp"] = modified["max_hp"]

    elif btype == "turret":
        cd_mult = c_mod.get("turret_cooldown_mult", 1.0)
        range_bonus = c_mod.get("turret_range_bonus", 0)
        dmg_mult = c_mod.get("turret_damage_mult", 1.0)

        modified["cooldown"] = float(modified.get("cooldown", 1.0) * cd_mult)
        modified["attack_range_hops"] = int(modified.get("attack_range_hops", 2) + range_bonus)
        modified["damage"] = float(modified.get("damage", 25.0) * dmg_mult)

    elif btype == "purifier":
        p_mult = c_mod.get("purify_rate_mult", 1.0)
        modified["purify_rate"] = float(modified.get("purify_rate", 15.0) * p_mult)

    return modified


def calculate_incoming_damage(raw_damage, is_target_structure, attacker_race_id=None, defender_race_id=None, attacker_role="heavy"):
    """
    Calcula el daño final recibido considerando:
    - Blindaje de estructuras: Unidades ligeras ('light') infligen 50% de daño a edificios/fortificaciones.
    - Multiplicador contra estructuras del atacante (Vorash = x2).
    - Reducción pasiva de daño del defensor (Titanforge = -20%).
    """
    damage = float(raw_damage)

    if is_target_structure:
        if attacker_role == "light":
            damage *= 0.5
        if attacker_race_id:
            att_race = get_race_data(attacker_race_id)
            damage *= att_race["combat_modifiers"].get("structure_damage_mult", 1.0)

    if defender_race_id:
        def_race = get_race_data(defender_race_id)
        reduction = def_race["combat_modifiers"].get("damage_reduction", 0.0)
        damage *= (1.0 - reduction)

    return max(0.0, damage)


def get_race_squad_composition(race_id):
    """
    Retorna la lista de especificaciones de unidades que componen el escuadrón de asalto de la raza.
    """
    race = get_race_data(race_id)
    doctrine = race.get("squad_doctrine")
    if doctrine and "units" in doctrine:
        return [dict(u) for u in doctrine["units"]]

    # Fallback genérico si no estuviese definida
    unique = race.get("unique_unit", {})
    return [
        {
            "archetype": unique.get("type", "vanguard"),
            "name": unique.get("name", "Vanguard Mech"),
            "hp": float(unique.get("hp", 120.0)),
            "max_hp": float(unique.get("max_hp", 120.0)),
            "speed": float(unique.get("speed", 0.5)),
            "damage": float(unique.get("damage", 20.0)),
            "role": "heavy",
            "spawn_delay": 0.0,
            "scale": 1.2,
        },
        {
            "archetype": "scout",
            "name": "Scout",
            "hp": 40.0,
            "max_hp": 40.0,
            "speed": 0.8,
            "damage": 10.0,
            "role": "light",
            "spawn_delay": 0.35,
            "scale": 0.75,
        },
        {
            "archetype": "scout",
            "name": "Scout",
            "hp": 40.0,
            "max_hp": 40.0,
            "speed": 0.8,
            "damage": 10.0,
            "role": "light",
            "spawn_delay": 0.70,
            "scale": 0.75,
        },
    ]

