import unittest
from logic.icosphere import create_icosphere, find_antipodal_node
from logic.territory import initialize_world_state, place_building
from logic.purification import (
    PURIFIER_SPECS,
    can_purify_crater,
    initialize_craters_data,
    update_purification_tick,
)


class TestPurificationLogic(unittest.TestCase):
    def setUp(self):
        # Icosfera con subdivisión 2 (162 nodos)
        self.icosphere = create_icosphere(subdivisions=2, radius=5.0)
        self.base_node = 0
        self.crater_node = find_antipodal_node(self.icosphere["nodes"], self.base_node)

    def test_can_purify_crater_range(self):
        # Vecino directo (1 salto) o perimetral (3 saltos)
        neighbor = self.icosphere["nodes"][self.crater_node]["neighbors"][0]
        self.assertTrue(
            can_purify_crater(neighbor, self.crater_node, self.icosphere, max_hops=4),
            "Un nodo vecino debe estar en rango de purificación de 4 saltos"
        )

        # La base (nodo 0) está en el polo opuesto, a más de 4 saltos (8 saltos)
        self.assertFalse(
            can_purify_crater(self.base_node, self.crater_node, self.icosphere, max_hops=4),
            "El polo opuesto no debe estar en rango de purificación"
        )

    def test_purification_tick_damages_crater(self):
        world = initialize_world_state(self.icosphere, self.base_node, [self.crater_node])
        
        # Simular colocación de un purificador en un vecino del cráter
        # Buscamos un vecino a 2 saltos del cráter
        crater_neighbors = self.icosphere["nodes"][self.crater_node]["neighbors"]
        purifier_node = crater_neighbors[0]

        # Forzar colocación del purificador
        world["nodes"][purifier_node]["building"] = dict(PURIFIER_SPECS)

        # Ejecutar 1 tick de 1.0 segundo (purify_rate = 15.0)
        new_world, events = update_purification_tick(world, self.icosphere, delta=1.0)

        cdata = new_world["craters"][self.crater_node]
        self.assertAlmostEqual(cdata["hp"], 85.0, places=2)
        
        beam_events = [e for e in events if e["type"] == "purification_beam"]
        self.assertEqual(len(beam_events), 1)
        self.assertEqual(beam_events[0]["purifier_node"], purifier_node)
        self.assertEqual(beam_events[0]["crater_node"], self.crater_node)

    def test_crater_sealing_and_offensive_victory(self):
        world = initialize_world_state(self.icosphere, self.base_node, [self.crater_node])
        crater_neighbors = self.icosphere["nodes"][self.crater_node]["neighbors"]
        purifier_node = crater_neighbors[0]

        world["nodes"][purifier_node]["building"] = dict(PURIFIER_SPECS)
        # Dejar el cráter con 10 HP
        world["craters"][self.crater_node]["hp"] = 10.0

        # Con 1 segundo de purificación (tasa 15.0/s), el cráter se sella por completo
        new_world, events = update_purification_tick(world, self.icosphere, delta=1.0)

        cdata = new_world["craters"][self.crater_node]
        self.assertEqual(cdata["hp"], 0.0)
        self.assertTrue(cdata["is_sealed"])
        self.assertNotIn(self.crater_node, new_world["crater_node_ids"])
        self.assertFalse(new_world["nodes"][self.crater_node]["is_crater"])

        # Al sellar el único cráter, se declara victoria ofensiva
        self.assertEqual(new_world["game_status"], "victory")

        victory_events = [e for e in events if e["type"] == "all_craters_sealed"]
        self.assertEqual(len(victory_events), 1)


if __name__ == "__main__":
    unittest.main()
