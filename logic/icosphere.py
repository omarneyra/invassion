"""
Módulo matemático para la generación y navegación del grafo de la Icosfera.
Enfoque procedimental puro: funciones independientes y estructuras de datos planas (diccionarios y listas).
"""

import math
from collections import deque


def _normalize(v, radius=1.0):
    x, y, z = v
    length = math.sqrt(x * x + y * y + z * z)
    if length == 0:
        return (0.0, 0.0, 0.0)
    scale = radius / length
    return (round(x * scale, 6), round(y * scale, 6), round(z * scale, 6))


def _get_midpoint(v1, v2, radius=1.0):
    mid = (
        (v1[0] + v2[0]) * 0.5,
        (v1[1] + v2[1]) * 0.5,
        (v1[2] + v2[2]) * 0.5,
    )
    return _normalize(mid, radius)


def create_base_icosahedron(radius=1.0):
    """
    Crea los 12 vértices iniciales y 20 caras triangulares de un icosaedro regular.
    """
    phi = (1.0 + math.sqrt(5.0)) * 0.5

    raw_vertices = [
        (-1.0,  phi, 0.0),
        ( 1.0,  phi, 0.0),
        (-1.0, -phi, 0.0),
        ( 1.0, -phi, 0.0),
        (0.0, -1.0,  phi),
        (0.0,  1.0,  phi),
        (0.0, -1.0, -phi),
        (0.0,  1.0, -phi),
        ( phi, 0.0, -1.0),
        ( phi, 0.0,  1.0),
        (-phi, 0.0, -1.0),
        (-phi, 0.0,  1.0),
    ]

    vertices = [_normalize(v, radius) for v in raw_vertices]

    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]

    return vertices, faces


def create_icosphere(subdivisions=2, radius=1.0):
    """
    Genera el grafo completo de una icosfera.
    Retorna un diccionario plano con:
      - 'nodes': diccionario {id: {'id': int, 'pos': (x,y,z), 'neighbors': [ids]}}
      - 'faces': lista de tuplas (i1, i2, i3)
      - 'node_count': cantidad total de nodos (162 para subdivisión 2)
    """
    vertices, faces = create_base_icosahedron(radius)
    midpoint_cache = {}

    def get_or_create_midpoint(idx1, idx2):
        key = (min(idx1, idx2), max(idx1, idx2))
        if key in midpoint_cache:
            return midpoint_cache[key]

        v1 = vertices[idx1]
        v2 = vertices[idx2]
        new_v = _get_midpoint(v1, v2, radius)
        new_idx = len(vertices)
        vertices.append(new_v)
        midpoint_cache[key] = new_idx
        return new_idx

    for _ in range(subdivisions):
        new_faces = []
        for v1, v2, v3 in faces:
            m12 = get_or_create_midpoint(v1, v2)
            m23 = get_or_create_midpoint(v2, v3)
            m31 = get_or_create_midpoint(v3, v1)

            new_faces.append((v1, m12, m31))
            new_faces.append((v2, m23, m12))
            new_faces.append((v3, m31, m23))
            new_faces.append((m12, m23, m31))
        faces = new_faces

    # Construir lista de adyacencias (vecinos)
    adjacency = {i: set() for i in range(len(vertices))}
    for a, b, c in faces:
        adjacency[a].add(b)
        adjacency[a].add(c)
        adjacency[b].add(a)
        adjacency[b].add(c)
        adjacency[c].add(a)
        adjacency[c].add(b)

    nodes = {}
    for idx, pos in enumerate(vertices):
        nodes[idx] = {
            "id": idx,
            "pos": pos,
            "neighbors": sorted(list(adjacency[idx])),
        }

    return {
        "nodes": nodes,
        "faces": faces,
        "node_count": len(vertices),
        "radius": radius,
        "subdivisions": subdivisions,
    }


def get_spherical_distance(pos1, pos2, radius=1.0):
    """
    Calcula la distancia sobre la superficie de la esfera (ortodrómica / gran círculo).
    """
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2
    # Producto escalar
    dot = (x1 * x2 + y1 * y2 + z1 * z2) / (radius * radius)
    dot = max(-1.0, min(1.0, dot))
    angle = math.acos(dot)
    return radius * angle


def get_nodes_within_hops(nodes, start_id, max_hops):
    """
    Retorna el conjunto de IDs de nodos alcanzables a un máximo de `max_hops` saltos en el grafo.
    """
    if start_id not in nodes:
        return set()

    visited = {start_id}
    queue = deque([(start_id, 0)])

    while queue:
        curr_id, hops = queue.popleft()
        if hops < max_hops:
            for neighbor in nodes[curr_id]["neighbors"]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, hops + 1))

    return visited


def find_shortest_path(nodes, start_id, target_id, excluded_nodes=None):
    """
    Encuentra la ruta geodésica más corta entre dos nodos usando BFS sobre el grafo.
    Permite opcionalmente omitir un conjunto de 'excluded_nodes'.
    Retorna la lista ordenada de IDs de nodos desde start_id hasta target_id.
    """
    if start_id not in nodes or target_id not in nodes:
        return []
    if start_id == target_id:
        return [start_id]

    excluded = set(excluded_nodes) if excluded_nodes else set()
    excluded.discard(start_id)
    excluded.discard(target_id)

    queue = deque([start_id])
    predecessor = {start_id: None}

    while queue:
        curr_id = queue.popleft()
        if curr_id == target_id:
            break

        for neighbor in nodes[curr_id]["neighbors"]:
            if neighbor not in predecessor and neighbor not in excluded:
                predecessor[neighbor] = curr_id
                queue.append(neighbor)

    if target_id not in predecessor:
        return []

    # Reconstruir camino
    path = []
    curr = target_id
    while curr is not None:
        path.append(curr)
        curr = predecessor[curr]

    path.reverse()
    return path


def find_antipodal_node(nodes, start_node_id):
    """
    Encuentra el nodo diametralmente opuesto (antípoda) en la esfera buscando el producto punto mínimo.
    """
    if start_node_id not in nodes:
        return 0
    start_pos = nodes[start_node_id]["pos"]
    best_id = start_node_id
    min_dot = 2.0
    for nid, ndata in nodes.items():
        p = ndata["pos"]
        dot = start_pos[0] * p[0] + start_pos[1] * p[1] + start_pos[2] * p[2]
        if dot < min_dot:
            min_dot = dot
            best_id = nid
    return best_id
