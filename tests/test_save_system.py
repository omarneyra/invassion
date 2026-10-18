import os
import tempfile
import unittest
from logic.icosphere import create_icosphere, find_antipodal_node
from logic.territory import initialize_world_state, place_building
from logic.economy import create_initial_economy
from logic.purification import PURIFIER_SPECS
from logic.save_system import (
    serialize_game_state,
    deserialize_game_state,
    save_state_to_file,
    load_state_from_file,
    SAVE_SCHEMA_VERSION,
)


class TestSaveSystem(unittest.TestCase):
    def setUp(self):
        self.icosphere = create_icosphere(subdivisions=2, radius=5.0)
        self.base_node = 0
        self.crater_node = find_antipodal_node(self.icosphere["nodes"], self.base_node)
        self.world_state = initialize_world_state(self.icosphere, self.base_node, [self.crater_node])
        self.economy_state = create_initial_economy(starting_energy=150.0, base_income=6.0)
        self.wave_state = {
            "current_wave": 1,
            "wave_countdown": 20.0,
            "is_wave_active": False,
            "invader_counter": 0,
            "active_invaders": [],
        }

    def test_serialization_and_deserialization_roundtrip(self):
        # Configurar algún estado con edificios y cráteres
        neighbor = self.icosphere["nodes"][self.base_node]["neighbors"][0]
        building_data = {"type": "relay", "hp": 100.0, "max_hp": 100.0, "influence_hops": 2}
        success, self.world_state = place_building(self.world_state, self.icosphere, neighbor, building_data)
        self.assertTrue(success)

        # Modificar oleada y cráter
        self.world_state["craters"][self.crater_node]["hp"] = 72.5
        self.wave_state["current_wave"] = 3
        self.wave_state["wave_countdown"] = 12.4
        self.wave_state["active_invaders"] = [
            {"id": 1, "current_node": self.crater_node, "target_node": neighbor, "hp": 50.0, "progress": 0.5}
        ]

        # Serializar
        serialized = serialize_game_state(self.world_state, self.economy_state, self.wave_state)
        self.assertEqual(serialized["version"], SAVE_SCHEMA_VERSION)
        self.assertEqual(serialized["world"]["base_node_id"], self.base_node)
        self.assertIn(str(neighbor), serialized["world"]["nodes"])
        self.assertEqual(serialized["world"]["nodes"][str(neighbor)]["building"]["type"], "relay")

        # Deserializar
        valid, restored, err = deserialize_game_state(serialized)
        self.assertTrue(valid, f"Error en deserialización: {err}")

        # Comprobar tipos de datos restaurados (claves enteros)
        self.assertIn(neighbor, restored["world"]["nodes"])
        self.assertEqual(restored["world"]["nodes"][neighbor]["building"]["type"], "relay")
        self.assertEqual(restored["world"]["base_node_id"], self.base_node)
        self.assertEqual(restored["world"]["craters"][self.crater_node]["hp"], 72.5)

        # Comprobar economía y oleadas
        self.assertEqual(restored["economy"]["energy"], 150.0)
        self.assertEqual(restored["economy"]["base_income_rate"], 6.0)
        self.assertEqual(restored["wave"]["current_wave"], 3)
        self.assertAlmostEqual(restored["wave"]["wave_countdown"], 12.4, places=2)
        self.assertEqual(len(restored["wave"]["active_invaders"]), 1)
        self.assertEqual(restored["wave"]["active_invaders"][0]["id"], 1)

    def test_file_save_and_load(self):
        serialized = serialize_game_state(self.world_state, self.economy_state, self.wave_state)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_save.json")
            save_ok = save_state_to_file(save_path, serialized)
            self.assertTrue(save_ok, "El guardado en archivo debe retornar True")
            self.assertTrue(os.path.exists(save_path))

            load_ok, restored, err = load_state_from_file(save_path)
            self.assertTrue(load_ok, f"La carga de archivo falló: {err}")
            self.assertEqual(restored["world"]["base_node_id"], self.base_node)

    def test_deserialize_invalid_data(self):
        # Datos corruptos o vacíos
        valid, _, err = deserialize_game_state("no es dict")
        self.assertFalse(valid)
        self.assertIn("no son un diccionario", err)

        valid, _, err = deserialize_game_state({"mundo": {}})
        self.assertFalse(valid)
        self.assertIn("incompleta", err)

        # Archivo inexistente
        load_ok, _, err = load_state_from_file("/ruta/inexistente/no_existe.json")
        self.assertFalse(load_ok)
        self.assertIn("no existe", err)


if __name__ == "__main__":
    unittest.main()
