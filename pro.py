"""
================================================================================
Mesh Unwrapper with Symmetry Control - Grasshopper Python Component
================================================================================

功能说明:
    对输入网格执行 UV 展开，支持三种展开方法和对称平面控制。
    输出带 UV 坐标的网格、UV 点云和 UV 平面网格。

使用方法:
    1. 连接输入网格 (input_mesh)
    2. 设置 run = True 执行展开
    3. 选择展开方法 (method: 0=LSCM, 1=ABFPP, 2=ARAP)
    4. 可选: 启用对称并指定对称平面
    5. 点击 reset 清空所有输出

参数说明:
    input_mesh      - 要展开的原始网格 (Mesh)
    run             - 运行控制开关 (Boolean: True=运行, False=停止)
    reset           - 复位按钮 (Boolean: True=清空输出)
    method          - 展开方法 (Integer: 0=LSCM, 1=ABFPP, 2=ARAP)
    use_symmetry    - 启用对称 (Boolean: True=启用, False=禁用)
    symmetry_plane  - 对称平面 (Plane: 自定义平面，可选)

输出说明:
    unwrapped_mesh  - 带有 UV 坐标的原始网格 (Mesh)
    uv_points       - UV 坐标点云 (List of Point3d)
    uv_mesh         - UV 空间的平面网格 (Mesh)

版本: 1.0
作者: Grasshopper Python Script
日期: 2026-04-28
================================================================================
"""

import Rhino.Geometry as rg

# ================================================================================
# 函数定义区
# ================================================================================

def create_uv_mesh(mesh, uv_coords):
    """
    从 UV 坐标创建平面网格
    
    参数:
        mesh: 原始网格 (用于获取面拓扑结构)
        uv_coords: UV 坐标列表 (Point2f)
    
    返回:
        uv_mesh: 在 UV 空间中创建的平面网格 (Mesh)
    
    说明:
        - 网格顶点位置由 UV 坐标 (X=U, Y=V, Z=0) 决定
        - 保持原始网格的三角形/四边形面结构
        - 自动计算法线以便正确显示
    """
    if not mesh or not uv_coords:
        return None
    
    uv_mesh = rg.Mesh()
    
    # 步骤1: 添加顶点 (使用 UV 坐标作为 3D 位置)
    for uv in uv_coords:
        uv_mesh.Vertices.Add(uv.X, uv.Y, 0)
    
    # 步骤2: 复制面的拓扑结构
    for i in range(mesh.Faces.Count):
        face = mesh.Faces[i]
        
        if face.IsTriangle:
            # 三角形面: 3个顶点索引
            uv_mesh.Faces.AddFace(face.A, face.B, face.C)
        elif face.IsQuad:
            # 四边形面: 4个顶点索引
            uv_mesh.Faces.AddFace(face.A, face.B, face.C, face.D)
    
    # 步骤3: 计算法线并清理
    uv_mesh.Normals.ComputeNormals()  # 用于正确着色显示
    uv_mesh.Compact()                 # 移除未使用的顶点
    
    return uv_mesh


def unwrap_mesh(input_mesh, method, use_symmetry, symmetry_plane):
    """
    执行网格 UV 展开
    
    参数:
        input_mesh: 输入网格 (Mesh)
        method: 展开方法 (int: 0=LSCM, 1=ABFPP, 2=ARAP)
        use_symmetry: 是否启用对称 (bool)
        symmetry_plane: 对称平面 (Plane, 可选)
    
    返回:
        working_mesh: 带 UV 坐标的网格 (Mesh)
        uv_points: UV 坐标点云 (List of Point3d)
        uv_mesh: UV 平面网格 (Mesh)
    
    算法说明:
        LSCM  (0): 最小二乘共形映射 - 平衡保角性和面积拉伸
        ABFPP (1): 基于角度的展平 - 最优保角性
        ARAP  (2): 尽可能刚性 - 最优保面积性
    
    注意事项:
        - 网格会被复制以避免修改原始数据
        - 使用单精度顶点以规避 Rhino 的已知 bug
        - 对称平面仅对本身对称的网格有效
    """
    # ===== 输入验证 =====
    if not input_mesh:
        print("错误: 没有输入网格")
        return None, None, None
    
    # ===== 步骤1: 复制网格并修正精度 =====
    # 创建网格副本，避免修改原始数据
    working_mesh = input_mesh.DuplicateMesh()
    
    # 规避 Rhino 的已知精度 bug
    # 使用单精度顶点 (Float) 代替双精度 (Double)
    working_mesh.Vertices.UseDoublePrecisionVertices = False
    
    # ===== 步骤2: 创建 Unwrapper 实例 =====
    # MeshUnwrapper 类是 Rhino 专门用于 UV 展开的核心类
    unwrapper = rg.MeshUnwrapper(working_mesh)
    
    # ===== 步骤3: 设置对称平面（如果启用）=====
    if use_symmetry:
        if symmetry_plane is not None:
            # 使用用户指定的对称平面
            unwrapper.SymmetryPlane = symmetry_plane
            print(f"✓ 对称已启用 - 使用自定义平面: {symmetry_plane}")
        else:
            # 使用默认的 XY 平面作为对称平面
            unwrapper.SymmetryPlane = rg.Plane.WorldXY
            print("✓ 对称已启用 - 使用默认平面 (World XY)")
    else:
        print("○ 对称未启用")
    
    # ===== 步骤4: 选择并执行展开方法 =====
    # 方法映射表: 用户输入值 → Rhino API 枚举值
    method_map = {
        0: rg.MeshUnwrapMethod.LSCM,   # 最小二乘共形映射
        1: rg.MeshUnwrapMethod.ABFPP,  # 基于角度的展平
        2: rg.MeshUnwrapMethod.ARAP    # 尽可能刚性
    }
    
    # 获取选中的方法，默认为 LSCM
    unwrap_method = method_map.get(method, rg.MeshUnwrapMethod.LSCM)
    
    # 方法名称（用于输出信息）
    method_names = {
        rg.MeshUnwrapMethod.LSCM: "LSCM (最小二乘共形映射)",
        rg.MeshUnwrapMethod.ABFPP: "ABF++ (基于角度的展平)",
        rg.MeshUnwrapMethod.ARAP: "ARAP (尽可能刚性)"
    }
    
    print(f"→ 执行展开方法: {method_names[unwrap_method]}")
    
    # 执行展开计算
    success = unwrapper.Unwrap(unwrap_method)
    
    if not success:
        print("✗ 展开失败！请检查网格是否有效")
        return None, None, None
    
    print("✓ 展开成功")
    
    # ===== 步骤5: 提取 UV 坐标 =====
    # 从网格中获取计算好的纹理坐标
    # TextureCoordinates 属性返回 Point2f 列表 (U, V 坐标)
    uv_coords = []
    uv_points = []
    
    texture_count = working_mesh.TextureCoordinates.Count
    print(f"→ 提取 UV 坐标: {texture_count} 个顶点")
    
    for i in range(texture_count):
        uv = working_mesh.TextureCoordinates[i]
        uv_coords.append(uv)
        # 转换为 Point3d (Z=0) 以便在 3D 空间中显示
        uv_points.append(rg.Point3d(uv.X, uv.Y, 0))
    
    # ===== 步骤6: 创建 UV 平面网格 =====
    uv_mesh = create_uv_mesh(working_mesh, uv_coords)
    
    if uv_mesh:
        print(f"✓ UV 平面网格创建成功: {uv_mesh.Vertices.Count} 顶点, {uv_mesh.Faces.Count} 面")
    
    # ===== 步骤7: 清理资源 =====
    # 释放 Unwrapper 占用的内存
    unwrapper.Dispose()
    
    # ===== 返回结果 =====
    print("=" * 50)
    print("展开完成！输出说明:")
    print("  - unwrapped_mesh: 带 UV 坐标的原始网格")
    print(f"  - uv_points: {len(uv_points)} 个 UV 坐标点")
    print("  - uv_mesh: UV 空间的平面网格")
    print("=" * 50)
    
    return working_mesh, uv_points, uv_mesh


def get_mesh_statistics(mesh):
    """
    获取网格统计信息（调试用）
    
    参数:
        mesh: 输入网格
    
    返回:
        dict: 包含顶点数、面数等统计信息
    """
    if not mesh:
        return {"error": "No mesh"}
    
    return {
        "vertices": mesh.Vertices.Count,
        "faces": mesh.Faces.Count,
        "triangles": sum(1 for f in mesh.Faces if f.IsTriangle),
        "quads": sum(1 for f in mesh.Faces if f.IsQuad),
        "has_uv": mesh.TextureCoordinates.Count > 0
    }


# ================================================================================
# Grasshopper 组件主逻辑
# ================================================================================

"""
Grasshopper 输入参数:
    input_mesh (Mesh)       - 要展开的网格
    run (bool)              - 运行控制 (Boolean Toggle)
    reset (bool)            - 复位控制 (Button)
    method (int)            - 展开方法 (Value List: 0,1,2)
    use_symmetry (bool)     - 对称开关 (Boolean Toggle)
    symmetry_plane (Plane)  - 对称平面 (Plane 组件，可选)

Grasshopper 输出参数:
    unwrapped_mesh (Mesh)   - 带 UV 坐标的网格
    uv_points (Point3d)     - UV 坐标点云
    uv_mesh (Mesh)          - UV 平面网格
"""

# ===== 状态管理 =====
# 使用函数属性存储缓存状态，避免每次运行都重新计算
if not hasattr(unwrap_mesh, 'cache'):
    unwrap_mesh.cache = {
        'result': (None, None, None),           # 缓存的结果
        'last_run': False,                       # 上次运行状态
        'last_reset': False,                     # 上次复位状态
        'last_method': -1,                       # 上次使用的方法
        'last_mesh': None,                       # 上次处理的网格ID
        'last_symmetry': False,                  # 上次对称状态
        'last_plane': None,                      # 上次平面ID
        'initialized': True                      # 初始化标志
    }

# 获取当前输入的唯一标识
current_mesh_id = id(input_mesh) if input_mesh is not None else None
current_plane_id = id(symmetry_plane) if symmetry_plane is not None else None

# ===== 复位逻辑 =====
# 检测 reset 按钮的上升沿 (False → True)
if reset and not unwrap_mesh.cache['last_reset']:
    # 执行复位: 清空所有输出和缓存
    unwrap_mesh.cache['result'] = (None, None, None)
    unwrapped_mesh = None
    uv_points = []
    uv_mesh = None
    unwrap_mesh.cache['last_reset'] = reset
    unwrap_mesh.cache['last_run'] = False
    unwrap_mesh.cache['last_method'] = -1
    unwrap_mesh.cache['last_symmetry'] = False
    unwrap_mesh.cache['last_plane'] = None
    print("\n" + "=" * 50)
    print("【复位】所有输出已清空")
    print("=" * 50)
    
elif not reset:
    # 正常执行模式 (reset = False 或 已处理)
    unwrap_mesh.cache['last_reset'] = reset
    
    # ===== 运行逻辑 =====
    if run:
        # 检查是否需要重新计算
        needs_recompute = False
        
        # 条件1: 运行状态改变
        if run != unwrap_mesh.cache['last_run']:
            needs_recompute = True
            print("\n→ 触发重新计算: 运行状态改变")
        
        # 条件2: 输入网格改变
        if current_mesh_id != unwrap_mesh.cache['last_mesh']:
            needs_recompute = True
            stats = get_mesh_statistics(input_mesh)
            if "error" not in stats:
                print(f"\n→ 触发重新计算: 输入网格改变 ({stats['vertices']} 顶点, {stats['faces']} 面)")
            else:
                print("\n→ 触发重新计算: 输入网格改变")
        
        # 条件3: 展开方法改变
        if method != unwrap_mesh.cache['last_method']:
            needs_recompute = True
            method_names_display = ["LSCM", "ABF++", "ARAP"]
            method_text = method_names_display[method] if 0 <= method <= 2 else "Unknown"
            print(f"\n→ 触发重新计算: 方法改变为 {method_text}")
        
        # 条件4: 对称开关状态改变
        if use_symmetry != unwrap_mesh.cache['last_symmetry']:
            needs_recompute = True
            print(f"\n→ 触发重新计算: 对称{'启用' if use_symmetry else '禁用'}")
        
        # 条件5: 对称平面改变
        if current_plane_id != unwrap_mesh.cache['last_plane']:
            needs_recompute = True
            print("\n→ 触发重新计算: 对称平面改变")
        
        # ===== 执行重新计算 =====
        if needs_recompute:
            print("\n" + "=" * 50)
            print("【开始执行 UV 展开】")
            print("=" * 50)
            
            result = unwrap_mesh(input_mesh, method, use_symmetry, symmetry_plane)
            
            if result[0] is not None:
                unwrap_mesh.cache['result'] = result
                unwrap_mesh.cache['last_method'] = method
                unwrap_mesh.cache['last_mesh'] = current_mesh_id
                unwrap_mesh.cache['last_symmetry'] = use_symmetry
                unwrap_mesh.cache['last_plane'] = current_plane_id
                print("\n✓ 计算完成，结果已缓存")
            else:
                print("\n✗ 计算失败，保留上次结果")
        
        # ===== 输出结果 =====
        unwrapped_mesh, uv_points, uv_mesh = unwrap_mesh.cache['result']
        unwrap_mesh.cache['last_run'] = run
        
    else:
        # run = False: 不执行计算，显示缓存结果
        if unwrap_mesh.cache['result'][0] is not None:
            unwrapped_mesh, uv_points, uv_mesh = unwrap_mesh.cache['result']
            # 可选的调试信息: print("○ 停止模式 - 显示缓存结果")
        else:
            unwrapped_mesh, uv_points, uv_mesh = (None, None, None)
        unwrap_mesh.cache['last_run'] = run
        
else:
    # reset = True 且已经处理过的状态
    if unwrap_mesh.cache['result'][0] is not None:
        unwrap_mesh.cache['result'] = (None, None, None)
        unwrap_mesh.cache['last_method'] = -1
        unwrap_mesh.cache['last_symmetry'] = False
    unwrapped_mesh, uv_points, uv_mesh = (None, None, None)


# ================================================================================
# 可选: 输出调试信息（取消注释以启用）
# ================================================================================

# 如果需要输出详细的调试信息，取消以下行的注释
"""
if input_mesh and run and not reset:
    print("\n[调试信息]")
    print(f"  - 输入网格: {get_mesh_statistics(input_mesh)}")
    print(f"  - UV点数量: {len(uv_points)}")
    print(f"  - UV网格顶点: {uv_mesh.Vertices.Count if uv_mesh else 0}")
    print(f"  - UV网格面数: {uv_mesh.Faces.Count if uv_mesh else 0}")
"""

# ================================================================================
# 使用说明（在 Grasshopper 中右键组件可查看）
# ================================================================================

"""
===============================================================================
使用说明
===============================================================================

【快速开始】
1. 连接一个网格到 input_mesh
2. 连接 Boolean Toggle 到 run，并设置为 True
3. 连接 Value List 到 method，选择展开方法
4. 查看 uv_mesh 输出查看展开结果

【对称功能】
1. 连接 Boolean Toggle 到 use_symmetry，设置为 True
2. 可选: 连接 Plane 组件到 symmetry_plane
3. 如果不连接 Plane，自动使用 World XY 平面

【控制选项】
- Run (True/False): 控制是否执行展开
- Reset (Button): 点击清空所有输出
- Method (0/1/2): LSCM=0, ABFPP=1, ARAP=2

【输出说明】
- unwrapped_mesh: 原始网格 + UV 坐标（可用于进一步处理）
- uv_points: UV 坐标点云（可用于可视化 UV 分布）
- uv_mesh: UV 空间的平面网格（可直接查看展开形状）

【常见问题】
Q: 展开失败怎么办？
A: 检查网格是否为流形网格，尝试简化网格或使用 LSCM 方法

Q: 对称不起作用？
A: 确保网格本身具有对称性，且对称平面位置正确

Q: UV 网格显示不完整？
A: 检查 uv_mesh 输出是否有数据，可能需要缩放视图

===============================================================================
"""
