"""
Unit tests for procedural 3D Krynn Swarm building & unit models generator.
Validates topology, material assignments, and geometric boundaries for all 6 Krynn models:
- Base (Swarm Matrix Spire)
- Turret (Acid Spore Cannon)
- Harvester (Biomass Digestive Rhizome)
- Wall (Chitin Bone Crest)
- Purifier (Biomorphic Spore Vent)
- Ravager (Krynn Ravager Beast)
"""

import os
import unittest
from tools.generate_krynn_models import (
    make_builder,
    add_vertex,
    add_box,
    add_cylinder_y,
    add_sphere,
    add_spike,
    build_krynn_base_mesh,
    build_krynn_turret_mesh,
    build_krynn_harvester_mesh,
    build_krynn_wall_mesh,
    build_krynn_purifier_mesh,
    build_krynn_ravager_mesh,
    write_krynn_obj_mtl,
    export_all_krynn_models,
)


class TestKrynnModelsGenerator(unittest.TestCase):

    def setUp(self):
        self.output_dir = "assets/models"

    def test_krynn_mesh_primitives(self):
        b = make_builder()
        v1 = add_vertex(b, 0, 0, 0)
        self.assertEqual(v1, 1)

        add_sphere(b, 0, 0, 0, 0.5, 4, 6, "Mat_KrynnAcid")
        self.assertIn("Mat_KrynnAcid", b["faces"])
        self.assertGreaterEqual(len(b["verts"]), 10)

        add_spike(b, (0, 0, 0), (0, 1, 0), 0.1, 6, "Mat_KrynnBone")
        self.assertIn("Mat_KrynnBone", b["faces"])

    def test_krynn_base_mesh_spec(self):
        b = build_krynn_base_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_base.obj", f"{self.output_dir}/test_krynn_base.mtl")
        self.assertGreaterEqual(res["verts_count"], 300)
        self.assertGreaterEqual(res["faces_count"], 400)
        expected_mats = {"Mat_KrynnChitin", "Mat_KrynnFlesh", "Mat_KrynnAcid", "Mat_KrynnBone"}
        self.assertEqual(set(res["materials"]), expected_mats)

        if os.path.exists(f"{self.output_dir}/test_krynn_base.obj"):
            os.remove(f"{self.output_dir}/test_krynn_base.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_base.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_base.mtl")

    def test_krynn_turret_mesh_spec(self):
        b = build_krynn_turret_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_turret.obj", f"{self.output_dir}/test_krynn_turret.mtl")
        self.assertGreaterEqual(res["verts_count"], 150)
        self.assertGreaterEqual(res["faces_count"], 200)
        self.assertIn("Mat_KrynnChitin", res["materials"])
        self.assertIn("Mat_KrynnAcid", res["materials"])
        self.assertIn("Mat_KrynnBone", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_krynn_turret.obj"):
            os.remove(f"{self.output_dir}/test_krynn_turret.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_turret.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_turret.mtl")

    def test_krynn_harvester_mesh_spec(self):
        b = build_krynn_harvester_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_harv.obj", f"{self.output_dir}/test_krynn_harv.mtl")
        self.assertGreaterEqual(res["verts_count"], 200)
        self.assertGreaterEqual(res["faces_count"], 250)
        self.assertIn("Mat_KrynnAcid", res["materials"])
        self.assertIn("Mat_KrynnChitin", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_krynn_harv.obj"):
            os.remove(f"{self.output_dir}/test_krynn_harv.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_harv.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_harv.mtl")

    def test_krynn_wall_mesh_spec(self):
        b = build_krynn_wall_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_wall.obj", f"{self.output_dir}/test_krynn_wall.mtl")
        self.assertGreaterEqual(res["verts_count"], 100)
        self.assertGreaterEqual(res["faces_count"], 120)
        self.assertIn("Mat_KrynnBone", res["materials"])
        self.assertIn("Mat_KrynnChitin", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_krynn_wall.obj"):
            os.remove(f"{self.output_dir}/test_krynn_wall.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_wall.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_wall.mtl")

    def test_krynn_purifier_mesh_spec(self):
        b = build_krynn_purifier_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_purifier.obj", f"{self.output_dir}/test_krynn_purifier.mtl")
        self.assertGreaterEqual(res["verts_count"], 200)
        self.assertGreaterEqual(res["faces_count"], 250)
        self.assertIn("Mat_KrynnAcid", res["materials"])
        self.assertIn("Mat_KrynnBone", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_krynn_purifier.obj"):
            os.remove(f"{self.output_dir}/test_krynn_purifier.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_purifier.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_purifier.mtl")

    def test_krynn_ravager_mesh_spec(self):
        b = build_krynn_ravager_mesh()
        res = write_krynn_obj_mtl(b, f"{self.output_dir}/test_krynn_ravager.obj", f"{self.output_dir}/test_krynn_ravager.mtl")
        self.assertGreaterEqual(res["verts_count"], 200)
        self.assertGreaterEqual(res["faces_count"], 250)
        self.assertIn("Mat_KrynnChitin", res["materials"])
        self.assertIn("Mat_KrynnBone", res["materials"])
        self.assertIn("Mat_KrynnAcid", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_krynn_ravager.obj"):
            os.remove(f"{self.output_dir}/test_krynn_ravager.obj")
        if os.path.exists(f"{self.output_dir}/test_krynn_ravager.mtl"):
            os.remove(f"{self.output_dir}/test_krynn_ravager.mtl")

    def test_export_all_krynn_models(self):
        results = export_all_krynn_models(self.output_dir)
        self.assertEqual(len(results), 6)
        expected_keys = {
            "krynn_base",
            "krynn_turret",
            "krynn_harvester",
            "krynn_wall",
            "krynn_purifier",
            "krynn_ravager",
        }
        self.assertEqual(set(results.keys()), expected_keys)
        for name in expected_keys:
            self.assertTrue(os.path.exists(f"{self.output_dir}/{name}.obj"))
            self.assertTrue(os.path.exists(f"{self.output_dir}/{name}.mtl"))
            self.assertGreater(os.path.getsize(f"{self.output_dir}/{name}.obj"), 500)
            self.assertGreater(os.path.getsize(f"{self.output_dir}/{name}.mtl"), 100)


if __name__ == "__main__":
    unittest.main()
