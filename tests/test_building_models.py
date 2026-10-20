"""
Unit tests for modular procedural 3D building models generator.
Validates topology, material assignments, and geometric boundaries for all faction buildings:
- Turret (Pulse Defense Cannon)
- Base (Planetary Command Core)
- Harvester (Mining Rig / Energy Extractor)
- Wall (Defense Barrier / Shield Pylon)
- Purifier (Orbital Void Emitter)
"""

import os
import unittest
from tools.generate_building_models import (
    make_builder,
    add_vertex,
    add_box,
    add_cylinder_y,
    add_cylinder_between,
    add_bunker_plinth,
    add_outriggers,
    add_turntable,
    build_turret_mesh,
    build_base_mesh,
    build_harvester_mesh,
    build_wall_mesh,
    build_purifier_mesh,
    build_vanguard_mesh,
    build_marine_mesh,
    write_obj_mtl,
    export_all_models
)

class TestBuildingModelsGenerator(unittest.TestCase):

    def setUp(self):
        self.output_dir = "assets/models"

    def test_core_mesh_builder_primitives(self):
        b = make_builder()
        v1 = add_vertex(b, 0, 0, 0)
        self.assertEqual(v1, 1)
        self.assertEqual(len(b["verts"]), 1)

        add_box(b, 0, 0, 0, 1.0, 1.0, 1.0, "Mat_DarkTitanium")
        self.assertGreaterEqual(len(b["verts"]), 8)
        self.assertIn("Mat_DarkTitanium", b["faces"])
        self.assertEqual(len(b["faces"]["Mat_DarkTitanium"]), 12) # 6 quads * 2 tris

        add_cylinder_y(b, 0, 1.0, 0, 0.5, 0.5, 0.5, 8, "Mat_FactionArmor")
        self.assertIn("Mat_FactionArmor", b["faces"])

        add_cylinder_between(b, (0, 0, 0), (1, 1, 1), 0.1, 8, "Mat_CopperCoil")
        self.assertIn("Mat_CopperCoil", b["faces"])

    def test_reusable_faction_kit_subassemblies(self):
        b = make_builder()
        add_bunker_plinth(b, 0, 0.03, 0, 0.88, 0.88, 0.06)
        add_outriggers(b, 0.32, 4)
        add_turntable(b, 0.10, 0.34, 0.30, 0.03)

        self.assertGreater(len(b["verts"]), 100)
        self.assertIn("Mat_DarkTitanium", b["faces"])
        self.assertIn("Mat_FactionArmor", b["faces"])
        self.assertIn("Mat_PlasmaCyan", b["faces"])

    def test_turret_mesh_spec(self):
        b = build_turret_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_turret.obj", f"{self.output_dir}/test_turret.mtl")
        self.assertGreaterEqual(res["verts_count"], 1000)
        self.assertGreaterEqual(res["faces_count"], 1500)
        expected_mats = {"Mat_DarkTitanium", "Mat_FactionArmor", "Mat_PlasmaCyan", "Mat_Optics", "Mat_CopperCoil"}
        self.assertEqual(set(res["materials"]), expected_mats)

        # Cleanup test files
        if os.path.exists(f"{self.output_dir}/test_turret.obj"):
            os.remove(f"{self.output_dir}/test_turret.obj")
        if os.path.exists(f"{self.output_dir}/test_turret.mtl"):
            os.remove(f"{self.output_dir}/test_turret.mtl")

    def test_base_mesh_spec(self):
        b = build_base_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_base.obj", f"{self.output_dir}/test_base.mtl")
        self.assertGreaterEqual(res["verts_count"], 400)
        self.assertGreaterEqual(res["faces_count"], 600)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_FactionArmor", res["materials"])
        self.assertIn("Mat_PlasmaCyan", res["materials"])
        self.assertIn("Mat_CopperCoil", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_base.obj"):
            os.remove(f"{self.output_dir}/test_base.obj")
        if os.path.exists(f"{self.output_dir}/test_base.mtl"):
            os.remove(f"{self.output_dir}/test_base.mtl")

    def test_harvester_mesh_spec(self):
        b = build_harvester_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_harv.obj", f"{self.output_dir}/test_harv.mtl")
        self.assertGreaterEqual(res["verts_count"], 400)
        self.assertGreaterEqual(res["faces_count"], 600)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_CopperCoil", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_harv.obj"):
            os.remove(f"{self.output_dir}/test_harv.obj")
        if os.path.exists(f"{self.output_dir}/test_harv.mtl"):
            os.remove(f"{self.output_dir}/test_harv.mtl")

    def test_wall_mesh_spec(self):
        b = build_wall_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_wall.obj", f"{self.output_dir}/test_wall.mtl")
        self.assertGreaterEqual(res["verts_count"], 80)
        self.assertGreaterEqual(res["faces_count"], 120)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_FactionArmor", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_wall.obj"):
            os.remove(f"{self.output_dir}/test_wall.obj")
        if os.path.exists(f"{self.output_dir}/test_wall.mtl"):
            os.remove(f"{self.output_dir}/test_wall.mtl")

    def test_purifier_mesh_spec(self):
        b = build_purifier_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_purifier.obj", f"{self.output_dir}/test_purifier.mtl")
        self.assertGreaterEqual(res["verts_count"], 350)
        self.assertGreaterEqual(res["faces_count"], 500)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_CopperCoil", res["materials"])
        self.assertIn("Mat_PlasmaCyan", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_purifier.obj"):
            os.remove(f"{self.output_dir}/test_purifier.obj")
        if os.path.exists(f"{self.output_dir}/test_purifier.mtl"):
            os.remove(f"{self.output_dir}/test_purifier.mtl")

    def test_vanguard_mesh_spec(self):
        b = build_vanguard_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_vanguard.obj", f"{self.output_dir}/test_vanguard.mtl")
        self.assertGreaterEqual(res["verts_count"], 400)
        self.assertGreaterEqual(res["faces_count"], 600)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_FactionArmor", res["materials"])
        self.assertIn("Mat_CopperCoil", res["materials"])
        self.assertIn("Mat_PlasmaCyan", res["materials"])
        self.assertIn("Mat_Optics", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_vanguard.obj"):
            os.remove(f"{self.output_dir}/test_vanguard.obj")
        if os.path.exists(f"{self.output_dir}/test_vanguard.mtl"):
            os.remove(f"{self.output_dir}/test_vanguard.mtl")

    def test_marine_mesh_spec(self):
        b = build_marine_mesh()
        res = write_obj_mtl(b, f"{self.output_dir}/test_marine.obj", f"{self.output_dir}/test_marine.mtl")
        self.assertGreaterEqual(res["verts_count"], 250)
        self.assertGreaterEqual(res["faces_count"], 400)
        self.assertIn("Mat_DarkTitanium", res["materials"])
        self.assertIn("Mat_FactionArmor", res["materials"])
        self.assertIn("Mat_CopperCoil", res["materials"])
        self.assertIn("Mat_PlasmaCyan", res["materials"])
        self.assertIn("Mat_Optics", res["materials"])

        if os.path.exists(f"{self.output_dir}/test_marine.obj"):
            os.remove(f"{self.output_dir}/test_marine.obj")
        if os.path.exists(f"{self.output_dir}/test_marine.mtl"):
            os.remove(f"{self.output_dir}/test_marine.mtl")

    def test_all_models_scale_fit_geodesic_nodes(self):
        results = export_all_models(self.output_dir)
        self.assertEqual(len(results), 7)

        for name in ["turret", "base", "harvester", "wall", "purifier", "vanguard", "marine"]:
            obj_path = f"{self.output_dir}/{name}.obj"
            self.assertTrue(os.path.exists(obj_path))

            xs, ys, zs = [], [], []
            with open(obj_path, "r") as f:
                for line in f:
                    if line.startswith("v "):
                        parts = line.strip().split()
                        xs.append(float(parts[1]))
                        ys.append(float(parts[2]))
                        zs.append(float(parts[3]))

            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            depth = max(zs) - min(zs)

            # Footprint must fit comfortably on a planetary node (width/depth <= 1.25, height <= 0.85)
            self.assertLessEqual(width, 1.25, f"{name} width exceeds node boundary")
            self.assertLessEqual(depth, 1.25, f"{name} depth exceeds node boundary")
            self.assertLessEqual(height, 0.85, f"{name} height exceeds node boundary")

if __name__ == "__main__":
    unittest.main()
