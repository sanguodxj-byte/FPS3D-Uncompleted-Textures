# FPS3D 建筑模型交付规范（GLB）

所有 `models/*.glb` 都必须满足本规范。提交前运行 `python3 tools/validate_glb.py`（需 `pip install numpy`），全部通过才能提交；
`tools/hooks/pre-commit` 会对暂存的 GLB 自动执行同一校验：
`cp tools/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`。

## A. 文件结构（自动校验）
1. **只含本体网格**：一个 mesh（名 `Body`）、一个网格节点。**不得带 Outline 描边网格、节点或材质**；描边由模组引擎 `BuildHull` 按本体几何统一生成（方案 A）。
2. **必须写入法线**：每个图元都有 `POSITION`、`NORMAL`、`TEXCOORD_0`。法线归一化、朝外，与三角形绕序（逆时针为正面）一致；硬边低模用逐面平直法线（顶点按面拆分）。
3. **应用全部变换**：网格节点没有平移、旋转或缩放，几何直接位于模型坐标系。
4. **接地**：本体最低点精确在 `Y = 0`，误差不超过 2 mm，不得悬空或下陷。例外是炮塔可旋转部件 `__Top`，它的原点就是与基座共用的枢轴。
5. **材质**：`KHR_materials_unlit`，带 `baseColorTexture`；贴图为内嵌 PNG，不外链；UV 在 0–1 之内。
6. **元数据**：`asset.extras` 包含 `defName`、`label`、`sources`、`size_cells`；变体写 `variant`，炮塔顶部写 `part: turretTop`。

## B. 坐标与命名
- 坐标：+X 东，+Y 上，+Z 南（正面），单位米，1 格 = 1 m；`size_cells` 和 MANIFEST/维基一致。
- 文件：`Building_<Def>.glb`；贴图变体为 `Building_<Def>__<变体>.glb`；炮塔分成基座 `Building_X.glb` 和炮身 `Building_X__Top.glb`，炮管朝 -Z。

## C. 贴图与外观（人工审核）
- 贴图取自本仓库原版 PNG。精灵图的黑描边、轮廓线（宽度不到 3 px 的深色线）必须先去掉再贴到 3D 面上，否则会放大成黑条或黑印。隐藏面和底面不得用近黑色。
- UV 语义要对：屏幕、面板、门、格栅贴在功能面上。终端的斜面控制板贴在斜面上，不能贴到侧面、顶面或背面。可见面上不得出现洋红、透明穿帮或描边条纹。
- 形体按真实结构拆件：圆形件用圆柱或旋转体；动物、人像等有机形体用多段椭球拼，侧影要和精灵图一致，禁止竖直堆叠成“雪人”。部件之间不得悬空、断开，也不得明显穿插。
- 每个模型都要出 8 方位印相图，与 south/east 贴图对照审核：不看文件名能认出是什么，尺寸、朝向和变体差异都正确。连续三轮不合格的标 blocked，不提交。

## 修订
- 2026-10-15：去掉 Outline 网格，必须写入 NORMAL，接地 Y=0，并应用全部变换。起因是引擎侧报告“法线缺失导致光照错误、个别模型悬空或下陷”。精灵墨线须全局去除。
