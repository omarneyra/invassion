import unittest
import math
from logic.threat_radar import (
    is_point_occluded_by_sphere,
    project_to_camera_screen_dir,
    clamp_direction_to_screen_bounds,
    get_arrow_glyph,
    compute_threat_indicators,
)


class TestThreatRadar(unittest.TestCase):
    def test_point_occlusion_exact_geometry(self):
        radius = 5.0
        camera_pos = (0.0, 0.0, 15.0)

        # Punto directamente frente a la cámara
        front_point = (0.0, 0.0, 5.0)
        self.assertFalse(
            is_point_occluded_by_sphere(front_point, camera_pos, radius),
            "El punto frontal debe ser visible"
        )

        # Punto en el hemisferio opuesto (detrás del planeta)
        back_point = (0.0, 0.0, -5.0)
        self.assertTrue(
            is_point_occluded_by_sphere(back_point, camera_pos, radius),
            "El punto posterior debe estar oculto por el planeta"
        )

        # Punto ligeramente tras el horizonte
        # El horizonte desde distancia 15 tiene cos(θ) = 5/15 = 1/3 ~ 0.333
        # Si cos(θ) < 0.333 está oculto
        horizon_hidden = (0.0, 4.9, 1.0) # z / 5 = 0.2 < 0.333
        self.assertTrue(is_point_occluded_by_sphere(horizon_hidden, camera_pos, radius))

    def test_screen_direction_projection(self):
        camera_right = (1.0, 0.0, 0.0)
        camera_up = (0.0, 1.0, 0.0)

        # Punto a la derecha
        pt_right = (10.0, 0.0, -5.0)
        dx, dy = project_to_camera_screen_dir(pt_right, camera_right, camera_up)
        self.assertAlmostEqual(dx, 1.0, places=4)
        self.assertAlmostEqual(dy, 0.0, places=4)

        # Punto hacia arriba (en pantalla Y es negativo hacia arriba)
        pt_up = (0.0, 10.0, -5.0)
        dx, dy = project_to_camera_screen_dir(pt_up, camera_right, camera_up)
        self.assertAlmostEqual(dx, 0.0, places=4)
        self.assertAlmostEqual(dy, -1.0, places=4)

    def test_screen_clamping(self):
        screen_w, screen_h = 1000.0, 800.0
        margin = 50.0

        # Derecha (1, 0) -> x = 950, y = 400
        sx, sy, angle = clamp_direction_to_screen_bounds(1.0, 0.0, screen_w, screen_h, margin)
        self.assertAlmostEqual(sx, 950.0)
        self.assertAlmostEqual(sy, 400.0)
        self.assertAlmostEqual(angle, 0.0)

        # Arriba (0, -1) -> x = 500, y = 50
        sx, sy, angle = clamp_direction_to_screen_bounds(0.0, -1.0, screen_w, screen_h, margin)
        self.assertAlmostEqual(sx, 500.0)
        self.assertAlmostEqual(sy, 50.0)
        self.assertAlmostEqual(angle, -math.pi / 2)

    def test_arrow_glyphs(self):
        self.assertEqual(get_arrow_glyph(0.0), "➡")
        self.assertEqual(get_arrow_glyph(math.pi / 2), "⬇")
        self.assertEqual(get_arrow_glyph(math.pi), "⬅")
        self.assertEqual(get_arrow_glyph(-math.pi / 2), "⬆")
        self.assertEqual(get_arrow_glyph(math.pi / 4), "↘")
        self.assertEqual(get_arrow_glyph(3 * math.pi / 4), "↙")
        self.assertEqual(get_arrow_glyph(-math.pi / 4), "↗")
        self.assertEqual(get_arrow_glyph(-3 * math.pi / 4), "↖")

    def test_compute_threat_indicators_filtering(self):
        radius = 5.0
        camera_pos = (0.0, 0.0, 15.0)
        camera_right = (1.0, 0.0, 0.0)
        camera_up = (0.0, 1.0, 0.0)
        screen_w, screen_h = 1024.0, 768.0

        nodes_data = {
            1: {"id": 1, "pos": (0.0, 0.0, 5.0)},     # Visible (frente)
            2: {"id": 2, "pos": (0.0, 0.0, -5.0)},    # Ciego (detrás)
            3: {"id": 3, "pos": (3.0, 0.0, -4.0)},    # Ciego (derecha atrás)
        }

        invaders = [
            # Invasor visible en el frente
            {"id": 101, "archetype": "crawler", "current_node": 1, "state": "marching", "path": [2, 1], "path_index": 1},
            # Invasor en hemisferio ciego
            {"id": 102, "archetype": "brute", "current_node": 2, "state": "marching", "path": [2, 3, 1], "path_index": 0},
            # Invasor muerto (ignorado)
            {"id": 103, "archetype": "scout", "current_node": 3, "state": "dead", "path": [3, 1], "path_index": 0},
            # Invasor haciendo spawn (ignorado)
            {"id": 104, "archetype": "crawler", "current_node": 3, "state": "spawning", "path": [3, 1], "path_index": 0},
        ]

        indicators = compute_threat_indicators(
            invaders, nodes_data, camera_pos, camera_right, camera_up,
            radius, screen_w, screen_h, base_node_id=1, margin=40.0
        )

        self.assertEqual(len(indicators), 1, "Solo debe haber 1 invasor vivo en el hemisferio ciego")
        ind = indicators[0]
        self.assertEqual(ind["invader_id"], 102)
        self.assertEqual(ind["archetype"], "brute")
        self.assertEqual(ind["remaining_hops"], 2)
        self.assertTrue(ind["is_occluded"])


if __name__ == "__main__":
    unittest.main()
