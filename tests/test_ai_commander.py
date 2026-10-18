import unittest
from logic.icosphere import create_icosphere
from logic.factions import initialize_factions_game, set_diplomatic_stance
from logic.ai_commander import (
    analyze_faction_territory,
    find_closest_enemy_base,
    decide_ai_construction,
    decide_ai_assault,
    process_ai_diplomacy_reaction,
    run_ai_tick,
    launch_faction_assault,
)


class TestAICommander(unittest.TestCase):
    def setUp(self):
        self.icosphere = create_icosphere(subdivisions=2, radius=5.0)
        self.configs = [
            {"name": "Solarian", "race": "solarian", "is_ai": False, "team": 1, "starting_energy": 100.0},
            {"name": "Krynn", "race": "krynn", "is_ai": True, "team": 2, "starting_energy": 100.0},
        ]
        self.game_state = initialize_factions_game(self.icosphere, self.configs)
        self.base_1 = self.game_state["factions"][1]["base_node"]
        self.base_2 = self.game_state["factions"][2]["base_node"]

        self.world_nodes = {nid: {"controller": 0, "building": None} for nid in self.icosphere["nodes"]}
        self.world_nodes[self.base_1] = {"controller": 1, "building": {"type": "base", "faction_id": 1, "hp": 1500.0, "max_hp": 1500.0}}
        self.world_nodes[self.base_2] = {"controller": 2, "building": {"type": "base", "faction_id": 2, "hp": 1500.0, "max_hp": 1500.0}}

    def test_analyze_faction_territory(self):
        # Asignar nodos alrededor de base 2 a la facción 2
        neighbors = self.icosphere["nodes"][self.base_2]["neighbors"]
        for neigh in neighbors:
            self.world_nodes[neigh]["controller"] = 2

        analysis = analyze_faction_territory(2, self.world_nodes, self.icosphere, self.game_state)
        self.assertEqual(analysis["controlled_count"], 1 + len(neighbors))
        # Debe haber nodos vacíos disponibles para construir
        self.assertTrue(len(analysis["frontier_empty"]) > 0 or len(analysis["interior_empty"]) > 0)

    def test_find_closest_enemy_base(self):
        target_fid, target_base, path = find_closest_enemy_base(2, self.world_nodes, self.game_state, self.icosphere)
        self.assertEqual(target_fid, 1)
        self.assertEqual(target_base, self.base_1)
        self.assertTrue(len(path) > 1)
        self.assertEqual(path[0], self.base_2)
        self.assertEqual(path[-1], self.base_1)

    def test_decide_ai_construction_harvester(self):
        # Rodear un nodo para que sea considerado "interior"
        target_interior = self.icosphere["nodes"][self.base_2]["neighbors"][0]
        self.world_nodes[target_interior]["controller"] = 2
        for n in self.icosphere["nodes"][target_interior]["neighbors"]:
            self.world_nodes[n]["controller"] = 2

        self.game_state["factions"][2]["energy"] = 80.0
        can_build, node, btype, template, cost = decide_ai_construction(
            2, self.game_state, self.world_nodes, self.icosphere
        )
        self.assertTrue(can_build)
        self.assertEqual(btype, "harvester")
        self.assertEqual(template["faction_id"], 2)
        self.assertTrue(cost > 0.0)

    def test_decide_ai_assault(self):
        # Con 150 de energía pero sin torretas defensivas, la IA debe priorizar defenderse antes de atacar
        self.game_state["factions"][2]["energy"] = 150.0
        can_assault_no_turrets, squad_no_turrets, _, _ = decide_ai_assault(
            2, self.game_state, self.world_nodes, self.icosphere, assault_threshold=110.0
        )
        self.assertFalse(can_assault_no_turrets, "La IA no debe lanzar asalto si tiene menos de 2 torretas perimetrales")

        # Plantar 2 torretas aliadas para la facción 2
        neighs = self.icosphere["nodes"][self.base_2]["neighbors"]
        self.world_nodes[neighs[0]]["controller"] = 2
        self.world_nodes[neighs[0]]["building"] = {"type": "turret", "faction_id": 2, "hp": 400.0}
        self.world_nodes[neighs[1]]["controller"] = 2
        self.world_nodes[neighs[1]]["building"] = {"type": "turret", "faction_id": 2, "hp": 400.0}

        # Ahora con 2 torretas y 150 E (> 110 threshold), la IA Krynn lanza asalto
        can_assault, squad, cost, target_base = decide_ai_assault(
            2, self.game_state, self.world_nodes, self.icosphere, assault_threshold=110.0
        )
        self.assertTrue(can_assault)
        self.assertEqual(len(squad), 5)  # 1 Ravager + 4 Broodlings
        self.assertEqual(target_base, self.base_1)
        self.assertEqual(squad[0]["archetype"], "ravager")  # Unidad de choque Krynn

        # Con poca energía (< 110), no debe lanzar asalto
        self.game_state["factions"][2]["energy"] = 40.0
        can_assault_low, squad_low, _, _ = decide_ai_assault(
            2, self.game_state, self.world_nodes, self.icosphere, assault_threshold=110.0
        )
        self.assertFalse(can_assault_low)
        self.assertEqual(len(squad_low), 0)

    def test_process_ai_diplomacy_reaction_tribute_and_betrayal(self):
        # 1. Tributo de 60 E de un enemigo -> acepta tregua neutral
        event_tribute_neutral = {
            "type": "tribute_received",
            "from_faction": 1,
            "to_faction": 2,
            "amount": 60.0,
        }
        reacted, self.game_state, msg = process_ai_diplomacy_reaction(2, self.game_state, event_tribute_neutral)
        self.assertTrue(reacted)
        self.assertIn("tregua", msg.lower())
        self.assertEqual(self.game_state["diplomacy_matrix"][2][1], "neutral")

        # 2. Tributo generoso de 120 E -> acepta alianza plena
        event_tribute_ally = {
            "type": "tribute_received",
            "from_faction": 1,
            "to_faction": 2,
            "amount": 120.0,
        }
        reacted, self.game_state, msg = process_ai_diplomacy_reaction(2, self.game_state, event_tribute_ally)
        self.assertTrue(reacted)
        self.assertIn("alianza", msg.lower())
        self.assertEqual(self.game_state["diplomacy_matrix"][2][1], "ally")

        # 3. Ataque traicionero a edificio propio -> declara guerra inmediata
        event_attack = {
            "type": "building_damaged",
            "target_faction": 2,
            "attacker_faction": 1,
        }
        reacted, self.game_state, msg = process_ai_diplomacy_reaction(2, self.game_state, event_attack)
        self.assertTrue(reacted)
        self.assertIn("guerra", msg.lower())
        self.assertEqual(self.game_state["diplomacy_matrix"][2][1], "enemy")

    def test_run_ai_tick_full_cycle(self):
        # Dar energía suficiente para construir y atacar
        self.game_state["factions"][2]["energy"] = 160.0

        # Asignar un nodo contiguo para que pueda construir
        neigh = self.icosphere["nodes"][self.base_2]["neighbors"][0]
        self.world_nodes[neigh]["controller"] = 2

        updated_state, updated_nodes, spawns, actions = run_ai_tick(
            2, self.game_state, self.world_nodes, self.icosphere, delta_time=1.0
        )

        self.assertTrue(len(actions) > 0)
        # La energía debe haber disminuido por las acciones tomadas
        self.assertLess(updated_state["factions"][2]["energy"], 160.0)

    def test_launch_faction_assault_player(self):
        # Facción 1 (Jugador Solarian) lanza asalto militar con 100 de energía (coste 85 E)
        self.game_state["factions"][1]["energy"] = 100.0
        success, squad, cost, enemy_base, msg = launch_faction_assault(
            1, self.game_state, self.world_nodes, self.icosphere, assault_cost=85.0
        )
        self.assertTrue(success)
        self.assertEqual(cost, 85.0)
        self.assertEqual(self.game_state["factions"][1]["energy"], 15.0)
        self.assertEqual(len(squad), 3) # 1 Vanguard + 2 Marines
        self.assertEqual(squad[0]["faction_id"], 1)
        self.assertEqual(squad[0]["archetype"], "vanguard")
        self.assertEqual(squad[0]["color"], "#22c55e")
        self.assertEqual(enemy_base, self.base_2)
    def test_decide_ai_tech_research(self):
        from logic.ai_commander import decide_ai_tech_research
        self.game_state["factions"][2]["energy"] = 140.0
        did_r, tid, cost, msg = decide_ai_tech_research(2, self.game_state, self.world_nodes, energy_threshold=110.0)
        self.assertTrue(did_r)
        self.assertIn(tid, ["composite_armor", "laser_optics", "rapid_fire", "quantum_harvesters", "military_training"])
        self.assertIn(tid, self.game_state["factions"][2]["researched_techs"])
        self.assertEqual(self.game_state["factions"][2]["energy"], 140.0 - cost)


if __name__ == "__main__":
    unittest.main()
