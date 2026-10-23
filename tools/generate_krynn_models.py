"""
Procedural 3D Model Generator for Invassion (Faction 2: Krynn Swarm / Bio-Insectoid).
Strictly follows functional/procedural Python (NO OOP, NO classes).
Provides an organic biological architectural kit and building generators for the Krynn Swarm:
1. Base (Swarm Matrix Spire)
2. Turret (Acid Spore Cannon)
3. Harvester (Biomass Digestive Rhizome)
4. Wall (Chitin Bone Crest)
5. Purifier (Biomorphic Spore Vent)
6. Ravager (Krynn Ravager Beast)

All models share the unified Krynn organic aesthetic:
- Segmented glossy black-purple chitin plates (Mat_KrynnChitin)
- Deep crimson/burgundy muscular flesh and fibrous sinews (Mat_KrynnFlesh)
- Bioluminescent toxic lime/acid green glowing sacs and conduits (Mat_KrynnAcid)
- Calcified ivory bone thorns, mandibles, and scythe ribs (Mat_KrynnBone)
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

def add_box(b, cx, cy, cz, sx, sy, sz, mat_name):
    """Draws an axis-aligned box centered at (cx, cy, cz)."""
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
    c = [add_vertex(b, *pt) for pt in raw_corners]
    add_quad(b, c[4], c[5], c[6], c[7], (0, 0, 1), mat_name)   # Front (+Z)
    add_quad(b, c[1], c[0], c[3], c[2], (0, 0, -1), mat_name)  # Back (-Z)
    add_quad(b, c[7], c[6], c[2], c[3], (0, 1, 0), mat_name)   # Top (+Y)
    add_quad(b, c[0], c[1], c[5], c[4], (0, -1, 0), mat_name)  # Bottom (-Y)
    add_quad(b, c[5], c[1], c[2], c[6], (1, 0, 0), mat_name)   # Right (+X)
    add_quad(b, c[0], c[4], c[7], c[3], (-1, 0, 0), mat_name)  # Left (-X)

def add_cylinder_y(b, cx, cy, cz, r_top, r_bot, height, segments, mat_name):
    """Draws a vertical cylinder or truncated cone along the Y axis."""
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

    p1_idx = add_vertex(b, p1[0], p1[1], p1[2])
    p2_idx = add_vertex(b, p2[0], p2[1], p2[2])
    vn_bot = add_normal(b, -dx, -dy, -dz)
    vn_top = add_normal(b, dx, dy, dz)
    t0 = add_uv(b, 0.5, 0.5)

    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    for i in range(segments):
        next_i = (i + 1) % segments
        b["faces"][mat_name].append([(p1_idx, t0, vn_bot), (bot_verts[i], t0, vn_bot), (bot_verts[next_i], t0, vn_bot)])
        b["faces"][mat_name].append([(p2_idx, t0, vn_top), (top_verts[next_i], t0, vn_top), (top_verts[i], t0, vn_top)])
        angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
        cx_mid = math.cos(angle_mid)
        sx_mid = math.sin(angle_mid)
        norm_dir = (cx_mid * ux + sx_mid * vx, cx_mid * uy + sx_mid * vy, cx_mid * uz + sx_mid * vz)
        add_quad(b, bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], norm_dir, mat_name)

def add_sphere(b, cx, cy, cz, radius, rings, segments, mat_name):
    """Draws an organic UV sphere (for acid sacs, pustules, eggs)."""
    grid = []
    for r in range(rings + 1):
        theta = r * math.pi / rings
        sin_t, cos_t = math.sin(theta), math.cos(theta)
        ring_verts = []
        for s in range(segments):
            phi = s * 2.0 * math.pi / segments
            sin_p, cos_p = math.sin(phi), math.cos(phi)
            x = cx + radius * sin_t * cos_p
            y = cy + radius * cos_t
            z = cz + radius * sin_t * sin_p
            ring_verts.append(add_vertex(b, x, y, z))
        grid.append(ring_verts)

    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    t0 = add_uv(b, 0.5, 0.5)
    for r in range(rings):
        for s in range(segments):
            next_s = (s + 1) % segments
            v_tl = grid[r][s]
            v_tr = grid[r][next_s]
            v_bl = grid[r + 1][s]
            v_br = grid[r + 1][next_s]

            # Normal from center
            vx = b["verts"][v_tl - 1][0] - cx
            vy = b["verts"][v_tl - 1][1] - cy
            vz = b["verts"][v_tl - 1][2] - cz
            vn = add_normal(b, vx, vy, vz)

            if r == 0:
                # Top cap
                b["faces"][mat_name].append([(v_tl, t0, vn), (v_bl, t0, vn), (v_br, t0, vn)])
            elif r == rings - 1:
                # Bottom cap
                b["faces"][mat_name].append([(v_tl, t0, vn), (v_bl, t0, vn), (v_tr, t0, vn)])
            else:
                add_quad(b, v_bl, v_br, v_tr, v_tl, (vx, vy, vz), mat_name)

def add_spike(b, base_pos, tip_pos, base_radius, segments, mat_name):
    """Draws a tapering bone spike / horn / fang pointing from base_pos to tip_pos."""
    ax, ay, az = tip_pos[0] - base_pos[0], tip_pos[1] - base_pos[1], tip_pos[2] - base_pos[2]
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

    bot_verts = []
    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        ca, sa = math.cos(angle) * base_radius, math.sin(angle) * base_radius
        ox = ca * ux + sa * vx
        oy = ca * uy + sa * vy
        oz = ca * uz + sa * vz
        bot_verts.append(add_vertex(b, base_pos[0] + ox, base_pos[1] + oy, base_pos[2] + oz))

    tip_idx = add_vertex(b, tip_pos[0], tip_pos[1], tip_pos[2])
    base_idx = add_vertex(b, base_pos[0], base_pos[1], base_pos[2])
    vn_base = add_normal(b, -dx, -dy, -dz)
    t0 = add_uv(b, 0.5, 0.5)

    if mat_name not in b["faces"]:
        b["faces"][mat_name] = []

    for i in range(segments):
        next_i = (i + 1) % segments
        # Base cap
        b["faces"][mat_name].append([(base_idx, t0, vn_base), (bot_verts[i], t0, vn_base), (bot_verts[next_i], t0, vn_base)])
        # Cone sides
        angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
        cx_mid = math.cos(angle_mid)
        sx_mid = math.sin(angle_mid)
        side_norm = (cx_mid * ux + sx_mid * vx + dx * 0.3, cx_mid * uy + sx_mid * vy + dy * 0.3, cx_mid * uz + sx_mid * vz + dz * 0.3)
        vn_side = add_normal(b, *side_norm)
        b["faces"][mat_name].append([(bot_verts[i], t0, vn_side), (tip_idx, t0, vn_side), (bot_verts[next_i], t0, vn_side)])


# ==============================================================================
# 2. REUSABLE KRYNN ORGANIC SUB-ASSEMBLIES
# ==============================================================================

def add_organic_root_plinth(b, radius_outer, radius_inner, height, segments=8):
    """Draws the fibrous organic base with root tendrils anchoring to ground."""
    # Fleshy spreading mound
    add_cylinder_y(b, 0, height * 0.5, 0, radius_inner, radius_outer, height, segments, "Mat_KrynnFlesh")
    # Outer chitinous rim plates
    rim_h = height * 0.7
    add_cylinder_y(b, 0, rim_h * 0.5, 0, radius_outer * 0.95, radius_outer * 1.05, rim_h, segments, "Mat_KrynnChitin")
    # 4 to 6 sprawling root tendrils embedding into planetary surface
    tendril_count = 6
    for i in range(tendril_count):
        ang = i * (2.0 * math.pi / tendril_count)
        ca, sa = math.cos(ang), math.sin(ang)
        p1 = (ca * radius_inner * 0.9, height * 0.4, sa * radius_inner * 0.9)
        p2 = (ca * radius_outer * 1.3, 0.01, sa * radius_outer * 1.3)
        add_cylinder_between(b, p1, p2, 0.035, 6, "Mat_KrynnFlesh")

def add_carapace_tier(b, cy, r_top, r_bot, height, segments=8):
    """Draws a segmented insectoid carapace ring with overlapping chitin plates."""
    add_cylinder_y(b, 0, cy, 0, r_top, r_bot, height, segments, "Mat_KrynnChitin")


# ==============================================================================
# 3. KRYNN BUILDING & UNIT GENERATORS
# ==============================================================================

def build_krynn_base_mesh():
    """Generates the Krynn Swarm Matrix Spire (Living Hive Spire)."""
    b = make_builder()

    # 1. Sprawling organic root mound
    add_organic_root_plinth(b, 0.48, 0.38, 0.09, segments=10)

    # 2. Tiered segmented chitinous hive tower
    add_carapace_tier(b, 0.12, 0.34, 0.40, 0.08, segments=8)
    add_carapace_tier(b, 0.20, 0.26, 0.34, 0.10, segments=8)
    add_carapace_tier(b, 0.31, 0.18, 0.26, 0.12, segments=8)
    add_carapace_tier(b, 0.43, 0.11, 0.18, 0.12, segments=8)
    add_carapace_tier(b, 0.54, 0.06, 0.11, 0.10, segments=8)

    # 3. Central pulsing acid core / Queen egg chamber
    add_sphere(b, 0, 0.28, 0, 0.12, 6, 8, "Mat_KrynnAcid")

    # 4. Spire pinnacle: Crown of calcified bone horns
    horn_count = 5
    for i in range(horn_count):
        ang = i * (2.0 * math.pi / horn_count)
        ca, sa = math.cos(ang), math.sin(ang)
        base_pt = (ca * 0.06, 0.58, sa * 0.06)
        tip_pt = (ca * 0.12, 0.76, sa * 0.12)
        add_spike(b, base_pt, tip_pt, 0.02, 6, "Mat_KrynnBone")

    # 5. External acid pustules around the middle tiers
    pustule_count = 4
    for i in range(pustule_count):
        ang = (i + 0.5) * (2.0 * math.pi / pustule_count)
        ca, sa = math.cos(ang), math.sin(ang)
        add_sphere(b, ca * 0.24, 0.22, sa * 0.24, 0.045, 5, 6, "Mat_KrynnAcid")

    # 6. Secondary radial bone ribs along the base
    for i in range(6):
        ang = i * (2.0 * math.pi / 6)
        ca, sa = math.cos(ang), math.sin(ang)
        base_pt = (ca * 0.28, 0.10, sa * 0.28)
        tip_pt = (ca * 0.44, 0.24, sa * 0.44)
        add_spike(b, base_pt, tip_pt, 0.025, 6, "Mat_KrynnBone")

    return b


def build_krynn_turret_mesh():
    """Generates the Krynn Acid Spore Cannon (Predatory Maw Biotower)."""
    b = make_builder()

    # 1. Anchored organic root mound
    add_organic_root_plinth(b, 0.38, 0.28, 0.08, segments=8)

    # 2. Articulated fleshy vertebral stalk
    add_cylinder_between(b, (0, 0.06, 0), (0, 0.22, -0.04), 0.10, 8, "Mat_KrynnFlesh")
    add_cylinder_between(b, (0, 0.22, -0.04), (0, 0.36, 0.04), 0.09, 8, "Mat_KrynnChitin")

    # 3. Swollen glowing acid sac beneath the head
    add_sphere(b, 0, 0.26, -0.08, 0.09, 6, 8, "Mat_KrynnAcid")

    # 4. Predatory chitinous head / Maw housing
    add_box(b, 0, 0.42, 0.06, 0.18, 0.16, 0.24, "Mat_KrynnChitin")

    # 5. Acid cannon nozzle / Spore throat
    add_cylinder_between(b, (0, 0.42, 0.12), (0, 0.44, 0.28), 0.045, 8, "Mat_KrynnAcid")

    # 6. Calcified predatory fangs / Mandibles framing the maw
    # Upper crest
    add_spike(b, (0, 0.48, 0.14), (0, 0.58, 0.26), 0.025, 6, "Mat_KrynnBone")
    # Left mandible
    add_spike(b, (-0.09, 0.40, 0.12), (-0.14, 0.42, 0.32), 0.022, 6, "Mat_KrynnBone")
    # Right mandible
    add_spike(b, (0.09, 0.40, 0.12), (0.14, 0.42, 0.32), 0.022, 6, "Mat_KrynnBone")
    # Lower chin barb
    add_spike(b, (0, 0.34, 0.14), (0, 0.26, 0.24), 0.02, 6, "Mat_KrynnBone")

    return b


def build_krynn_harvester_mesh():
    """Generates the Krynn Biomass Digestive Rhizome (Mantle Siphoning Pustule)."""
    b = make_builder()

    # 1. Sprawling organic rim
    add_organic_root_plinth(b, 0.42, 0.32, 0.07, segments=8)

    # 2. Central swollen digestive sac cluster
    add_sphere(b, 0, 0.16, 0, 0.14, 6, 8, "Mat_KrynnAcid")
    add_sphere(b, 0.08, 0.12, 0.07, 0.09, 5, 6, "Mat_KrynnAcid")
    add_sphere(b, -0.08, 0.13, -0.06, 0.08, 5, 6, "Mat_KrynnAcid")

    # 3. Protective chitinous claw segments wrapping around the pustule
    claw_count = 4
    for i in range(claw_count):
        ang = i * (2.0 * math.pi / claw_count)
        ca, sa = math.cos(ang), math.sin(ang)
        base_pt = (ca * 0.28, 0.05, sa * 0.28)
        mid_pt = (ca * 0.22, 0.26, sa * 0.22)
        tip_pt = (ca * 0.09, 0.34, sa * 0.09)
        add_cylinder_between(b, base_pt, mid_pt, 0.035, 6, "Mat_KrynnChitin")
        add_spike(b, mid_pt, tip_pt, 0.03, 6, "Mat_KrynnBone")

    # 4. Siphon conduits burrowing into ground
    for i in range(3):
        ang = (i * 2.0 * math.pi / 3) + 0.3
        ca, sa = math.cos(ang), math.sin(ang)
        p1 = (ca * 0.12, 0.22, sa * 0.12)
        p2 = (ca * 0.34, 0.02, sa * 0.34)
        add_cylinder_between(b, p1, p2, 0.025, 6, "Mat_KrynnFlesh")

    return b


def build_krynn_wall_mesh():
    """Generates the Krynn Chitin Bone Crest (Carapace Barrier Pylon)."""
    b = make_builder()

    # 1. Hardened chitin foundation
    add_box(b, 0, 0.04, 0, 0.46, 0.08, 0.22, "Mat_KrynnChitin")

    # 2. Interlocking calcified bone ribs (3 prominent vertical spines)
    rib_offsets = [-0.14, 0.0, 0.14]
    rib_heights = [0.44, 0.52, 0.44]
    for i, x in enumerate(rib_offsets):
        h = rib_heights[i]
        # Main spine
        add_spike(b, (x, 0.06, 0), (x, h, 0.03), 0.04, 6, "Mat_KrynnBone")
        # Forward deflection hook
        add_spike(b, (x, h * 0.6, 0.02), (x, h * 0.75, 0.14), 0.022, 6, "Mat_KrynnBone")

    # 3. Dense fibrous muscular webbing between bone ribs
    add_box(b, 0, 0.22, 0, 0.36, 0.26, 0.06, "Mat_KrynnFlesh")

    # 4. Toxic venomous pustules embedded in wall face
    for x in [-0.07, 0.07]:
        add_sphere(b, x, 0.18, 0.04, 0.035, 5, 6, "Mat_KrynnAcid")
        add_sphere(b, x, 0.18, -0.04, 0.035, 5, 6, "Mat_KrynnAcid")

    return b


def build_krynn_purifier_mesh():
    """Generates the Krynn Biomorphic Spore Vent (Planetary Cleansing Vent)."""
    b = make_builder()

    # 1. Base mound with anchoring roots
    add_organic_root_plinth(b, 0.44, 0.34, 0.08, segments=8)

    # 2. Main chimney stalk (segmented chitin trunk)
    add_cylinder_y(b, 0, 0.18, 0, 0.20, 0.28, 0.20, 8, "Mat_KrynnChitin")
    add_cylinder_y(b, 0, 0.36, 0, 0.15, 0.20, 0.16, 8, "Mat_KrynnFlesh")
    add_cylinder_y(b, 0, 0.50, 0, 0.22, 0.15, 0.14, 8, "Mat_KrynnChitin")

    # 3. Glowing central spore crucible inside chimney
    add_sphere(b, 0, 0.48, 0, 0.11, 6, 8, "Mat_KrynnAcid")

    # 4. Crown of flared organic petal sphincters / Vent lips
    petal_count = 6
    for i in range(petal_count):
        ang = i * (2.0 * math.pi / petal_count)
        ca, sa = math.cos(ang), math.sin(ang)
        base_pt = (ca * 0.18, 0.54, sa * 0.18)
        tip_pt = (ca * 0.30, 0.68, sa * 0.30)
        add_spike(b, base_pt, tip_pt, 0.03, 6, "Mat_KrynnBone")

    # 5. External pulsating air sacs along the trunk
    for i in range(4):
        ang = (i + 0.5) * (2.0 * math.pi / 4)
        ca, sa = math.cos(ang), math.sin(ang)
        add_sphere(b, ca * 0.18, 0.28, sa * 0.18, 0.05, 5, 6, "Mat_KrynnAcid")

    return b


def build_krynn_ravager_mesh():
    """Generates the Krynn Ravager (Armored Insectoid Assault Beast)."""
    b = make_builder()

    # 1. Low-slung hunched thorax & abdomen
    add_box(b, 0, 0.24, -0.06, 0.24, 0.16, 0.32, "Mat_KrynnChitin")
    # Posterior swollen acid sac
    add_sphere(b, 0, 0.22, -0.26, 0.11, 6, 8, "Mat_KrynnAcid")

    # 2. Aggressive head with compound acid eyes
    add_box(b, 0, 0.26, 0.18, 0.16, 0.14, 0.18, "Mat_KrynnChitin")
    # Eyes
    add_sphere(b, -0.06, 0.29, 0.24, 0.025, 4, 6, "Mat_KrynnAcid")
    add_sphere(b, 0.06, 0.29, 0.24, 0.025, 4, 6, "Mat_KrynnAcid")

    # 3. Giant scythe mantis claws (front)
    for sign in [-1, 1]:
        # Shoulder joint
        shoulder = (sign * 0.14, 0.26, 0.14)
        elbow = (sign * 0.26, 0.38, 0.22)
        claw_tip = (sign * 0.10, 0.04, 0.38)
        add_cylinder_between(b, shoulder, elbow, 0.035, 6, "Mat_KrynnChitin")
        add_spike(b, elbow, claw_tip, 0.04, 6, "Mat_KrynnBone")

    # 4. Quadruped walking legs (4 legs: 2 middle, 2 rear)
    leg_anchors = [
        # (sign, anchor_z, knee_x, foot_z)
        (1, 0.04, 0.30, 0.08),
        (-1, 0.04, -0.30, 0.08),
        (1, -0.16, 0.28, -0.22),
        (-1, -0.16, -0.28, -0.22),
    ]
    for sign, az, kx, fz in leg_anchors:
        hip = (sign * 0.12, 0.22, az)
        knee = (kx, 0.30, az)
        foot = (sign * 0.22, 0.0, fz)
        add_cylinder_between(b, hip, knee, 0.028, 6, "Mat_KrynnChitin")
        add_spike(b, knee, foot, 0.025, 6, "Mat_KrynnBone")

    # 5. Dorsal armor crests & spines
    for z, h in [(-0.12, 0.38), (0.0, 0.40), (0.10, 0.37)]:
        add_spike(b, (0, 0.31, z), (0, h, z - 0.04), 0.025, 6, "Mat_KrynnBone")

    return b


# ==============================================================================
# 4. EXPORT ENGINE (OBJ & MTL WRITER FOR KRYNN SWARM)
# ==============================================================================

def write_krynn_obj_mtl(b, output_obj_path, output_mtl_path):
    """Writes Krynn geometry to Wavefront OBJ & MTL format with organic PBR spec."""
    os.makedirs(os.path.dirname(output_obj_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_mtl_path), exist_ok=True)
    mtl_filename = os.path.basename(output_mtl_path)

    with open(output_mtl_path, "w") as f:
        f.write("# Materials for Invassion Krynn Swarm (Organic Bio-PBR Spec)\n\n")
        # Glossy deep purple-black chitin carapace
        f.write("newmtl Mat_KrynnChitin\nKa 0.15 0.08 0.22\nKd 0.24 0.12 0.35\nKs 0.85 0.80 0.95\nNs 60.0\nd 1.0\n\n")
        # Muscular burgundy/crimson sinews and tissue
        f.write("newmtl Mat_KrynnFlesh\nKa 0.28 0.08 0.18\nKd 0.45 0.15 0.28\nKs 0.35 0.25 0.30\nNs 20.0\nd 1.0\n\n")
        # Bioluminescent toxic lime/acid green glowing sacs
        f.write("newmtl Mat_KrynnAcid\nKa 0.35 0.85 0.10\nKd 0.50 0.92 0.15\nKs 0.20 0.80 0.20\nKe 0.65 1.00 0.20\nNs 80.0\nd 1.0\n\n")
        # Calcified pale ivory bone thorns, mandibles, and scythe claws
        f.write("newmtl Mat_KrynnBone\nKa 0.70 0.68 0.62\nKd 0.85 0.82 0.76\nKs 0.50 0.48 0.45\nNs 35.0\nd 1.0\n")

    with open(output_obj_path, "w") as f:
        f.write(f"# Invassion Procedural 3D Model (Krynn Swarm)\nmtllib {mtl_filename}\no ModelMesh\n\n")
        for v in b["verts"]:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for vt in b["uvs"]:
            f.write(f"vt {vt[0]} {vt[1]}\n")
        for vn in b["normals"]:
            f.write(f"vn {vn[0]} {vn[1]} {vn[2]}\n")

        MATERIAL_ORDER = [
            "Mat_KrynnChitin",
            "Mat_KrynnFlesh",
            "Mat_KrynnAcid",
            "Mat_KrynnBone"
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

def export_all_krynn_models(models_dir="assets/models"):
    """Generates all 6 3D models for Krynn Swarm in assets/models/."""
    generators = {
        "krynn_base": build_krynn_base_mesh,
        "krynn_turret": build_krynn_turret_mesh,
        "krynn_harvester": build_krynn_harvester_mesh,
        "krynn_wall": build_krynn_wall_mesh,
        "krynn_purifier": build_krynn_purifier_mesh,
        "krynn_ravager": build_krynn_ravager_mesh,
    }
    results = {}
    for name, gen_fn in generators.items():
        obj_p = os.path.join(models_dir, f"{name}.obj")
        mtl_p = os.path.join(models_dir, f"{name}.mtl")
        b = gen_fn()
        res = write_krynn_obj_mtl(b, obj_p, mtl_p)
        results[name] = res
        print(f"Generated {name}.obj ({res['verts_count']} verts, {res['faces_count']} faces, materials: {res['materials']})")
    return results

if __name__ == "__main__":
    export_all_krynn_models()
