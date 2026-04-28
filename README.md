# Grasshopper-LSCM-unwrapper-uv

Grasshopper LSCM纹理映射脚本 <br>
**通过deepseek生成实现。** <br>
**适用于Mac和Windows** <br>
**适用版本：Rhino8** <br>

## Grasshopper 组件设置(GH_LSCM.py)

| 输入参数         | 类型    | 设置                                                           |
| ------------------ | --------- | ---------------------------------------------------------------- |
| `input_mesh` | Mesh    | 连接你的网格数据                                               |
| `run`        | Boolean | 使用 **Boolean Toggle**                                  |
| `reset`      | Boolean | 使用 **Button**      |
| **输出**       |         |                      |
| `unwrapped_mesh` | Mesh    | 带有UV坐标的原始网格 |
| `uv_points`      | Point3d | UV坐标点云           |
| `uv_mesh`        | Mesh    | UV空间的平面网格     |


![这是GH_LSCM.py](GH_LSCM_image.png "GH_LSCM")


## Grasshopper 设置(GH_UV_unwrapp.py)

| 输入参数         | 类型    | 说明     | 设置                                             |
| ------------------ | --------- | ---------- | -------------------------------------------------- |
| `input_mesh` | Mesh    | 输入网格 | 连接你的网格                                     |
| `run`        | Boolean | 运行控制 | **Boolean Toggle**                         |
| `reset`      | Boolean | 复位按钮 | **Button**                                 |
| `method`     | Integer | 方法选择 | **Integer Slider** 或 **Value List** |
| **输出**       |         |                      |
| `unwrapped_mesh` | Mesh    | 带有UV坐标的原始网格 |
| `uv_points`      | Point3d | UV坐标点云           |
| `uv_mesh`        | Mesh    | UV空间的平面网格     |

1. ### 推荐的 Value List 设置
   
   在 Grasshopper 中为 `method` 输入添加 **Value List**：

| 名称  | 值 | 说明                        |
| ----- | -- | --------------------------- |
| LSCM  | 0  | 最小二乘共形映射 (最均衡)   |
| ABF++ | 1  | 基于角度的展平 (保角性好)   |
| ARAP  | 2  | 尽可能刚性的展平 (保面积好) |

2. ### 三种方法的特点对比



| 方法      | 特点                               | 适用场景                   |
| --------- | ---------------------------------- | -------------------------- |
| **LSCM**  | 最小二乘共形映射，平衡保角性和拉伸 | 一般用途，最常用           |
| **ABF++** | 基于角度的展平，保角性最好         | 需要保持形状的纹理映射     |
| **ARAP**  | 尽可能刚性，保面积好               | 减少面积变形，适合物理模拟 |


![这是GH_UV_unwrapp](GH_UV_unwrapp_image.png "GH_UV_unwrapp")
