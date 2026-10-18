"""
Unit tests para el módulo matemático de la Icosfera.
"""

import math
import sys
import unittest
from pathlib import Path

# Agregar la raíz del proyecto al sys.path para importar logic
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.icosphere import (
    create_base_icosahedron,
    create_icosphere,
    get_spherical_distance,
    get_nodes_within_hops,
    find_shortest_path,
)


class TestIcosphereMath(unittest.TestCase):

    def test_base_icosahedron_topology(self):
        vertices, faces = create_base_icosahedron(radius=1.0)
        self.assertEqual(len(vertices), 12, "El icosaedro base debe tener exactamente 12 vértices")
        self.assertEqual(len(faces), 20, "El icosaedro base debe tener exactamente 20 caras triangulares")

        # Verificar que todos los vértices estén sobre la esfera de radio 1.0
        for x, y, z in vertices:
            dist = math.sqrt(x * x + y * y + z * z)
            self.assertAlmostEqual(dist, 1.0, places=5)

    def test_subdivision_scales(self):
        # Subdivisión 0 -> 12 nodos
        iso_0 = create_icosphere(subdivisions=0, radius=5.0)
        self.assertEqual(iso_0["node_count"], 12)
        self.assertEqual(len(iso_0["faces"]), 20)

        # Subdivisión 1 -> 42 nodos
        iso_1 = create_icosphere(subdivisions=1, radius=5.0)
        self.assertEqual(iso_1["node_count"], 42)
        self.assertEqual(len(iso_1["faces"]), 80)

        # Subdivisión 2 -> 162 nodos
        iso_2 = create_icosphere(subdivisions=2, radius=5.0)
        self.assertEqual(iso_2["node_count"], 162)
        self.assertEqual(len(iso_2["faces"]), 320)

        # Subdivisión 3 -> 642 nodos (Nueva escala expandida)
        iso_3 = create_icosphere(subdivisions=3, radius=5.0)
        self.assertEqual(iso_3["node_count"], 642)
        self.assertEqual(len(iso_3["faces"]), 1280)

        from logic.icosphere import find_antipodal_node
        antipode = find_antipodal_node(iso_3["nodes"], 0)
        self.assertNotEqual(antipode, 0)
        # La distancia entre antípodas debe ser prácticamente pi * R
        dist = get_spherical_distance(iso_3["nodes"][0]["pos"], iso_3["nodes"][antipode]["pos"], 5.0)
        self.assertAlmostEqual(dist, math.pi * 5.0, delta=0.5)

    def test_node_neighbors_valence(self):
        # En una icosfera geodésica, exactamente 12 nodos tienen valencia 5 (los vértices originales)
        # y el resto tiene valencia 6.
        iso = create_icosphere(subdivisions=2, radius=1.0)
        valences = [len(n["neighbors"]) for n in iso["nodes"].values()]

        five_count = valences.count(5)
        six_count = valences.count(6)

        self.assertEqual(five_count, 12, "Exactamente 12 nodos deben tener 5 vecinos")
        self.assertEqual(six_count, 162 - 12, "Los 150 nodos restantes deben tener 6 vecinos")

    def test_spherical_distance(self):
        radius = 10.0
        p_north = (0.0, radius, 0.0)
        p_south = (0.0, -radius, 0.0)
        p_equator = (radius, 0.0, 0.0)

        # Mismo punto
        self.assertAlmostEqual(get_spherical_distance(p_north, p_north, radius), 0.0, places=5)

        # Puntos opuestos (antípodas) -> distancia = pi * R
        dist_antipodal = get_spherical_distance(p_north, p_south, radius)
        self.assertAlmostEqual(dist_antipodal, math.pi * radius, places=5)

        # Puntos ortogonales -> distancia = (pi / 2) * R
        dist_ortho = get_spherical_distance(p_north, p_equator, radius)
        self.assertAlmostEqual(dist_ortho, (math.pi / 2.0) * radius, places=5)

    def test_nodes_within_hops(self):
        iso = create_icosphere(subdivisions=2, radius=1.0)
        nodes = iso["nodes"]

        # 0 saltos -> solo el nodo raíz
        hops_0 = get_nodes_within_hops(nodes, start_id=0, max_hops=0)
        self.assertEqual(hops_0, {0})

        # 1 salto -> nodo raíz + sus vecinos inmediatos
        hops_1 = get_nodes_within_hops(nodes, start_id=0, max_hops=1)
        expected_1 = {0} | set(nodes[0]["neighbors"])
        self.assertEqual(hops_1, expected_1)

        # 2 saltos -> debe contener a hops_1 y expandirse a los vecinos de estos
        hops_2 = get_nodes_within_hops(nodes, start_id=0, max_hops=2)
        self.assertTrue(hops_1.issubset(hops_2))
        self.assertGreater(len(hops_2), len(hops_1))

    def test_shortest_path(self):
        iso = create_icosphere(subdivisions=2, radius=1.0)
        nodes = iso["nodes"]

        # Ruta de un nodo a sí mismo
        path_self = find_shortest_path(nodes, 5, 5)
        self.assertEqual(path_self, [5])

        # Ruta entre vecinos inmediatos
        neighbor = nodes[0]["neighbors"][0]
        path_neighbor = find_shortest_path(nodes, 0, neighbor)
        self.assertEqual(path_neighbor, [0, neighbor])

        # Ruta entre nodos distantes
        start_id = 0
        target_id = 85
        path = find_shortest_path(nodes, start_id, target_id)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], start_id)
        self.assertEqual(path[-1], target_id)

        # Verificar que cada paso en el camino sea realmente vecino del siguiente
        for i in range(len(path) - 1):
            curr_id = path[i]
            next_id = path[i + 1]
            self.assertIn(next_id, nodes[curr_id]["neighbors"])


if __name__ == "__main__":
    unittest.main()
