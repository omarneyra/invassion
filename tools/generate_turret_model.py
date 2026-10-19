"""
Procedural 3D OBJ & MTL Generator for the Invassion Pulse Defense Cannon.
Strictly matches the concept art:
- Heavy base with 4 outrigger stabilizer treads
- Rotating mechanical turntable with hydraulic elevation rams
- Armored cockpit chassis with commander cupola & side sensor pod
- Twin heavy pulse railgun cannons with rear breach cooling coils, glowing plasma channels, and quad-prong muzzle compensators.
- All faces wound Counter-Clockwise (CCW) outwards with verified normal vectors.
"""

import math
import os

def create_turret_obj(output_obj_path="assets/models/turret.obj", output_mtl_path="assets/models/turret.mtl"):
    verts = []
    normals = []
    uvs = []
    faces = {} # mat_name -> list of faces (each face is list of (v_idx, vt_idx, vn_idx))

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

    def add_box(cx, cy, cz, sx, sy, sz, mat_name):
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        # 8 corners (1-indexed for OBJ)
        c0 = add_vertex(cx - hx, cy - hy, cz - hz) # ---
        c1 = add_vertex(cx + hx, cy - hy, cz - hz) # +--
        c2 = add_vertex(cx + hx, cy + hy, cz - hz) # ++-
        c3 = add_vertex(cx - hx, cy + hy, cz - hz) # -+-
        c4 = add_vertex(cx - hx, cy - hy, cz + hz) # --+
        c5 = add_vertex(cx + hx, cy - hy, cz + hz) # +-+
        c6 = add_vertex(cx + hx, cy + hy, cz + hz) # +++
        c7 = add_vertex(cx - hx, cy + hy, cz + hz) # -++

        # All quads wound CCW looking from outside
        # Front (+Z)
        add_quad(c4, c5, c6, c7, (0, 0, 1), mat_name)
        # Back (-Z)
        add_quad(c1, c0, c3, c2, (0, 0, -1), mat_name)
        # Top (+Y)
        add_quad(c7, c6, c2, c3, (0, 1, 0), mat_name)
        # Bottom (-Y)
        add_quad(c0, c1, c5, c4, (0, -1, 0), mat_name)
        # Right (+X)
        add_quad(c5, c1, c2, c6, (1, 0, 0), mat_name)
        # Left (-X)
        add_quad(c0, c4, c7, c3, (-1, 0, 0), mat_name)

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
            # Top cap (CCW looking down +Y: center -> next -> curr)
            faces[mat_name].append([(top_center, t0, vn_up), (top_verts[next_i], t0, vn_up), (top_verts[i], t0, vn_up)])
            # Bottom cap (CCW looking up -Y: center -> curr -> next)
            faces[mat_name].append([(bot_center, t0, vn_down), (bot_verts[i], t0, vn_down), (bot_verts[next_i], t0, vn_down)])
            # Side quad (CCW looking from outside)
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            n_side = (math.cos(angle_mid), 0, math.sin(angle_mid))
            add_quad(bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i], n_side, mat_name)

    def add_cylinder_z(cx, cy, cz, r_front, r_back, length, segments, mat_name):
        hz = length * 0.5
        front_verts = []
        back_verts = []
        for i in range(segments):
            angle = i * (2.0 * math.pi / segments)
            ca, sa = math.cos(angle), math.sin(angle)
            front_verts.append(add_vertex(cx + ca * r_front, cy + sa * r_front, cz + hz))
            back_verts.append(add_vertex(cx + ca * r_back, cy + sa * r_back, cz - hz))

        front_center = add_vertex(cx, cy, cz + hz)
        back_center = add_vertex(cx, cy, cz - hz)

        vn_fwd = add_normal(0, 0, 1)
        vn_bck = add_normal(0, 0, -1)
        t0 = add_uv(0.5, 0.5)

        if mat_name not in faces:
            faces[mat_name] = []

        for i in range(segments):
            next_i = (i + 1) % segments
            # Front cap (CCW looking from +Z: center -> curr -> next)
            faces[mat_name].append([(front_center, t0, vn_fwd), (front_verts[i], t0, vn_fwd), (front_verts[next_i], t0, vn_fwd)])
            # Back cap (CCW looking from -Z: center -> next -> curr)
            faces[mat_name].append([(back_center, t0, vn_bck), (back_verts[next_i], t0, vn_bck), (back_verts[i], t0, vn_bck)])
            # Side quad
            angle_mid = (i + 0.5) * (2.0 * math.pi / segments)
            n_side = (math.cos(angle_mid), math.sin(angle_mid), 0)
            add_quad(back_verts[i], back_verts[next_i], front_verts[next_i], front_verts[i], n_side, mat_name)

    # ================= BUILD TURRET GEOMETRY =================

    # 1. Base Pedestal / Heavy Octagonal Foundation
    add_cylinder_y(0, 0.04, 0, 0.38, 0.44, 0.08, 8, "Mat_DarkTitanium")
    # Base ring bevel
    add_cylinder_y(0, 0.09, 0, 0.34, 0.38, 0.04, 12, "Mat_FactionArmor")

    # 4 Stabilizer Outriggers / Tread Pods (at 45, 135, 225, 315 degrees)
    for i in range(4):
        angle = i * (math.pi / 2.0) + (math.pi / 4.0)
        ca, sa = math.cos(angle), math.sin(angle)
        ox, oz = ca * 0.40, sa * 0.40
        # Heavy Outrigger arm
        add_box(ox, 0.05, oz, 0.13, 0.08, 0.16, "Mat_DarkTitanium")
        # Hydraulic foot / track pad
        add_box(ca * 0.48, 0.02, sa * 0.48, 0.15, 0.04, 0.13, "Mat_DarkTitanium")
        # Status energy light on outrigger
        add_box(ca * 0.42, 0.10, sa * 0.42, 0.04, 0.02, 0.04, "Mat_PlasmaCyan")

    # 2. Rotating Turntable Ring
    add_cylinder_y(0, 0.13, 0, 0.28, 0.30, 0.06, 16, "Mat_FactionArmor")
    # Turret rotation flange
    add_cylinder_y(0, 0.17, 0, 0.25, 0.25, 0.03, 16, "Mat_DarkTitanium")

    # Elevation Hydraulics (Left and Right rams)
    add_cylinder_y(-0.16, 0.22, 0.02, 0.035, 0.035, 0.16, 8, "Mat_DarkTitanium")
    add_cylinder_y(0.16, 0.22, 0.02, 0.035, 0.035, 0.16, 8, "Mat_DarkTitanium")

    # 3. Main Armored Turret Housing (Carriage)
    # Lower chassis block
    add_box(0, 0.24, -0.02, 0.32, 0.12, 0.34, "Mat_DarkTitanium")
    # Sloped upper armor mantle
    add_box(0, 0.31, -0.04, 0.26, 0.10, 0.28, "Mat_FactionArmor")

    # Rear Power Capacitor Pack (Two heavy cylindrical cells)
    add_cylinder_y(-0.08, 0.27, -0.20, 0.05, 0.05, 0.14, 8, "Mat_DarkTitanium")
    add_cylinder_y(0.08, 0.27, -0.20, 0.05, 0.05, 0.14, 8, "Mat_DarkTitanium")
    # Capacitor glowing energy rings
    add_cylinder_y(-0.08, 0.27, -0.20, 0.053, 0.053, 0.03, 8, "Mat_PlasmaCyan")
    add_cylinder_y(0.08, 0.27, -0.20, 0.053, 0.053, 0.03, 8, "Mat_PlasmaCyan")

    # Top Commander Observation Cupola
    add_cylinder_y(0, 0.38, -0.06, 0.09, 0.11, 0.06, 8, "Mat_DarkTitanium")
    # Vision slit / optic periscope band
    add_cylinder_y(0, 0.42, -0.06, 0.06, 0.07, 0.03, 8, "Mat_Optics")
    # Antenna mast
    add_cylinder_y(0.05, 0.48, -0.10, 0.008, 0.008, 0.12, 4, "Mat_DarkTitanium")

    # Side Optical Targeting Sensor Pod
    add_box(-0.17, 0.34, 0.08, 0.08, 0.09, 0.12, "Mat_DarkTitanium")
    add_box(-0.17, 0.34, 0.15, 0.05, 0.06, 0.02, "Mat_Optics")

    # 4. HEAVY TWIN PULSE RAILGUNS (Left and Right)
    barrel_x_offsets = [-0.11, 0.11]
    for bx in barrel_x_offsets:
        # Breech Mount Trunnion
        add_box(bx, 0.25, 0.16, 0.11, 0.11, 0.14, "Mat_DarkTitanium")

        # Rear Breech Cooling Ribs (Concentric rings along Z-axis)
        add_cylinder_z(bx, 0.25, 0.25, 0.056, 0.056, 0.02, 8, "Mat_FactionArmor")
        add_cylinder_z(bx, 0.25, 0.29, 0.056, 0.056, 0.02, 8, "Mat_FactionArmor")
        add_cylinder_z(bx, 0.25, 0.33, 0.056, 0.056, 0.02, 8, "Mat_FactionArmor")

        # Main Heavy Barrel Structure (Chunky rectangular beam along Z)
        add_box(bx, 0.25, 0.54, 0.08, 0.09, 0.44, "Mat_DarkTitanium")

        # GLOWING CYAN PLASMA ACCELERATION CHANNEL (Top & Bottom inner rails)
        add_box(bx, 0.278, 0.54, 0.04, 0.028, 0.40, "Mat_PlasmaCyan")
        add_box(bx, 0.222, 0.54, 0.04, 0.028, 0.40, "Mat_PlasmaCyan")

        # Quad-Prong Heavy Muzzle Brake at the tip
        add_box(bx, 0.25, 0.77, 0.10, 0.11, 0.05, "Mat_DarkTitanium")
        # Hollow muzzle bore exit (glowing cyan firing chamber)
        add_box(bx, 0.25, 0.796, 0.05, 0.06, 0.01, "Mat_PlasmaCyan")

    # ================= WRITE OBJ & MTL FILES =================
    os.makedirs(os.path.dirname(output_obj_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_mtl_path), exist_ok=True)

    with open(output_mtl_path, "w") as f:
        f.write("# Materials for Invassion Pulse Defense Cannon\n\n")
        f.write("newmtl Mat_DarkTitanium\n")
        f.write("Ka 0.12 0.15 0.18\n")
        f.write("Kd 0.16 0.20 0.24\n")
        f.write("Ks 0.80 0.85 0.90\n")
        f.write("Ns 45.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_FactionArmor\n")
        f.write("Ka 0.10 0.40 0.20\n")
        f.write("Kd 0.14 0.65 0.30\n")
        f.write("Ks 0.50 0.70 0.55\n")
        f.write("Ns 30.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_PlasmaCyan\n")
        f.write("Ka 0.00 0.90 1.00\n")
        f.write("Kd 0.00 0.95 1.00\n")
        f.write("Ks 0.20 0.80 1.00\n")
        f.write("Ke 0.00 0.95 1.00\n")
        f.write("Ns 100.0\n")
        f.write("d 1.0\n\n")

        f.write("newmtl Mat_Optics\n")
        f.write("Ka 0.02 0.10 0.18\n")
        f.write("Kd 0.05 0.20 0.35\n")
        f.write("Ks 0.95 0.95 0.98\n")
        f.write("Ke 0.02 0.30 0.50\n")
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

        for mat_name, face_list in faces.items():
            f.write(f"\nusemtl {mat_name}\n")
            for face in face_list:
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
