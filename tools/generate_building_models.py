"""
Procedural 3D Model Generator for Invassion (Faction 1: Imperio Solar / Cyber-Industrial).
Strictly follows functional/procedural Python (NO OOP, NO classes).
Provides a comprehensive architectural kit and building generators for the entire faction:
1. Turret (Pulse Defense Cannon)
2. Base (Planetary Command Core)
3. Harvester (Industrial Geothermal Extractor)
4. Wall (Heavy Perimeter Barrier / Shield Pylon)
5. Purifier (Orbital Purification Emitter)

All models share the same unified PBR industrial aesthetic:
- Heavy bunker plinths with corner reinforcement brackets
- Articulated outriggers with hydraulic struts and track footpads
- Stepped turntables and mechanical gear collars
- Dual hydraulic elevation/actuation rams
- Concentric copper induction coils (Mat_CopperCoil)
- Recessed plasma channels with segmented cooling grills
- Commander cupolas with optical visor slits
- Full CCW face winding, normals, UVs, and PBR MTL export.
"""

import math
import os

# ==============================================================================
# 1. CORE PROCEDURAL MESH BUILDER (DICTIONARY STATE, PURE FUNCTIONS)
# ==============================================================================

def make_builder():
    """Initializes a new mesh builder state dictionary."""
    return {
        "verts": [],
        "normals": [],
        "uvs": [],
        "faces": {} # mat_name -> list of [(v, vt, vn), ...]
    }

def add_vertex(b, x, y, z):
    b["verts"].append((round(x, 5), round(y, 5), round(z, 5)))
    return len(b["verts"])

def add_normal(b, nx, ny, nz):
    mag = math.sqrt(nx*nx + ny*ny + nz*nz)
    if mag > 1e-6:
        b["normals"].append((round(nx/mag, 4), round(ny/mag, 4), round(nz/mag, 4)))
    else:
        b["normals"].append((0.0, 1.0, 0.0))
    return len(b["normals"])

def add_uv(b, u, v):
    b["uvs"].append((round(u, 4), round(v, 4)))
    return len(b["uvs"])

def add_quad(b, v1, v2, v3, v4, n, mat_name):
    vn = add_normal(b, n[0], n[1], n[2])
    t1 = add_uv(b, 0.0, 0.0)
    t2 = add_uv(b, 1.0, 0.0)
    t3 = add_uv(b, 1.0, 1.0)
    t4 = add_uv(b, 0.0, 1.0)
    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []
    # Two CCW triangles forming a quad
    b["faces"][mat_name].append([(v1, t1, vn), (v2, t2, vn), (v3, t3, vn)])
    b["faces"][mat_name].append([(v1, t1, vn), (v3, t3, vn), (v4, t4, vn)])

def rotate_point_x(x, y, z, angle_rad, pivot_y=0.0, pivot_z=0.0):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dy = y - pivot_y
    dz = z - pivot_z
    ry = pivot_y + dy * cos_a + dz * sin_a
    rz = pivot_z - dy * sin_a + dz * cos_a
    return (x, ry, rz)

def rotate_normal_x(nx, ny, nz, angle_rad):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rny = ny * cos_a + nz * sin_a
    rnz = -ny * sin_a + nz * cos_a
    return (nx, rny, rnz)

def add_box(b, cx, cy, cz, sx, sy, sz, mat_name, rx=0.0, py=0.0, pz=0.0):
    hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
    raw_corners = [
        (cx - hx, cy - hy, cz - hz), # 0: ---
        (cx + hx, cy - hy, cz - hz), # 1: +--
        (cx + hx, cy + hy, cz - hz), # 2: ++-
        (cx - hx, cy + hy, cz - hz), # 3: -+-
        (cx - hx, cy - hy, cz + hz), # 4: --+
        (cx + hx, cy - hy, cz + hz), # 5: +-+
        (cx + hx, cy + hy, cz + hz), # 6: +++
        (cx - hx, cy + hy, cz + hz), # 7: -++
    ]

    if abs(rx) > 1e-5:
        c = [add_vertex(b, *rotate_point_x(pt[0], pt[1], pt[2], rx, py, pz)) for pt in raw_corners]
        n_fwd = rotate_normal_x(0, 0, 1, rx)
        n_bck = rotate_normal_x(0, 0, -1, rx)
        n_top = rotate_normal_x(0, 1, 0, rx)
        n_bot = rotate_normal_x(0, -1, 0, rx)
        n_rgt = rotate_normal_x(1, 0, 0, rx)
        n_lft = rotate_normal_x(-1, 0, 0, rx)
    else:
        c = [add_vertex(b, *pt) for pt in raw_corners]
        n_fwd = (0, 0, 1)
        n_bck = (0, 0, -1)
        n_top = (0, 1, 0)
        n_bot = (0, -1, 0)
        n_rgt = (1, 0, 0)
        n_lft = (-1, 0, 0)

    # CCW wound external faces
    add_quad(b, c[4], c[5], c[6], c[7], n_fwd, mat_name) # Front (+Z)
    add_quad(b, c[1], c[0], c[3], c[2], n_bck, mat_name) # Back (-Z)
    add_quad(b, c[7], c[6], c[2], c[3], n_top, mat_name) # Top (+Y)
    add_quad(b, c[0], c[1], c[5], c[4], n_bot, mat_name) # Bottom (-Y)
    add_quad(b, c[5], c[1], c[2], c[6], n_rgt, mat_name) # Right (+X)
    add_quad(b, c[0], c[4], c[7], c[3], n_lft, mat_name) # Left (-X)

def add_cylinder_y(b, cx, cy, cz, r_top, r_bot, height, segments, mat_name):
    hy = height * 0.5
    top_verts = []
    bot_verts = []
    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        ca, sa = math.cos(angle), math.sin(angle)
        top_verts.append(add_vertex(b, cx + ca * r_top, cy + hy, cz + sa * r_top))
        bot_verts.append(add_vertex(b, cx + ca * r_bot, cy - hy, cz + sa * r_bot))

    top_center = add_vertex(b, cx, cy + hy, cz)
    bot_center = add_vertex(b, cx, cy - hy, cz)

    vn_up = add_normal(b, 0, 1, 0)
    vn_down = add_normal(b, 0, -1, 0)
    t0 = add_uv(b, 0.5, 0.5)

    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    for i in range(segments):
        next_i = (i + 1) % segments
        b["faces"][mat_name].append([(top_center, t0, vn_up), (top_verts[next_i], t0, vn_up), (top_verts[i], t0, vn_up)])
        b["faces"][mat_name].append([(bot_center, t0, vn_down), (bot_verts[i], t0, vn_down), (bot_verts[next_i], t0, vn_down)])
        angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
        n_side = (math.cos(angle_mid), 0, math.sin(angle_mid))
        add_quad(b, bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], n_side, mat_name)

def add_cylinder_z(b, cx, cy, cz, r_front, r_back, length, segments, mat_name, rx=0.0, py=0.0, pz=0.0):
    hz = length * 0.5
    front_verts = []
    back_verts = []
    elevated = abs(rx) > 1e-5

    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        ca, sa = math.cos(angle), math.sin(angle)
        pt_f = (cx + ca * r_front, cy + sa * r_front, cz + hz)
        pt_b = (cx + ca * r_back, cy + sa * r_back, cz - hz)
        if elevated:
            front_verts.append(add_vertex(b, *rotate_point_x(pt_f[0], pt_f[1], pt_f[2], rx, py, pz)))
            back_verts.append(add_vertex(b, *rotate_point_x(pt_b[0], pt_b[1], pt_b[2], rx, py, pz)))
        else:
            front_verts.append(add_vertex(b, *pt_f))
            back_verts.append(add_vertex(b, *pt_b))

    if elevated:
        front_center = add_vertex(b, *rotate_point_x(cx, cy, cz + hz, rx, py, pz))
        back_center = add_vertex(b, *rotate_point_x(cx, cy, cz - hz, rx, py, pz))
        vn_fwd = add_normal(b, *rotate_normal_x(0, 0, 1, rx))
        vn_bck = add_normal(b, *rotate_normal_x(0, 0, -1, rx))
    else:
        front_center = add_vertex(b, cx, cy, cz + hz)
        back_center = add_vertex(b, cx, cy, cz - hz)
        vn_fwd = add_normal(b, 0, 0, 1)
        vn_bck = add_normal(b, 0, 0, -1)

    t0 = add_uv(b, 0.5, 0.5)
    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    for i in range(segments):
        next_i = (i + 1) % segments
        b["faces"][mat_name].append([(front_center, t0, vn_fwd), (front_verts[i], t0, vn_fwd), (front_verts[next_i], t0, vn_fwd)])
        b["faces"][mat_name].append([(back_center, t0, vn_bck), (back_verts[next_i], t0, vn_bck), (back_verts[i], t0, vn_bck)])
        angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
        raw_n_side = (math.cos(angle_mid), math.sin(angle_mid), 0)
        n_side = rotate_normal_x(raw_n_side[0], raw_n_side[1], raw_n_side[2], rx) if elevated else raw_n_side
        add_quad(b, back_verts[i], back_verts[next_i], front_verts[next_i], front_verts[i], n_side, mat_name)

def add_cylinder_between(b, p1, p2, radius, segments, mat_name):
    """Draws a solid cylinder connecting any two 3D points p1 and p2."""
    ax, ay, az = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    length = math.sqrt(ax*ax + ay*ay + az*az)
    if length < 1e-5:
        return

    dx, dy, dz = ax / length, ay / length, az / length
    if abs(dy) < 0.9:
        rx, ry, rz = 0.0, 1.0, 0.0
    else:
        rx, ry, rz = 1.0, 0.0, 0.0

    ux = dy * rz - dz * ry
    uy = dz * rx - dx * rz
    uz = dx * ry - dy * rx
    umag = math.sqrt(ux*ux + uy*uy + uz*uz)
    ux, uy, uz = ux / umag, uy / umag, uz / umag

    vx = dy * uz - dz * uy
    vy = dz * ux - dx * uz
    vz = dx * uy - dy * ux

    bot_verts, top_verts = [], []
    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        ca, sa = math.cos(angle) * radius, math.sin(angle) * radius
        ox = ca * ux + sa * vx
        oy = ca * uy + sa * vy
        oz = ca * uz + sa * vz
        bot_verts.append(add_vertex(b, p1[0] + ox, p1[1] + oy, p1[2] + oz))
        top_verts.append(add_vertex(b, p2[0] + ox, p2[1] + oy, p2[2] + oz))

    b_center = add_vertex(b, *p1)
    t_center = add_vertex(b, *p2)
    vn_bot = add_normal(b, -dx, -dy, -dz)
    vn_top = add_normal(b, dx, dy, dz)
    t0 = add_uv(b, 0.5, 0.5)

    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    for i in range(segments):
        next_i = (i + 1) % segments
        b["faces"][mat_name].append([(b_center, t0, vn_bot), (bot_verts[next_i], t0, vn_bot), (bot_verts[i], t0, vn_bot)])
        b["faces"][mat_name].append([(t_center, t0, vn_top), (top_verts[i], t0, vn_top), (top_verts[next_i], t0, vn_top)])
        angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
        ca, sa = math.cos(angle_mid), math.sin(angle_mid)
        n_side = (ca * ux + sa * vx, ca * uy + sa * vy, ca * uz + sa * vz)
        add_quad(b, bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], n_side, mat_name)


# ==============================================================================
# 2. REUSABLE ARCHITECTURAL SUBASSEMBLIES (IMPERIO SOLAR FACTION KIT)
# ==============================================================================

def add_bunker_plinth(b, cx=0.0, cy=0.03, cz=0.0, width=0.88, depth=0.88, height=0.06):
    """Heavy industrial bunker base slab with corner brackets and collar ring."""
    add_box(b, cx, cy, cz, width, height, depth, "Mat_DarkTitanium")
    bx_off = width * 0.44
    bz_off = depth * 0.44
    b_size = width * 0.11
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            add_box(b, cx + sx * bx_off, cy + height * 0.35, cz + sz * bz_off, b_size, height * 1.3, b_size, "Mat_DarkTitanium")
    add_cylinder_y(b, cx, cy + height * 0.75, cz, width * 0.48, width * 0.52, height * 0.5, 16, "Mat_DarkTitanium")

def add_outriggers(b, radius=0.32, count=4):
    """Articulated stabilizer arms with hydraulic struts and track footpads."""
    for i in range(count):
        angle = i * (2.0 * math.pi / count) + (math.pi / count)
        ca, sa = math.cos(angle), math.sin(angle)
        # Shoulder mount
        add_box(b, ca * radius, 0.10, sa * radius, 0.12, 0.06, 0.12, "Mat_DarkTitanium")
        # Hydraulic diagonal strut
        p_sh = (ca * (radius - 0.02), 0.10, sa * (radius - 0.02))
        p_ft = (ca * (radius + 0.13), 0.04, sa * (radius + 0.13))
        add_cylinder_between(b, p_sh, p_ft, 0.024, 8, "Mat_DarkTitanium")
        # Heavy track footpad
        add_box(b, ca * (radius + 0.16), 0.035, sa * (radius + 0.16), 0.15, 0.06, 0.16, "Mat_DarkTitanium")
        # Status telemetry indicator
        add_box(b, ca * (radius + 0.16), 0.07, sa * (radius + 0.16), 0.04, 0.02, 0.04, "Mat_PlasmaCyan")

def add_turntable(b, cy=0.105, r_base=0.34, r_ring=0.30, height=0.03):
    """Concentric mechanical gear ring and faction accent collar."""
    add_cylinder_y(b, 0, cy, 0, r_base - 0.01, r_base + 0.01, height, 16, "Mat_DarkTitanium")
    add_cylinder_y(b, 0, cy + height, 0, r_ring - 0.01, r_ring + 0.01, height, 16, "Mat_FactionArmor")
    add_cylinder_y(b, 0, cy + height * 2.0, 0, r_ring - 0.03, r_ring - 0.01, height, 16, "Mat_DarkTitanium")

def add_commander_cupola(b, cx=0.0, cy=0.365, cz=-0.06):
    """Armored dome with optical vision slits, sensor turret pod, and comms antennae."""
    add_cylinder_y(b, cx, cy, cz, 0.09, 0.11, 0.05, 8, "Mat_DarkTitanium")
    add_cylinder_y(b, cx, cy + 0.03, cz, 0.065, 0.075, 0.02, 8, "Mat_Optics")
    # Sensor pod
    add_box(b, cx + 0.09, cy + 0.07, cz + 0.03, 0.07, 0.06, 0.09, "Mat_DarkTitanium")
    add_box(b, cx + 0.09, cy + 0.085, cz + 0.08, 0.04, 0.018, 0.012, "Mat_Optics")
    add_box(b, cx + 0.09, cy + 0.055, cz + 0.08, 0.04, 0.018, 0.012, "Mat_Optics")
    # Antenna needles
    add_cylinder_between(b, (cx - 0.09, cy + 0.015, cz - 0.06), (cx - 0.09, cy + 0.155, cz - 0.06), 0.005, 4, "Mat_DarkTitanium")
    add_cylinder_between(b, (cx + 0.05, cy + 0.015, cz - 0.10), (cx + 0.05, cy + 0.125, cz - 0.10), 0.005, 4, "Mat_DarkTitanium")

def add_recoil_accumulators(b, z_pos=-0.22):
    """4 horizontal recoil buffer canisters with glowing telemetry caps."""
    for ox in [-0.10, 0.10]:
        for oy in [0.24, 0.30]:
            add_cylinder_z(b, ox, oy, z_pos, 0.035, 0.035, 0.12, 8, "Mat_DarkTitanium")
            add_cylinder_z(b, ox, oy, z_pos - 0.065, 0.025, 0.025, 0.012, 8, "Mat_PlasmaCyan")


# ==============================================================================
# 3. CONCRETE BUILDING MODEL BUILDERS
# ==============================================================================

def build_turret_mesh():
    """Builds the full 3D mesh for the Pulse Defense Cannon."""
    b = make_builder()
    ELEVATION_ANGLE = math.radians(7.5)
    PIVOT_Y = 0.30
    PIVOT_Z = 0.04

    # 1. Foundation & Stabilizers
    add_bunker_plinth(b, 0, 0.03, 0, 0.88, 0.88, 0.06)
    add_outriggers(b, 0.32, 4)
    add_turntable(b, 0.105, 0.34, 0.30, 0.03)

    # 2. Armored Carriage & Mantlet
    add_box(b, 0, 0.24, -0.04, 0.36, 0.13, 0.34, "Mat_DarkTitanium")
    add_box(b, 0, 0.31, -0.06, 0.30, 0.07, 0.28, "Mat_FactionArmor")
    add_box(b, -0.21, 0.27, 0.04, 0.05, 0.16, 0.14, "Mat_DarkTitanium")
    add_box(b, 0.21, 0.27, 0.04, 0.05, 0.16, 0.14, "Mat_DarkTitanium")
    add_box(b, 0, PIVOT_Y, PIVOT_Z + 0.10, 0.16, 0.12, 0.20, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
    add_box(b, 0, PIVOT_Y + 0.05, PIVOT_Z + 0.08, 0.12, 0.04, 0.16, "Mat_FactionArmor", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)

    # Hydraulic Elevation Rams
    for hx in [-0.10, 0.10]:
        add_cylinder_between(b, (hx, 0.165, 0.14), (hx, 0.23, 0.11), 0.022, 8, "Mat_DarkTitanium")
        add_cylinder_between(b, (hx, 0.23, 0.11), (hx, 0.29, 0.08), 0.015, 8, "Mat_FactionArmor")

    # Side Trunnion Recoil Hubs
    add_cylinder_between(b, (-0.24, PIVOT_Y, PIVOT_Z), (-0.20, PIVOT_Y, PIVOT_Z), 0.085, 12, "Mat_DarkTitanium")
    add_cylinder_between(b, (-0.25, PIVOT_Y, PIVOT_Z), (-0.24, PIVOT_Y, PIVOT_Z), 0.055, 12, "Mat_FactionArmor")
    add_cylinder_between(b, (0.20, PIVOT_Y, PIVOT_Z), (0.24, PIVOT_Y, PIVOT_Z), 0.085, 12, "Mat_DarkTitanium")
    add_cylinder_between(b, (0.24, PIVOT_Y, PIVOT_Z), (0.25, PIVOT_Y, PIVOT_Z), 0.055, 12, "Mat_FactionArmor")

    add_commander_cupola(b, 0, 0.365, -0.06)
    add_recoil_accumulators(b, -0.22)

    # 3. Twin Railgun Cannons
    for bx in [-0.165, 0.165]:
        add_box(b, bx, PIVOT_Y, PIVOT_Z, 0.11, 0.12, 0.14, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        # Copper induction coils
        add_cylinder_z(b, bx, PIVOT_Y, PIVOT_Z + 0.09, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_cylinder_z(b, bx, PIVOT_Y, PIVOT_Z + 0.13, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_cylinder_z(b, bx, PIVOT_Y, PIVOT_Z + 0.17, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_cylinder_z(b, bx, PIVOT_Y, PIVOT_Z + 0.11, 0.057, 0.057, 0.014, 10, "Mat_PlasmaCyan", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_cylinder_z(b, bx, PIVOT_Y, PIVOT_Z + 0.15, 0.057, 0.057, 0.014, 10, "Mat_PlasmaCyan", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)

        # Upper & Lower Rail Beams
        add_box(b, bx, PIVOT_Y + 0.038, PIVOT_Z + 0.36, 0.095, 0.032, 0.36, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx, PIVOT_Y - 0.038, PIVOT_Z + 0.36, 0.095, 0.032, 0.36, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        side_dir = 1.0 if bx > 0 else -1.0
        add_box(b, bx + side_dir * 0.048, PIVOT_Y, PIVOT_Z + 0.33, 0.014, 0.08, 0.28, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx - side_dir * 0.048, PIVOT_Y, PIVOT_Z + 0.33, 0.014, 0.08, 0.28, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx, PIVOT_Y, PIVOT_Z + 0.36, 0.048, 0.048, 0.34, "Mat_PlasmaCyan", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)

        for vz in [0.25, 0.31, 0.37, 0.43]:
            add_box(b, bx, PIVOT_Y + 0.042, PIVOT_Z + vz, 0.052, 0.010, 0.020, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
            add_box(b, bx, PIVOT_Y - 0.042, PIVOT_Z + vz, 0.052, 0.010, 0.020, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
            add_box(b, bx + side_dir * 0.052, PIVOT_Y, PIVOT_Z + vz, 0.012, 0.022, 0.025, "Mat_PlasmaCyan", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)

        add_box(b, bx, PIVOT_Y, PIVOT_Z + 0.55, 0.110, 0.120, 0.05, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx, PIVOT_Y + 0.055, PIVOT_Z + 0.575, 0.065, 0.02, 0.025, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx, PIVOT_Y - 0.055, PIVOT_Z + 0.575, 0.065, 0.02, 0.025, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx - 0.054, PIVOT_Y, PIVOT_Z + 0.575, 0.02, 0.065, 0.025, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx + 0.054, PIVOT_Y, PIVOT_Z + 0.575, 0.02, 0.065, 0.025, "Mat_DarkTitanium", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)
        add_box(b, bx, PIVOT_Y, PIVOT_Z + 0.578, 0.052, 0.052, 0.01, "Mat_PlasmaCyan", rx=ELEVATION_ANGLE, py=PIVOT_Y, pz=PIVOT_Z)

    return b

def build_base_mesh():
    """Builds the 3D mesh for the Planetary Command Core (Fortress HQ)."""
    b = make_builder()
    # 1. Octagonal Citadel Foundation Plinth
    add_bunker_plinth(b, 0, 0.04, 0, 1.05, 1.05, 0.08)
    add_outriggers(b, 0.40, 4)

    # 2. Stepped Fortress Hull
    add_cylinder_y(b, 0, 0.15, 0, 0.42, 0.48, 0.14, 8, "Mat_DarkTitanium")
    add_cylinder_y(b, 0, 0.24, 0, 0.36, 0.40, 0.06, 8, "Mat_FactionArmor")
    add_cylinder_y(b, 0, 0.30, 0, 0.28, 0.32, 0.06, 8, "Mat_DarkTitanium")

    # 3. Glowing Planetary Shield Reactor Core
    add_cylinder_y(b, 0, 0.38, 0, 0.18, 0.18, 0.10, 12, "Mat_PlasmaCyan")
    # Reactor Containment Rings with Copper Conduits
    add_cylinder_y(b, 0, 0.35, 0, 0.21, 0.21, 0.02, 12, "Mat_CopperCoil")
    add_cylinder_y(b, 0, 0.41, 0, 0.21, 0.21, 0.02, 12, "Mat_CopperCoil")

    # 4. Four Orbital Relay Comms Pylons
    for i in range(4):
        angle = i * (math.pi * 0.5)
        ca, sa = math.cos(angle), math.sin(angle)
        px, pz = ca * 0.32, sa * 0.32
        add_box(b, px, 0.34, pz, 0.08, 0.18, 0.08, "Mat_DarkTitanium")
        add_cylinder_between(b, (px, 0.43, pz), (px, 0.58, pz), 0.008, 4, "Mat_CopperCoil")
        add_box(b, px, 0.59, pz, 0.025, 0.025, 0.025, "Mat_PlasmaCyan")

    # 5. Commander Observation Cupola on Top
    add_commander_cupola(b, 0, 0.46, 0)
    return b

def build_harvester_mesh():
    """Builds the 3D mesh for the Industrial Mining Rig / Energy Extractor."""
    b = make_builder()
    # 1. Industrial Anchor Foundation
    add_bunker_plinth(b, 0, 0.03, 0, 0.82, 0.82, 0.06)
    add_outriggers(b, 0.30, 4)

    # 2. Central Rotary Bore Housing
    add_cylinder_y(b, 0, 0.14, 0, 0.30, 0.34, 0.12, 12, "Mat_DarkTitanium")
    add_cylinder_y(b, 0, 0.21, 0, 0.26, 0.28, 0.04, 12, "Mat_FactionArmor")

    # 3. Glowing Geothermal Separation Chamber
    add_cylinder_y(b, 0, 0.29, 0, 0.22, 0.22, 0.12, 12, "Mat_PlasmaCyan")
    # Copper heat exchange coils wrapped around chamber
    for cy in [0.25, 0.29, 0.33]:
        add_cylinder_y(b, 0, cy, 0, 0.24, 0.24, 0.02, 12, "Mat_CopperCoil")

    # 4. Dual Industrial Transfer Conduits
    for sx in [-0.22, 0.22]:
        add_cylinder_between(b, (sx, 0.08, -0.10), (sx, 0.32, 0.05), 0.030, 8, "Mat_DarkTitanium")
        add_cylinder_between(b, (sx, 0.32, 0.05), (sx * 0.5, 0.38, 0.0), 0.022, 8, "Mat_CopperCoil")

    # 5. Top Exhaust Smokestack & Pressure Relief Valves
    add_cylinder_y(b, 0, 0.40, 0, 0.12, 0.16, 0.10, 8, "Mat_DarkTitanium")
    add_cylinder_y(b, 0, 0.46, 0, 0.08, 0.08, 0.04, 8, "Mat_Optics")
    return b

def build_wall_mesh():
    """Builds the 3D mesh for the Heavy Perimeter Defense Barrier."""
    b = make_builder()
    # 1. Foundation Slab
    add_box(b, 0, 0.03, 0, 0.88, 0.06, 0.42, "Mat_DarkTitanium")
    for sx in [-0.36, 0.36]:
        add_box(b, sx, 0.05, 0, 0.14, 0.08, 0.46, "Mat_DarkTitanium")

    # 2. Interlocking Armored Chevron Bastions
    add_box(b, 0, 0.18, 0, 0.74, 0.24, 0.24, "Mat_DarkTitanium")
    add_box(b, 0, 0.22, 0.08, 0.64, 0.16, 0.10, "Mat_FactionArmor")

    # 3. Dual Force-Field Projector Pylons
    for sx in [-0.32, 0.32]:
        add_box(b, sx, 0.28, 0, 0.10, 0.32, 0.16, "Mat_DarkTitanium")
        add_cylinder_between(b, (sx, 0.36, 0), (sx, 0.46, 0), 0.024, 8, "Mat_CopperCoil")
        add_box(b, sx, 0.48, 0, 0.04, 0.04, 0.04, "Mat_PlasmaCyan")

    # 4. Central Energy Barrier Emitter Window
    add_box(b, 0, 0.22, 0, 0.38, 0.08, 0.26, "Mat_PlasmaCyan")
    return b

def build_purifier_mesh():
    """Builds the 3D mesh for the Orbital Void Purification Array."""
    b = make_builder()
    # 1. Quad Stabilizing Anchor Base
    add_bunker_plinth(b, 0, 0.03, 0, 0.86, 0.86, 0.06)
    add_outriggers(b, 0.32, 4)

    # 2. Concentric Accelerator Housing
    add_cylinder_y(b, 0, 0.14, 0, 0.32, 0.36, 0.12, 16, "Mat_DarkTitanium")
    add_cylinder_y(b, 0, 0.22, 0, 0.26, 0.28, 0.04, 16, "Mat_FactionArmor")

    # 3. High-Energy Beam Spire with Copper Induction Rings
    add_cylinder_y(b, 0, 0.34, 0, 0.14, 0.20, 0.20, 12, "Mat_DarkTitanium")
    for cy in [0.28, 0.34, 0.40]:
        add_cylinder_y(b, 0, cy, 0, 0.18, 0.18, 0.02, 12, "Mat_CopperCoil")

    # 4. Focusing Plasma Core & Emitter Nozzle
    add_cylinder_y(b, 0, 0.48, 0, 0.10, 0.12, 0.08, 12, "Mat_PlasmaCyan")
    add_cylinder_y(b, 0, 0.54, 0, 0.06, 0.09, 0.04, 12, "Mat_Optics")
    add_box(b, 0, 0.57, 0, 0.04, 0.03, 0.04, "Mat_PlasmaCyan")
    return b


# ==============================================================================
# 4. EXPORT ENGINE (OBJ & MTL WRITER)
# ==============================================================================

def write_obj_mtl(b, output_obj_path, output_mtl_path):
    """Writes builder geometry to Wavefront OBJ & MTL format with full PBR spec."""
    os.makedirs(os.path.dirname(output_obj_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_mtl_path), exist_ok=True)
    mtl_filename = os.path.basename(output_mtl_path)

    with open(output_mtl_path, "w") as f:
        f.write("# Materials for Invassion Imperio Solar (PBR Industrial Spec)\n\n")
        f.write("newmtl Mat_DarkTitanium\nKa 0.22 0.26 0.32\nKd 0.35 0.40 0.48\nKs 0.85 0.88 0.92\nNs 45.0\nd 1.0\n\n")
        f.write("newmtl Mat_FactionArmor\nKa 0.10 0.35 0.20\nKd 0.15 0.55 0.28\nKs 0.60 0.75 0.65\nNs 35.0\nd 1.0\n\n")
        f.write("newmtl Mat_PlasmaCyan\nKa 0.00 0.95 1.00\nKd 0.00 0.98 1.00\nKs 0.10 0.90 1.00\nKe 0.00 0.98 1.00\nNs 100.0\nd 1.0\n\n")
        f.write("newmtl Mat_Optics\nKa 0.04 0.12 0.22\nKd 0.08 0.25 0.40\nKs 0.95 0.98 1.00\nKe 0.02 0.25 0.45\nNs 90.0\nd 1.0\n\n")
        f.write("newmtl Mat_CopperCoil\nKa 0.45 0.25 0.12\nKd 0.75 0.42 0.18\nKs 0.90 0.80 0.65\nKe 0.25 0.12 0.03\nNs 60.0\nd 1.0\n")

    with open(output_obj_path, "w") as f:
        f.write(f"# Invassion Procedural 3D Model\nmtllib {mtl_filename}\no ModelMesh\n\n")
        for v in b["verts"]:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for vt in b["uvs"]:
            f.write(f"vt {vt[0]} {vt[1]}\n")
        for vn in b["normals"]:
            f.write(f"vn {vn[0]} {vn[1]} {vn[2]}\n")

        MATERIAL_ORDER = [
            "Mat_DarkTitanium",
            "Mat_FactionArmor",
            "Mat_PlasmaCyan",
            "Mat_Optics",
            "Mat_CopperCoil"
        ]

        for mat_name in MATERIAL_ORDER:
            if mat_name in b["faces"]:
                f.write(f"\nusemtl {mat_name}\n")
                for face in b["faces"][mat_name]:
                    f_str = " ".join([f"{idx[0]}/{idx[1]}/{idx[2]}" for idx in face])
                    f.write(f"f {f_str}\n")

    return {
        "verts_count": len(b["verts"]),
        "normals_count": len(b["normals"]),
        "uvs_count": len(b["uvs"]),
        "faces_count": sum(len(fl) for fl in b["faces"].values()),
        "materials": list(b["faces"].keys())
    }

def export_all_models(models_dir="assets/models"):
    """Generates all 3D models for this faction in assets/models/."""
    generators = {
        "turret": build_turret_mesh,
        "base": build_base_mesh,
        "harvester": build_harvester_mesh,
        "wall": build_wall_mesh,
        "purifier": build_purifier_mesh,
    }
    results = {}
    for name, gen_fn in generators.items():
        obj_p = os.path.join(models_dir, f"{name}.obj")
        mtl_p = os.path.join(models_dir, f"{name}.mtl")
        b = gen_fn()
        res = write_obj_mtl(b, obj_p, mtl_p)
        results[name] = res
        print(f"Generated {name}.obj ({res['verts_count']} verts, {res['faces_count']} faces, materials: {res['materials']})")
    return results

if __name__ == "__main__":
    export_all_models()
