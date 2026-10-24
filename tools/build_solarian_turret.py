"""
Builds the Solarian Heavy Turret 3D model (.glb) using Blender's Python API (bpy).
Matches the concept art:
- Octagonal heavy armored platform base with 4 outrigger stabilizer anchors
- Dual-ring circular azimuth turntable bearing (360 deg rotation)
- Armored trunnion yoke with dual hydraulic elevation pistons
- Commander sensor cupola dome with targeting optics
- Over-under twin heavy railgun barrels with glowing cyan plasma rails and copper induction coils
- Rear breech counterweights and power conduits
- PBR Materials: Gunmetal steel, armor plating, cyan plasma glow, copper induction, targeting optics
- Armature with: Root -> Base -> Turret_Yaw -> Cannons_Pitch
- Embedded animations: 'idle' (scanning sweep), 'fire' (barrel recoil & recovery)
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
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
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
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    elif mesh_type == 'cylinder':
        r = kwargs.get('radius', 0.5)
        d = kwargs.get('depth', 1.0)
        verts = kwargs.get('vertices', 16)
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=location, rotation=rotation)
    elif mesh_type == 'cone':
        r1 = kwargs.get('radius1', 0.5)
        d = kwargs.get('depth', 1.0)
        bpy.ops.mesh.primitive_cone_add(radius1=r1, depth=d, location=location, rotation=rotation)
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

def build_turret(output_path):
    clear_scene()
    
    # 1. PBR Materials
    mat_gunmetal = create_material("Mat_Turret_Gunmetal", (0.16, 0.18, 0.20, 1.0), metallic=0.88, roughness=0.36)
    mat_armor = create_material("Mat_Turret_Armor", (0.28, 0.32, 0.35, 1.0), metallic=0.70, roughness=0.30)
    mat_dark_frame = create_material("Mat_Turret_DarkFrame", (0.08, 0.09, 0.10, 1.0), metallic=0.92, roughness=0.48)
    mat_cyan_glow = create_material("Mat_Turret_CyanGlow", (0.0, 0.9, 1.0, 1.0), metallic=0.1, roughness=0.1,
                                    emission_color=(0.0, 0.95, 1.0, 1.0), emission_energy=5.5)
    mat_copper = create_material("Mat_Turret_Copper", (0.75, 0.45, 0.22, 1.0), metallic=0.95, roughness=0.22)
    mat_optics = create_material("Mat_Turret_Optics", (0.05, 0.10, 0.15, 1.0), metallic=0.90, roughness=0.08,
                                 emission_color=(0.0, 0.8, 1.0, 1.0), emission_energy=2.5)

    # 2. Armature Setup
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0,0,0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Armature_SolarianTurret"
    edit_bones = arm_obj.data.edit_bones
    
    # Root
    b_root = edit_bones[0]
    b_root.name = "Root"
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.2)
    
    # Base Platform
    b_base = edit_bones.new("Base")
    b_base.head = (0, 0, 0.2)
    b_base.tail = (0, 0, 0.45)
    b_base.parent = b_root
    
    # Turret Yaw (Swivel 360)
    b_turret = edit_bones.new("Turret_Head")
    b_turret.head = (0, 0, 0.5)
    b_turret.tail = (0, 0, 1.3)
    b_turret.parent = b_base
    
    # Cannons Pitch (Elevate / Depress)
    b_cannons = edit_bones.new("Cannons_Elevation")
    b_cannons.head = (0, 0.05, 1.15)
    b_cannons.tail = (0, 1.5, 1.35)
    b_cannons.parent = b_turret
    
    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Geometry Construction
    
    # --- STATIC BASE PLATFORM ---
    # Lower Plinth
    b_plinth = create_mesh_object("Base_Plinth", 'cylinder', location=(0,0,0.08), scale=(1.25, 1.25, 0.16), vertices=8)
    assign_material(b_plinth, mat_dark_frame)
    parent_to_bone(b_plinth, arm_obj, "Base")
    
    # Mid Armor Ring
    b_ring = create_mesh_object("Base_ArmorRing", 'cylinder', location=(0,0,0.22), scale=(1.05, 1.05, 0.14), vertices=16)
    assign_material(b_ring, mat_armor)
    parent_to_bone(b_ring, arm_obj, "Base")
    
    # Turntable Bearing Ring
    b_bearing = create_mesh_object("Base_BearingRing", 'torus', location=(0,0,0.32), scale=(0.85, 0.85, 0.85), major_radius=0.85, minor_radius=0.06)
    assign_material(b_bearing, mat_gunmetal)
    parent_to_bone(b_bearing, arm_obj, "Base")
    
    # 4 Outrigger Stabilizers / Anchors
    for i in range(4):
        ang = i * (math.pi / 2) + (math.pi / 4)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        
        # Outrigger Leg Strut
        leg = create_mesh_object(f"Outrigger_{i}_Strut", 'cube', location=(cos_a * 1.1, sin_a * 1.1, 0.12), scale=(0.35, 0.22, 0.16), rotation=(0, 0, ang))
        assign_material(leg, mat_armor)
        parent_to_bone(leg, arm_obj, "Base")
        
        # Hydraulic Foot Anchor
        foot = create_mesh_object(f"Outrigger_{i}_Foot", 'cube', location=(cos_a * 1.35, sin_a * 1.35, 0.08), scale=(0.28, 0.25, 0.14), rotation=(0, 0, ang))
        assign_material(foot, mat_dark_frame)
        parent_to_bone(foot, arm_obj, "Base")

    # --- TURRET ROTATING HEAD (Attached to Turret_Head bone) ---
    # Rotating Turntable Cap
    t_cap = create_mesh_object("Turret_RotaryCap", 'cylinder', location=(0,0,0.42), scale=(0.82, 0.82, 0.14), vertices=24)
    assign_material(t_cap, mat_gunmetal)
    parent_to_bone(t_cap, arm_obj, "Turret_Head")
    
    # Trunnion Yoke (Left & Right support stanchions)
    for sign in [-1, 1]:
        stanchion = create_mesh_object(f"Trunnion_Stanchion_{sign}", 'cube', location=(sign * 0.48, -0.05, 0.85), scale=(0.24, 0.65, 0.75), rotation=(math.radians(15), 0, 0))
        assign_material(stanchion, mat_armor)
        parent_to_bone(stanchion, arm_obj, "Turret_Head")
        
        # Hydraulic Elevation Cylinder
        piston = create_mesh_object(f"Hydraulic_Piston_{sign}", 'cylinder', location=(sign * 0.42, 0.20, 0.75), scale=(0.08, 0.08, 0.55), rotation=(math.radians(-35), 0, 0))
        assign_material(piston, mat_dark_frame)
        parent_to_bone(piston, arm_obj, "Turret_Head")

    # Rear Armored Avionics / Power Pack
    t_avionics = create_mesh_object("Turret_AvionicsPack", 'cube', location=(0, -0.55, 1.05), scale=(0.65, 0.55, 0.65))
    assign_material(t_avionics, mat_gunmetal)
    parent_to_bone(t_avionics, arm_obj, "Turret_Head")
    
    # Commander Observation Cupola Dome
    t_dome = create_mesh_object("Turret_CupolaDome", 'cylinder', location=(0, -0.45, 1.45), scale=(0.35, 0.35, 0.22), vertices=12)
    assign_material(t_dome, mat_armor)
    parent_to_bone(t_dome, arm_obj, "Turret_Head")
    
    # Targeting Optics Mast
    t_optics = create_mesh_object("Turret_TargetingSensor", 'cube', location=(0.25, -0.25, 1.55), scale=(0.18, 0.22, 0.25))
    assign_material(t_optics, mat_optics)
    parent_to_bone(t_optics, arm_obj, "Turret_Head")
    
    # Antenna Mast
    t_antenna = create_mesh_object("Turret_CommAntenna", 'cylinder', location=(-0.25, -0.65, 1.65), scale=(0.02, 0.02, 0.75))
    assign_material(t_antenna, mat_dark_frame)
    parent_to_bone(t_antenna, arm_obj, "Turret_Head")

    # --- TWIN ELEVATING RAILGUN CANNONS (Attached to Cannons_Elevation bone) ---
    # Central Gun Cradle / Mantlet
    c_mantlet = create_mesh_object("Cannons_Mantlet", 'cube', location=(0, 0.05, 1.15), scale=(0.68, 0.65, 0.58))
    assign_material(c_mantlet, mat_gunmetal)
    parent_to_bone(c_mantlet, arm_obj, "Cannons_Elevation")
    
    # Twin Over-Under Railguns (Upper & Lower)
    for barrel_idx, z_pos in enumerate([1.30, 1.02]):
        prefix = f"Railgun_{barrel_idx}"
        
        # Breech Housing
        breech = create_mesh_object(f"{prefix}_Breech", 'cube', location=(0, 0.45, z_pos), scale=(0.48, 0.65, 0.22))
        assign_material(breech, mat_armor)
        parent_to_bone(breech, arm_obj, "Cannons_Elevation")
        
        # Dual Rails (Left Prong & Right Prong)
        for side, sign_x in [("L", 1), ("R", -1)]:
            rail = create_mesh_object(f"{prefix}_Rail_{side}", 'cube', location=(sign_x * 0.16, 1.45, z_pos), scale=(0.08, 1.45, 0.12))
            assign_material(rail, mat_gunmetal)
            parent_to_bone(rail, arm_obj, "Cannons_Elevation")
            
        # Glowing Cyan Plasma Channel in between rails
        plasma = create_mesh_object(f"{prefix}_PlasmaCore", 'cube', location=(0, 1.40, z_pos), scale=(0.12, 1.25, 0.08))
        assign_material(plasma, mat_cyan_glow)
        parent_to_bone(plasma, arm_obj, "Cannons_Elevation")
        
        # Copper Induction Magnetic Coils
        for c_idx, coil_y in enumerate([0.55, 0.85, 1.15]):
            coil = create_mesh_object(f"{prefix}_Coil_{c_idx}", 'torus', location=(0, coil_y, z_pos), scale=(0.26, 0.26, 0.26), major_radius=0.26, minor_radius=0.04, rotation=(math.radians(90), 0, 0))
            assign_material(coil, mat_copper)
            parent_to_bone(coil, arm_obj, "Cannons_Elevation")
            
        # Heavy Muzzle Shroud / Flash Compensator
        muzzle = create_mesh_object(f"{prefix}_MuzzleBrake", 'cube', location=(0, 2.18, z_pos), scale=(0.42, 0.16, 0.18))
        assign_material(muzzle, mat_dark_frame)
        parent_to_bone(muzzle, arm_obj, "Cannons_Elevation")

    # 4. Create Animations
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = arm_obj.pose.bones
    
    # Action 1: "idle" (80 frames: smooth azimuth 360 scanning sweep & tracking pitch)
    act_idle = bpy.data.actions.new(name="idle")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act_idle
    
    idle_keys = [
        # Frame, Turret_Yaw_deg, Cannons_Pitch_deg
        (1,     0.0,  5.0),
        (20,   35.0,  9.0),
        (40,    0.0,  4.0),
        (60,  -35.0,  8.0),
        (80,    0.0,  5.0),
    ]
    for frame, yaw, pitch in idle_keys:
        bpy.context.scene.frame_set(frame)
        pose_bones["Turret_Head"].rotation_euler = (0, 0, math.radians(yaw))
        pose_bones["Turret_Head"].keyframe_insert(data_path="rotation_euler", frame=frame)
        
        pose_bones["Cannons_Elevation"].rotation_euler = (math.radians(-pitch), 0, 0)
        pose_bones["Cannons_Elevation"].keyframe_insert(data_path="rotation_euler", frame=frame)

    # Action 2: "fire" (25 frames: devastating dual railgun discharge with heavy recoil impulse)
    act_fire = bpy.data.actions.new(name="fire")
    arm_obj.animation_data.action = act_fire
    
    fire_keys = [
        # Frame, Cannons_Pitch, Recoil_Y
        (1,   -6.0,  0.00),
        (3,  -14.0, -0.28), # Heavy recoil thrust
        (8,  -10.0, -0.15), # Hydraulic damping
        (16,  -5.0, -0.04), # Settling
        (25,  -6.0,  0.00), # Return to battery
    ]
    for frame, pitch, ry in fire_keys:
        bpy.context.scene.frame_set(frame)
        pose_bones["Cannons_Elevation"].location = (0, ry, 0)
        pose_bones["Cannons_Elevation"].keyframe_insert(data_path="location", frame=frame)
        pose_bones["Cannons_Elevation"].rotation_euler = (math.radians(pitch), 0, 0)
        pose_bones["Cannons_Elevation"].keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Push to NLA tracks for glTF export
    for action in [act_idle, act_fire]:
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = action.name
        track.strips.new(action.name, 1, action)

    # 5. Export to .glb
    print(f"Exporting Solarian Heavy Turret to {output_path}...")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='NLA_TRACKS'
    )
    print("Turret export complete!")

if __name__ == "__main__":
    out_file = "assets/models/solarian_turret.glb"
    if len(sys.argv) > 1 and sys.argv[-1].endswith(".glb"):
        out_file = sys.argv[-1]
    build_turret(out_file)
