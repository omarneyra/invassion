"""
Unit tests para el módulo de combate, invasión y daño.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.icosphere import create_icosphere
from logic.territory import initialize_world_state, place_building
from logic.combat import (
    INVADER_ARCHETYPES,
    generate_invasion_lane,
    generate_multiple_invasion_lanes,
    create_wave_composition,
    spawn_invader,
    find_turret_target,
    update_combat_tick,
)


class TestCombatLogic(unittest.TestCase):

    def setUp(self):
        self.iso = create_icosphere(subdivisions=2, radius=5.0)
        self.base_id = 0
        self.crater_id = 85
        self.world = initialize_world_state(self.iso, self.base_id, [self.crater_id])
        self.lane = generate_invasion_lane(self.iso, self.crater_id, self.base_id)

    def test_invasion_lane_integrity(self):
        self.assertGreater(len(self.lane), 2)
        self.assertEqual(self.lane[0], self.crater_id)
        self.assertEqual(self.lane[-1], self.base_id)

    def test_invader_archetypes_balance(self):
        scout = INVADER_ARCHETYPES["scout"]
        crawler = INVADER_ARCHETYPES["crawler"]
        brute = INVADER_ARCHETYPES["brute"]

        # Scout debe ser el más rápido
        self.assertGreater(scout["speed"], crawler["speed"])
        self.assertGreater(crawler["speed"], brute["speed"])

        # Brute debe ser el más resistente y tener mayor daño
        self.assertGreater(brute["hp"], crawler["hp"])
        self.assertGreater(crawler["hp"], scout["hp"])
        self.assertGreater(brute["damage"], crawler["damage"])

    def test_wave_composition_progression(self):
        wave_1 = create_wave_composition(1)
        self.assertEqual(len(wave_1), 2)
        self.assertEqual(wave_1, ["crawler", "crawler"])

        wave_2 = create_wave_composition(2)
        self.assertIn("scout", wave_2)

        wave_3 = create_wave_composition(3)
        self.assertIn("brute", wave_3)

        # La oleada 5 debe tener más enemigos totales que la oleada 1
        wave_5 = create_wave_composition(5)
        self.assertGreater(len(wave_5), len(wave_1))

    def test_spawn_invader_archetype(self):
        brute = spawn_invader(invader_id=1, path=self.lane, archetype="brute")
        self.assertEqual(brute["archetype"], "brute")
        self.assertEqual(brute["hp"], 220.0)
        self.assertEqual(brute["state"], "marching")

        # Spawn con delay
        queued_scout = spawn_invader(invader_id=2, path=self.lane, archetype="scout", custom_delay=2.0)
        self.assertEqual(queued_scout["state"], "spawning")
        self.assertEqual(queued_scout["spawn_delay"], 2.0)

    def test_turret_targeting_and_attack(self):
        turret_node = self.iso["nodes"][self.base_id]["neighbors"][0]
        turret_data = {
            "type": "turret",
            "hp": 150.0,
            "max_hp": 150.0,
            "influence_hops": 1,
            "attack_range_hops": 2,
            "damage": 30.0,
            "cooldown": 1.0,
            "shoot_timer": 1.0,
        }
        success, world_with_turret = place_building(self.world, self.iso, turret_node, turret_data)
        self.assertTrue(success)

        target_node = self.iso["nodes"][turret_node]["neighbors"][0]
        test_path = [target_node, self.base_id]
        invader = spawn_invader(invader_id=10, path=test_path, archetype="scout") # 35 HP

        target = find_turret_target(turret_node, turret_data, [invader], self.iso)
        self.assertIsNotNone(target)
        self.assertEqual(target["id"], 10)

        # Primer disparo: torreta inflige 30 de daño (35 - 30 = 5 HP)
        updated_world, updated_invaders, events = update_combat_tick(
            world_with_turret, [invader], self.iso, delta_time=0.1
        )
        self.assertEqual(updated_invaders[0]["hp"], 5.0)

        # Segundo disparo (cooldown listo): mata al scout
        updated_world["nodes"][turret_node]["building"]["shoot_timer"] = 1.0
        final_world, final_invaders, second_events = update_combat_tick(
            updated_world, updated_invaders, self.iso, delta_time=0.1
        )
        killed_events = [e for e in second_events if e["type"] == "invader_killed"]
        self.assertEqual(len(killed_events), 1)
        self.assertEqual(len(final_invaders), 0)

    def test_wall_blocks_and_resists_attacks(self):
        wall_node = self.lane[-2]
        wall_data = {
            "type": "wall",
            "hp": 300.0,
            "max_hp": 300.0,
            "influence_hops": 0,
        }
        self.world["nodes"][wall_node]["controller"] = "player"
        success, world_with_wall = place_building(self.world, self.iso, wall_node, wall_data)
        self.assertTrue(success)

        # Invasor Brute (35 de daño por ataque)
        brute = spawn_invader(
            invader_id=55,
            path=[wall_node, self.base_id],
            archetype="brute",
        )
        brute["attack_timer"] = 1.0

        # Un ataque del Brute: el muro recibe 35 de daño (300 - 35 = 265 HP) y NO se destruye
        updated_world, invaders, events = update_combat_tick(
            world_with_wall, [brute], self.iso, delta_time=0.1
        )

        wall_after = updated_world["nodes"][wall_node]["building"]
        self.assertIsNotNone(wall_after)
        self.assertEqual(wall_after["hp"], 265.0)
        self.assertEqual(invaders[0]["state"], "attacking")

    def test_multiple_invasion_lanes_divergence(self):
        lanes = generate_multiple_invasion_lanes(self.iso, self.crater_id, self.base_id, count=2)
        self.assertEqual(len(lanes), 2, "Debe generar 2 carriles geodésicos")

        lane_1, lane_2 = lanes[0], lanes[1]
        self.assertEqual(lane_1[0], self.crater_id)
        self.assertEqual(lane_2[0], self.crater_id)
        self.assertEqual(lane_1[-1], self.base_id)
        self.assertEqual(lane_2[-1], self.base_id)

        # Los primeros pasos deben salir por vecinos diferentes del cráter
        self.assertNotEqual(lane_1[1], lane_2[1], "Los dos carriles deben divergir de inmediato")

        # Nodos intermedios deben ser distintos (rutas por costados opuestos)
        mid_1 = set(lane_1[1:-2])
        mid_2 = set(lane_2[1:-2])
        self.assertTrue(mid_1.isdisjoint(mid_2), "Los carriles no deben compartir nodos intermedios")


    def test_faction_aware_combat_tick(self):
        factions_data = {
            "factions": {
                1: {"name": "Solarian", "team": 1, "is_alive": True},
                2: {"name": "Nexus", "team": 1, "is_alive": True},
                3: {"name": "Krynn", "team": 2, "is_alive": True},
            },
            "diplomacy_matrix": {
                1: {1: "ally", 2: "ally", 3: "enemy"},
                2: {1: "ally", 2: "ally", 3: "enemy"},
                3: {1: "enemy", 2: "enemy", 3: "ally"},
            }
        }
        turret_node = self.iso["nodes"][self.base_id]["neighbors"][0]
        turret_data = {
            "type": "turret",
            "hp": 150.0,
            "max_hp": 150.0,
            "influence_hops": 1,
            "attack_range_hops": 2,
            "damage": 30.0,
            "cooldown": 1.0,
            "shoot_timer": 1.0,
            "faction_id": 1,
        }
        success, world_with_turret = place_building(self.world, self.iso, turret_node, turret_data)
        self.assertTrue(success)

        target_node = self.iso["nodes"][turret_node]["neighbors"][0]
        test_path = [target_node, self.base_id]

        # 1. Unidad aliada (Facción 2): La torreta NO debe dispararle
        ally_unit = spawn_invader(invader_id=20, path=test_path, archetype="scout")
        ally_unit["faction_id"] = 2
        w1, invs1, events1 = update_combat_tick(
            world_with_turret, [ally_unit], self.iso, delta_time=0.1, factions_data=factions_data
        )
        self.assertEqual(invs1[0]["hp"], ally_unit["hp"], "La torreta no debe disparar a unidades aliadas")
        turret_shots = [e for e in events1 if e.get("type") == "turret_shot"]
        self.assertEqual(len(turret_shots), 0)

        # 2. Unidad enemiga (Facción 3): La torreta SÍ debe dispararle
        enemy_unit = spawn_invader(invader_id=30, path=test_path, archetype="scout")
        enemy_unit["faction_id"] = 3
        w2, invs2, events2 = update_combat_tick(
            world_with_turret, [enemy_unit], self.iso, delta_time=0.1, factions_data=factions_data
        )
        self.assertLess(invs2[0]["hp"], enemy_unit["hp"], "La torreta debe atacar unidades hostiles")
        turret_shots_enemy = [e for e in events2 if e.get("type") == "turret_shot"]
        self.assertEqual(len(turret_shots_enemy), 1)

    def test_turret_siege_bombardment_on_enemy_buildings(self):
        factions_data = {
            "factions": {
                1: {"name": "Solarian", "team": 1, "is_alive": True},
                2: {"name": "Krynn", "team": 2, "is_alive": True},
            },
            "diplomacy_matrix": {
                1: {1: "ally", 2: "enemy"},
                2: {1: "enemy", 2: "ally"},
            }
        }
        turret_node = self.iso["nodes"][self.base_id]["neighbors"][0]
        turret_data = {
            "type": "turret",
            "hp": 150.0,
            "max_hp": 150.0,
            "influence_hops": 1,
            "attack_range_hops": 2,
            "damage": 30.0,
            "cooldown": 1.0,
            "shoot_timer": 1.0,
            "faction_id": 1,
        }
        success, world_with_turret = place_building(self.world, self.iso, turret_node, turret_data)
        self.assertTrue(success)

        # Colocar un muro enemigo de Facción 2 en nodo adyacente a la torreta (a 1 salto)
        enemy_node = self.iso["nodes"][turret_node]["neighbors"][0]
        world_with_turret["nodes"][enemy_node]["building"] = {
            "type": "wall",
            "hp": 50.0,
            "max_hp": 50.0,
            "faction_id": 2,
        }

        # Sin tropas móviles activas, la torreta debe bombardear el edificio enemigo
        w1, invs1, events1 = update_combat_tick(
            world_with_turret, [], self.iso, delta_time=0.1, factions_data=factions_data
        )
        siege_shots = [e for e in events1 if e.get("type") == "turret_shot_building"]
        self.assertEqual(len(siege_shots), 1)
        self.assertEqual(siege_shots[0]["target_node"], enemy_node)
        self.assertEqual(w1["nodes"][enemy_node]["building"]["hp"], 20.0)

        # Segundo disparo derriba el muro enemigo (50 - 30 - 30 <= 0)
        w1["nodes"][turret_node]["building"]["shoot_timer"] = 1.0
        w2, invs2, events2 = update_combat_tick(
            w1, [], self.iso, delta_time=0.1, factions_data=factions_data
        )
        self.assertIsNone(w2["nodes"][enemy_node]["building"], "El muro enemigo debe haber sido destruido")
        destroyed_events = [e for e in events2 if e.get("type") == "building_destroyed"]
        self.assertEqual(len(destroyed_events), 1)

    def test_base_defensive_battery_fires_at_enemy(self):
        factions_data = {
            "factions": {
                1: {"name": "Player", "team": 1, "is_alive": True},
                2: {"name": "Enemy", "team": 2, "is_alive": True},
            },
            "matrix": {
                1: {2: "enemy"},
                2: {1: "enemy"},
            }
        }
        # Configurar base del jugador con defensa propia
        self.world["nodes"][self.base_id]["building"] = {
            "type": "base",
            "hp": 500.0,
            "max_hp": 500.0,
            "faction_id": 1,
            "attack_range_hops": 1,
            "damage": 20.0,
            "cooldown": 1.0,
            "shoot_timer": 1.0,
        }
        adj_node = self.iso["nodes"][self.base_id]["neighbors"][0]
        test_path = [adj_node, self.base_id]
        enemy_unit = spawn_invader(invader_id=99, path=test_path, archetype="scout")
        enemy_unit["faction_id"] = 2
        enemy_unit["hp"] = 40.0
        enemy_unit["max_hp"] = 40.0
        w_res, inv_res, events = update_combat_tick(
            self.world, [enemy_unit], self.iso, delta_time=0.1, factions_data=factions_data
        )
        shots = [e for e in events if e.get("type") == "turret_shot"]
        self.assertEqual(len(shots), 1)
        self.assertEqual(shots[0]["turret_node"], self.base_id)
        self.assertEqual(inv_res[0]["hp"], 20.0)

    def test_turret_smart_focus_fire_prioritizes_lowest_hp(self):
        factions_data = {
            "factions": {
                1: {"name": "Player", "team": 1, "is_alive": True},
                2: {"name": "Enemy", "team": 2, "is_alive": True},
            },
            "matrix": {
                1: {2: "enemy"},
                2: {1: "enemy"},
            }
        }
        turret_node = self.iso["nodes"][self.base_id]["neighbors"][0]
        turret_data = {
            "type": "turret",
            "hp": 280.0,
            "max_hp": 280.0,
            "influence_hops": 1,
            "attack_range_hops": 2,
            "damage": 35.0,
            "cooldown": 0.8,
            "shoot_timer": 0.8,
            "faction_id": 1,
        }
        success, world_with_turret = place_building(self.world, self.iso, turret_node, turret_data)
        self.assertTrue(success)

        target_node = self.iso["nodes"][turret_node]["neighbors"][0]
        test_path = [target_node, self.base_id]

        tank_unit = spawn_invader(invader_id=101, path=test_path, archetype="brute")
        tank_unit["faction_id"] = 2
        tank_unit["hp"] = 140.0

        scout_unit = spawn_invader(invader_id=102, path=test_path, archetype="scout")
        scout_unit["faction_id"] = 2
        scout_unit["hp"] = 35.0

        target = find_turret_target(turret_node, turret_data, [tank_unit, scout_unit], self.iso, factions_data)
        self.assertIsNotNone(target)
        self.assertEqual(target["id"], 102, "La torreta debe priorizar con Focus Fire la unidad con menor HP (scout)")


if __name__ == "__main__":
    unittest.main()


