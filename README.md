# FPS3D-Uncompleted-Textures

RimWorld 1.7 第一人称模组（FirstPerson3D）待建模物体原版/DLC贴图素材库。

## 仓库说明
本仓库汇集了 RimWorld 1.7 官方本体（Core）及全 DLC（Royalty、Ideology、Biotech、Anomaly、Odyssey）中当前**尚未完成 3D 几何建模**的所有建筑、地面物品与树木的全部原版高清纹理（已从 DDS 解包并转为标准 RGBA PNG 格式），供 3D 建模师作为三维造型与 UV 贴图的基准参考。

## 范围约定（已排除无需建模类别）
- **手持武器枪械**：第一人称下按原版 UI 图标在视口手部绘制，无需 3D 实体模型。
- **人形 Pawn**：由原版 RenderTree/烘焙图集处理，无需额外建模。
- **草地与普通植被/农作物/花卉/草本**：全部保持当前十字交叉面片（CrossMesh）与草地风吹摇摆着色器方式，观感自然且节省性能，无需 3D 实体模型；**仅对大型乔木/树木进行 3D 建模**。

> 说明：`Pawn 生物` 豁免的**只有人形**。动物与机械族全部纳入，见下。

## 动物模块

动物与机械族是独立模块，与建筑/物品/树木并列：

- 贴图：`Animal_<DefName>_<east|south|north>.png`（单图实体为 `_single`）
- 索引：`INDEX_ANIMALS.md`
- 进度：`PROGRESS_ANIMALS.md`
- 规范：`docs/ANIMAL_SPEC.md`
- 模型：`models/Animal_<DefName>.glb`
- 预览：`previews/ANIM_*.png`

模块范围**包含机械族与无人机**（`Mech_*` / `Drone_*`），它们使用硬边块体建模，与有机形体的椭球分段是两套手法，批次分开排。

统计：待建模 42 种（机械族与无人机 24 / 有机形体 17 / 暂缓 1），贴图 118 张。

## 提交前门禁

`tools/hooks/pre-commit` 会在提交前检查暂存的 GLB 是否符合 `docs/GLB_SPEC.md`，
不符则拦下。克隆仓库后执行一次启用：

```sh
git config core.hooksPath tools/hooks
```

## 文件架构与命名规范
- 全仓库遵循**完全扁平化架构**，所有贴图直放在根目录下，无任何子文件夹嵌套。
- 命名规范：`<类别>_<DefName>_<子部件/视角/状态>.png`
  - 建筑：`Building_<DefName>_...`
  - 地面物品：`Item_<DefName>_...`
  - 树木：`Plant_<DefName>_...`
  - 动物：`Animal_<DefName>_...`
- 完整映射关系详见 `MANIFEST.json` 与 `INDEX.md`（建筑/物品/树木）、`INDEX_ANIMALS.md`（动物）。

## 统计概览
- 涵盖待建模物体定义总数：845 种（建筑: 409, 地面物品: 408, 树木: 28）
- 导出标准 PNG 贴图总数：2674 张
