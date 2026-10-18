"""
Módulo de Radar y Alertas de Amenazas en Hemisferio Ciego.
Estilo procedimental puro: funciones matemáticas independientes sin OOP.
Permite proyectar indicadores en la periferia de pantalla para invasores ocultos tras el horizonte planetario.
"""

import math


def vector_length(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def vector_normalize(v):
    length = vector_length(v)
    if length <= 1e-8:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def vector_dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def is_point_occluded_by_sphere(point, camera_pos, sphere_radius):
    """
    Determina analíticamente si un punto sobre una esfera centrada en el origen
    está oculto tras el horizonte esférico visto desde 'camera_pos'.

    Condición geométrica exacta:
    Si la distancia al centro es d = |camera_pos|, el ángulo del horizonte es cos(θ_h) = R / d.
    El punto es visible si dot(normal_punto, dir_camara) >= R / d.
    Si dot < R / d, el punto está oculto en el hemisferio ciego.
    """
    cam_dist = vector_length(camera_pos)
    if cam_dist <= sphere_radius or cam_dist <= 1e-6:
        return False

    norm_cam = (camera_pos[0] / cam_dist, camera_pos[1] / cam_dist, camera_pos[2] / cam_dist)

    pt_len = vector_length(point)
    if pt_len <= 1e-6:
        return False

    norm_pt = (point[0] / pt_len, point[1] / pt_len, point[2] / pt_len)
    cos_angle = vector_dot(norm_pt, norm_cam)

    horizon_cos = sphere_radius / cam_dist
    # Margen de seguridad leve para ocultamiento claro
    return cos_angle < (horizon_cos - 0.02)


def project_to_camera_screen_dir(point, camera_right, camera_up):
    """
    Proyecta un punto 3D sobre los ejes ortogonales de la pantalla (Right y Up de la cámara).
    Devuelve un vector 2D normalizado (dir_x, dir_y) donde +Y es hacia abajo en pantalla.
    """
    dx = vector_dot(point, camera_right)
    dy = -vector_dot(point, camera_up)  # En pantalla 2D, Y crece hacia abajo

    mag = math.sqrt(dx * dx + dy * dy)
    if mag <= 1e-6:
        return (0.0, -1.0)  # Predeterminado hacia arriba
    return (dx / mag, dy / mag)


def clamp_direction_to_screen_bounds(dir_x, dir_y, screen_w, screen_h, margin=50.0):
    """
    Calcula la posición (sx, sy) en los bordes de la pantalla dentro de los márgenes dados.
    Devuelve (screen_x, screen_y, angle_radians).
    """
    cx = screen_w * 0.5
    cy = screen_h * 0.5

    half_w = max(10.0, cx - margin)
    half_h = max(10.0, cy - margin)

    t_x = half_w / abs(dir_x) if abs(dir_x) > 1e-6 else 1e9
    t_y = half_h / abs(dir_y) if abs(dir_y) > 1e-6 else 1e9

    t = min(t_x, t_y)
    sx = cx + dir_x * t
    sy = cy + dir_y * t

    angle = math.atan2(dir_y, dir_x)
    return (sx, sy, angle)


def get_arrow_glyph(angle_radians):
    """
    Retorna el glifo de flecha direccional en 8 cuadrantes correspondiente al ángulo dado.
    """
    pi = math.pi
    # Normalizar a [-pi, pi]
    a = (angle_radians + pi) % (2.0 * pi) - pi
    step = pi / 4.0

    if -step * 0.5 <= a < step * 0.5:
        return "➡"
    elif step * 0.5 <= a < step * 1.5:
        return "↘"
    elif step * 1.5 <= a < step * 2.5:
        return "⬇"
    elif step * 2.5 <= a < step * 3.5:
        return "↙"
    elif a >= step * 3.5 or a < -step * 3.5:
        return "⬅"
    elif -step * 3.5 <= a < -step * 2.5:
        return "↖"
    elif -step * 2.5 <= a < -step * 1.5:
        return "⬆"
    else:
        return "↗"


def compute_threat_indicators(invaders, nodes_data, camera_pos, camera_right, camera_up,
                              planet_radius, screen_w, screen_h, base_node_id, margin=50.0):
    """
    Genera la lista de indicadores de amenaza para el HUD/Radar.
    Filtra los invasores vivos y determina si están ocultos en el hemisferio ciego.
    """
    indicators = []

    for inv in invaders:
        if inv.get("state") in ("dead", "spawning"):
            continue

        nid = inv.get("current_node")
        if nid not in nodes_data:
            continue

        pos = nodes_data[nid]["pos"]
        occluded = is_point_occluded_by_sphere(pos, camera_pos, planet_radius)

        # Si está en el hemisferio ciego (oculto tras el horizonte planetario)
        if occluded:
            dir_x, dir_y = project_to_camera_screen_dir(pos, camera_right, camera_up)
            sx, sy, angle = clamp_direction_to_screen_bounds(dir_x, dir_y, screen_w, screen_h, margin)
            arrow = get_arrow_glyph(angle)

            path = inv.get("path", [])
            path_idx = inv.get("path_index", 0)
            remaining_hops = max(0, len(path) - 1 - path_idx)

            indicators.append({
                "invader_id": inv["id"],
                "archetype": inv.get("archetype", "crawler"),
                "hp": inv.get("hp", 0.0),
                "max_hp": inv.get("max_hp", 1.0),
                "current_node": nid,
                "remaining_hops": remaining_hops,
                "screen_pos": (sx, sy),
                "angle": angle,
                "arrow": arrow,
                "is_occluded": True,
                "world_pos": pos,
            })

    return indicators
