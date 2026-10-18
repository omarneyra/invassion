"""
Unit tests para el módulo de territorio y control de zonas.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.icosphere import create_icosphere
from logic.territory import (
    initialize_world_state,
    can_build_on_node,
    place_building,
    remove_building,
)


class TestTerritoryLogic(unittest.TestCase):

    def setUp(self):
        # Icosfera de 162 nodos para las pruebas
        self.iso = create_icosphere(subdivisions=2, radius=5.0)
        self.base_id = 0
        self.crater_id = 85  # Nodo en el hemisferio opuesto
        self.world = initialize_world_state(self.iso, self.base_id, [self.crater_id])

    def test_initial_state(self):
        nodes = self.world["nodes"]

        # La base debe ser del jugador
        self.assertEqual(nodes[self.base_id]["controller"], "player")
        self.assertTrue(nodes[self.base_id]["is_base"])

        # Los vecinos inmediatos de la base deben ser del jugador (radio 2 hops)
        for neighbor in self.iso["nodes"][self.base_id]["neighbors"]:
            self.assertEqual(nodes[neighbor]["controller"], "player")

        # El cráter y sus vecinos deben ser corruptos
        self.assertEqual(nodes[self.crater_id]["controller"], "corrupt")
        for c_neighbor in self.iso["nodes"][self.crater_id]["neighbors"]:
            self.assertEqual(nodes[c_neighbor]["controller"], "corrupt")

        # Nodos lejanos no cubiertos deben ser neutros
        neutral_nodes = [nid for nid, d in nodes.items() if d["controller"] == "neutral"]
        self.assertGreater(len(neutral_nodes), 50)
        self.assertEqual(self.world["game_status"], "in_progress")

    def test_building_validation(self):
        # 1. No se puede construir en un nodo que ya tiene la base
        can_build, _ = can_build_on_node(self.world, self.base_id)
        self.assertFalse(can_build)

        # 2. No se puede construir en un nodo neutro (fuera de territorio)
        neutral_id = next(nid for nid, d in self.world["nodes"].items() if d["controller"] == "neutral")
        can_build, _ = can_build_on_node(self.world, neutral_id)
        self.assertFalse(can_build)

        # 3. No se puede construir en zona corrupta
        can_build, _ = can_build_on_node(self.world, self.crater_id)
        self.assertFalse(can_build)

        # 4. Sí se puede construir en un nodo dominado por el jugador y libre
        player_empty_id = next(
            nid for nid, d in self.world["nodes"].items()
            if d["controller"] == "player" and d["building"] is None
        )
        can_build, reason = can_build_on_node(self.world, player_empty_id)
        self.assertTrue(can_build, f"Debería poder construir pero falló con: {reason}")

    def test_place_and_remove_building_expansion(self):
        # Encontrar un nodo en la frontera del territorio del jugador
        frontier_node = next(
            nid for nid, d in self.world["nodes"].items()
            if d["controller"] == "player" and d["building"] is None
        )

        initial_player_count = sum(
            1 for d in self.world["nodes"].values() if d["controller"] == "player"
        )

        # Colocar una torreta con radio de 1 salto
        turret = {"type": "turret", "hp": 150.0, "max_hp": 150.0, "influence_hops": 1}
        success, updated_world = place_building(self.world, self.iso, frontier_node, turret)
        self.assertTrue(success)

        # El nuevo estado debe tener al menos la misma cantidad o más nodos dominados
        new_player_count = sum(
            1 for d in updated_world["nodes"].values() if d["controller"] == "player"
        )
        self.assertGreaterEqual(new_player_count, initial_player_count)

        # Si removemos la torreta, el territorio debe contraerse al inicial
        collapsed_world = remove_building(updated_world, self.iso, frontier_node)
        collapsed_count = sum(
            1 for d in collapsed_world["nodes"].values() if d["controller"] == "player"
        )
        self.assertEqual(collapsed_count, initial_player_count)

    def test_defeat_condition(self):
        # Si la base cae a 0 HP, debe declararse derrota
        world_destroyed = dict(self.world)
        world_destroyed["nodes"][self.base_id]["building"]["hp"] = 0.0

        # Recalcular
        from logic.territory import update_territory
        updated = update_territory(world_destroyed, self.iso)
        self.assertEqual(updated["game_status"], "defeat")


if __name__ == "__main__":
    unittest.main()
