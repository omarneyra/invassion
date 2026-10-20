import os
import unittest
import math
from tools.generate_turret_model import create_turret_obj

class TestTurretModelGenerator(unittest.TestCase):
    """
    Unit tests for procedural 3D Wavefront OBJ/MTL Turret Generator.
    Validates topology, material assignments, and geometric boundaries.
    """

    def setUp(self):
        self.test_obj = "assets/models/turret.obj"
        self.test_mtl = "assets/models/turret.mtl"

    def test_turret_generation_counts(self):
        result = create_turret_obj(self.test_obj, self.test_mtl)
        self.assertGreaterEqual(result["verts_count"], 400)
        self.assertGreaterEqual(result["normals_count"], 50)
        self.assertGreaterEqual(result["faces_count"], 600)
        
        expected_materials = {"Mat_DarkTitanium", "Mat_FactionArmor", "Mat_PlasmaCyan", "Mat_Optics", "Mat_CopperCoil"}
        self.assertEqual(set(result["materials"]), expected_materials)

    def test_turret_file_integrity(self):
        self.assertTrue(os.path.exists(self.test_obj), "turret.obj must exist")
        self.assertTrue(os.path.exists(self.test_mtl), "turret.mtl must exist")

        with open(self.test_mtl, "r") as f:
            mtl_content = f.read()
            self.assertIn("newmtl Mat_DarkTitanium", mtl_content)
            self.assertIn("newmtl Mat_FactionArmor", mtl_content)
            self.assertIn("newmtl Mat_PlasmaCyan", mtl_content)
            self.assertIn("newmtl Mat_Optics", mtl_content)
            self.assertIn("newmtl Mat_CopperCoil", mtl_content)

        with open(self.test_obj, "r") as f:
            lines = f.readlines()
            v_lines = [l for l in lines if l.startswith("v ")]
            f_lines = [l for l in lines if l.startswith("f ")]
            usemtl_lines = [l for l in lines if l.startswith("usemtl ")]

            self.assertGreaterEqual(len(v_lines), 400)
            self.assertGreaterEqual(len(f_lines), 600)
            self.assertGreaterEqual(len(usemtl_lines), 5)

    def test_turret_bounding_box_scale(self):
        # Reads vertices to ensure scale fits the planetary geodesic nodes
        min_x, max_x = float("inf"), float("-inf")
        min_y, max_y = float("inf"), float("-inf")
        min_z, max_z = float("inf"), float("-inf")

        with open(self.test_obj, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    min_x, max_x = min(min_x, x), max(max_x, x)
                    min_y, max_y = min(min_y, y), max(max_y, y)
                    min_z, max_z = min(min_z, z), max(max_z, z)

        # Footprint should fit within node distance (~1.0)
        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        self.assertLessEqual(width, 1.2)
        self.assertGreaterEqual(width, 0.5)
        self.assertLessEqual(height, 0.8)
        self.assertGreaterEqual(height, 0.3)
        self.assertLessEqual(depth, 1.35)
        self.assertGreaterEqual(depth, 0.6)

if __name__ == "__main__":
    unittest.main()
