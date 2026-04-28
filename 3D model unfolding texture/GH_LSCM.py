import Rhino.Geometry as rg

# 全局变量用于存储上次运行状态
previous_run = False

def run_lscm_unwrap(input_mesh):
    """Perform LSCM unwrapping and return texture coordinates as Point3d."""
    
    if not input_mesh:
        return None, None, None
    
    # 1. Create a working copy
    working_mesh = input_mesh.DuplicateMesh()
    
    # 2. Disable double precision to avoid MeshUnwrapper bug
    working_mesh.Vertices.UseDoublePrecisionVertices = False
    
    # 3. Initialize unwrapper and compute LSCM mapping
    unwrapper = rg.MeshUnwrapper(working_mesh)
    success = unwrapper.Unwrap(rg.MeshUnwrapMethod.LSCM)
    
    if not success:
        print("LSCM unwrapping failed.")
        return None, None, None
    
    # 4. Extract texture coordinates directly from the mesh
    uv_points = []
    uv_coords = []
    
    for i in range(working_mesh.TextureCoordinates.Count):
        uv = working_mesh.TextureCoordinates[i]
        uv_points.append(rg.Point3d(uv.X, uv.Y, 0))
        uv_coords.append(uv)
    
    # 5. Create UV plane mesh
    uv_mesh = create_uv_mesh(working_mesh, uv_coords)
    
    return working_mesh, uv_points, uv_mesh


def create_uv_mesh(original_mesh, uv_coords):
    """Create a flat mesh using UV coordinates as vertex positions."""
    
    if len(uv_coords) == 0:
        return None
    
    uv_mesh = rg.Mesh()
    
    # Add vertices using UV coordinates as 3D points (Z=0)
    for uv in uv_coords:
        uv_mesh.Vertices.Add(uv.X, uv.Y, 0)
    
    # Copy the face topology from original mesh
    for i in range(original_mesh.Faces.Count):
        face = original_mesh.Faces[i]
        
        if face.IsTriangle:
            uv_mesh.Faces.AddFace(face.A, face.B, face.C)
        elif face.IsQuad:
            uv_mesh.Faces.AddFace(face.A, face.B, face.C, face.D)
    
    uv_mesh.Normals.ComputeNormals()
    uv_mesh.Compact()
    
    return uv_mesh


def reset_outputs():
    """Reset all outputs to None"""
    return None, None, None


# ----- Grasshopper Component Input/Output -----
# Inputs:
#   - input_mesh (Mesh): 输入的网格
#   - run (bool): Boolean Toggle 控制是否运行
#   - reset (bool): Button 控制复位刷新

# 检测复位按钮（上升沿触发）
if reset and not hasattr(run_lscm_unwrap, 'last_reset'):
    # 复位：清空所有输出
    unwrapped_mesh = None
    uv_points = []
    uv_mesh = None
    run_lscm_unwrap.last_reset = reset
elif reset and run_lscm_unwrap.last_reset != reset:
    # 复位按钮从False变为True时清空输出
    unwrapped_mesh = None
    uv_points = []
    uv_mesh = None
    run_lscm_unwrap.last_reset = reset
else:
    # 正常逻辑：根据run状态决定是否执行
    if run:
        if input_mesh is not None:
            unwrapped_mesh, uv_points, uv_mesh = run_lscm_unwrap(input_mesh)
        else:
            unwrapped_mesh = None
            uv_points = []
            uv_mesh = None
    else:
        # 不运行时保持上次结果或输出None
        if 'unwrapped_mesh' not in locals():
            unwrapped_mesh = None
            uv_points = []
            uv_mesh = None

# 如果没有last_reset属性，初始化
if not hasattr(run_lscm_unwrap, 'last_reset'):
    run_lscm_unwrap.last_reset = False
