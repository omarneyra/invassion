"""
Unit tests para el módulo de economía y recursos.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.icosphere import create_icosphere
from logic.territory import initialize_world_state, place_building
from logic.economy import (
    create_initial_economy,
    calculate_tick_income,
    apply_income,
    can_afford,
    purchase_building,
    BUILDING_CATALOG,
)


class TestEconomyLogic(unittest.TestCase):

    def setUp(self):
        self.iso = create_icosphere(subdivisions=2, radius=5.0)
        self.base_id = 0
        self.crater_id = 85
        self.world = initialize_world_state(self.iso, self.base_id, [self.crater_id])
        self.econ = create_initial_economy(starting_energy=100.0, base_income=5.0)

    def test_base_income(self):
        # 2 segundos de tiempo transcurrido con base activa
        income = calculate_tick_income(self.econ, self.world, self.iso, delta_seconds=2.0)
        self.assertAlmostEqual(income, 10.0, places=3)

        updated_econ = apply_income(self.econ, income)
        self.assertAlmostEqual(updated_econ["energy"], 110.0, places=3)

    def test_base_destroyed_zero_base_income(self):
        # Si la base tiene HP 0, el ingreso base debe ser 0
        self.world["nodes"][self.base_id]["building"]["hp"] = 0.0
        income = calculate_tick_income(self.econ, self.world, self.iso, delta_seconds=5.0)
        self.assertEqual(income, 0.0)

    def test_harvester_income_bonus(self):
        # Encontrar nodo del jugador libre para colocar un extractor
        target_node = next(
            nid for nid, d in self.world["nodes"].items()
            if d["controller"] == "player" and d["building"] is None
        )

        harvester_template = dict(BUILDING_CATALOG["harvester"])
        harvester_template["type"] = "harvester"

        success, world_with_harvester = place_building(
            self.world, self.iso, target_node, harvester_template
        )
        self.assertTrue(success)

        # Ingreso con base (5/s) + extractor (1.5/s por nodo dominado en su radio)
        income_base_only = calculate_tick_income(self.econ, self.world, self.iso, delta_seconds=1.0)
        income_with_harvester = calculate_tick_income(
            self.econ, world_with_harvester, self.iso, delta_seconds=1.0
        )

        self.assertGreater(income_with_harvester, income_base_only)

    def test_affordability_and_purchase(self):
        # Con 100 de energía:
        # Puede comprar torreta (75)
        affordable, cost = can_afford(self.econ, "turret")
        self.assertTrue(affordable)
        self.assertEqual(cost, 75.0)

        # Comprar torreta
        success, new_econ, template = purchase_building(self.econ, "turret")
        self.assertTrue(success)
        self.assertEqual(new_econ["energy"], 25.0)
        self.assertEqual(template["type"], "turret")

        # Con 25 de energía restante:
        # Puede comprar muro (25)
        affordable_wall, _ = can_afford(new_econ, "wall")
        self.assertTrue(affordable_wall)

        # NO puede comprar otro extractor (50)
        affordable_harvester, _ = can_afford(new_econ, "harvester")
        self.assertFalse(affordable_harvester)

        # Intento de compra debe fallar limpiamente
        fail_success, unchanged_econ, _ = purchase_building(new_econ, "harvester")
        self.assertFalse(fail_success)
        self.assertEqual(unchanged_econ["energy"], 25.0)


if __name__ == "__main__":
    unittest.main()
