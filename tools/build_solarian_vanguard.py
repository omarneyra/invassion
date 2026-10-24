"""
Builds the Solarian Vanguard Mech 3D model (.glb) using Blender's Python API (bpy).
Matches the concept art:
- Angular military cockpit chassis with glowing cyan visor
- Reactor backpack with orange thermal radiators and exhaust stacks
- Right arm: Heavy plasma railgun with copper coils and glowing cyan channel
- Left arm: Rotary 6-barrel gatling cannon with ammo drum
- Bipedal reverse-joint hydraulic legs with wide industrial footpads
- PBR materials: Gunmetal titanium, armor plating, cyan plasma glow, copper, thermal reactor
- Skeleton3D armature with clean mechanical bone hierarchy
- Embedded animations: 'idle', 'walk', 'attack'
"""

import sys
import math
import bpy

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, base_color, metallic=0.0, roughness=0.5, emission_color=(0,0,0,1), emission_energy=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Base Color
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        # Metallic
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        # Roughness
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        # Emission
        if emission_energy > 0.0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_energy
    return mat

def create_mesh_object(name, mesh_type, location=(0,0,0), scale=(1,1,1), rotation=(0,0,0), **kwargs):
    if mesh_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation, scale=scale)
    elif mesh_type == 'cylinder':
        r = kwargs.get('radius', 0.5)
        d = kwargs.get('depth', 1.0)
        verts = kwargs.get('vertices', 16)
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=location, rotation=rotation, scale=scale)
    elif mesh_type == 'cone':
        r1 = kwargs.get('radius1', 0.5)
        d = kwargs.get('depth', 1.0)
        bpy.ops.mesh.primitive_cone_add(radius1=r1, depth=d, location=location, rotation=rotation, scale=scale)
    elif mesh_type == 'torus':
        mr = kwargs.get('major_radius', 0.5)
        mnr = kwargs.get('minor_radius', 0.1)
        bpy.ops.mesh.primitive_torus_add(major_radius=mr, minor_radius=mnr, location=location, rotation=rotation)
    
    obj = bpy.context.active_object
    obj.scale = scale
    obj.name = name
    return obj

def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def parent_to_bone(obj, armature_obj, bone_name):
    obj.parent = armature_obj
    obj.parent_type = 'BONE'
    obj.parent_bone = bone_name

def build_vanguard_mech(output_path):
    clear_scene()
    
    # 1. Create Materials
    mat_gunmetal = create_material("Mat_Gunmetal", (0.16, 0.18, 0.20, 1.0), metallic=0.88, roughness=0.38)
    mat_armor = create_material("Mat_ArmorPlating", (0.28, 0.32, 0.35, 1.0), metallic=0.65, roughness=0.32)
    mat_dark_frame = create_material("Mat_DarkFrame", (0.08, 0.09, 0.10, 1.0), metallic=0.92, roughness=0.50)
    mat_cyan_glow = create_material("Mat_CyanGlow", (0.0, 0.9, 1.0, 1.0), metallic=0.1, roughness=0.1,
                                    emission_color=(0.0, 0.9, 1.0, 1.0), emission_energy=5.0)
    mat_reactor_heat = create_material("Mat_ReactorHeat", (1.0, 0.35, 0.05, 1.0), metallic=0.2, roughness=0.2,
                                       emission_color=(1.0, 0.35, 0.05, 1.0), emission_energy=4.5)
    mat_copper = create_material("Mat_Copper", (0.72, 0.42, 0.22, 1.0), metallic=0.95, roughness=0.22)
    mat_hazard = create_material("Mat_HazardYellow", (0.85, 0.70, 0.08, 1.0), metallic=0.3, roughness=0.4)

    # 2. Build Armature
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0,0,0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Armature_SolarianVanguard"
    edit_bones = arm_obj.data.edit_bones
    
    # Root bone
    b_root = edit_bones[0]
    b_root.name = "Root"
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.3)
    
    # Pelvis
    b_pelvis = edit_bones.new("Pelvis")
    b_pelvis.head = (0, 0, 1.4)
    b_pelvis.tail = (0, 0, 1.7)
    b_pelvis.parent = b_root
    
    # Torso
    b_torso = edit_bones.new("Torso")
    b_torso.head = (0, 0, 1.7)
    b_torso.tail = (0, 0, 2.7)
    b_torso.parent = b_pelvis
    
    # Weapon Arms
    b_shoulder_r = edit_bones.new("Shoulder_R") # Mech Right (Plasma Railgun)
    b_shoulder_r.head = (-0.75, 0.1, 2.3)
    b_shoulder_r.tail = (-1.05, 0.1, 2.3)
    b_shoulder_r.parent = b_torso
    
    b_weapon_r = edit_bones.new("Weapon_R")
    b_weapon_r.head = (-1.05, 0.1, 2.3)
    b_weapon_r.tail = (-1.05, 1.0, 2.0)
    b_weapon_r.parent = b_shoulder_r
    
    b_shoulder_l = edit_bones.new("Shoulder_L") # Mech Left (Gatling)
    b_shoulder_l.head = (0.75, 0.1, 2.3)
    b_shoulder_l.tail = (1.05, 0.1, 2.3)
    b_shoulder_l.parent = b_torso
    
    b_weapon_l = edit_bones.new("Weapon_L")
    b_weapon_l.head = (1.05, 0.1, 2.3)
    b_weapon_l.tail = (1.05, 1.0, 2.0)
    b_weapon_l.parent = b_shoulder_l
    
    # Legs (Reverse-joint: Thigh -> Knee back -> Shin forward -> Foot)
    for side, sign in [("L", 1), ("R", -1)]:
        b_thigh = edit_bones.new(f"Thigh_{side}")
        b_thigh.head = (sign * 0.45, 0.0, 1.4)
        b_thigh.tail = (sign * 0.50, -0.4, 0.85) # slant back
        b_thigh.parent = b_pelvis
        
        b_shin = edit_bones.new(f"Shin_{side}")
        b_shin.head = (sign * 0.50, -0.4, 0.85)
        b_shin.tail = (sign * 0.50, 0.2, 0.25) # slant forward to ankle
        b_shin.parent = b_thigh
        
        b_foot = edit_bones.new(f"Foot_{side}")
        b_foot.head = (sign * 0.50, 0.2, 0.25)
        b_foot.tail = (sign * 0.50, 0.55, 0.0) # flat footpad
        b_foot.parent = b_shin
        
    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Create Geometric Parts & Attach to Bones
    
    # --- Pelvis ---
    p_turntable = create_mesh_object("Pelvis_Turntable", 'cylinder', location=(0, 0, 1.45), scale=(0.55, 0.55, 0.25))
    assign_material(p_turntable, mat_dark_frame)
    parent_to_bone(p_turntable, arm_obj, "Pelvis")
    
    p_core = create_mesh_object("Pelvis_Armor", 'cube', location=(0, 0, 1.55), scale=(0.7, 0.5, 0.35))
    assign_material(p_core, mat_gunmetal)
    parent_to_bone(p_core, arm_obj, "Pelvis")

    # --- Torso (Cabin, Visor, Radiators, Exhausts) ---
    t_chassis = create_mesh_object("Torso_Chassis", 'cube', location=(0, 0.05, 2.2), scale=(1.1, 0.9, 0.9))
    assign_material(t_chassis, mat_armor)
    parent_to_bone(t_chassis, arm_obj, "Torso")
    
    t_chest_plate = create_mesh_object("Torso_ChestPlate", 'cube', location=(0, 0.45, 2.15), scale=(0.85, 0.25, 0.65), rotation=(math.radians(18), 0, 0))
    assign_material(t_chest_plate, mat_gunmetal)
    parent_to_bone(t_chest_plate, arm_obj, "Torso")
    
    # Visor slit (Glowing cyan)
    t_visor = create_mesh_object("Torso_Visor", 'cube', location=(0, 0.56, 2.38), scale=(0.52, 0.06, 0.12), rotation=(math.radians(18), 0, 0))
    assign_material(t_visor, mat_cyan_glow)
    parent_to_bone(t_visor, arm_obj, "Torso")
    
    # Reactor Backpack & Radiator Fins
    t_backpack = create_mesh_object("Torso_Backpack", 'cube', location=(0, -0.48, 2.3), scale=(0.85, 0.35, 0.8))
    assign_material(t_backpack, mat_dark_frame)
    parent_to_bone(t_backpack, arm_obj, "Torso")
    
    for offset_x in [-0.25, 0.25]:
        t_fins = create_mesh_object(f"Torso_Radiator_{offset_x}", 'cube', location=(offset_x, -0.52, 2.75), scale=(0.28, 0.25, 0.45))
        assign_material(t_fins, mat_reactor_heat)
        parent_to_bone(t_fins, arm_obj, "Torso")
        
        t_exhaust = create_mesh_object(f"Torso_Exhaust_{offset_x}", 'cylinder', location=(offset_x * 1.6, -0.52, 2.5), scale=(0.10, 0.10, 0.6), rotation=(math.radians(-15), 0, 0))
        assign_material(t_exhaust, mat_gunmetal)
        parent_to_bone(t_exhaust, arm_obj, "Torso")

    # --- Right Arm (Plasma Railgun) ---
    r_pauldron = create_mesh_object("Shoulder_R_Armor", 'cube', location=(-0.95, 0.08, 2.35), scale=(0.45, 0.55, 0.55))
    assign_material(r_pauldron, mat_hazard)
    parent_to_bone(r_pauldron, arm_obj, "Shoulder_R")
    
    r_gun_body = create_mesh_object("Railgun_Housing", 'cube', location=(-1.05, 0.55, 2.05), scale=(0.32, 0.95, 0.38))
    assign_material(r_gun_body, mat_gunmetal)
    parent_to_bone(r_gun_body, arm_obj, "Weapon_R")
    
    # Dual Rail Prongs
    for prong_z in [2.15, 1.95]:
        r_prong = create_mesh_object(f"Railgun_Prong_{prong_z}", 'cube', location=(-1.05, 1.45, prong_z), scale=(0.18, 0.95, 0.08))
        assign_material(r_prong, mat_dark_frame)
        parent_to_bone(r_prong, arm_obj, "Weapon_R")
        
    # Glowing Plasma Channel
    r_plasma = create_mesh_object("Railgun_PlasmaCore", 'cube', location=(-1.05, 1.35, 2.05), scale=(0.08, 0.75, 0.06))
    assign_material(r_plasma, mat_cyan_glow)
    parent_to_bone(r_plasma, arm_obj, "Weapon_R")
    
    # Magnetic Copper Coils
    for coil_y in [0.4, 0.65, 0.9]:
        r_coil = create_mesh_object(f"Railgun_Coil_{coil_y}", 'torus', location=(-1.05, coil_y, 2.05), scale=(0.28, 0.28, 0.28), rotation=(0, math.radians(90), 0))
        assign_material(r_coil, mat_copper)
        parent_to_bone(r_coil, arm_obj, "Weapon_R")

    # --- Left Arm (Rotary Gatling Cannon) ---
    l_pauldron = create_mesh_object("Shoulder_L_Armor", 'cube', location=(0.95, 0.08, 2.35), scale=(0.45, 0.55, 0.55))
    assign_material(l_pauldron, mat_armor)
    parent_to_bone(l_pauldron, arm_obj, "Shoulder_L")
    
    l_drum = create_mesh_object("Gatling_AmmoDrum", 'cylinder', location=(1.25, 0.25, 1.95), scale=(0.35, 0.35, 0.45), rotation=(0, math.radians(90), 0))
    assign_material(l_drum, mat_dark_frame)
    parent_to_bone(l_drum, arm_obj, "Weapon_L")
    
    l_housing = create_mesh_object("Gatling_RotorHousing", 'cylinder', location=(1.05, 0.65, 2.05), scale=(0.26, 0.26, 0.45), rotation=(math.radians(90), 0, 0))
    assign_material(l_housing, mat_gunmetal)
    parent_to_bone(l_housing, arm_obj, "Weapon_L")
    
    # 6 Gatling Barrels
    for i in range(6):
        angle = i * (2 * math.pi / 6)
        bx = 1.05 + 0.12 * math.cos(angle)
        bz = 2.05 + 0.12 * math.sin(angle)
        barrel = create_mesh_object(f"Gatling_Barrel_{i}", 'cylinder', location=(bx, 1.25, bz), scale=(0.035, 0.035, 0.85), rotation=(math.radians(90), 0, 0))
        assign_material(barrel, mat_dark_frame)
        parent_to_bone(barrel, arm_obj, "Weapon_L")
        
    l_clamp = create_mesh_object("Gatling_BarrelClamp", 'torus', location=(1.05, 1.5, 2.05), scale=(0.18, 0.18, 0.18), rotation=(math.radians(90), 0, 0))
    assign_material(l_clamp, mat_armor)
    parent_to_bone(l_clamp, arm_obj, "Weapon_L")

    # --- Legs & Feet ---
    for side, sign in [("L", 1), ("R", -1)]:
        # Thigh Upper Assembly
        thigh_joint = create_mesh_object(f"Thigh_{side}_Joint", 'cylinder', location=(sign * 0.45, 0.0, 1.4), scale=(0.22, 0.22, 0.35), rotation=(0, math.radians(90), 0))
        assign_material(thigh_joint, mat_dark_frame)
        parent_to_bone(thigh_joint, arm_obj, f"Thigh_{side}")
        
        thigh_plate = create_mesh_object(f"Thigh_{side}_Armor", 'cube', location=(sign * 0.48, -0.2, 1.15), scale=(0.32, 0.38, 0.65), rotation=(math.radians(-25), 0, 0))
        assign_material(thigh_plate, mat_armor)
        parent_to_bone(thigh_plate, arm_obj, f"Thigh_{side}")
        
        # Knee Knuckle
        knee = create_mesh_object(f"Knee_{side}_Joint", 'cylinder', location=(sign * 0.50, -0.4, 0.85), scale=(0.20, 0.20, 0.32), rotation=(0, math.radians(90), 0))
        assign_material(knee, mat_gunmetal)
        parent_to_bone(knee, arm_obj, f"Shin_{side}")
        
        # Shin Struts (Hydraulic Dual Rods)
        shin_strut = create_mesh_object(f"Shin_{side}_Strut", 'cube', location=(sign * 0.50, -0.1, 0.55), scale=(0.28, 0.32, 0.68), rotation=(math.radians(35), 0, 0))
        assign_material(shin_strut, mat_armor)
        parent_to_bone(shin_strut, arm_obj, f"Shin_{side}")
        
        piston = create_mesh_object(f"Shin_{side}_Piston", 'cylinder', location=(sign * 0.50, 0.05, 0.55), scale=(0.06, 0.06, 0.65), rotation=(math.radians(35), 0, 0))
        assign_material(piston, mat_dark_frame)
        parent_to_bone(piston, arm_obj, f"Shin_{side}")
        
        # Ankle & Footpad
        ankle = create_mesh_object(f"Ankle_{side}_Joint", 'cylinder', location=(sign * 0.50, 0.2, 0.25), scale=(0.18, 0.18, 0.28), rotation=(0, math.radians(90), 0))
        assign_material(ankle, mat_gunmetal)
        parent_to_bone(ankle, arm_obj, f"Foot_{side}")
        
        # Industrial Stabilizer Footpad (Main Sole + Toes + Heel Claw)
        foot_sole = create_mesh_object(f"Foot_{side}_Sole", 'cube', location=(sign * 0.50, 0.28, 0.08), scale=(0.42, 0.65, 0.16))
        assign_material(foot_sole, mat_dark_frame)
        parent_to_bone(foot_sole, arm_obj, f"Foot_{side}")
        
        toe_outer = create_mesh_object(f"Foot_{side}_ToeOut", 'cube', location=(sign * 0.62, 0.55, 0.06), scale=(0.14, 0.28, 0.12), rotation=(0, 0, math.radians(sign * 12)))
        assign_material(toe_outer, mat_armor)
        parent_to_bone(toe_outer, arm_obj, f"Foot_{side}")
        
        toe_inner = create_mesh_object(f"Foot_{side}_ToeIn", 'cube', location=(sign * 0.38, 0.55, 0.06), scale=(0.14, 0.28, 0.12), rotation=(0, 0, math.radians(sign * -12)))
        assign_material(toe_inner, mat_armor)
        parent_to_bone(toe_inner, arm_obj, f"Foot_{side}")
        
        heel_spur = create_mesh_object(f"Foot_{side}_HeelSpur", 'cube', location=(sign * 0.50, -0.05, 0.08), scale=(0.28, 0.22, 0.14))
        assign_material(heel_spur, mat_armor)
        parent_to_bone(heel_spur, arm_obj, f"Foot_{side}")

    # 4. Create Animations on Armature
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bones = arm_obj.pose.bones
    
    # ----------------------------------------------------
    # Action 1: "idle" (60 frames, smooth reactor hum & weight shift)
    # ----------------------------------------------------
    act_idle = bpy.data.actions.new(name="idle")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act_idle
    
    # Keyframe Pelvis & Torso subtle breathing
    for frame, z_offset, tilt_deg in [(1, 0.0, 0.0), (30, -0.03, 1.5), (60, 0.0, 0.0)]:
        bpy.context.scene.frame_set(frame)
        pose_bones["Pelvis"].location = (0, 0, z_offset)
        pose_bones["Pelvis"].keyframe_insert(data_path="location", frame=frame)
        
        pose_bones["Torso"].rotation_euler = (math.radians(tilt_deg), 0, 0)
        pose_bones["Torso"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Subtle weapon steadying
        pose_bones["Weapon_R"].rotation_euler = (math.radians(-tilt_deg * 0.5), 0, 0)
        pose_bones["Weapon_R"].keyframe_insert(data_path="rotation_euler", frame=frame)
        pose_bones["Weapon_L"].rotation_euler = (math.radians(-tilt_deg * 0.5), 0, 0)
        pose_bones["Weapon_L"].keyframe_insert(data_path="rotation_euler", frame=frame)

    # ----------------------------------------------------
    # Action 2: "walk" (40 frames, cyclic bipedal hydraulic stride)
    # ----------------------------------------------------
    act_walk = bpy.data.actions.new(name="walk")
    arm_obj.animation_data.action = act_walk
    
    walk_keys = [
        # Frame, Pelvis_z, L_thigh_deg, L_shin_deg, R_thigh_deg, R_shin_deg, Torso_yaw
        (1,   0.00,  18.0, -15.0, -18.0,  20.0,   3.0),
        (10, -0.04,   0.0,   5.0, -25.0,  35.0,   0.0),
        (20,  0.00, -18.0,  20.0,  18.0, -15.0,  -3.0),
        (30, -0.04, -25.0,  35.0,   0.0,   5.0,   0.0),
        (40,  0.00,  18.0, -15.0, -18.0,  20.0,   3.0),
    ]
    for frame, pz, lt, ls, rt, rs, ty in walk_keys:
        bpy.context.scene.frame_set(frame)
        pose_bones["Pelvis"].location = (0, 0, pz)
        pose_bones["Pelvis"].keyframe_insert(data_path="location", frame=frame)
        
        pose_bones["Torso"].rotation_euler = (0, 0, math.radians(ty))
        pose_bones["Torso"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Left Leg
        pose_bones["Thigh_L"].rotation_euler = (math.radians(lt), 0, 0)
        pose_bones["Thigh_L"].keyframe_insert(data_path="rotation_euler", frame=frame)
        pose_bones["Shin_L"].rotation_euler = (math.radians(ls), 0, 0)
        pose_bones["Shin_L"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Right Leg
        pose_bones["Thigh_R"].rotation_euler = (math.radians(rt), 0, 0)
        pose_bones["Thigh_R"].keyframe_insert(data_path="rotation_euler", frame=frame)
        pose_bones["Shin_R"].rotation_euler = (math.radians(rs), 0, 0)
        pose_bones["Shin_R"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Arm counter-sway
        pose_bones["Weapon_R"].rotation_euler = (math.radians(-lt * 0.4), 0, 0)
        pose_bones["Weapon_R"].keyframe_insert(data_path="rotation_euler", frame=frame)
        pose_bones["Weapon_L"].rotation_euler = (math.radians(-rt * 0.4), 0, 0)
        pose_bones["Weapon_L"].keyframe_insert(data_path="rotation_euler", frame=frame)

    # ----------------------------------------------------
    # Action 3: "attack" (30 frames, Railgun recoil & Gatling spin kick)
    # ----------------------------------------------------
    act_attack = bpy.data.actions.new(name="attack")
    arm_obj.animation_data.action = act_attack
    
    attack_keys = [
        # Frame, Torso_pitch, Railgun_recoil_y, Railgun_pitch, Gatling_pitch
        (1,   0.0,  0.00,  0.0,  0.0),
        (5,  -3.0, -0.15, -6.0,  2.0), # Heavy recoil impulse
        (12, -1.5, -0.08, -3.0,  1.0), # Recovery
        (20,  0.5, -0.02,  0.5, -0.5), # Settling
        (30,  0.0,  0.00,  0.0,  0.0), # Return to battery
    ]
    for frame, tp, ry, rp, gp in attack_keys:
        bpy.context.scene.frame_set(frame)
        pose_bones["Torso"].rotation_euler = (math.radians(tp), 0, 0)
        pose_bones["Torso"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        pose_bones["Weapon_R"].location = (0, ry, 0)
        pose_bones["Weapon_R"].keyframe_insert(data_path="location", frame=frame)
        pose_bones["Weapon_R"].rotation_euler = (math.radians(rp), 0, 0)
        pose_bones["Weapon_R"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        pose_bones["Weapon_L"].rotation_euler = (math.radians(gp), 0, 0)
        pose_bones["Weapon_L"].keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Push all actions to NLA tracks so glTF exporter embeds all of them
    for action in [act_idle, act_walk, act_attack]:
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = action.name
        track.strips.new(action.name, 1, action)

    # 5. Export to .glb
    print(f"Exporting Solarian Vanguard Mech to {output_path}...")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='NLA_TRACKS'
    )
    print("Export complete!")

if __name__ == "__main__":
    out_file = "assets/models/solarian_vanguard.glb"
    if len(sys.argv) > 1 and sys.argv[-1].endswith(".glb"):
        out_file = sys.argv[-1]
    build_vanguard_mech(out_file)
