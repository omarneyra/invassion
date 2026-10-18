"""
Unit tests para el Árbol Tecnológico y Mejoras de Base (tech_tree).
Estilo procedimental puro: funciones estáticas y diccionarios planos.
"""
import unittest
from logic.tech_tree import (
    get_tech_catalog,
    can_research_tech,
    research_tech,
    apply_tech_to_building,
    apply_tech_to_squad,
    get_tech_economic_multiplier,
)


class TestTechTree(unittest.TestCase):

    def setUp(self):
        self.faction_data = {
            "name": "Imperio Solar",
            "energy": 200.0,
            "researched_techs": [],
        }

    def test_tech_catalog_integrity(self):
        catalog = get_tech_catalog()
        self.assertIn("laser_optics", catalog)
        self.assertIn("rapid_fire", catalog)
        self.assertIn("composite_armor", catalog)
        self.assertIn("quantum_harvesters", catalog)
        self.assertIn("military_training", catalog)

        for tid, data in catalog.items():
            self.assertIn("name", data)
            self.assertIn("cost", data)
            self.assertIn("description", data)
            self.assertGreater(data["cost"], 0.0)

    def test_can_research_tech_conditions(self):
        # 1. Energía insuficiente
        poor_faction = {"energy": 10.0, "researched_techs": []}
        can_r, reason = can_research_tech("laser_optics", poor_faction)
        self.assertFalse(can_r)
        self.assertIn("insuficiente", reason.lower())

        # 2. Energía suficiente
        can_r, reason = can_research_tech("laser_optics", self.faction_data)
        self.assertTrue(can_r)

        # 3. Ya investigada
        already_faction = {"energy": 200.0, "researched_techs": ["laser_optics"]}
        can_r, reason = can_research_tech("laser_optics", already_faction)
        self.assertFalse(can_r)
        self.assertIn("investigada", reason.lower())

    def test_research_tech_execution(self):
        initial_energy = self.faction_data["energy"]
        success, updated_fdata, cost, msg = research_tech("laser_optics", self.faction_data)

        self.assertTrue(success)
        self.assertIn("laser_optics", updated_fdata["researched_techs"])
        self.assertEqual(updated_fdata["energy"], initial_energy - cost)
        self.assertIn("investigada con éxito", msg.lower())

    def test_research_tech_retroactive_building_upgrade(self):
        nodes = {
            10: {
                "building": {
                    "type": "turret",
                    "hp": 80.0,
                    "max_hp": 80.0,
                    "attack_range_hops": 2,
                    "faction_id": 1,
                }
            },
            20: {
                "building": {
                    "type": "turret",
                    "hp": 80.0,
                    "max_hp": 80.0,
                    "attack_range_hops": 2,
                    "faction_id": 2, # Facción enemiga no debe recibir la mejora
                }
            }
        }
        fdata = {"id": 1, "energy": 100.0, "researched_techs": []}
        success, updated_fdata, cost, msg = research_tech("laser_optics", fdata, nodes)
        self.assertTrue(success)
        self.assertEqual(nodes[10]["building"]["attack_range_hops"], 3)
        self.assertEqual(nodes[20]["building"]["attack_range_hops"], 2)

    def test_apply_tech_to_building(self):
        turret = {
            "type": "turret",
            "hp": 80.0,
            "max_hp": 80.0,
            "attack_range_hops": 2,
            "cooldown": 1.0,
        }
        wall = {
            "type": "wall",
            "hp": 150.0,
            "max_hp": 150.0,
        }

        # Sin mejoras
        t_base = apply_tech_to_building(turret, [])
        self.assertEqual(t_base["attack_range_hops"], 2)
        self.assertEqual(t_base["cooldown"], 1.0)

        # Con óptica láser y cadencia
        t_upgraded = apply_tech_to_building(turret, ["laser_optics", "rapid_fire"])
        self.assertEqual(t_upgraded["attack_range_hops"], 3)
        self.assertAlmostEqual(t_upgraded["cooldown"], 0.70)

        # Con blindaje compuesto en muro
        w_upgraded = apply_tech_to_building(wall, ["composite_armor"])
        self.assertAlmostEqual(w_upgraded["max_hp"], 210.0)
        self.assertAlmostEqual(w_upgraded["hp"], 210.0)

    def test_apply_tech_to_squad(self):
        squad = [
            {"id": "u1", "damage": 20.0, "speed": 0.5},
            {"id": "u2", "damage": 10.0, "speed": 0.8},
        ]
        upgraded_squad = apply_tech_to_squad(squad, ["military_training"])
        self.assertAlmostEqual(upgraded_squad[0]["damage"], 26.0)
        self.assertAlmostEqual(upgraded_squad[0]["speed"], 0.625)
        self.assertAlmostEqual(upgraded_squad[1]["damage"], 13.0)
        self.assertAlmostEqual(upgraded_squad[1]["speed"], 1.0)

    def test_get_tech_economic_multiplier(self):
        mult_base = get_tech_economic_multiplier([])
        self.assertAlmostEqual(mult_base, 1.0)

        mult_upgraded = get_tech_economic_multiplier(["quantum_harvesters"])
        self.assertAlmostEqual(mult_upgraded, 1.5)


if __name__ == "__main__":
    unittest.main()
