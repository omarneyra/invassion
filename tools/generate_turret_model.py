"""
Procedural 3D OBJ & MTL Generator for the Invassion Pulse Defense Cannon.
Delegates to the shared faction building toolkit in tools/generate_building_models.py.
Maintains 100% backward compatibility with test suites and external callers.
"""

from tools.generate_building_models import build_turret_mesh, write_obj_mtl

def create_turret_obj(output_obj_path="assets/models/turret.obj", output_mtl_path="assets/models/turret.mtl"):
    """Generates the 3D Pulse Defense Cannon OBJ & MTL files."""
    b = build_turret_mesh()
    return write_obj_mtl(b, output_obj_path, output_mtl_path)

if __name__ == "__main__":
    res = create_turret_obj()
    print(f"Generated turret.obj with {res['verts_count']} verts and {res['faces_count']} faces across materials: {res['materials']}")
