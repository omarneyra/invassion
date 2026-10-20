"""
Procedural 3D OBJ & MTL Generator for the Invassion Pulse Defense Cannon.
Strictly matches the concept art:
- Heavy base with 4 outrigger stabilizer treads
- Rotating mechanical turntable with hydraulic elevation rams
- Armored cockpit chassis with commander cupola & side sensor pod
- Twin heavy pulse railgun cannons ELEVATED AT 28 DEGREES with rear breech cooling coils,
  glowing cyan plasma channels, and quad-prong muzzle compensators.
- 100% verified outward Counter-Clockwise (CCW) face winding.
"""

import math
import os

def create_turret_obj(output_obj_path="assets/models/turret.obj", output_mtl_path="assets/models/turret.mtl"):
    verts = []
    normals = []
    uvs = []
    faces = {} # mat_name -> list of faces

    # Elevation angle: 28 degrees
    ELEVATION_ANGLE = math.radians(28.0)
    cos_el = math.cos(ELEVATION_ANGLE)
    sin_el = math.sin(ELEVATION_ANGLE)
    PIVOT_Y = 0.26
    PIVOT_Z = 0.10

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
        # Front (+Z)
        add_quad(c[4], c[5], c[6], c[7], n_fwd, mat_name)
        # Back (-Z)
        add_quad(c[1], c[0], c[3], c[2], n_bck, mat_name)
        # Top (+Y)
        add_quad(c[7], c[6], c[2], c[3], n_top, mat_name)
        # Bottom (-Y)
        add_quad(c[0], c[1], c[5], c[4], n_bot, mat_name)
        # Right (+X)
        add_quad(c[5], c[1], c[2], c[6], n_rgt, mat_name)
        # Left (-X)
        add_quad(c[0], c[4], c[7], c[3], n_lft, mat_name)

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
            # Top cap (CCW looking down +Y)
            faces[mat_name].append([(top_center, t0, vn_up), (top_verts[next_i], t0, vn_up), (top_verts[i], t0, vn_up)])
            # Bottom cap (CCW looking up -Y)
            faces[mat_name].append([(bot_center, t0, vn_down), (bot_verts[i], t0, vn_down), (bot_verts[next_i], t0, vn_down)])
            # Side quad
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
            # Front cap (+Z)
            faces[mat_name].append([(front_center, t0, vn_fwd), (front_verts[i], t0, vn_fwd), (front_verts[next_i], t0, vn_fwd)])
            # Back cap (-Z)
            faces[mat_name].append([(back_center, t0, vn_bck), (back_verts[next_i], t0, vn_bck), (back_verts[i], t0, vn_bck)])
            # Side quad
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            raw_n_side = (math.cos(angle_mid), math.sin(angle_mid), 0)
            n_side = rotate_normal(*raw_n_side) if elevated else raw_n_side
            add_quad(back_verts[i], back_verts[next_i], front_verts[next_i], front_verts[i], n_side, mat_name)

    # ================= BUILD TURRET GEOMETRY =================

    # 1. Industrial Foundation Pedestal
    # Heavy rectangular crate block underneath
    add_box(0, 0.025, 0, 0.68, 0.05, 0.68, "Mat_DarkTitanium")
    # Base bevel rim
    add_cylinder_y(0, 0.065, 0, 0.38, 0.44, 0.04, 12, "Mat_DarkTitanium")

    # 4 Heavy Outrigger Stabilizer Treads (at 45, 135, 225, 315 degrees)
    for i in range(4):
        angle = i * (math.pi / 2.0) + (math.pi / 4.0)
        ca, sa = math.cos(angle), math.sin(angle)
        ox, oz = ca * 0.38, sa * 0.38
        # Outrigger diagonal arm
        add_box(ox, 0.06, oz, 0.14, 0.07, 0.18, "Mat_DarkTitanium")
        # Articulated knee joint
        add_cylinder_y(ca * 0.42, 0.08, sa * 0.42, 0.04, 0.04, 0.06, 8, "Mat_DarkTitanium")
        # Heavy track footpad
        add_box(ca * 0.48, 0.03, sa * 0.48, 0.16, 0.05, 0.14, "Mat_DarkTitanium")
        # Status light / bolt on outrigger foot
        add_box(ca * 0.42, 0.11, sa * 0.42, 0.03, 0.02, 0.03, "Mat_PlasmaCyan")

    # 2. Rotating Turntable Ring & Gear Collar
    add_cylinder_y(0, 0.10, 0, 0.30, 0.32, 0.04, 16, "Mat_DarkTitanium")
    add_cylinder_y(0, 0.13, 0, 0.27, 0.29, 0.04, 16, "Mat_FactionArmor")
    add_cylinder_y(0, 0.16, 0, 0.24, 0.26, 0.03, 16, "Mat_DarkTitanium")

    # Dual Hydraulic Elevation Rams connecting turntable to trunnions
    add_box(-0.15, 0.19, 0.06, 0.04, 0.10, 0.12, "Mat_DarkTitanium")
    add_box(0.15, 0.19, 0.06, 0.04, 0.10, 0.12, "Mat_DarkTitanium")

    # 3. Main Armored Turret Hull & Cupola
    # Central armored carriage body
    add_box(0, 0.24, -0.04, 0.30, 0.12, 0.30, "Mat_DarkTitanium")
    # Faction armor cowl / sloped mantle
    add_box(0, 0.29, -0.06, 0.24, 0.08, 0.24, "Mat_FactionArmor")

    # Top Commander Observation Cupola
    add_cylinder_y(0, 0.35, -0.07, 0.08, 0.10, 0.05, 8, "Mat_DarkTitanium")
    add_cylinder_y(0, 0.38, -0.07, 0.05, 0.06, 0.03, 8, "Mat_Optics")
    # Antenna mast
    add_cylinder_y(0.06, 0.43, -0.11, 0.007, 0.007, 0.10, 4, "Mat_DarkTitanium")

    # Rear Heavy Power Capacitors (Twin cylindrical cells)
    add_cylinder_y(-0.08, 0.26, -0.21, 0.05, 0.05, 0.13, 8, "Mat_DarkTitanium")
    add_cylinder_y(0.08, 0.26, -0.21, 0.05, 0.05, 0.13, 8, "Mat_DarkTitanium")
    # Capacitor glowing energy rings
    add_cylinder_y(-0.08, 0.26, -0.21, 0.053, 0.053, 0.025, 8, "Mat_PlasmaCyan")
    add_cylinder_y(0.08, 0.26, -0.21, 0.053, 0.053, 0.025, 8, "Mat_PlasmaCyan")

    # Side Optical Sensor Pod (Left flank)
    add_box(-0.16, 0.31, 0.04, 0.07, 0.08, 0.11, "Mat_DarkTitanium")
    add_box(-0.16, 0.31, 0.10, 0.05, 0.05, 0.02, "Mat_Optics")

    # 4. TWIN HEAVY PULSE RAILGUNS (ELEVATED AT 28 DEGREES)
    barrel_x_offsets = [-0.11, 0.11]
    for bx in barrel_x_offsets:
        # Breech Trunnion Mount
        add_box(bx, PIVOT_Y, PIVOT_Z, 0.10, 0.11, 0.12, "Mat_DarkTitanium", elevated=True)

        # Concentric Breech Cooling Coils (Heat dissipation rings along barrel axis)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.11, 0.055, 0.055, 0.02, 8, "Mat_FactionArmor", elevated=True)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.15, 0.055, 0.055, 0.02, 8, "Mat_FactionArmor", elevated=True)
        add_cylinder_z(bx, PIVOT_Y, PIVOT_Z + 0.19, 0.055, 0.055, 0.02, 8, "Mat_FactionArmor", elevated=True)

        # Main Heavy Armored Barrel Beam (Rectangular structural rail casing)
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.38, 0.085, 0.095, 0.38, "Mat_DarkTitanium", elevated=True)

        # GLOWING CYAN PLASMA ACCELERATION CHANNELS (Top, Bottom & Inner Rails)
        # Inner-facing high energy rail
        inner_sign = 1.0 if bx < 0 else -1.0
        add_box(bx + inner_sign * 0.038, PIVOT_Y, PIVOT_Z + 0.38, 0.015, 0.065, 0.36, "Mat_PlasmaCyan", elevated=True)
        # Top plasma conduit
        add_box(bx, PIVOT_Y + 0.042, PIVOT_Z + 0.38, 0.040, 0.015, 0.36, "Mat_PlasmaCyan", elevated=True)

        # Quad-Prong Heavy Muzzle Brake
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.58, 0.10, 0.11, 0.05, "Mat_DarkTitanium", elevated=True)
        # Glowing Muzzle Bore Exit
        add_box(bx, PIVOT_Y, PIVOT_Z + 0.606, 0.05, 0.06, 0.01, "Mat_PlasmaCyan", elevated=True)

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
            "Mat_Optics"
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
