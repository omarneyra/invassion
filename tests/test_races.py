import unittest
from logic.races import (
    RACES_CATALOG,
    get_all_race_ids,
    get_race_data,
    calculate_building_cost,
    calculate_harvester_income,
    calculate_base_passive_income,
    calculate_initial_influence_hops,
    apply_building_combat_stats,
    calculate_incoming_damage,
)


class TestRacesCatalog(unittest.TestCase):
    def test_catalog_has_eight_unique_races(self):
        race_ids = get_all_race_ids()
        self.assertEqual(len(race_ids), 8, "Debe haber exactamente 8 razas en el catálogo")
        expected_ids = {
            "solarian",
            "krynn",
            "nexus",
            "aethelian",
            "vorash",
            "titanforge",
            "zephyrian",
            "umbral",
        }
        self.assertEqual(set(race_ids), expected_ids)

    def test_race_data_integrity(self):
        for rid in get_all_race_ids():
            data = get_race_data(rid)
            self.assertEqual(data["id"], rid)
            self.assertTrue(len(data["name"]) > 0)
            self.assertTrue(data["color"].startswith("#"))
            self.assertIn("econ_modifiers", data)
            self.assertIn("combat_modifiers", data)
            self.assertIn("unique_unit", data)
            self.assertIn("team_bonus", data)

    def test_default_fallback_for_unknown_race(self):
        fallback = get_race_data("raza_inexistente")
        self.assertEqual(fallback["id"], "solarian", "Debe retornar Solarian por defecto si el ID no existe")

    def test_economic_modifiers_building_cost(self):
        # Base Wall = 25.0, Harvester = 50.0
        # Krynn: 20% descuento en todo
        self.assertAlmostEqual(calculate_building_cost(50.0, "harvester", "krynn"), 40.0)
        self.assertAlmostEqual(calculate_building_cost(25.0, "wall", "krynn"), 20.0)

        # Titanforge: Muros a 48% (12.0 E)
        self.assertAlmostEqual(calculate_building_cost(25.0, "wall", "titanforge"), 12.0)
        # Otros edificios no tienen descuento en Titanforge
        self.assertAlmostEqual(calculate_building_cost(50.0, "harvester", "titanforge"), 50.0)

        # Solarian: Costo normal
        self.assertAlmostEqual(calculate_building_cost(50.0, "harvester", "solarian"), 50.0)

    def test_economic_modifiers_harvester_yield(self):
        # 1.5 E/nodo para 4 nodos = 6.0 E
        # Solarian: +25% -> 7.5 E
        solarian_yield = calculate_harvester_income(1.5, 4, "solarian")
        self.assertAlmostEqual(solarian_yield, 7.5)

        # Krynn: estándar 6.0 E
        krynn_yield = calculate_harvester_income(1.5, 4, "krynn")
        self.assertAlmostEqual(krynn_yield, 6.0)

    def test_economic_modifiers_base_income(self):
        # Base estándar = 5.0 E/s
        # Nexus: +3.0 E/s adicional -> 8.0 E/s
        self.assertAlmostEqual(calculate_base_passive_income(5.0, "nexus"), 8.0)
        self.assertAlmostEqual(calculate_base_passive_income(5.0, "solarian"), 5.0)

    def test_initial_influence_hops(self):
        # Aethelian: 3 saltos
        self.assertEqual(calculate_initial_influence_hops("aethelian"), 3)
        # Otros: 2 saltos
        self.assertEqual(calculate_initial_influence_hops("solarian"), 2)
        self.assertEqual(calculate_initial_influence_hops("krynn"), 2)

    def test_combat_modifiers_building_stats(self):
        # 1. Solarian Muro (+25% HP): 300 * 1.25 = 375
        wall = {"type": "wall", "hp": 300.0, "max_hp": 300.0}
        mod_wall = apply_building_combat_stats(wall, "solarian")
        self.assertAlmostEqual(mod_wall["max_hp"], 375.0)
        self.assertAlmostEqual(mod_wall["hp"], 375.0)

        # 2. Solarian Torreta (cooldown * 0.80)
        turret = {"type": "turret", "damage": 25.0, "cooldown": 1.0, "attack_range_hops": 2}
        mod_turret_solarian = apply_building_combat_stats(turret, "solarian")
        self.assertAlmostEqual(mod_turret_solarian["cooldown"], 0.80)

        # 3. Nexus Torreta (+1 rango de ataque): 2 + 1 = 3
        mod_turret_nexus = apply_building_combat_stats(turret, "nexus")
        self.assertEqual(mod_turret_nexus["attack_range_hops"], 3)

        # 4. Aethelian Purificador (purify_rate * 2.0): 15.0 * 2.0 = 30.0
        purifier = {"type": "purifier", "purify_rate": 15.0}
        mod_purifier = apply_building_combat_stats(purifier, "aethelian")
        self.assertAlmostEqual(mod_purifier["purify_rate"], 30.0)

    def test_damage_modifiers_calculation(self):
        raw_damage = 50.0

        # Titanforge Defensor: -20% reducción de daño -> 40.0
        titan_def = calculate_incoming_damage(raw_damage, is_target_structure=False, attacker_race_id="solarian", defender_race_id="titanforge")
        self.assertAlmostEqual(titan_def, 40.0)

        # Vorash Atacante contra estructura: x2 daño -> 100.0
        vorash_vs_struct = calculate_incoming_damage(raw_damage, is_target_structure=True, attacker_race_id="vorash", defender_race_id="solarian")
        self.assertAlmostEqual(vorash_vs_struct, 100.0)

        # Vorash Atacante contra unidad (no estructura): daño normal -> 50.0
        vorash_vs_unit = calculate_incoming_damage(raw_damage, is_target_structure=False, attacker_race_id="vorash", defender_race_id="solarian")
        self.assertAlmostEqual(vorash_vs_unit, 50.0)

        # Vorash contra Titanforge en estructura: (50 * 2.0) * 0.80 = 80.0
        vorash_vs_titan_struct = calculate_incoming_damage(raw_damage, is_target_structure=True, attacker_race_id="vorash", defender_race_id="titanforge")
        self.assertAlmostEqual(vorash_vs_titan_struct, 80.0)


if __name__ == "__main__":
    unittest.main()
