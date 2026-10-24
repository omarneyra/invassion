import bpy
import math
import os

def reset_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_material(name, base_color, metallic, roughness, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color and emission_strength > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_color
    return mat

def get_titanforge_palette():
    return {
        "dark_iron": create_material("TF_DarkIron", (0.12, 0.12, 0.14, 1.0), 0.92, 0.38),
        "steel": create_material("TF_Steel", (0.34, 0.35, 0.38, 1.0), 0.88, 0.28),
        "copper": create_material("TF_Copper", (0.70, 0.38, 0.14, 1.0), 0.90, 0.30),
        "magma": create_material("TF_Magma", (1.0, 0.35, 0.04, 1.0), 0.1, 0.2, (1.0, 0.30, 0.02, 1.0), 4.5),
        "track": create_material("TF_Track", (0.08, 0.08, 0.09, 1.0), 0.20, 0.70),
    }

def add_box(size, location, material=None, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def add_cylinder(radius, depth, location, vertices=16, material=None, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    if material:
        obj.data.materials.append(material)
    return obj

def build_turret(pal):
    reset_scene()
    # 1. Base octogonal fortificada
    add_cylinder(radius=0.88, depth=0.30, location=(0, 0, 0.15), vertices=8, material=pal["dark_iron"])
    
    # 4 Anclajes / Patas de apoyo
    for angle in [math.radians(45), math.radians(135), math.radians(225), math.radians(315)]:
        x = math.cos(angle) * 0.95
        y = math.sin(angle) * 0.95
        add_box(size=(0.32, 0.32, 0.22), location=(x, y, 0.11), material=pal["steel"], rotation=(0, 0, angle))
    
    # 2. Anillo de rotación (Turntable)
    add_cylinder(radius=0.70, depth=0.14, location=(0, 0, 0.37), vertices=16, material=pal["steel"])
    
    # 3. Cúpula blindada del mortero
    add_box(size=(0.82, 0.92, 0.52), location=(0, -0.06, 0.68), material=pal["dark_iron"])
    # Blindaje frontal en cuña
    add_box(size=(0.76, 0.30, 0.38), location=(0, 0.38, 0.62), material=pal["steel"], rotation=(-math.radians(25), 0, 0))
    
    # 4. Cañones dobles de asedio Magma Mortar (elevados a 30 grados)
    barrel_rot = (-math.radians(30), 0, 0)
    for bx in [-0.22, 0.22]:
        # Cañón principal
        add_cylinder(radius=0.14, depth=1.15, location=(bx, 0.55, 0.82), vertices=16, material=pal["dark_iron"], rotation=barrel_rot)
        # Freno de boca pesado
        add_cylinder(radius=0.19, depth=0.22, location=(bx, 1.05, 1.12), vertices=8, material=pal["steel"], rotation=barrel_rot)
        # Cilindro hidráulico superior
        add_cylinder(radius=0.06, depth=0.80, location=(bx, 0.40, 1.00), vertices=12, material=pal["copper"], rotation=barrel_rot)
    
    # 5. Chimeneas de ventilación de calor y magma trasero
    add_box(size=(0.54, 0.22, 0.32), location=(0, -0.48, 0.72), material=pal["dark_iron"])
    add_cylinder(radius=0.09, depth=0.45, location=(-0.16, -0.48, 0.98), vertices=12, material=pal["steel"])
    add_cylinder(radius=0.09, depth=0.45, location=(0.16, -0.48, 0.98), vertices=12, material=pal["steel"])
    
    # Rejillas de magma ardiente
    add_box(size=(0.86, 0.50, 0.08), location=(0, -0.06, 0.70), material=pal["magma"])
    add_cylinder(radius=0.06, depth=0.10, location=(-0.16, -0.48, 1.20), vertices=8, material=pal["magma"])
    add_cylinder(radius=0.06, depth=0.10, location=(0.16, -0.48, 1.20), vertices=8, material=pal["magma"])

def build_harvester(pal):
    reset_scene()
    # 1. Orugas de tracción izquierda y derecha
    for tx in [-0.62, 0.62]:
        # Oruga de goma/oruga reforzada
        add_box(size=(0.34, 1.60, 0.44), location=(tx, 0, 0.22), material=pal["track"])
        # Faldón blindado
        add_box(size=(0.36, 1.45, 0.16), location=(tx, 0, 0.46), material=pal["dark_iron"])
        # Ruedas tractoras en extremos
        add_cylinder(radius=0.20, depth=0.35, location=(tx, -0.70, 0.22), vertices=12, material=pal["steel"], rotation=(0, math.radians(90), 0))
        add_cylinder(radius=0.20, depth=0.35, location=(tx, 0.70, 0.22), vertices=12, material=pal["steel"], rotation=(0, math.radians(90), 0))

    # 2. Chasis central / Planta de refinación
    add_box(size=(0.84, 1.30, 0.54), location=(0, 0, 0.54), material=pal["dark_iron"])
    add_box(size=(0.76, 0.90, 0.32), location=(0, -0.15, 0.92), material=pal["steel"])
    
    # 3. Dos chimeneas geotérmicas de enfriamiento traseras
    for cx in [-0.22, 0.22]:
        add_cylinder(radius=0.12, depth=0.65, location=(cx, -0.45, 1.25), vertices=12, material=pal["dark_iron"])
        # Núcleo de escape de vapor/magma
        add_cylinder(radius=0.08, depth=0.15, location=(cx, -0.45, 1.58), vertices=8, material=pal["magma"])

    # 4. Módulo frontal de trituración / taladro minero
    add_box(size=(0.70, 0.42, 0.36), location=(0, 0.75, 0.38), material=pal["steel"])
    # Tambor triturador rotativo horizontal
    add_cylinder(radius=0.24, depth=0.74, location=(0, 0.98, 0.28), vertices=16, material=pal["dark_iron"], rotation=(0, math.radians(90), 0))
    # Dientes / picos del triturador
    for da in range(0, 360, 60):
        rad = math.radians(da)
        y = 0.98 + math.sin(rad) * 0.26
        z = 0.28 + math.cos(rad) * 0.26
        add_box(size=(0.70, 0.06, 0.06), location=(0, y, z), material=pal["copper"])

    # 5. Conductos de magma sobre la cubierta
    add_cylinder(radius=0.06, depth=1.10, location=(0, 0.05, 1.08), vertices=8, material=pal["copper"], rotation=(math.radians(90), 0, 0))
    add_box(size=(0.50, 0.70, 0.08), location=(0, 0.05, 0.82), material=pal["magma"])

def build_base(pal):
    reset_scene()
    # 1. Base colosal octogonal (Cimientos del Monolito)
    add_cylinder(radius=1.55, depth=0.38, location=(0, 0, 0.19), vertices=8, material=pal["dark_iron"])
    add_cylinder(radius=1.35, depth=0.25, location=(0, 0, 0.48), vertices=8, material=pal["steel"])

    # 4 Bastiones esquineros de defensa
    for bx, by in [(-0.95, -0.95), (0.95, -0.95), (-0.95, 0.95), (0.95, 0.95)]:
        add_box(size=(0.52, 0.52, 0.75), location=(bx, by, 0.58), material=pal["dark_iron"])
        add_box(size=(0.38, 0.38, 0.20), location=(bx, by, 0.98), material=pal["steel"])
        add_box(size=(0.42, 0.12, 0.08), location=(bx, by, 0.85), material=pal["magma"])

    # 2. Estructura principal de la Fundición / Magma Monolith
    add_box(size=(1.40, 1.40, 0.85), location=(0, 0, 0.95), material=pal["dark_iron"])

    # 3. Crisol central de fundición con núcleo de magma visible
    add_cylinder(radius=0.55, depth=1.05, location=(0, 0, 1.70), vertices=16, material=pal["steel"])
    # Ranuras ardientes de magma en el crisol
    add_cylinder(radius=0.52, depth=0.70, location=(0, 0, 1.70), vertices=16, material=pal["magma"])
    # Costillas protectoras de acero sobre el crisol
    for ca in [0, 45, 90, 135]:
        add_box(size=(1.16, 0.14, 0.85), location=(0, 0, 1.70), material=pal["dark_iron"], rotation=(0, 0, math.radians(ca)))

    # 4. Cuatro chimeneas de escape masivas
    for sx, sy in [(-0.45, -0.45), (0.45, -0.45), (-0.45, 0.45), (0.45, 0.45)]:
        add_cylinder(radius=0.14, depth=1.10, location=(sx, sy, 2.05), vertices=12, material=pal["dark_iron"])
        add_cylinder(radius=0.10, depth=0.15, location=(sx, sy, 2.62), vertices=8, material=pal["magma"])

    # Puente grúa / pórtico superior
    add_box(size=(1.50, 0.25, 0.18), location=(0, 0, 2.45), material=pal["steel"])

def build_wall(pal):
    reset_scene()
    # 1. Muro ciclópeo angulado (Barrera blindada en cuña)
    add_box(size=(1.60, 0.65, 0.75), location=(0, 0, 0.375), material=pal["dark_iron"])
    
    # 2. Deflectores inclinados de blindaje pesado frontal
    add_box(size=(1.55, 0.35, 0.60), location=(0, 0.22, 0.45), material=pal["steel"], rotation=(-math.radians(20), 0, 0))
    add_box(size=(1.55, 0.35, 0.60), location=(0, -0.22, 0.45), material=pal["steel"], rotation=(math.radians(20), 0, 0))

    # 3. Dos pilares octogonales de anclaje en los extremos
    add_cylinder(radius=0.38, depth=0.95, location=(-0.82, 0, 0.475), vertices=8, material=pal["dark_iron"])
    add_cylinder(radius=0.38, depth=0.95, location=(0.82, 0, 0.475), vertices=8, material=pal["dark_iron"])
    
    # 4. Riel / Conductor de energía de magma superior
    add_box(size=(1.70, 0.16, 0.12), location=(0, 0, 0.85), material=pal["magma"])
    add_cylinder(radius=0.20, depth=0.15, location=(-0.82, 0, 0.98), vertices=8, material=pal["magma"])
    add_cylinder(radius=0.20, depth=0.15, location=(0.82, 0, 0.98), vertices=8, material=pal["magma"])

def build_purifier(pal):
    reset_scene()
    # 1. Base trípode/cuadrípode de anclaje sísmico pesado
    add_cylinder(radius=0.90, depth=0.22, location=(0, 0, 0.11), vertices=8, material=pal["dark_iron"])
    for angle in [0, math.radians(90), math.radians(180), math.radians(270)]:
        x = math.cos(angle) * 0.95
        y = math.sin(angle) * 0.95
        add_box(size=(0.35, 0.45, 0.18), location=(x, y, 0.09), material=pal["steel"], rotation=(0, 0, angle))

    # 2. Torre de soporte vertical (Gantry del martinete)
    for tx, ty in [(-0.35, -0.35), (0.35, -0.35), (-0.35, 0.35), (0.35, 0.35)]:
        add_box(size=(0.14, 0.14, 1.60), location=(tx, ty, 0.90), material=pal["dark_iron"])

    # 3. Cilindro hidráulico central sísmico
    add_cylinder(radius=0.26, depth=1.40, location=(0, 0, 0.95), vertices=16, material=pal["copper"])
    
    # 4. Cabeza de impacto de tungsteno (Impact Hammer)
    add_cylinder(radius=0.48, depth=0.38, location=(0, 0, 0.32), vertices=8, material=pal["dark_iron"])
    
    # 5. Anillos radiadores de magma sísmico
    add_cylinder(radius=0.55, depth=0.12, location=(0, 0, 1.30), vertices=16, material=pal["magma"])
    add_cylinder(radius=0.45, depth=0.12, location=(0, 0, 1.55), vertices=16, material=pal["magma"])
    add_box(size=(0.80, 0.80, 0.22), location=(0, 0, 1.75), material=pal["steel"])

def build_juggernaut(pal):
    reset_scene()
    # 1. Super-Chasis de asedio con 4 orugas
    for jx in [-0.75, 0.75]:
        add_box(size=(0.38, 1.80, 0.52), location=(jx, 0, 0.26), material=pal["track"])
        add_box(size=(0.42, 1.65, 0.20), location=(jx, 0, 0.54), material=pal["dark_iron"])
    
    # 2. Casamata blindada central
    add_box(size=(1.05, 1.45, 0.65), location=(0, -0.10, 0.65), material=pal["dark_iron"])
    
    # 3. Pala de empuje frontal reforzada (Ramming prow)
    add_box(size=(1.75, 0.28, 0.55), location=(0, 0.95, 0.35), material=pal["steel"], rotation=(math.radians(15), 0, 0))
    
    # 4. Cañones duales super-pesados de asedio
    for cx in [-0.35, 0.35]:
        add_cylinder(radius=0.16, depth=1.45, location=(cx, 0.85, 0.75), vertices=16, material=pal["dark_iron"], rotation=(math.radians(90), 0, 0))
        add_cylinder(radius=0.22, depth=0.30, location=(cx, 1.50, 0.75), vertices=8, material=pal["steel"], rotation=(math.radians(90), 0, 0))
    
    # 5. Núcleo reactor de magma trasero
    add_box(size=(0.70, 0.45, 0.40), location=(0, -0.75, 0.70), material=pal["magma"])

def export_model(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB')
    print(f"Exported: {filepath}")

def main():
    target_dir = "/home/xor/Proyectos/invassion/assets/models/titanforge"
    
    builders = {
        "titanforge_turret.glb": build_turret,
        "titanforge_harvester.glb": build_harvester,
        "titanforge_base.glb": build_base,
        "titanforge_wall.glb": build_wall,
        "titanforge_purifier.glb": build_purifier,
        "titanforge_juggernaut.glb": build_juggernaut,
    }

    for filename, builder_func in builders.items():
        pal = get_titanforge_palette()
        builder_func(pal)
        out_path = os.path.join(target_dir, filename)
        export_model(out_path)

if __name__ == "__main__":
    main()
