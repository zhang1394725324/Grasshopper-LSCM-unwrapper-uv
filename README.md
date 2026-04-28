# Grasshopper-LSCM-unwrapper-uv

Grasshopper LSCM纹理映射脚本 <br>
**通过deepseek生成实现。** <br>
**适用于Mac和Windows** <br>

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


![这是图片](GH_LSCM_image.png "GH_LSCM")


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

![这是GH_UV_unwrapp](GH_UV_unwrapp.png "GH_UV_unwrapp")
