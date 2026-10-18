import unittest
from logic.icosphere import create_icosphere
from logic.factions import (
    find_distributed_base_nodes,
    create_faction,
    initialize_factions_game,
    are_allies,
    are_enemies,
    get_enemy_factions,
    get_allied_factions,
    calculate_multi_faction_territory,
    update_multi_faction_economy,
    evaluate_factions_victory_defeat,
    get_diplomatic_stance,
    set_diplomatic_stance,
    send_tribute,
)


class TestFactionsLogic(unittest.TestCase):
    def setUp(self):
        # Icosfera Subdiv 2 (162 nodos) para tests rápidos
        self.icosphere = create_icosphere(subdivisions=2, radius=5.0)

    def test_find_distributed_base_nodes(self):
        nodes = self.icosphere["nodes"]

        # 2 bases: polo 0 y antipodal
        bases_2 = find_distributed_base_nodes(nodes, count=2)
        self.assertEqual(len(bases_2), 2)
        self.assertEqual(bases_2[0], 0)
        self.assertNotEqual(bases_2[0], bases_2[1])

        # 4 bases: 4 nodos distintos y bien separados
        bases_4 = find_distributed_base_nodes(nodes, count=4)
        self.assertEqual(len(bases_4), 4)
        self.assertEqual(len(set(bases_4)), 4)

    def test_initialize_factions_game_ffa_and_teams(self):
        # 1. Modo Todos contra Todos (FFA): cada facción en su propio equipo
        ffa_configs = [
            {"name": "Solarian", "race": "solarian", "is_ai": False},
            {"name": "Krynn", "race": "krynn", "is_ai": True},
            {"name": "Nexus", "race": "nexus", "is_ai": True},
        ]
        game_ffa = initialize_factions_game(self.icosphere, ffa_configs)
        self.assertEqual(game_ffa["game_mode"], "ffa")
        self.assertEqual(len(game_ffa["factions"]), 3)
        self.assertTrue(are_enemies(1, 2, game_ffa["factions"]))
        self.assertTrue(are_enemies(1, 3, game_ffa["factions"]))
        self.assertTrue(are_enemies(2, 3, game_ffa["factions"]))

        # 2. Modo Alianzas / Equipos: 2v1 (Equipo 1: Solarian + Nexus vs Equipo 2: Krynn)
        team_configs = [
            {"name": "Solarian", "race": "solarian", "is_ai": False, "team": 1},
            {"name": "Nexus", "race": "nexus", "is_ai": True, "team": 1},
            {"name": "Krynn", "race": "krynn", "is_ai": True, "team": 2},
        ]
        game_teams = initialize_factions_game(self.icosphere, team_configs)
        self.assertEqual(game_teams["game_mode"], "teams")
        factions = game_teams["factions"]

        self.assertTrue(are_allies(1, 2, factions))
        self.assertFalse(are_enemies(1, 2, factions))
        self.assertTrue(are_enemies(1, 3, factions))
        self.assertTrue(are_enemies(2, 3, factions))

        self.assertEqual(get_enemy_factions(1, factions), [3])
        self.assertEqual(get_allied_factions(1, factions, include_self=False), [2])

    def test_multi_faction_territory_projection(self):
        nodes = {nid: {"controller": 0, "building": None} for nid in self.icosphere["nodes"]}

        # Base 1 (Solarian, fid 1) en nodo 0 (radio 2)
        nodes[0]["building"] = {"type": "base", "faction_id": 1, "hp": 500.0, "max_hp": 500.0, "influence_hops": 2}

        # Base 2 (Aethelian, fid 2) en nodo opuesto (radio 3 por bono racial de Aethelian)
        base_2_id = find_distributed_base_nodes(self.icosphere["nodes"], count=2)[1]
        nodes[base_2_id]["building"] = {"type": "base", "faction_id": 2, "hp": 500.0, "max_hp": 500.0, "influence_hops": 2}

        factions = {
            1: create_faction(1, "Solarian", "solarian", False, 1, 0),
            2: create_faction(2, "Aethelian", "aethelian", True, 2, base_2_id),
        }

        updated_nodes = calculate_multi_faction_territory(self.icosphere, nodes, factions)

        # La base 1 y sus vecinos directos deben pertenecer a la facción 1
        self.assertEqual(updated_nodes[0]["controller"], 1)
        for neigh in self.icosphere["nodes"][0]["neighbors"]:
            self.assertEqual(updated_nodes[neigh]["controller"], 1)

        # La base 2 debe pertenecer a la facción 2
        self.assertEqual(updated_nodes[base_2_id]["controller"], 2)

    def test_multi_faction_economy_and_team_bonus(self):
        nodes = {nid: {"controller": 0, "building": None} for nid in self.icosphere["nodes"]}

        # Configurar 2 facciones aliadas en equipo 1: Solarian (fid 1) y Nexus (fid 2)
        base_1 = 0
        base_2 = find_distributed_base_nodes(self.icosphere["nodes"], count=2)[1]

        nodes[base_1]["controller"] = 1
        nodes[base_1]["building"] = {"type": "base", "faction_id": 1, "hp": 500.0}

        nodes[base_2]["controller"] = 2
        nodes[base_2]["building"] = {"type": "base", "faction_id": 2, "hp": 500.0}

        factions = {
            1: create_faction(1, "Solarian", "solarian", False, team_id=1, base_node_id=base_1, starting_energy=100.0),
            2: create_faction(2, "Nexus", "nexus", True, team_id=1, base_node_id=base_2, starting_energy=100.0),
        }

        # Nexus tiene base_income = 5.0 + 3.0 = 8.0 E/s
        # Además, al ser aliado de Solarian (que otorga +10% de ingreso pasivo a sus aliados), Nexus recibe 8.0 + 0.8 = 8.8 E/s
        # Solarian tiene base_income = 5.0 E/s
        updated_factions = update_multi_faction_economy(factions, nodes, self.icosphere, delta_seconds=1.0)

        self.assertAlmostEqual(updated_factions[1]["energy"], 105.0)
        self.assertAlmostEqual(updated_factions[2]["energy"], 108.8)

    def test_evaluate_factions_victory_defeat(self):
        nodes = {nid: {"controller": 0, "building": None} for nid in self.icosphere["nodes"]}
        base_1 = 0
        base_2 = 100

        nodes[base_1]["building"] = {"type": "base", "faction_id": 1, "hp": 500.0}
        nodes[base_2]["building"] = {"type": "base", "faction_id": 2, "hp": 500.0}

        factions = {
            1: create_faction(1, "Solarian", "solarian", False, team_id=1, base_node_id=base_1),
            2: create_faction(2, "Krynn", "krynn", True, team_id=2, base_node_id=base_2),
        }

        # 1. En progreso
        status, winning_team, _ = evaluate_factions_victory_defeat(factions, nodes, player_faction_id=1)
        self.assertEqual(status, "in_progress")

        # 2. Destrucción de base enemiga (Krynn cae a 0 HP) -> Victoria del jugador
        nodes[base_2]["building"]["hp"] = 0.0
        status, winning_team, updated = evaluate_factions_victory_defeat(factions, nodes, player_faction_id=1)
        self.assertEqual(status, "victory")
        self.assertEqual(winning_team, 1)
        self.assertFalse(updated[2]["is_alive"])

        # 3. Destrucción de base del jugador -> Derrota
        nodes[base_1]["building"]["hp"] = 0.0
        nodes[base_2]["building"] = {"type": "base", "hp": 500.0, "max_hp": 500.0, "faction_id": 2}
        factions[2]["is_alive"] = True
        status, _, updated = evaluate_factions_victory_defeat(factions, nodes, player_faction_id=1)
        self.assertEqual(status, "defeat")
        self.assertFalse(updated[1]["is_alive"])

    def test_dynamic_diplomacy_stance_changes(self):
        configs = [
            {"name": "Solarian", "race": "solarian", "is_ai": False, "team": 1},
            {"name": "Nexus", "race": "nexus", "is_ai": True, "team": 2},
        ]
        game_state = initialize_factions_game(self.icosphere, configs)

        # Inicialmente son enemigos (equipos distintos)
        self.assertEqual(get_diplomatic_stance(game_state, 1, 2), "enemy")
        self.assertEqual(get_diplomatic_stance(game_state, 2, 1), "enemy")
        self.assertTrue(are_enemies(1, 2, game_state))
        self.assertFalse(are_allies(1, 2, game_state))

        # 1. Jugador cambia postura a "neutral" hacia Nexus
        ok, game_state, msg = set_diplomatic_stance(game_state, 1, 2, "neutral")
        self.assertTrue(ok)
        self.assertEqual(get_diplomatic_stance(game_state, 1, 2), "neutral")
        # Pero Nexus aún considera al jugador "enemy" -> sigue habiendo hostilidad unilateral
        self.assertEqual(get_diplomatic_stance(game_state, 2, 1), "enemy")
        self.assertTrue(are_enemies(1, 2, game_state))

        # 2. Nexus también cambia postura a "neutral" -> cese de hostilidades / tregua
        ok, game_state, msg = set_diplomatic_stance(game_state, 2, 1, "neutral")
        self.assertTrue(ok)
        self.assertFalse(are_enemies(1, 2, game_state), "Si ambos son neutrales, no están en guerra activa")
        self.assertFalse(are_allies(1, 2, game_state), "Neutral no es aliado")

        # 3. Pacto de Alianza Mutua: ambos fijan "ally"
        set_diplomatic_stance(game_state, 1, 2, "ally")
        set_diplomatic_stance(game_state, 2, 1, "ally")
        self.assertTrue(are_allies(1, 2, game_state))
        self.assertFalse(are_enemies(1, 2, game_state))

        # 4. Traición sorpresa: Nexus cambia a "enemy"
        set_diplomatic_stance(game_state, 2, 1, "enemy")
        self.assertTrue(are_enemies(1, 2, game_state), "La traición unilateral reactiva la guerra de inmediato")
        self.assertFalse(are_allies(1, 2, game_state))

    def test_send_tribute_system(self):
        configs = [
            {"name": "Solarian", "race": "solarian", "is_ai": False, "starting_energy": 200.0},
            {"name": "Titanforge", "race": "titanforge", "is_ai": True, "starting_energy": 50.0},
        ]
        game_state = initialize_factions_game(self.icosphere, configs)

        # 1. Enviar tributo de 100 E sin arancel
        ok, game_state, msg = send_tribute(game_state, from_faction_id=1, to_faction_id=2, amount=100.0, fee_rate=0.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(game_state["factions"][1]["energy"], 100.0)
        self.assertAlmostEqual(game_state["factions"][2]["energy"], 150.0)

        # 2. Enviar tributo de 50 E con 20% de arancel (fee_rate=0.20)
        # Recibido neto = 50 * 0.80 = 40.0 E
        ok, game_state, msg = send_tribute(game_state, from_faction_id=1, to_faction_id=2, amount=50.0, fee_rate=0.20)
        self.assertTrue(ok)
        self.assertAlmostEqual(game_state["factions"][1]["energy"], 50.0)
        self.assertAlmostEqual(game_state["factions"][2]["energy"], 190.0)

        # 3. Intento de enviar más energía de la disponible -> debe fallar limpiamente
        ok, game_state, err = send_tribute(game_state, from_faction_id=1, to_faction_id=2, amount=500.0)
        self.assertFalse(ok)
        self.assertIn("insuficiente", err.lower())
        self.assertAlmostEqual(game_state["factions"][1]["energy"], 50.0)

        # 4. Intento de enviarse tributo a sí mismo -> rechazo
        ok, game_state, err = send_tribute(game_state, from_faction_id=1, to_faction_id=1, amount=10.0)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()

