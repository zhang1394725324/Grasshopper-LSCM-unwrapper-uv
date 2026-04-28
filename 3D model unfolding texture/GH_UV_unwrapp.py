import Rhino.Geometry as rg

# 方法定义（与Rhino API对应）
# LSCM = 0 (Least Squares Conformal Map)
# ABFPP = 1 (Angle Based Flattening ++)
# ARAP = 2 (As Rigid As Possible)

def run_unwrap(input_mesh, method_type):
    """Perform mesh unwrapping with selected method."""
    
    if not input_mesh:
        return None, None, None
    
    # 1. Create a working copy
    working_mesh = input_mesh.DuplicateMesh()
    
    # 2. Disable double precision to avoid MeshUnwrapper bug
    working_mesh.Vertices.UseDoublePrecisionVertices = False
    
    # 3. 根据选择的 method_type 设置展开方法
    if method_type == 0:
        unwrap_method = rg.MeshUnwrapMethod.LSCM
        method_name = "LSCM (Least Squares Conformal Map)"
    elif method_type == 1:
        unwrap_method = rg.MeshUnwrapMethod.ABFPP
        method_name = "ABF++ (Angle Based Flattening)"
    elif method_type == 2:
        unwrap_method = rg.MeshUnwrapMethod.ARAP
        method_name = "ARAP (As Rigid As Possible)"
    else:
        # 默认使用 LSCM
        unwrap_method = rg.MeshUnwrapMethod.LSCM
        method_name = "LSCM (Default)"
    
    # 4. Initialize unwrapper and compute mapping
    unwrapper = rg.MeshUnwrapper(working_mesh)
    success = unwrapper.Unwrap(unwrap_method)
    
    if not success:
        print(f"Unwrapping failed with method: {method_name}")
        return None, None, None
    
    print(f"Successfully unwrapped using: {method_name}")
    
    # 5. Extract texture coordinates
    uv_points = []
    uv_coords = []
    
    for i in range(working_mesh.TextureCoordinates.Count):
        uv = working_mesh.TextureCoordinates[i]
        uv_points.append(rg.Point3d(uv.X, uv.Y, 0))
        uv_coords.append(uv)
    
    # 6. Create UV plane mesh
    uv_mesh = create_uv_mesh(working_mesh, uv_coords)
    
    return working_mesh, uv_points, uv_mesh


def create_uv_mesh(original_mesh, uv_coords):
    """Create a flat mesh using UV coordinates as vertex positions."""
    
    if len(uv_coords) == 0:
        return None
    
    uv_mesh = rg.Mesh()
    
    # Add vertices using UV coordinates (Z=0)
    for uv in uv_coords:
        uv_mesh.Vertices.Add(uv.X, uv.Y, 0)
    
    # Copy face topology
    for i in range(original_mesh.Faces.Count):
        face = original_mesh.Faces[i]
        
        if face.IsTriangle:
            uv_mesh.Faces.AddFace(face.A, face.B, face.C)
        elif face.IsQuad:
            uv_mesh.Faces.AddFace(face.A, face.B, face.C, face.D)
    
    uv_mesh.Normals.ComputeNormals()
    uv_mesh.Compact()
    
    return uv_mesh


# ----- Grasshopper Component -----
# Inputs:
#   input_mesh (Mesh): 输入的网格
#   run (bool): Boolean Toggle - 控制是否运行
#   reset (bool): Button - 复位刷新
#   method (int): Method选择 - 0:LSCM, 1:ABFPP, 2:ARAP

# 使用模块级变量存储状态
if not hasattr(run_unwrap, 'cached_result'):
    run_unwrap.cached_result = (None, None, None)
    run_unwrap.last_run = False
    run_unwrap.last_reset = False
    run_unwrap.last_method = -1
    run_unwrap.last_mesh_id = None

# 获取当前网格的唯一标识（用于检测网格变化）
current_mesh_id = id(input_mesh) if input_mesh is not None else None

# 处理复位按钮（上升沿检测）
if reset and not run_unwrap.last_reset:
    # 复位：清空缓存和输出
    run_unwrap.cached_result = (None, None, None)
    unwrapped_mesh, uv_points, uv_mesh = (None, None, None)
    run_unwrap.last_reset = reset
    run_unwrap.last_run = False
    run_unwrap.last_method = -1
    print("Reset: All outputs cleared")
    
elif not reset:
    run_unwrap.last_reset = reset
    
    # 检查是否需要重新计算
    needs_recompute = False
    
    if run:
        # 检查各种触发重新计算的条件
        if run != run_unwrap.last_run:
            needs_recompute = True
            print("Recompute triggered: Run state changed")
        
        if current_mesh_id != run_unwrap.last_mesh_id:
            needs_recompute = True
            print("Recompute triggered: Input mesh changed")
        
        if method != run_unwrap.last_method:
            needs_recompute = True
            method_names = ["LSCM", "ABFPP", "ARAP"]
            print(f"Recompute triggered: Method changed to {method_names[method] if 0 <= method <= 2 else 'Unknown'}")
        
        if needs_recompute:
            # 执行展开计算
            result = run_unwrap(input_mesh, method)
            if result[0] is not None:
                run_unwrap.cached_result = result
                # 更新缓存的状态
                run_unwrap.last_method = method
                run_unwrap.last_mesh_id = current_mesh_id
        
        # 输出缓存的结果
        unwrapped_mesh, uv_points, uv_mesh = run_unwrap.cached_result
        run_unwrap.last_run = run
        
    else:
        # 不运行时，如果有缓存结果则显示，否则输出None
        if run_unwrap.cached_result[0] is not None:
            unwrapped_mesh, uv_points, uv_mesh = run_unwrap.cached_result
        else:
            unwrapped_mesh, uv_points, uv_mesh = (None, None, None)
        run_unwrap.last_run = run
        
else:
    # reset 为 True 且已经处理过
    if run_unwrap.cached_result[0] is not None:
        run_unwrap.cached_result = (None, None, None)
        run_unwrap.last_method = -1
    unwrapped_mesh, uv_points, uv_mesh = (None, None, None)
