"""
Procedural 3D OBJ & MTL Generator for the Invassion Pulse Defense Cannon.
Faithfully recreates the visual silhouette, proportions, and details of the studio concept art:
- Heavy industrial square bunker foundation plinth with corner brackets
- 4 articulated outrigger stabilizer legs with hydraulic struts and track footpads
- Rotating mechanical turntable with gear collar and faction accent ring
- Armored carriage hull with commander cupola, viewport slits, and top sensor pod
- Dual prominent hydraulic elevation rams connecting turntable front to gun cradle
- Side cylindrical trunnion recoil hubs with concentric cap discs
- 4 rear recoil buffer accumulator tubes with glowing cyan status indicators
- Twin heavy pulse railguns with chunky wide-spaced artillery profile (7.5 deg elevation):
  * Breech trunnion blocks with central heavy armored mantlet
  * 3 concentric ribbed induction copper coils per barrel (Mat_CopperCoil)
  * Heavy rectangular upper & lower rail beams with side armor shrouds
  * Recessed central plasma acceleration channel with segmented cooling louvers
  * Quad-prong heavy muzzle compensators with glowing bore exit
- 100% verified Counter-Clockwise (CCW) outward face winding.
"""

import math
import os

def create_turret_obj(output_obj_path="assets/models/turret.obj", output_mtl_path="assets/models/turret.mtl"):
    verts = []
    normals = []
    uvs = []
    faces = {} # mat_name -> list of faces

    # Low-profile ground artillery elevation angle: 7.5 degrees
    # This prevents the cannons from looking like vertical chimneys on curved planets.
    ELEVATION_ANGLE = math.radians(7.5)
    cos_el = math.cos(ELEVATION_ANGLE)
    sin_el = math.sin(ELEVATION_ANGLE)
    PIVOT_Y = 0.30
    PIVOT_Z = 0.04

    def add_vertex(x, y, z):
        verts.append((round(x, 5), round(y, 5), round(z, 5)))
        return len(verts)

    def add_normal(nx, ny, nz):
        mag = math.sqrt(nx*nx + ny*ny + nz*nz)
        if mag > 1e-6:
            normals.append((round(nx/mag, 4), round(ny/mag, 4), round(nz/mag, 4)))
        else:
            normals.append((0.0, 1.0, 0.0))
        return len(normals)

    def add_uv(u, v):
        uvs.append((round(u, 4), round(v, 4)))
        return len(uvs)

    def add_quad(v1, v2, v3, v4, n, mat_name):
        vn = add_normal(n[0], n[1], n[2])
        t1 = add_uv(0.0, 0.0)
        t2 = add_uv(1.0, 0.0)
        t3 = add_uv(1.0, 1.0)
        t4 = add_uv(0.0, 1.0)
        if mat_name not in faces:
            faces[mat_name] = []
        # Two CCW triangles for quad
        faces[mat_name].append([(v1, t1, vn), (v2, t2, vn), (v3, t3, vn)])
        faces[mat_name].append([(v1, t1, vn), (v3, t3, vn), (v4, t4, vn)])

    def rotate_point(x, y, z):
        dy = y - PIVOT_Y
        dz = z - PIVOT_Z
        ry = PIVOT_Y + dy * cos_el + dz * sin_el
        rz = PIVOT_Z - dy * sin_el + dz * cos_el
        return (x, ry, rz)

    def rotate_normal(nx, ny, nz):
        rny = ny * cos_el + nz * sin_el
        rnz = -ny * sin_el + nz * cos_el
        return (nx, rny, rnz)

    def add_box(cx, cy, cz, sx, sy, sz, mat_name, elevated=False):
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

        if elevated:
            c = [add_vertex(*rotate_point(*pt)) for pt in raw_corners]
            n_fwd = rotate_normal(0, 0, 1)
            n_bck = rotate_normal(0, 0, -1)
            n_top = rotate_normal(0, 1, 0)
            n_bot = rotate_normal(0, -1, 0)
            n_rgt = rotate_normal(1, 0, 0)
            n_lft = rotate_normal(-1, 0, 0)
        else:
            c = [add_vertex(*pt) for pt in raw_corners]
            n_fwd = (0, 0, 1)
            n_bck = (0, 0, -1)
            n_top = (0, 1, 0)
            n_bot = (0, -1, 0)
            n_rgt = (1, 0, 0)
            n_lft = (-1, 0, 0)

        # All quads wound CCW looking from outside
        add_quad(c[4], c[5], c[6], c[7], n_fwd, mat_name) # Front (+Z)
        add_quad(c[1], c[0], c[3], c[2], n_bck, mat_name) # Back (-Z)
        add_quad(c[7], c[6], c[2], c[3], n_top, mat_name) # Top (+Y)
        add_quad(c[0], c[1], c[5], c[4], n_bot, mat_name) # Bottom (-Y)
        add_quad(c[5], c[1], c[2], c[6], n_rgt, mat_name) # Right (+X)
        add_quad(c[0], c[4], c[7], c[3], n_lft, mat_name) # Left (-X)

    def add_cylinder_y(cx, cy, cz, r_top, r_bot, height, segments, mat_name):
        hy = height * 0.5
        top_verts = []
        bot_verts = []
        for i in range(segments):
            angle = i * (2.0 * math.pi / segments)
            ca, sa = math.cos(angle), math.sin(angle)
            top_verts.append(add_vertex(cx + ca * r_top, cy + hy, cz + sa * r_top))
            bot_verts.append(add_vertex(cx + ca * r_bot, cy - hy, cz + sa * r_bot))

        top_center = add_vertex(cx, cy + hy, cz)
        bot_center = add_vertex(cx, cy - hy, cz)

        vn_up = add_normal(0, 1, 0)
        vn_down = add_normal(0, -1, 0)
        t0 = add_uv(0.5, 0.5)

        if mat_name not in faces:
            faces[mat_name] = []

        for i in range(segments):
            next_i = (i + 1) % segments
            faces[mat_name].append([(top_center, t0, vn_up), (top_verts[next_i], t0, vn_up), (top_verts[i], t0, vn_up)])
            faces[mat_name].append([(bot_center, t0, vn_down), (bot_verts[i], t0, vn_down), (bot_verts[next_i], t0, vn_down)])
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            n_side = (math.cos(angle_mid), 0, math.sin(angle_mid))
            add_quad(bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], n_side, mat_name)

    def add_cylinder_z(cx, cy, cz, r_front, r_back, length, segments, mat_name, elevated=False):
        hz = length * 0.5
        front_verts = []
        back_verts = []
        for i in range(segments):
            angle = i * (2.0 * math.pi / segments)
            ca, sa = math.cos(angle), math.sin(angle)
            pt_f = (cx + ca * r_front, cy + sa * r_front, cz + hz)
            pt_b = (cx + ca * r_back, cy + sa * r_back, cz - hz)
            if elevated:
                front_verts.append(add_vertex(*rotate_point(*pt_f)))
                back_verts.append(add_vertex(*rotate_point(*pt_b)))
            else:
                front_verts.append(add_vertex(*pt_f))
                back_verts.append(add_vertex(*pt_b))

        if elevated:
            front_center = add_vertex(*rotate_point(cx, cy, cz + hz))
            back_center = add_vertex(*rotate_point(cx, cy, cz - hz))
            vn_fwd = add_normal(*rotate_normal(0, 0, 1))
            vn_bck = add_normal(*rotate_normal(0, 0, -1))
        else:
            front_center = add_vertex(cx, cy, cz + hz)
            back_center = add_vertex(cx, cy, cz - hz)
            vn_fwd = add_normal(0, 0, 1)
            vn_bck = add_normal(0, 0, -1)

        t0 = add_uv(0.5, 0.5)
        if mat_name not in faces:
            faces[mat_name] = []

        for i in range(segments):
            next_i = (i + 1) % segments
            faces[mat_name].append([(front_center, t0, vn_fwd), (front_verts[i], t0, vn_fwd), (front_verts[next_i], t0, vn_fwd)])
            faces[mat_name].append([(back_center, t0, vn_bck), (back_verts[next_i], t0, vn_bck), (back_verts[i], t0, vn_bck)])
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            raw_n_side = (math.cos(angle_mid), math.sin(angle_mid), 0)
            n_side = rotate_normal(*raw_n_side) if elevated else raw_n_side
            add_quad(back_verts[i], back_verts[next_i], front_verts[next_i], front_verts[i], n_side, mat_name)

    def add_cylinder_between(p1, p2, radius, segments, mat_name, elevated=False):
        ax = p2[0] - p1[0]
        ay = p2[1] - p1[1]
        az = p2[2] - p1[2]
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
        top_verts = []
        for i in range(segments):
            angle = i * (2.0 * math.pi / segments)
            ca, sa = math.cos(angle) * radius, math.sin(angle) * radius
            offset_x = ca * ux + sa * vx
            offset_y = ca * uy + sa * vy
            offset_z = ca * uz + sa * vz

            pt_b = (p1[0] + offset_x, p1[1] + offset_y, p1[2] + offset_z)
            pt_t = (p2[0] + offset_x, p2[1] + offset_y, p2[2] + offset_z)

            if elevated:
                bot_verts.append(add_vertex(*rotate_point(*pt_b)))
                top_verts.append(add_vertex(*rotate_point(*pt_t)))
            else:
                bot_verts.append(add_vertex(*pt_b))
                top_verts.append(add_vertex(*pt_t))

        if elevated:
            b_center = add_vertex(*rotate_point(*p1))
            t_center = add_vertex(*rotate_point(*p2))
            vn_bot = add_normal(*rotate_normal(-dx, -dy, -dz))
            vn_top = add_normal(*rotate_normal(dx, dy, dz))
        else:
            b_center = add_vertex(*p1)
            t_center = add_vertex(*p2)
            vn_bot = add_normal(-dx, -dy, -dz)
            vn_top = add_normal(dx, dy, dz)

        t0 = add_uv(0.5, 0.5)
        if mat_name not in faces:
            faces[mat_name] = []

        for i in range(segments):
            next_i = (i + 1) % segments
            faces[mat_name].append([(b_center, t0, vn_bot), (bot_verts[next_i], t0, vn_bot), (bot_verts[i], t0, vn_bot)])
            faces[mat_name].append([(t_center, t0, vn_top), (top_verts[i], t0, vn_top), (top_verts[next_i], t0, vn_top)])
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            ca, sa = math.cos(angle_mid), math.sin(angle_mid)
            nx = ca * ux + sa * vx
            ny = ca * uy + sa * vy
            nz = ca * uz + sa * vz
            n_side = rotate_normal(nx, ny, nz) if elevated else (nx, ny, nz)
            add_quad(bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], n_side, mat_name)

    # ================= BUILD TURRET GEOMETRY =================

    # 1. Industrial Foundation Bunker Plinth
    # Heavy square steel base slab
    add_box(0, 0.03, 0, 0.88, 0.06, 0.88, "Mat_DarkTitanium")
    # Corner heavy reinforcement brackets
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            add_box(sx * 0.39, 0.05, sz * 0.39, 0.10, 0.08, 0.10, "Mat_DarkTitanium")

    # Foundation octagonal beveled collar ring
    add_cylinder_y(0, 0.075, 0, 0.43, 0.47, 0.03, 16, "Mat_DarkTitanium")

    # 2. Four Articulated Outrigger Stabilizers (at 45, 135, 225, 315 degrees)
    for i in range(4):
        angle = i * (math.pi / 2.0) + (math.pi / 4.0)
        ca, sa = math.cos(angle), math.sin(angle)
        # Shoulder mount on turntable perimeter
        add_box(ca * 0.32, 0.10, sa * 0.32, 0.12, 0.06, 0.12, "Mat_DarkTitanium")
        # Heavy diagonal hydraulic strut to footpad
        p_sh = (ca * 0.30, 0.10, sa * 0.30)
        p_ft = (ca * 0.45, 0.04, sa * 0.45)
        add_cylinder_between(p_sh, p_ft, 0.024, 8, "Mat_DarkTitanium")
        # Heavy tank-tread footpad
        add_box(ca * 0.48, 0.035, sa * 0.48, 0.15, 0.06, 0.16, "Mat_DarkTitanium")
        # Cyan telemetry indicator on footpad
        add_box(ca * 0.48, 0.07, sa * 0.48, 0.04, 0.02, 0.04, "Mat_PlasmaCyan")

    # 3. Rotating Turntable Ring & Gear Collar
    add_cylinder_y(0, 0.105, 0, 0.34, 0.36, 0.03, 16, "Mat_DarkTitanium")
    add_cylinder_y(0, 0.135, 0, 0.30, 0.32, 0.03, 16, "Mat_FactionArmor")
    add_cylinder_y(0, 0.165, 0, 0.27, 0.29, 0.03, 16, "Mat_DarkTitanium")

    # 4. Armored Gun Carriage Body & Trunnion Stanchions
    # Central armored housing
    add_box(0, 0.24, -0.04, 0.36, 0.13, 0.34, "Mat_DarkTitanium")
    # Sloped faction armor cowl / upper mantlet
    add_box(0, 0.31, -0.06, 0.30, 0.07, 0.28, "Mat_FactionArmor")

    # Left & Right heavy trunnion upright stanchions
    add_box(-0.21, 0.27, 0.04, 0.05, 0.16, 0.14, "Mat_DarkTitanium")
    add_box(0.21, 0.27, 0.04, 0.05, 0.16, 0.14, "Mat_DarkTitanium")

    # Central armored mantlet between the twin barrels
    add_box(0, PIVOT_Y, PIVOT_Z + 0.10, 0.16, 0.12, 0.20, "Mat_DarkTitanium", elevated=True)
    add_box(0, PIVOT_Y + 0.05, PIVOT_Z + 0.08, 0.12, 0.04, 0.16, "Mat_FactionArmor", elevated=True)

    # DUAL PROMINENT HYDRAULIC ELEVATION RAMS (Connecting turntable front directly to gun cradle)
    for hx in [-0.10, 0.10]:
        p_base = (hx, 0.165, 0.14)
        p_mid = (hx, 0.23, 0.11)
        p_top = (hx, 0.29, 0.08)
        # Lower cylinder casing
        add_cylinder_between(p_base, p_mid, 0.022, 8, "Mat_DarkTitanium")
        # Chrome/satin piston rod
        add_cylinder_between(p_mid, p_top, 0.015, 8, "Mat_FactionArmor")

    # 5. Side Trunnion Recoil Hubs
    # Left trunnion cylindrical disk
    add_cylinder_between((-0.24, PIVOT_Y, PIVOT_Z), (-0.20, PIVOT_Y, PIVOT_Z), 0.085, 12, "Mat_DarkTitanium")
    add_cylinder_between((-0.25, PIVOT_Y, PIVOT_Z), (-0.24, PIVOT_Y, PIVOT_Z), 0.055, 12, "Mat_FactionArmor")
    # Right trunnion cylindrical disk
    add_cylinder_between((0.20, PIVOT_Y, PIVOT_Z), (0.24, PIVOT_Y, PIVOT_Z), 0.085, 12, "Mat_DarkTitanium")
    add_cylinder_between((0.24, PIVOT_Y, PIVOT_Z), (0.25, PIVOT_Y, PIVOT_Z), 0.055, 12, "Mat_FactionArmor")

    # 6. Top Commander Cupola & Sensor Pod
    # Commander dome (octagonal cupola)
    add_cylinder_y(0, 0.365, -0.06, 0.09, 0.11, 0.05, 8, "Mat_DarkTitanium")
    # Vision slit band
    add_cylinder_y(0, 0.395, -0.06, 0.065, 0.075, 0.02, 8, "Mat_Optics")
    # Top rotating sensor pod (on top-right)
    add_box(0.09, 0.435, -0.03, 0.07, 0.06, 0.09, "Mat_DarkTitanium")
    # Dual cyan optical targeting lenses
    add_box(0.09, 0.45, 0.02, 0.04, 0.018, 0.012, "Mat_Optics")
    add_box(0.09, 0.42, 0.02, 0.04, 0.018, 0.012, "Mat_Optics")

    # Dual antenna needles
    add_cylinder_between((-0.09, 0.38, -0.12), (-0.09, 0.52, -0.12), 0.005, 4, "Mat_DarkTitanium")
    add_cylinder_between((0.05, 0.38, -0.16), (0.05, 0.49, -0.16), 0.005, 4, "Mat_DarkTitanium")

    # 7. Four Rear Recoil Buffer Accumulators (Horizontal tubes at rear)
    for ox in [-0.10, 0.10]:
        for oy in [0.24, 0.30]:
            add_cylinder_z(ox, oy, -0.22, 0.035, 0.035, 0.12, 8, "Mat_DarkTitanium")
            add_cylinder_z(ox, oy, -0.285, 0.025, 0.025, 0.012, 8, "Mat_PlasmaCyan")

    # 8. TWIN HEAVY PULSE RAILGUNS (WIDE SPACING, LOW-PROFILE ARTILLERY POSTURE AT 7.5 DEGREES)
    barrel_x_offsets = [-0.165, 0.165]
    for bx in barrel_x_offsets:
        # Breech Trunnion Mount Block
        add_box(bx, PIVOT_Y, PIVOT_Z, 0.11, 0.12, 0.14, "Mat_DarkTitanium", elevated=True)

        # Concentric Breech Induction Coils (3 segmented ribbed rings of COPPER)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.09, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", elevated=True)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.13, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", elevated=True)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.17, 0.064, 0.064, 0.022, 12, "Mat_CopperCoil", elevated=True)

        # Induction coil glowing plasma separators
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.11, 0.057, 0.057, 0.014, 10, "Mat_PlasmaCyan", elevated=True)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.15, 0.057, 0.057, 0.014, 10, "Mat_PlasmaCyan", elevated=True)

        # Upper and Lower Armored Rail Beams (Heavy structural rectangular casing)
        add_box(bx, PIVOT_Y + 0.038, PIVOT_Z + 0.36, 0.095, 0.032, 0.36, "Mat_DarkTitanium", elevated=True)
        add_box(bx, PIVOT_Y - 0.038, PIVOT_Z + 0.36, 0.095, 0.032, 0.36, "Mat_DarkTitanium", elevated=True)

        # Outer and Inner Side Armor Shroud Plates
        side_dir = 1.0 if bx > 0 else -1.0
        add_box(bx + side_dir * 0.048, PIVOT_Y, PIVOT_Z + 0.33, 0.014, 0.08, 0.28, "Mat_DarkTitanium", elevated=True)
        add_box(bx - side_dir * 0.048, PIVOT_Y, PIVOT_Z + 0.33, 0.014, 0.08, 0.28, "Mat_DarkTitanium", elevated=True)

        # Recessed Central Plasma Acceleration Channel (Glowing Cyan Core)
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.36, 0.048, 0.048, 0.34, "Mat_PlasmaCyan", elevated=True)

        # Armored grill ribs over the plasma channel (segmented windows)
        for vz in [0.25, 0.31, 0.37, 0.43]:
            add_box(bx, PIVOT_Y + 0.042, PIVOT_Z + vz, 0.052, 0.010, 0.020, "Mat_DarkTitanium", elevated=True)
            add_box(bx, PIVOT_Y - 0.042, PIVOT_Z + vz, 0.052, 0.010, 0.020, "Mat_DarkTitanium", elevated=True)
            # Side cooling vent slits
            add_box(bx + side_dir * 0.052, PIVOT_Y, PIVOT_Z + vz, 0.012, 0.022, 0.025, "Mat_PlasmaCyan", elevated=True)

        # Quad-Prong Heavy Muzzle Brake
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.55, 0.110, 0.120, 0.05, "Mat_DarkTitanium", elevated=True)
        add_box(bx, PIVOT_Y + 0.055, PIVOT_Z + 0.575, 0.065, 0.02, 0.025, "Mat_DarkTitanium", elevated=True)
        add_box(bx, PIVOT_Y - 0.055, PIVOT_Z + 0.575, 0.065, 0.02, 0.025, "Mat_DarkTitanium", elevated=True)
        add_box(bx - 0.054, PIVOT_Y, PIVOT_Z + 0.575, 0.02, 0.065, 0.025, "Mat_DarkTitanium", elevated=True)
        add_box(bx + 0.054, PIVOT_Y, PIVOT_Z + 0.575, 0.02, 0.065, 0.025, "Mat_DarkTitanium", elevated=True)

        # Glowing Muzzle Bore Exit
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.578, 0.052, 0.052, 0.01, "Mat_PlasmaCyan", elevated=True)

    # ================= WRITE OBJ & MTL FILES =================
    os.makedirs(os.path.dirname(output_obj_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_mtl_path), exist_ok=True)

    with open(output_mtl_path, "w") as f:
        f.write("# Materials for Invassion Pulse Defense Cannon (PBR Industrial Spec)\n\n")
        f.write("newmtl Mat_DarkTitanium\n")
        f.write("Ka 0.22 0.26 0.32\n")
        f.write("Kd 0.35 0.40 0.48\n")
        f.write("Ks 0.85 0.88 0.92\n")
        f.write("Ns 45.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_FactionArmor\n")
        f.write("Ka 0.10 0.35 0.20\n")
        f.write("Kd 0.15 0.55 0.28\n")
        f.write("Ks 0.60 0.75 0.65\n")
        f.write("Ns 35.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_PlasmaCyan\n")
        f.write("Ka 0.00 0.95 1.00\n")
        f.write("Kd 0.00 0.98 1.00\n")
        f.write("Ks 0.10 0.90 1.00\n")
        f.write("Ke 0.00 0.98 1.00\n")
        f.write("Ns 100.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_Optics\n")
        f.write("Ka 0.04 0.12 0.22\n")
        f.write("Kd 0.08 0.25 0.40\n")
        f.write("Ks 0.95 0.98 1.00\n")
        f.write("Ke 0.02 0.25 0.45\n")
        f.write("Ns 90.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_CopperCoil\n")
        f.write("Ka 0.45 0.25 0.12\n")
        f.write("Kd 0.75 0.42 0.18\n")
        f.write("Ks 0.90 0.80 0.65\n")
        f.write("Ke 0.25 0.12 0.03\n")
        f.write("Ns 60.0\n")
        f.write("d 1.0\n")

    with open(output_obj_path, "w") as f:
        f.write("# Invassion Pulse Defense Cannon 3D Model\n")
        f.write("mtllib turret.mtl\n")
        f.write("o PulseDefenseCannon\n\n")

        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")

        for vt in uvs:
            f.write(f"vt {vt[0]} {vt[1]}\n")

        for vn in normals:
            f.write(f"vn {vn[0]} {vn[1]} {vn[2]}\n")

        MATERIAL_ORDER = [
            "Mat_DarkTitanium",
            "Mat_FactionArmor",
            "Mat_PlasmaCyan",
            "Mat_Optics",
            "Mat_CopperCoil"
        ]

        for mat_name in MATERIAL_ORDER:
            if mat_name in faces:
                f.write(f"\nusemtl {mat_name}\n")
                for face in faces[mat_name]:
                    f_str = " ".join([f"{idx[0]}/{idx[1]}/{idx[2]}" for idx in face])
                    f.write(f"f {f_str}\n")

    return {
        "verts_count": len(verts),
        "normals_count": len(normals),
        "uvs_count": len(uvs),
        "faces_count": sum(len(fl) for fl in faces.values()),
        "materials": list(faces.keys())
    }

if __name__ == "__main__":
    res = create_turret_obj()
    print(f"Generated turret.obj with {res['verts_count']} verts and {res['faces_count']} faces across materials: {res['materials']}")
